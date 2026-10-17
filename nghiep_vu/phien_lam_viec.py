# Phần C
# Phiên làm việc và quản lý tài khoản: đăng nhập, đăng xuất, tạo tài khoản, đổi mật khẩu.
# Triển khai GiaoThucPhienLamViec; nhận tầng lưu trữ tài khoản qua hàm khởi tạo (tiêm phụ thuộc),
# nên file này không biết dữ liệu nằm ở đâu, chỉ gọi doc/ghi qua GiaoThucLuuTru.
#
# Lưu ý quan trọng: ở đây KHÔNG dùng TaiKhoan.kiem_tra() và TaiKhoan.doi_mat_khau() của thực thể,
# vì hiện hai hàm đó là hàm giữ chỗ của phần B (kiem_tra luôn trả True => ai nhập mật khẩu gì cũng qua).
# Việc so mật khẩu tự làm bằng tien_ich/bam_mat_khau.py; đổi mật khẩu thì tạo lại đối tượng TaiKhoan mới.
from functools import cache

from giao_thuc.luu_tru import GiaoThucLuuTru
from giao_thuc.nghiep_vu import GiaoThucPhienLamViec
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from tien_ich.bam_mat_khau import bam_mat_khau, kiem_tra_mat_khau
from tien_ich.regex import la_ma_sinh_vien, la_mat_khau, la_ten_dang_nhap

# Dùng chung một thông báo cho "không có tài khoản" và "sai mật khẩu" để người ngoài
# không dò được tên đăng nhập nào tồn tại.
_LOI_SAI_THONG_TIN = "Sai tên đăng nhập hoặc mật khẩu"


@cache
def _ma_bam_gia() -> str:
    """Mã băm giả, tính một lần khi cần. Dùng để khi tên đăng nhập không tồn tại ta vẫn tốn
    thời gian băm như bình thường, tránh lộ 'tên này không có' qua việc trả lời nhanh hơn."""
    return bam_mat_khau("mat-khau-gia-chi-de-can-thoi-gian")


class PhienLamViec(GiaoThucPhienLamViec):
    def __init__(self, luu_tru_tai_khoan: GiaoThucLuuTru[TaiKhoan]) -> None:
        self._luu_tru = luu_tru_tai_khoan
        self._tai_khoan_hien_tai: TaiKhoan | None = None  # None = chưa ai đăng nhập

    # ---- Hàm hỗ trợ nội bộ ----
    def _doc_tai_khoan(self) -> list[TaiKhoan]:
        """
        Đọc danh sách tài khoản. Nếu file chính hỏng hoặc bị sửa ngoài app (ValueError) thì
        đọc từ file sao lưu rồi ghi ngược lại để khôi phục file chính. Nếu sao lưu cũng hỏng thì
        để ValueError nổi lên cho giao diện báo lỗi.
        """
        try:
            return self._luu_tru.doc()
        except ValueError:
            danh_sach = self._luu_tru.doc_sao_luu()
            self._luu_tru.ghi(danh_sach)
            return danh_sach

    @staticmethod
    def _tim(danh_sach: list[TaiKhoan], ten_dang_nhap: str) -> TaiKhoan | None:
        return next((tk for tk in danh_sach if tk.ma == ten_dang_nhap), None)

    def _thay_the(self, danh_sach: list[TaiKhoan], cu: TaiKhoan, mat_khau_bam_moi: str) -> TaiKhoan:
        """
        Đổi mật khẩu bằng cách dựng một TaiKhoan mới (thực thể không có setter cho mật khẩu),
        giữ nguyên tên, loại, chủ thể và trạng thái hoạt động; thay vào đúng vị trí cũ rồi ghi xuống file.
        """
        moi = TaiKhoan(cu.ma, mat_khau_bam_moi, cu.loai_tai_khoan, cu.ma_chu_the)
        if not cu.con_hoat_dong:
            moi.luu_tru()
        vi_tri = danh_sach.index(cu)
        danh_sach[vi_tri] = moi
        self._luu_tru.ghi(danh_sach)
        # Nếu vừa đổi mật khẩu của chính người đang đăng nhập thì cập nhật đối tượng đang giữ
        if self._tai_khoan_hien_tai is not None and self._tai_khoan_hien_tai.ma == moi.ma:
            self._tai_khoan_hien_tai = moi
        return moi

    # ---- Giao thức ----
    @property
    def tai_khoan_hien_tai(self) -> TaiKhoan | None:
        return self._tai_khoan_hien_tai

    def tao_tai_khoan(self, tai_khoan: str, mat_khau: str, loai_tai_khoan: LoaiTaiKhoan, ma_chu_the: str | None) -> None:
        """
        Tạo tài khoản mới (mật khẩu được băm trước khi lưu).

        Quy tắc:
          - Chỉ quản trị viên đang đăng nhập mới được tạo tài khoản.
          - Ngoại lệ: khi hệ thống CHƯA có tài khoản nào thì cho tạo, nhưng bắt buộc là quản trị viên
            (nếu không sẽ không có ai để đăng nhập lần đầu).
          - Tài khoản sinh viên phải có mã sinh viên hợp lệ, và mỗi sinh viên chỉ có một tài khoản.
        Ném ValueError nếu vi phạm.
        """
        if not la_ten_dang_nhap(tai_khoan):
            raise ValueError("Tên đăng nhập gồm 3-30 ký tự: chữ không dấu, số, dấu _ hoặc dấu .")
        if not la_mat_khau(mat_khau):
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")
        if not isinstance(loai_tai_khoan, LoaiTaiKhoan):
            raise ValueError("Loại tài khoản không hợp lệ")

        danh_sach = self._doc_tai_khoan()

        # Kiểm tra quyền
        if danh_sach:
            if self._tai_khoan_hien_tai is None:
                raise ValueError("Cần đăng nhập bằng tài khoản quản trị để tạo tài khoản")
            if not self._tai_khoan_hien_tai.co_quyen_quan_tri:
                raise ValueError("Chỉ quản trị viên mới được tạo tài khoản")
        elif loai_tai_khoan != LoaiTaiKhoan.QUAN_TRI_VIEN:
            raise ValueError("Tài khoản đầu tiên của hệ thống phải là quản trị viên")

        if self._tim(danh_sach, tai_khoan) is not None:
            raise ValueError("Tên đăng nhập đã tồn tại")

        # Mã chủ thể: sinh viên thì bắt buộc, quản trị viên thì không có
        if loai_tai_khoan == LoaiTaiKhoan.SINH_VIEN:
            if ma_chu_the is None or not la_ma_sinh_vien(ma_chu_the):
                raise ValueError("Tài khoản sinh viên cần có mã sinh viên hợp lệ")
            if any(tk.ma_chu_the == ma_chu_the for tk in danh_sach):
                raise ValueError("Sinh viên này đã có tài khoản")
        else:
            ma_chu_the = None

        moi = TaiKhoan(tai_khoan, bam_mat_khau(mat_khau), loai_tai_khoan, ma_chu_the)
        self._luu_tru.ghi([moi], ghi_de=False)  # ghi thêm vào cuối, không đụng các tài khoản cũ

    def dang_nhap(self, tai_khoan: str, mat_khau: str) -> None:
        """Đăng nhập. Ném ValueError nếu đã đăng nhập, sai thông tin, hoặc tài khoản đã ngừng hoạt động."""
        if self._tai_khoan_hien_tai is not None:
            raise ValueError("Đã đăng nhập, hãy đăng xuất trước")

        tk = self._tim(self._doc_tai_khoan(), tai_khoan)
        if tk is None:
            kiem_tra_mat_khau(mat_khau, _ma_bam_gia())  # làm cho tốn thời gian như trường hợp có tài khoản
            raise ValueError(_LOI_SAI_THONG_TIN)
        if not kiem_tra_mat_khau(mat_khau, tk.mat_khau_bam):
            raise ValueError(_LOI_SAI_THONG_TIN)
        if not tk.con_hoat_dong:  # chỉ báo cho người đã nhập ĐÚNG mật khẩu
            raise ValueError("Tài khoản đã ngừng hoạt động")
        self._tai_khoan_hien_tai = tk

    def dang_xuat(self) -> None:
        """Đăng xuất. Ném ValueError nếu chưa đăng nhập."""
        if self._tai_khoan_hien_tai is None:
            raise ValueError("Chưa đăng nhập")
        self._tai_khoan_hien_tai = None

    def doi_mat_khau(self, mat_khau_moi: str, mat_khau_cu: str | None = None, tai_khoan: str | None = None) -> None:
        """
        Đổi mật khẩu.
          - tai_khoan=None: tự đổi mật khẩu của mình, BẮT BUỘC có mat_khau_cu đúng.
          - có tai_khoan: quản trị viên đặt lại mật khẩu cho tài khoản đó, không cần mat_khau_cu.
        Ném ValueError nếu: chưa đăng nhập, mật khẩu mới không hợp lệ, mật khẩu cũ sai/thiếu,
        không có quyền quản trị, hoặc tài khoản đích không tồn tại.
        """
        if self._tai_khoan_hien_tai is None:
            raise ValueError("Chưa đăng nhập")
        if not la_mat_khau(mat_khau_moi):
            raise ValueError("Mật khẩu mới phải có ít nhất 6 ký tự")

        danh_sach = self._doc_tai_khoan()

        if tai_khoan is None:
            # Tự đổi: lấy bản MỚI NHẤT trong file (không dùng đối tượng đã giữ từ lúc đăng nhập, có thể đã cũ)
            hien_tai = self._tim(danh_sach, self._tai_khoan_hien_tai.ma)
            if hien_tai is None:
                raise ValueError("Tài khoản hiện tại không còn tồn tại")
            if mat_khau_cu is None:
                raise ValueError("Cần nhập mật khẩu cũ")
            if not kiem_tra_mat_khau(mat_khau_cu, hien_tai.mat_khau_bam):
                raise ValueError("Mật khẩu cũ không đúng")
            if mat_khau_cu == mat_khau_moi:
                raise ValueError("Mật khẩu mới phải khác mật khẩu cũ")
            self._thay_the(danh_sach, hien_tai, bam_mat_khau(mat_khau_moi))
        else:
            # Quản trị viên đặt lại mật khẩu cho tài khoản khác
            if not self._tai_khoan_hien_tai.co_quyen_quan_tri:
                raise ValueError("Chỉ quản trị viên mới được đặt lại mật khẩu của tài khoản khác")
            dich = self._tim(danh_sach, tai_khoan)
            if dich is None:
                raise ValueError("Tài khoản không tồn tại")
            self._thay_the(danh_sach, dich, bam_mat_khau(mat_khau_moi))
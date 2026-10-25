# Phần C
# Phiên làm việc và quản lý tài khoản: đăng nhập, đăng xuất, tạo tài khoản, đổi mật khẩu.
# Triển khai GiaoThucPhienLamViec; nhận tầng lưu trữ tài khoản qua hàm khởi tạo (tiêm phụ thuộc),
# nên file này không biết dữ liệu nằm ở đâu, chỉ gọi doc/ghi qua GiaoThucLuuTru.
#
# Cách làm việc với dữ liệu: danh sách tài khoản chỉ được ĐỌC TỪ FILE MỘT LẦN lúc khởi tạo rồi giữ trong
# bộ nhớ (self._tai_khoan). Mọi thao tác sau đó (đăng nhập, tạo tài khoản, đổi mật khẩu) làm việc trên bản
# trong bộ nhớ, và chỉ GHI xuống file khi có thay đổi; không đọc lại file.
#
# Xác thực dùng TaiKhoan.kiem_tra(mat_khau) (bên trong gọi tiện ích tien_ich/bam_mat_khau); đổi mật khẩu dùng
# TaiKhoan.doi_mat_khau(). Mật khẩu chỉ được băm ở đây trước khi lưu, không bao giờ lưu mật khẩu gốc.
from functools import cache

from giao_thuc.luu_tru import GiaoThucLuuTru
from giao_thuc.nghiep_vu import GiaoThucPhienLamViec
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from tien_ich.bam_mat_khau import bam_mat_khau, kiem_tra_mat_khau
from tien_ich.regex import la_ma_sinh_vien, la_mat_khau, la_ten_dang_nhap

# Dùng chung một thông báo cho "không có tài khoản" và "sai mật khẩu" để người ngoài
# không dò được tên đăng nhập nào tồn tại.
_LOI_SAI_THONG_TIN = "Sai tên đăng nhập hoặc mật khẩu"
_LOI_MAT_KHAU = "Mật khẩu phải có ít nhất 6 ký tự, chỉ gồm chữ cái tiếng Anh không dấu, chữ số và ký hiệu (không có khoảng trắng)"


@cache
def _ma_bam_gia() -> str:
    """Mã băm giả, tính một lần khi cần. Dùng để khi tên đăng nhập không tồn tại ta vẫn tốn
    thời gian băm như bình thường, tránh lộ 'tên này không có' qua việc trả lời nhanh hơn."""
    return bam_mat_khau("mat-khau-gia-chi-de-can-thoi-gian")


class PhienLamViec(GiaoThucPhienLamViec):
    def __init__(self, luu_tru_tai_khoan: GiaoThucLuuTru[TaiKhoan]) -> None:
        self._luu_tru = luu_tru_tai_khoan
        # Đọc file đúng MỘT lần ở đây; dict {tên đăng nhập: TaiKhoan}
        self._tai_khoan: dict[str, TaiKhoan] = self._doc_luc_khoi_dong()
        self._tai_khoan_hien_tai: TaiKhoan | None = None  # None = chưa ai đăng nhập

    # ---- Hàm hỗ trợ nội bộ ----
    def _doc_luc_khoi_dong(self) -> dict[str, TaiKhoan]:
        """
        Đọc danh sách tài khoản lúc khởi động.
          - File chính đọc được: dùng luôn.
          - File chính chưa có (lần chạy đầu) mà cũng không có sao lưu: danh sách rỗng (sẽ tạo quản trị viên đầu tiên).
          - File chính hỏng / bị sửa ngoài app / bị xóa: đọc từ file sao lưu rồi ghi ngược lại để khôi phục file chính.
          - File chính hỏng mà không có sao lưu, hoặc sao lưu cũng hỏng: ném ValueError để giao diện báo lỗi,
            tuyệt đối không khởi động với danh sách rỗng vì sẽ mất hết tài khoản.
        Danh sách tài khoản do lớp này tự quản lý nên tự xử lý luôn, không nhờ tầng điều phối.
        """
        try:
            return dict(self._luu_tru.doc())
        except (FileNotFoundError, ValueError) as loi_chinh:
            try:
                du_lieu = dict(self._luu_tru.doc_sao_luu())
            except FileNotFoundError:
                if isinstance(loi_chinh, FileNotFoundError):
                    return {}  # chưa có file nào: lần chạy đầu tiên
                raise loi_chinh  # file chính hỏng mà không có sao lưu để khôi phục
            self._luu_tru.ghi(du_lieu)  # khôi phục file chính từ bản sao lưu
            return du_lieu

    def _luu(self, tai_khoan_moi: dict[str, TaiKhoan]) -> None:
        """
        Ghi bản danh sách mới xuống file, GHI THÀNH CÔNG rồi mới thay bản trong bộ nhớ.
        Nhờ vậy nếu ghi file lỗi thì bộ nhớ vẫn khớp với file, không bị lệch.
        """
        self._luu_tru.ghi(tai_khoan_moi)
        self._tai_khoan = tai_khoan_moi

    def _doi_mat_khau_bam(self, tai_khoan: TaiKhoan, mat_khau_bam_moi: str) -> None:
        """
        Đổi mật khẩu bằng TaiKhoan.doi_mat_khau() của thực thể (sửa tại chỗ, nên người đang đăng nhập
        cũng thấy ngay vì dùng chung một đối tượng), rồi ghi xuống file.
        Ghi file lỗi thì trả lại mật khẩu cũ để bộ nhớ vẫn khớp với file.
        """
        mat_khau_bam_cu = tai_khoan.mat_khau_bam
        tai_khoan.doi_mat_khau(mat_khau_bam_moi)
        try:
            self._luu_tru.ghi(self._tai_khoan)
        except Exception:
            tai_khoan.doi_mat_khau(mat_khau_bam_cu)
            raise

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
            raise ValueError(_LOI_MAT_KHAU)
        if not isinstance(loai_tai_khoan, LoaiTaiKhoan):
            raise ValueError("Loại tài khoản không hợp lệ")

        # Kiểm tra quyền
        if self._tai_khoan:
            if self._tai_khoan_hien_tai is None:
                raise ValueError("Cần đăng nhập bằng tài khoản quản trị để tạo tài khoản")
            if not self._tai_khoan_hien_tai.co_quyen_quan_tri:
                raise ValueError("Chỉ quản trị viên mới được tạo tài khoản")
        elif loai_tai_khoan != LoaiTaiKhoan.QUAN_TRI_VIEN:
            raise ValueError("Tài khoản đầu tiên của hệ thống phải là quản trị viên")

        if tai_khoan in self._tai_khoan:
            raise ValueError("Tên đăng nhập đã tồn tại")

        # Mã chủ thể: sinh viên thì bắt buộc, quản trị viên thì không có
        if loai_tai_khoan == LoaiTaiKhoan.SINH_VIEN:
            if ma_chu_the is None or not la_ma_sinh_vien(ma_chu_the):
                raise ValueError("Tài khoản sinh viên cần có mã sinh viên hợp lệ")
            if any(tk.ma_chu_the == ma_chu_the for tk in self._tai_khoan.values()):
                raise ValueError("Sinh viên này đã có tài khoản")
        else:
            ma_chu_the = None

        moi = TaiKhoan(tai_khoan, bam_mat_khau(mat_khau), loai_tai_khoan, ma_chu_the)
        self._luu({**self._tai_khoan, tai_khoan: moi})

    def dang_nhap(self, tai_khoan: str, mat_khau: str) -> None:
        """Đăng nhập. Ném ValueError nếu đã đăng nhập, sai thông tin, hoặc tài khoản đã ngừng hoạt động."""
        if self._tai_khoan_hien_tai is not None:
            raise ValueError("Đã đăng nhập, hãy đăng xuất trước")

        tk = self._tai_khoan.get(tai_khoan)
        if tk is None:
            kiem_tra_mat_khau(mat_khau, _ma_bam_gia())  # làm cho tốn thời gian như trường hợp có tài khoản
            raise ValueError(_LOI_SAI_THONG_TIN)
        if not tk.kiem_tra(mat_khau):
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
            raise ValueError(_LOI_MAT_KHAU)

        if tai_khoan is None:
            hien_tai = self._tai_khoan.get(self._tai_khoan_hien_tai.ma)
            if hien_tai is None:
                raise ValueError("Tài khoản hiện tại không còn tồn tại")
            if mat_khau_cu is None:
                raise ValueError("Cần nhập mật khẩu cũ")
            if not hien_tai.kiem_tra(mat_khau_cu):
                raise ValueError("Mật khẩu cũ không đúng")
            if mat_khau_cu == mat_khau_moi:
                raise ValueError("Mật khẩu mới phải khác mật khẩu cũ")
            self._doi_mat_khau_bam(hien_tai, bam_mat_khau(mat_khau_moi))
        else:
            # Quản trị viên đặt lại mật khẩu cho tài khoản khác
            if not self._tai_khoan_hien_tai.co_quyen_quan_tri:
                raise ValueError("Chỉ quản trị viên mới được đặt lại mật khẩu của tài khoản khác")
            dich = self._tai_khoan.get(tai_khoan)
            if dich is None:
                raise ValueError("Tài khoản không tồn tại")
            self._doi_mat_khau_bam(dich, bam_mat_khau(mat_khau_moi))
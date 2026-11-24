# Phần C
# Phiên làm việc và quản lý tài khoản: đăng nhập, đăng xuất, tạo tài khoản, đổi mật khẩu,
# ngừng / kích hoạt lại / xóa tài khoản. Triển khai GiaoThucPhienLamViec.
#
# Theo quy ước của hệ thống, dữ liệu tài khoản do TẦNG ĐIỀU PHỐI nắm (nạp lên bộ nhớ một lần lúc khởi động và ghi
# xuống file mỗi khi thay đổi). Vì vậy lớp này KHÔNG đọc hay ghi file nào cả: nó nhận một GiaoThucDieuPhoi qua hàm
# khởi tạo (tiêm phụ thuộc), hỏi danh sách tài khoản và nhờ điều phối thực hiện mọi thay đổi, còn bản thân chỉ lo
# phần luật của tài khoản (quyền quản trị, không tự ngừng chính mình, không xóa quản trị viên cuối cùng...).
# Thêm tài khoản dùng them() của điều phối (mã tài khoản là tên đăng nhập người dùng nhập, không sinh tự động).
# Giao diện không được gọi điều phối trực tiếp cho TaiKhoan mà phải đi qua lớp này.
#
# Mật khẩu: chỉ băm ở đây trước khi lưu (tien_ich/bam_mat_khau), không bao giờ lưu mật khẩu gốc.
# Xác thực dùng TaiKhoan.kiem_tra(mat_khau); đổi mật khẩu dùng TaiKhoan.doi_mat_khau().
from functools import cache

from nghiep_vu.dieu_phoi import DieuPhoiKTX
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from tien_ich.bam_mat_khau import bam_mat_khau, kiem_tra_mat_khau
from tien_ich.regex import la_ma_sinh_vien, la_mat_khau, la_ten_dang_nhap

# Dùng chung một thông báo cho "không có tài khoản" và "sai mật khẩu" để người ngoài
# không dò được tên đăng nhập nào tồn tại.
_LOI_SAI_THONG_TIN = "Sai tên đăng nhập hoặc mật khẩu"
_LOI_MAT_KHAU = "Mật khẩu phải có ít nhất 5 ký tự, chỉ gồm chữ cái tiếng Anh không dấu, chữ số và ký hiệu (không có khoảng trắng)"


@cache
def _ma_bam_gia() -> str:
    """Mã băm giả, tính một lần khi cần. Dùng để khi tên đăng nhập không tồn tại ta vẫn tốn
    thời gian băm như bình thường, tránh lộ 'tên này không có' qua việc trả lời nhanh hơn."""
    return bam_mat_khau("mat-khau-gia-chi-de-can-thoi-gian")


class PhienLamViec:
    """
    Giao thức phiên làm việc của hệ thống.
    Yêu cầu nhận vào một đối tượng GiaoThucDieuPhoi để thực hiện các thao tác nghiệp vụ liên quan đến tài khoản.
    """
    def __init__(self, dieu_phoi: DieuPhoiKTX) -> None:
        self._dieu_phoi = dieu_phoi
        self._tai_khoan_hien_tai: TaiKhoan | None = None  # None = chưa ai đăng nhập

    # ---- Hàm hỗ trợ nội bộ ----
    def _tat_ca(self) -> dict[str, TaiKhoan]:
        """Mọi tài khoản, kể cả đã ngừng hoạt động (lay_luu_tru=True). Lấy từ điều phối mỗi lần để luôn khớp dữ liệu hiện có."""
        return self._dieu_phoi.lay_tat_ca(TaiKhoan, lay_luu_tru=True)

    def _yeu_cau_quan_tri(self, thong_bao_khong_co_quyen: str) -> TaiKhoan:
        """Trả về tài khoản đang đăng nhập nếu là quản trị viên; ngược lại ném ValueError."""
        if self._tai_khoan_hien_tai is None:
            raise ValueError("Chưa đăng nhập")
        if not self._tai_khoan_hien_tai.co_quyen_quan_tri:
            raise ValueError(thong_bao_khong_co_quyen)
        return self._tai_khoan_hien_tai

    def _them_tai_khoan(self, tai_khoan: TaiKhoan) -> None:
        """
        Nhờ điều phối thêm một TaiKhoan đã dựng sẵn.
        Dùng them() chứ KHÔNG dùng tao_va_them(): tao_va_them chỉ dành cho thực thể có mã sinh tự động,
        còn mã của tài khoản chính là tên đăng nhập do người dùng nhập.
        """
        self._dieu_phoi.them(tai_khoan)

    def _dat_mat_khau_bam(self, tai_khoan: TaiKhoan, mat_khau_bam_moi: str) -> None:
        """
        Đổi mật khẩu bằng TaiKhoan.doi_mat_khau() rồi nhờ điều phối cập nhật.
        Lưu ý: lay_tat_ca của điều phối trả về BẢN SAO, nên sửa tại đây chưa ảnh hưởng dữ liệu thật cho đến khi cap_nhat thành công.
        Điều phối báo lỗi thì trả lại mật khẩu cũ trên bản sao này.
        """
        mat_khau_bam_cu = tai_khoan.mat_khau_bam
        tai_khoan.doi_mat_khau(mat_khau_bam_moi)
        try:
            self._dieu_phoi.cap_nhat(tai_khoan)
        except Exception:
            tai_khoan.doi_mat_khau(mat_khau_bam_cu)
            raise
        # Bản đang giữ cho người đăng nhập là một bản sao khác, nên đổi mật khẩu của chính họ thì phải làm mới nó
        if self._tai_khoan_hien_tai is not None and self._tai_khoan_hien_tai.ma == tai_khoan.ma:
            self._tai_khoan_hien_tai = tai_khoan

    # ---- Giao thức ----
    @property
    def tai_khoan_hien_tai(self) -> TaiKhoan | None:
        """
        - Tài khoản đang sử dụng hiện tại.
        """
        return self._tai_khoan_hien_tai

    def tao_tai_khoan(self, tai_khoan: str, mat_khau: str, loai_tai_khoan: LoaiTaiKhoan, ma_chu_the: str | None) -> None:
        """
        Tạo tài khoản mới (mật khẩu được băm trước khi lưu).

        Quy tắc:
          - Chỉ quản trị viên đang đăng nhập mới được tạo tài khoản.
          - Ngoại lệ: khi hệ thống CHƯA có tài khoản nào đang hoạt động thì cho tạo mà không cần đăng nhập,
            nhưng bắt buộc là quản trị viên (nếu không sẽ không có ai để đăng nhập).
          - Tài khoản sinh viên phải có mã sinh viên hợp lệ, và mỗi sinh viên chỉ có một tài khoản.
        Ném ValueError nếu vi phạm.
        """
        if not la_ten_dang_nhap(tai_khoan):
            raise ValueError("Tên đăng nhập gồm 3-30 ký tự: chữ không dấu, số, dấu _ hoặc dấu .")
        if not la_mat_khau(mat_khau):
            raise ValueError(_LOI_MAT_KHAU)
        if not isinstance(loai_tai_khoan, LoaiTaiKhoan):
            raise ValueError("Loại tài khoản không hợp lệ")

        tat_ca = self._tat_ca()

        # Kiểm tra quyền
        if any(tk.con_hoat_dong for tk in tat_ca.values()):
            self._yeu_cau_quan_tri("Chỉ quản trị viên mới được tạo tài khoản")
        elif loai_tai_khoan != LoaiTaiKhoan.QUAN_TRI_VIEN:
            raise ValueError("Tài khoản đầu tiên của hệ thống phải là quản trị viên")

        if tai_khoan in tat_ca:  # kể cả tài khoản đã ngừng: tên vẫn thuộc về nó
            raise ValueError("Tên đăng nhập đã tồn tại")

        # Mã chủ thể: sinh viên thì bắt buộc, quản trị viên thì không có
        if loai_tai_khoan == LoaiTaiKhoan.SINH_VIEN:
            if ma_chu_the is None or not la_ma_sinh_vien(ma_chu_the):
                raise ValueError("Tài khoản sinh viên cần có mã sinh viên hợp lệ")
            if any(tk.ma_chu_the == ma_chu_the for tk in tat_ca.values()):
                raise ValueError("Sinh viên này đã có tài khoản")
        else:
            ma_chu_the = None

        self._them_tai_khoan(TaiKhoan(tai_khoan, bam_mat_khau(mat_khau), loai_tai_khoan, ma_chu_the))

    def dang_nhap(self, tai_khoan: str, mat_khau: str) -> None:
        """Đăng nhập. Ném ValueError nếu đã đăng nhập, sai thông tin, hoặc tài khoản đã ngừng hoạt động."""
        if self._tai_khoan_hien_tai is not None:
            raise ValueError("Đã đăng nhập, hãy đăng xuất trước")

        tk = self._tat_ca().get(tai_khoan)
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

        tat_ca = self._tat_ca()
        if tai_khoan is None:
            hien_tai = tat_ca.get(self._tai_khoan_hien_tai.ma)
            if hien_tai is None:
                raise ValueError("Tài khoản hiện tại không còn tồn tại")
            if mat_khau_cu is None:
                raise ValueError("Cần nhập mật khẩu cũ")
            if not hien_tai.kiem_tra(mat_khau_cu):
                raise ValueError("Mật khẩu cũ không đúng")
            if mat_khau_cu == mat_khau_moi:
                raise ValueError("Mật khẩu mới phải khác mật khẩu cũ")
            self._dat_mat_khau_bam(hien_tai, bam_mat_khau(mat_khau_moi))
        else:
            # Quản trị viên đặt lại mật khẩu cho tài khoản khác
            self._yeu_cau_quan_tri("Chỉ quản trị viên mới được đặt lại mật khẩu của tài khoản khác")
            dich = tat_ca.get(tai_khoan)
            if dich is None:
                raise ValueError("Tài khoản không tồn tại")
            self._dat_mat_khau_bam(dich, bam_mat_khau(mat_khau_moi))

    def ngung_tai_khoan(self, tai_khoan: str) -> None:
        """
        Ngừng hoạt động của tài khoản (không xóa, có thể kích hoạt lại sau).
        Ném ValueError nếu: chưa đăng nhập, không có quyền, tài khoản không tồn tại hoặc đã ngừng hoạt động,
        là chính tài khoản đang đăng nhập, hoặc là quản trị viên hoạt động cuối cùng.
        """
        hien_tai = self._yeu_cau_quan_tri("Chỉ quản trị viên mới được ngừng tài khoản")
        tat_ca = self._tat_ca()
        dich = tat_ca.get(tai_khoan)
        if dich is None:
            raise ValueError("Tài khoản không tồn tại")
        if not dich.con_hoat_dong:
            raise ValueError("Tài khoản đã ngừng hoạt động")
        if dich.ma == hien_tai.ma:
            raise ValueError("Không thể ngừng chính tài khoản đang đăng nhập")
        # Quản trị viên cuối cùng: ngoài tài khoản này không còn quản trị viên nào đang hoạt động
        if dich.co_quyen_quan_tri and not any(
                tk.co_quyen_quan_tri and tk.con_hoat_dong and tk.ma != dich.ma for tk in tat_ca.values()):
            raise ValueError("Không thể ngừng quản trị viên hoạt động cuối cùng")
        self._dieu_phoi.luu_tru(dich)

    def kich_hoat_lai_tai_khoan(self, tai_khoan: str) -> None:
        """
        Kích hoạt lại tài khoản đã ngừng hoạt động.
        Ném ValueError nếu: chưa đăng nhập, không có quyền, tài khoản không tồn tại, hoặc tài khoản đang hoạt động.
        """
        self._yeu_cau_quan_tri("Chỉ quản trị viên mới được kích hoạt lại tài khoản")
        dich = self._tat_ca().get(tai_khoan)
        if dich is None:
            raise ValueError("Tài khoản không tồn tại")
        if dich.con_hoat_dong:
            raise ValueError("Tài khoản đang hoạt động")
        self._dieu_phoi.tai_kich_hoat(dich)

    def xoa_tai_khoan(self, tai_khoan: str) -> None:
        """
        Xóa hẳn tài khoản khỏi hệ thống. Hạn chế dùng: chỉ xóa được tài khoản đã ngừng hoạt động.
        Ném ValueError nếu: chưa đăng nhập, không có quyền, tài khoản không tồn tại hoặc còn hoạt động,
        hoặc là chính tài khoản đang đăng nhập.
        """
        hien_tai = self._yeu_cau_quan_tri("Chỉ quản trị viên mới được xóa tài khoản")
        dich = self._tat_ca().get(tai_khoan)
        if dich is None:
            raise ValueError("Tài khoản không tồn tại")
        if dich.ma == hien_tai.ma:  # kiểm tra trước để người dùng nhận thông báo đúng (tài khoản này cũng đang hoạt động)
            raise ValueError("Không thể xóa chính tài khoản đang đăng nhập")
        if dich.con_hoat_dong:
            raise ValueError("Chỉ xóa được tài khoản đã ngừng hoạt động")
        # ep_xoa=True vì điều phối từ chối xóa mọi thực thể lưu trữ được nếu thiếu cờ này; tài khoản đã được kiểm tra là đã ngừng ở trên
        self._dieu_phoi.xoa(dich, ep_xoa=True)
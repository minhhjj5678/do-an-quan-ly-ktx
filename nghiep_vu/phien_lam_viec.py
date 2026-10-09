import hashlib
from giao_thuc.nghiep_vu import GiaoThucPhienLamViec
from thuc_the.tai_khoan import TaiKhoan, LoaiTaiKhoan
from luu_tru.luu_tru_tai_khoan import LuuTruTaiKhoan

def bam_mat_khau(mat_khau: str, salt: str = "KTX_SECRET_SALT") -> str:
    """Hàm băm mật khẩu bằng SHA256"""
    chuoi_goc = f"{salt}:{mat_khau}"
    return hashlib.sha256(chuoi_goc.encode("utf-8")).hexdigest()

class QuanLyPhienLamViec(GiaoThucPhienLamViec):
    def __init__(self, luu_tru_tai_khoan: LuuTruTaiKhoan):
        self.luu_tru = luu_tru_tai_khoan
        self._tai_khoan_hien_tai: TaiKhoan | None = None

    @property
    def tai_khoan_hien_tai(self) -> TaiKhoan | None:
        return self._tai_khoan_hien_tai

    def tao_tai_khoan(self, tai_khoan: str, mat_khau: str, loai_tai_khoan: LoaiTaiKhoan, ma_chu_the: str | None) -> None:
        danh_sach = self.luu_tru.doc()
        for tk in danh_sach:
            if tk.ma == tai_khoan:
                raise ValueError(f"Tài khoản '{tai_khoan}' đã tồn tại.")

        hash_pass = bam_mat_khau(mat_khau)
        tk_moi = TaiKhoan(
            ma_dang_nhap=tai_khoan,
            mat_khau_bam=hash_pass,
            loai_tai_khoan=loai_tai_khoan,
            ma_chu_the=ma_chu_the
        )
        danh_sach.append(tk_moi)
        self.luu_tru.ghi(danh_sach)

    def dang_nhap(self, tai_khoan: str, mat_khau: str) -> None:
        if self._tai_khoan_hien_tai is not None:
            raise ValueError("Đã có tài khoản đăng nhập. Vui lòng đăng xuất trước.")

        danh_sach = self.luu_tru.doc()
        hash_pass = bam_mat_khau(mat_khau)

        for tk in danh_sach:
            if tk.ma == tai_khoan:
                if tk.kiem_tra(hash_pass):
                    self._tai_khoan_hien_tai = tk
                    return
                else:
                    raise ValueError("Mật khẩu không chính xác.")

        raise ValueError(f"Tài khoản '{tai_khoan}' không tồn tại.")

    def dang_xuat(self) -> None:
        if self._tai_khoan_hien_tai is None:
            raise ValueError("Chưa có tài khoản nào đăng nhập.")
        self._tai_khoan_hien_tai = None

    def doi_mat_khau(self, mat_khau_moi: str, mat_khau_cu: str | None = None, tai_khoan: str | None = None) -> None:
        if self._tai_khoan_hien_tai is None:
            raise ValueError("Bạn cần đăng nhập để thực hiện đổi mật khẩu.")

        danh_sach = self.luu_tru.doc()

        # Trường hợp Admin reset mật khẩu người khác
        if tai_khoan is not None:
            if not self._tai_khoan_hien_tai.co_quyen_quan_tri:
                raise ValueError("Chỉ Quản trị viên mới có quyền reset mật khẩu của tài khoản khác.")

            tk_target = next((tk for tk in danh_sach if tk.ma == tai_khoan), None)
            if not tk_target:
                raise ValueError(f"Không tìm thấy tài khoản '{tai_khoan}'.")

            tk_target.doi_mat_khau(bam_mat_khau(mat_khau_moi))
            self.luu_tru.ghi(danh_sach)
            return

        # Trường hợp người dùng tự đổi mật khẩu
        if mat_khau_cu is None:
            raise ValueError("Vui lòng nhập mật khẩu cũ.")

        if not self._tai_khoan_hien_tai.kiem_tra(bam_mat_khau(mat_khau_cu)):
            raise ValueError("Mật khẩu cũ không chính xác.")

        tk_target = next((tk for tk in danh_sach if tk.ma == self._tai_khoan_hien_tai.ma), None)
        if tk_target:
            hash_moi = bam_mat_khau(mat_khau_moi)
            tk_target.doi_mat_khau(hash_moi)
            self._tai_khoan_hien_tai.doi_mat_khau(hash_moi)
            self.luu_tru.ghi(danh_sach)
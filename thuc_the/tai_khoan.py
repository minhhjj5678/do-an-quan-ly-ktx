from enum import Enum

from thuc_the.thuc_the_goc import ThucTheGoc, ThucTheLuuTruDuoc


class LoaiTaiKhoan(Enum):
    QUAN_TRI_VIEN = "quản trị viên"
    SINH_VIEN = "sinh viên"

class TaiKhoan(ThucTheGoc, ThucTheLuuTruDuoc):
    def __init__(self, ma_dang_nhap: str, mat_khau_bam: str, loai_tai_khoan: LoaiTaiKhoan, ma_chu_the: str | None):
        ThucTheGoc.__init__(self, ma_dang_nhap)
        ThucTheLuuTruDuoc.__init__(self)
        self.__mat_khau_bam = mat_khau_bam
        self.__loai_tai_khoan = loai_tai_khoan
        self.__ma_chu_the = ma_chu_the

    @property
    def mat_khau_bam(self) -> str:
        """Chỉ dùng để lưu xuống file, để so sánh mật khẩu hãy dùng phương thức kiem_tra"""
        return self.__mat_khau_bam

    @property
    def loai_tai_khoan(self) -> LoaiTaiKhoan:
        """Chỉ dùng để lưu xuống file, để kiểm tra quyền hãy dùng phương thức co_quyen_quan_tri"""
        return self.__loai_tai_khoan

    @property
    def ma_chu_the(self) -> str | None:
        return self.__ma_chu_the

    @property
    def co_quyen_quan_tri(self) -> bool:
        """Kiểm tra xem tài khoản có quyền Admin hay không."""
        return self.__loai_tai_khoan == LoaiTaiKhoan.QUAN_TRI_VIEN

    def doi_mat_khau(self, mat_khau_bam_moi: str):
        self.__mat_khau_bam = mat_khau_bam_moi

    def kiem_tra(self, mat_khau_bam: str) -> bool:
        """Kiểm tra mật khẩu đã băm có khớp với mật khẩu tài khoản hay không"""
        return self.__mat_khau_bam == mat_khau_bam
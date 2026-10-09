from luu_tru.luu_tru_co_so import LuuTruCoSo
from thuc_the.ky_tuc_xa import SinhVien
from tien_ich.cau_hinh_tinh import FILE_SINH_VIEN

class LuuTruSinhVien(LuuTruCoSo[SinhVien]):
    def __init__(self):
        super().__init__(FILE_SINH_VIEN, SinhVien)
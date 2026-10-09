from luu_tru.luu_tru_co_so import LuuTruCoSo
from thuc_the.tai_khoan import TaiKhoan
from tien_ich.cau_hinh_tinh import FILE_TAI_KHOAN

class LuuTruTaiKhoan(LuuTruCoSo[TaiKhoan]):
    def __init__(self):
        super().__init__(FILE_TAI_KHOAN, TaiKhoan)
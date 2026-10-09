from luu_tru.luu_tru_co_so import LuuTruCoSo
from thuc_the.tai_chinh import HoaDonThang
from tien_ich.cau_hinh_tinh import FILE_HOA_DON_THANG

class LuuTruHoaDonThang(LuuTruCoSo[HoaDonThang]):
    def __init__(self):
        super().__init__(FILE_HOA_DON_THANG, HoaDonThang)
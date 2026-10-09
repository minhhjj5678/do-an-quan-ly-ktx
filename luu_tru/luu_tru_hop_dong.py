from luu_tru.luu_tru_co_so import LuuTruCoSo
from thuc_the.tai_chinh import HopDong
from tien_ich.cau_hinh_tinh import FILE_HOP_DONG

class LuuTruHopDong(LuuTruCoSo[HopDong]):
    def __init__(self):
        super().__init__(FILE_HOP_DONG, HopDong)
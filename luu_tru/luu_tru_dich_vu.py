from luu_tru.luu_tru_co_so import LuuTruCoSo
from thuc_the.tai_chinh import DichVuThem
from tien_ich.cau_hinh_tinh import FILE_DICH_VU_THEM

class LuuTruDichVuThem(LuuTruCoSo[DichVuThem]):
    def __init__(self):
        super().__init__(FILE_DICH_VU_THEM, DichVuThem)
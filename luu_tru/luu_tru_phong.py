from luu_tru.luu_tru_co_so import LuuTruCoSo
from thuc_the.ky_tuc_xa import Phong
from tien_ich.cau_hinh_tinh import FILE_PHONG

class LuuTruPhong(LuuTruCoSo[Phong]):
    def __init__(self):
        super().__init__(FILE_PHONG, Phong)
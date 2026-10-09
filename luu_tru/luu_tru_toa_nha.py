from luu_tru.luu_tru_co_so import LuuTruCoSo
from thuc_the.ky_tuc_xa import ToaNha
from tien_ich.cau_hinh_tinh import FILE_TOA_NHA

class LuuTruToaNha(LuuTruCoSo[ToaNha]):
    def __init__(self):
        super().__init__(FILE_TOA_NHA, ToaNha)
from abc import ABC, abstractmethod
from datetime import date
from enum import Enum

from thuc_the._kiem_tra_ma import ktra_ma_tham_chieu_hop_le
from thuc_the.thuc_the_goc import ThucTheGoc
from tien_ich.regex import ktra_chuoi, ktra_ngay, ktra_so, la_ma_vi_pham


class TrangThaiViPham(Enum):
    CHUA_XU_LY = "chưa xử lý"
    DA_XU_LY = "đã xử lý"

class ViPham(ThucTheGoc, ABC):
    @abstractmethod
    def __init__(self, ma: str, sinh_vien: str, ngay_vi_pham: date, mo_ta: str, trang_thai: TrangThaiViPham = TrangThaiViPham.CHUA_XU_LY):
        ktra_chuoi(ma, lambda x: la_ma_vi_pham(x), "Mã vi phạm không hợp lệ")
        super().__init__(ma)

        ktra_ma_tham_chieu_hop_le(sinh_vien, "Mã sinh viên")
        self.__sinh_vien = sinh_vien

        ktra_ngay(ngay_vi_pham, lambda x: True, "Ngày vi phạm rỗng hoặc không hợp lệ")
        self.__ngay_vi_pham = ngay_vi_pham

        ktra_chuoi(mo_ta, lambda x: True, "Mô tả vi phạm không được rỗng")
        self.__mo_ta = mo_ta

        self.__trang_thai = trang_thai

    @property
    def trang_thai(self) -> TrangThaiViPham:
        return self.__trang_thai

    @property
    def sinh_vien(self) -> str:
        return self.__sinh_vien

    @property
    def ngay_vi_pham(self) -> date:
        return self.__ngay_vi_pham

    @property
    def mo_ta(self) -> str:
        return self.__mo_ta

    def xu_ly(self):
        self.__trang_thai = TrangThaiViPham.DA_XU_LY

class ViPhamNoiQuy(ViPham):
    def __init__(self, ma: str, sinh_vien: str, ngay_vi_pham: date, mo_ta: str, hinh_thuc_ky_luat: str):
        super().__init__(ma, sinh_vien, ngay_vi_pham, mo_ta)

        ktra_chuoi(hinh_thuc_ky_luat, lambda x: True, "Hình thức kỷ luật không được rỗng")
        self.__hinh_thuc_ky_luat = hinh_thuc_ky_luat

    @property
    def hinh_thuc_ky_luat(self) -> str:
        return self.__hinh_thuc_ky_luat

class ViPhamTaiSan(ViPham):
    def __init__(self, ma: str, sinh_vien: str, ngay_vi_pham: date, mo_ta: str, tien_boi_thuong: float):
        super().__init__(ma, sinh_vien, ngay_vi_pham, mo_ta)

        ktra_so(tien_boi_thuong, lambda x: x >= 0, "Tiền bồi thường không được âm")
        self.__tien_boi_thuong = tien_boi_thuong

    @property
    def tien_boi_thuong(self) -> float:
        return self.__tien_boi_thuong

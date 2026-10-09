from abc import ABC, abstractmethod
from datetime import date
from enum import Enum

from thuc_the.thuc_the_goc import ThucTheGoc


class TrangThaiViPham(Enum):
    CHUA_XU_LY = "chưa xử lý"
    DA_XU_LY = "đã xử lý"

class ViPham(ThucTheGoc, ABC):
    # TODO: kiểm tra tính hợp lệ trước khi gán các biến
    @abstractmethod
    def __init__(self, ma: str, sinh_vien: str, ngay_vi_pham: date, mo_ta: str):
        super().__init__(ma)
        self.__sinh_vien = sinh_vien
        self.__ngay_vi_pham = ngay_vi_pham
        self.__mo_ta = mo_ta
        self.__trang_thai = TrangThaiViPham.CHUA_XU_LY

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
        self.__hinh_thuc_ky_luat = hinh_thuc_ky_luat

    @property
    def hinh_thuc_ky_luat(self) -> str:
        return self.__hinh_thuc_ky_luat

class ViPhamTaiSan(ViPham):
    def __init__(self, ma: str, sinh_vien: str, ngay_vi_pham: date, mo_ta: str, tien_boi_thuong: float):
        super().__init__(ma, sinh_vien, ngay_vi_pham, mo_ta)
        self.__tien_boi_thuong = tien_boi_thuong

    @property
    def tien_boi_thuong(self) -> float:
        return self.__tien_boi_thuong

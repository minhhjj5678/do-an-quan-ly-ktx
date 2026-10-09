from datetime import date
from enum import Enum

from thuc_the.thuc_the_goc import ThucTheCoTen, ThucTheGoc, ThucTheLuuTruDuoc


class TrangThaiHoaDon(Enum):
    CHUA_THANH_TOAN = "chưa thanh toán"
    DA_THANH_TOAN = "đã thanh toán"

class TrangThaiHopDong(Enum):
    CHUA_THANH_TOAN = "chưa thanh toán"
    DA_THANH_TOAN = "đã thanh toán"
    KET_THUC_HOP_DONG = "kết thúc hợp đồng"

class DichVuThem(ThucTheCoTen, ThucTheLuuTruDuoc):
    # TODO: kiểm tra tính hợp lệ trước khi gán biến
    def __init__(self, ma: str, ten: str, don_gia: float):
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)
        self.__don_gia = don_gia

    @property
    def don_gia(self) -> float:
        return self.__don_gia

class HopDong(ThucTheGoc):
    # TODO: kiểm tra tính hợp lệ trước khi gán các biến
    def __init__(self, ma: str, he_so_thang: int, ngay_bat_dau: date, ngay_ket_thuc: date, gia_phong: float, ma_sinh_vien: str, ma_phong: str, hoc_ky: str, dich_vu_them: list[str] | None = None):
        super().__init__(ma)
        self.__ngay_bat_dau = ngay_bat_dau
        self.__he_so_thang = he_so_thang
        self.__ngay_ket_thuc = ngay_ket_thuc
        self.__gia_phong = gia_phong
        self.__ma_sinh_vien = ma_sinh_vien
        self.__ma_phong = ma_phong
        self.__dich_vu_them = dich_vu_them if dich_vu_them is not None else []
        self.__trang_thai = TrangThaiHopDong.CHUA_THANH_TOAN
        self.__hoc_ky = hoc_ky

    @property
    def ngay_bat_dau(self) -> date:
        return self.__ngay_bat_dau

    @property
    def ngay_ket_thuc(self) -> date:
        return self.__ngay_ket_thuc

    @property
    def gia_phong(self) -> float:
        return self.__gia_phong

    @property
    def he_so_thang(self) -> int:
        return self.__he_so_thang

    @property
    def ma_sinh_vien(self) -> str:
        return self.__ma_sinh_vien

    @property
    def ma_phong(self) -> str:
        return self.__ma_phong

    @property
    def dich_vu_them(self) -> list[str]:
        return self.__dich_vu_them.copy()

    @property
    def trang_thai(self) -> TrangThaiHopDong:
        return self.__trang_thai

    @property
    def hoc_ky(self) -> str:
        return self.__hoc_ky

    # TODO: cần triển khai
    def thanh_toan(self) -> None:
        pass

    def ket_thuc(self) -> None:
        pass

    def tong_tien(self) -> float: return 1

class HoaDonThang(ThucTheGoc):
    # TODO: kiểm tra tính hợp lệ trước khi gán các biến
    def __init__(self, ma: str, thang: int, dien_cu: int, dien_moi: int, don_gia_dien: float, nuoc_cu: int, nuoc_moi: int, don_gia_nuoc: float, phong: str, han_chot: date):
        super().__init__(ma)
        self.__thang = thang
        self.__dien_cu = dien_cu
        self.__dien_moi = dien_moi
        self.__don_gia_dien = don_gia_dien
        self.__nuoc_cu = nuoc_cu
        self.__nuoc_moi = nuoc_moi
        self.__don_gia_nuoc = don_gia_nuoc
        self.__phong = phong
        self.__han_chot = han_chot
        self.__trang_thai = TrangThaiHoaDon.CHUA_THANH_TOAN

    @property
    def thang(self) -> int:
        return self.__thang

    @property
    def han_chot(self) -> date:
        return self.__han_chot

    @property
    def trang_thai(self) -> TrangThaiHoaDon:
        return self.__trang_thai

    @property
    def phong(self) -> str:
        return self.__phong

    @property
    def dien_cu(self) -> int:
        return self.__dien_cu

    @property
    def dien_moi(self) -> int:
        return self.__dien_moi

    @property
    def don_gia_dien(self) -> float:
        return self.__don_gia_dien

    @property
    def nuoc_cu(self) -> int:
        return self.__nuoc_cu

    @property
    def nuoc_moi(self) -> int:
        return self.__nuoc_moi

    @property
    def don_gia_nuoc(self) -> float:
        return self.__don_gia_nuoc

    def tong_tien(self) -> float: return 1

    def thanh_toan(self) -> None: pass

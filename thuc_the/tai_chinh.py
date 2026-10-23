from abc import ABC, abstractmethod
from datetime import date
from enum import Enum

from dataclasses import dataclass

from thuc_the._kiem_tra_ma import ktra_ma_tham_chieu_hop_le
from thuc_the.hoc_vu import ThangNam
from thuc_the.thuc_the_goc import ThucTheCoTen, ThucTheGoc, ThucTheLuuTruDuoc
from tien_ich.regex import ktra_chuoi, ktra_ngay, ktra_so, la_ma_dich_vu_them, la_ma_hoa_don_thang, la_ma_hop_dong, la_so_duong


class TrangThaiHoaDon(Enum):
    CHUA_THANH_TOAN = "chưa thanh toán"
    DA_THANH_TOAN = "đã thanh toán"

class TrangThaiHopDong(Enum):
    CHUA_THANH_TOAN = "chưa thanh toán"
    DA_THANH_TOAN = "đã thanh toán"
    KET_THUC_HOP_DONG = "kết thúc hợp đồng"

class DichVuCoSo(ThucTheCoTen, ThucTheLuuTruDuoc, ABC):
    @abstractmethod
    def __init__(self, ma: str, ten: str, don_gia: float):
        ktra_chuoi(ma, lambda x: la_ma_dich_vu_them(x), "Mã dịch vụ không hợp lệ")
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)

        ktra_so(don_gia, lambda x: la_so_duong(x), "Đơn giá phải là số dương")
        self.__don_gia = don_gia

    @property
    def don_gia(self) -> float:
        return self.__don_gia

class DichVuThem(DichVuCoSo):
    """
    Dịch vụ thêm tính theo tháng thuộc về hợp đồng
    """
    def __init__(self, ma: str, ten: str, don_gia: float):
        super().__init__(ma, ten, don_gia)

class TienIchPhong(DichVuCoSo):
    """
    Tiện ích tính theo tháng thuộc về phòng
    """
    def __init__(self, ma: str, ten: str, don_gia: float):
        super().__init__(ma, ten, don_gia)

class HopDong(ThucTheGoc):
    def __init__(self, ma: str, ngay_ky: date, ngay_het_han: date, ngay_bat_dau: date, ngay_ket_thuc: date, he_so_thang: int, gia_co_ban: float, tien_dat_coc: float, ma_sinh_vien: str, ma_phong: str, hoc_ky: str, dich_vu_them: dict[str, float] | None = None, phi_tien_nghi: float = 0, trang_thai: TrangThaiHopDong = TrangThaiHopDong.CHUA_THANH_TOAN):
        ktra_chuoi(ma, lambda x: la_ma_hop_dong(x), "Mã hợp đồng không hợp lệ")
        super().__init__(ma)

        ktra_ngay(ngay_ket_thuc, lambda x: True, "Ngày kết thúc rỗng hoặc không hợp lệ")
        ktra_ngay(ngay_bat_dau, lambda x: x < ngay_ket_thuc, "Ngày bắt đầu phải trước ngày kết thúc")
        ktra_ngay(ngay_ky, lambda x: x <= ngay_bat_dau, "Ngày ký không được sau ngày bắt đầu")
        ktra_ngay(ngay_het_han, lambda x: ngay_ky <= x <= ngay_bat_dau, "Ngày hết hạn không được trước ngày ký và sau ngày bắt đầu")
        self.__ngay_bat_dau = ngay_bat_dau
        self.__ngay_ket_thuc = ngay_ket_thuc
        self.__ngay_ky = ngay_ky
        self.__ngay_het_han = ngay_het_han

        ktra_so(he_so_thang, lambda x: la_so_duong(x), "Hệ số tháng phải là số dương")
        ktra_so(gia_co_ban, lambda x: la_so_duong(x), "Giá cơ bản phải là số dương")
        ktra_so(tien_dat_coc, lambda x: la_so_duong(x), "Tiền đặt cọc phải là số dương")
        ktra_so(phi_tien_nghi, lambda x: x >= 0, "Phí tiện nghi không được âm")
        self.__he_so_thang = he_so_thang
        self.__gia_co_ban = gia_co_ban
        self.__tien_dat_coc = tien_dat_coc
        self.__phi_tien_nghi = phi_tien_nghi

        if dich_vu_them is None:
            dich_vu_them = {}
        else:
            for ma_dich_vu, don_gia in dich_vu_them.items():
                ktra_ma_tham_chieu_hop_le(ma_dich_vu, "Mã dịch vụ thêm")
                ktra_so(don_gia, lambda x: la_so_duong(x), f"Đơn giá dịch vụ phải là số dương: {ma_dich_vu}")
        self.__dich_vu_them = dict(dich_vu_them)

        ktra_ma_tham_chieu_hop_le(ma_sinh_vien, "Mã sinh viên")
        ktra_ma_tham_chieu_hop_le(ma_phong, "Mã phòng")
        ktra_ma_tham_chieu_hop_le(hoc_ky, "Mã học kỳ")
        self.__ma_sinh_vien = ma_sinh_vien
        self.__ma_phong = ma_phong
        self.__hoc_ky = hoc_ky

        self.__trang_thai = trang_thai

    @property
    def ngay_bat_dau(self) -> date:
        return self.__ngay_bat_dau

    @property
    def ngay_ket_thuc(self) -> date:
        return self.__ngay_ket_thuc

    @property
    def ngay_ky(self) -> date:
        return self.__ngay_ky

    @property
    def ngay_het_han(self) -> date:
        return self.__ngay_het_han

    @property
    def gia_co_ban(self) -> float:
        return self.__gia_co_ban

    @property
    def tien_dat_coc(self) -> float:
        return self.__tien_dat_coc

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
    def dich_vu_them(self) -> dict[str, float]:
        return self.__dich_vu_them.copy()

    @property
    def phi_tien_nghi(self) -> float:
        return self.__phi_tien_nghi

    @property
    def trang_thai(self) -> TrangThaiHopDong:
        return self.__trang_thai

    @property
    def hoc_ky(self) -> str:
        return self.__hoc_ky

    @property
    def gia_phong(self) -> float:
        return self.__gia_co_ban + self.__phi_tien_nghi

    # TODO: cần triển khai
    def thanh_toan(self) -> None:
        pass

    def ket_thuc(self) -> None:
        pass

    def tong_tien(self) -> float: return 1

class HoaDonThang(ThucTheGoc):
    def __init__(self, ma: str, thang_nam: ThangNam, dien_cu: int, dien_moi: int, don_gia_dien: float, nuoc_cu: int, nuoc_moi: int, don_gia_nuoc: float, phong: str, han_chot: date, trang_thai: TrangThaiHoaDon = TrangThaiHoaDon.CHUA_THANH_TOAN):
        ktra_chuoi(ma, lambda x: la_ma_hoa_don_thang(x), "Mã hóa đơn tháng không hợp lệ")
        super().__init__(ma)

        if not isinstance(thang_nam, ThangNam):
            raise ValueError("Tháng năm không hợp lệ")
        ktra_so(dien_cu, lambda x: x >= 0 and x <= dien_moi, "Chỉ số điện cũ phải là số không âm và không lớn hơn chỉ số điện mới")
        ktra_so(nuoc_cu, lambda x: x >= 0 and x <= nuoc_moi, "Chỉ số nước cũ phải là số không âm và không lớn hơn chỉ số nước mới")
        ktra_so(dien_moi, lambda x: x >= 0, "Chỉ số điện mới phải là số không âm")
        ktra_so(nuoc_moi, lambda x: x >= 0, "Chỉ số nước mới phải là số không âm")
        ktra_so(don_gia_dien, lambda x: x >= 0, "Đơn giá điện phải là số không âm")
        ktra_so(don_gia_nuoc, lambda x: x >= 0, "Đơn giá nước phải là số không âm")
        self.__thang_nam = thang_nam
        self.__dien_cu = dien_cu
        self.__dien_moi = dien_moi
        self.__don_gia_dien = don_gia_dien
        self.__nuoc_cu = nuoc_cu
        self.__nuoc_moi = nuoc_moi
        self.__don_gia_nuoc = don_gia_nuoc

        ktra_ma_tham_chieu_hop_le(phong, "Mã phòng")
        self.__phong = phong

        ktra_ngay(han_chot, lambda x: True, "Hạn chốt rỗng hoặc không hợp lệ")
        self.__han_chot = han_chot

        self.__trang_thai = trang_thai

    @property
    def thang_nam(self) -> ThangNam:
        return self.__thang_nam

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

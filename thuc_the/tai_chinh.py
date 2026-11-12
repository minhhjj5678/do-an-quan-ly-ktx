from datetime import date
from enum import Enum
from dataclasses import dataclass
import calendar

from thuc_the._kiem_tra_ma import ktra_ma_tham_chieu_hop_le
from thuc_the.thuc_the_goc import ThucTheGoc
from tien_ich.regex import ktra_chuoi, ktra_ngay, ktra_so, la_ma_hoa_don_thang, la_ma_hop_dong, la_so_duong


class TrangThaiHoaDon(Enum):
    CHUA_THANH_TOAN = "chưa thanh toán"
    DA_THANH_TOAN = "đã thanh toán"

class TrangThaiHopDong(Enum):
    CHUA_THANH_TOAN = "chưa thanh toán"
    DA_THANH_TOAN = "đã thanh toán"
    KET_THUC_HOP_DONG = "kết thúc hợp đồng"

@dataclass(frozen=True, order=True)
class ThangNam:
    nam: int
    thang: int

    def __post_init__(self):
        ktra_so(self.nam, lambda x: x > date.today().year - 100 and x <= date.today().year + 100, "Năm không hợp lệ")
        ktra_so(self.thang, lambda x: x > 0 and x <= 12, "Tháng phải là số dương từ 1 đến 12")

    @classmethod
    def tu_ngay(cls, ngay: date) -> "ThangNam":
        return cls(ngay.year, ngay.month)

    @classmethod
    def tu_chuoi(cls, ngay: str) -> "ThangNam":
        ktra_chuoi(ngay, lambda x: len(x) == 7 and x[4] == "-" and x[0:4].isdigit() and x[5:7].isdigit(), "Chuỗi ngày không hợp lệ, định dạng phải là YYYY-MM")
        return cls(int(ngay[0:4]), int(ngay[5:7]))

    def lui(self, so_thang_lui: int = 1) -> "ThangNam":
        ktra_so(so_thang_lui, lambda x: x > 0, "Số tháng lùi phải là số dương")
        thang = self.thang - so_thang_lui
        nam = self.nam
        while thang <= 0:
            thang += 12
            nam -= 1
        return ThangNam(nam, thang)

    def ngay_dau(self) -> date:
        return date(self.nam, self.thang, 1)

    def ngay_cuoi(self) -> date:
        ngay_cuoi_thang = calendar.monthrange(self.nam, self.thang)[1]
        return date(self.nam, self.thang, ngay_cuoi_thang)

    def __str__(self) -> str:
        return f"{self.nam:04d}-{self.thang:02d}"

class HopDong(ThucTheGoc):
    def __init__(self, ma: str, ngay_ky: date, ngay_het_han: date, ngay_bat_dau: date, ngay_ket_thuc: date, he_so_thang: int, gia_phong: float, tien_dat_coc: float, ma_sinh_vien: str, ma_phong: str, trang_thai: TrangThaiHopDong = TrangThaiHopDong.CHUA_THANH_TOAN):
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
        ktra_so(gia_phong, lambda x: la_so_duong(x), "Giá cơ bản phải là số dương")
        ktra_so(tien_dat_coc, lambda x: la_so_duong(x), "Tiền đặt cọc phải là số dương")
        self.__he_so_thang = he_so_thang
        self.__gia_phong = gia_phong
        self.__tien_dat_coc = tien_dat_coc

        ktra_ma_tham_chieu_hop_le(ma_sinh_vien, "Mã sinh viên")
        ktra_ma_tham_chieu_hop_le(ma_phong, "Mã phòng")
        self.__ma_sinh_vien = ma_sinh_vien
        self.__ma_phong = ma_phong

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
    def trang_thai(self) -> TrangThaiHopDong:
        return self.__trang_thai

    @property
    def gia_phong(self) -> float:
        return self.__gia_phong

    def con_giu_cho(self, ngay_hom_nay: date | None = None) -> bool:
        ngay_hom_nay = ngay_hom_nay or date.today()
        return (self.__trang_thai == TrangThaiHopDong.CHUA_THANH_TOAN and self.__ngay_het_han >= ngay_hom_nay) or (self.__trang_thai == TrangThaiHopDong.DA_THANH_TOAN and self.__ngay_ket_thuc >= ngay_hom_nay)

    def thanh_toan(self) -> None:
        if self.__trang_thai == TrangThaiHopDong.CHUA_THANH_TOAN:
            self.__trang_thai = TrangThaiHopDong.DA_THANH_TOAN
        else:
            raise ValueError(f"Hợp đồng {self.ma} đã được thanh toán hoặc đã kết thúc, không thể thanh toán lại")

    def ket_thuc(self) -> None:
        if self.__trang_thai != TrangThaiHopDong.KET_THUC_HOP_DONG:
            self.__trang_thai = TrangThaiHopDong.KET_THUC_HOP_DONG
        else:
            raise ValueError(f"Hợp đồng {self.ma} đã kết thúc")

    def tong_tien(self) -> float:
        """
        Tính tổng tiền của hợp đồng, bao gồm: tiền phòng (giá cơ bản * hệ số tháng)
        """
        return self.gia_phong * self.__he_so_thang

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

    def tong_tien(self) -> float:
        """
        Tính tổng tiền của hóa đơn tháng, bao gồm: tiền điện, tiền nước.
        """
        tien_dien = (self.__dien_moi - self.__dien_cu) * self.__don_gia_dien
        tien_nuoc = (self.__nuoc_moi - self.__nuoc_cu) * self.__don_gia_nuoc
        return tien_dien + tien_nuoc

    def thanh_toan(self) -> None:
        if self.__trang_thai != TrangThaiHoaDon.DA_THANH_TOAN:
            self.__trang_thai = TrangThaiHoaDon.DA_THANH_TOAN
        else:
            raise ValueError(f"Hóa đơn tháng {self.ma} đã được thanh toán, không thể thanh toán lại")

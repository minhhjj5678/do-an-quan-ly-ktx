from dataclasses import dataclass
import calendar
from datetime import date

from thuc_the.thuc_the_goc import ThucTheCoTen
from tien_ich.regex import ktra_chuoi, ktra_ngay, ktra_so, la_ma_hoc_ky


class HocKy(ThucTheCoTen):
    def __init__(self, ma: str, ten: str, ngay_bat_dau: date, ngay_ket_thuc: date):
        ktra_chuoi(ma, lambda x: la_ma_hoc_ky(x), "Mã học kỳ không hợp lệ")
        super().__init__(ma, ten)

        ktra_ngay(ngay_ket_thuc, lambda x: True, "Ngày kết thúc rỗng hoặc không hợp lệ")
        ktra_ngay(ngay_bat_dau, lambda x: x < ngay_ket_thuc, "Ngày bắt đầu phải trước ngày kết thúc")
        self.__ngay_bat_dau = ngay_bat_dau
        self.__ngay_ket_thuc = ngay_ket_thuc

    @property
    def ngay_bat_dau(self) -> date:
        return self.__ngay_bat_dau

    @property
    def ngay_ket_thuc(self) -> date:
        return self.__ngay_ket_thuc

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
    
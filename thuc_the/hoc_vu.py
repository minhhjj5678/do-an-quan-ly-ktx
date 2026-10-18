from datetime import date

from thuc_the.thuc_the_goc import ThucTheCoTen
from tien_ich.regex import ktra_chuoi, ktra_ngay, la_ma_hoc_ky


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
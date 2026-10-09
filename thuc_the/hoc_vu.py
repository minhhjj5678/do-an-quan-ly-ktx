from datetime import date

from thuc_the.thuc_the_goc import ThucTheCoTen


class HocKy(ThucTheCoTen):
    # TODO: kiểm tra tính hợp lệ trước khi gán các biến
    def __init__(self, ma: str, ten: str, ngay_bat_dau: date, ngay_ket_thuc: date):
        super().__init__(ma, ten)
        self.__ngay_bat_dau = ngay_bat_dau
        self.__ngay_ket_thuc = ngay_ket_thuc

    @property
    def ngay_bat_dau(self) -> date:
        return self.__ngay_bat_dau

    @property
    def ngay_ket_thuc(self) -> date:
        return self.__ngay_ket_thuc
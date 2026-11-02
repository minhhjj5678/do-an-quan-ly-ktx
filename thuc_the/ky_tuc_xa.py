from datetime import date

from thuc_the._kiem_tra_ma import ktra_ma_tham_chieu_hop_le
from thuc_the.thuc_the_goc import ThucTheCoTen, ThucTheLuuTruDuoc
from tien_ich.regex import ktra_chuoi, ktra_so, la_cccd, la_ma_phong, la_ma_sinh_vien, la_ma_toa_nha, la_sdt, la_so_duong


class SinhVien(ThucTheCoTen, ThucTheLuuTruDuoc):
    def __init__(self, ma: str, ten: str, sdt: str, nam_sinh: int, cccd: str, dia_chi_chi_tiet: str, xa: str, tinh: str):
        ktra_chuoi(ma, lambda x: la_ma_sinh_vien(x), "Mã sinh viên không hợp lệ")
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)

        ktra_so(nam_sinh, lambda x: x > date.today().year - 100 and x <= date.today().year, "Năm sinh không hợp lệ")
        self.__nam_sinh = nam_sinh

        ktra_chuoi(cccd, lambda x: la_cccd(x), "CCCD không hợp lệ")
        self.__cccd = cccd

        self.sdt = sdt
        self.dia_chi_chi_tiet = dia_chi_chi_tiet
        self.xa = xa
        self.tinh = tinh
        self.phong_hien_tai = None
        self.hop_dong = None

    @property
    def sdt(self) -> str:
        return self.__sdt

    @property
    def nam_sinh(self) -> int:
        return self.__nam_sinh

    @property
    def cccd(self) -> str:
        return self.__cccd

    @property
    def phong_hien_tai(self) -> str | None:
        return self.__phong_hien_tai

    @property
    def hop_dong(self) -> str | None:
        return self.__hop_dong

    @property
    def dia_chi_chi_tiet(self) -> str:
        return self.__dia_chi_chi_tiet

    @property
    def xa(self) -> str:
        return self.__xa

    @property
    def tinh(self) -> str:
        return self.__tinh

    @sdt.setter
    def sdt(self, value: str):
        ktra_chuoi(value, lambda x: la_sdt(x), "Số điện thoại không hợp lệ")
        self.__sdt = value

    @phong_hien_tai.setter
    def phong_hien_tai(self, value: str | None):
        if value is not None:
            ktra_ma_tham_chieu_hop_le(value, "Mã phòng")
        self.__phong_hien_tai = value

    @hop_dong.setter
    def hop_dong(self, value: str | None):
        if value is not None:
            ktra_ma_tham_chieu_hop_le(value, "Mã hợp đồng")
        self.__hop_dong = value

    @dia_chi_chi_tiet.setter
    def dia_chi_chi_tiet(self, value: str):
        ktra_chuoi(value, lambda x: x.strip() != "", "Địa chỉ chi tiết không được rỗng")
        self.__dia_chi_chi_tiet = value

    @xa.setter
    def xa(self, value: str):
        ktra_ma_tham_chieu_hop_le(value, "Mã xã")
        self.__xa = value

    @tinh.setter
    def tinh(self, value: str):
        ktra_ma_tham_chieu_hop_le(value, "Mã tỉnh")
        self.__tinh = value


class Phong(ThucTheCoTen, ThucTheLuuTruDuoc):
    def __init__(self, ma: str, ten: str, suc_chua: int, gia_phong: float, toa_nha: str, tang: int):
        ktra_chuoi(ma, lambda x: la_ma_phong(x), "Mã phòng không hợp lệ")
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)

        ktra_ma_tham_chieu_hop_le(toa_nha, "Mã tòa nhà")
        self.__toa_nha = toa_nha

        ktra_so(tang, lambda x: la_so_duong(x), "Tầng phải là số dương")
        self.__tang = tang

        self.gia_phong = gia_phong
        self.suc_chua = suc_chua

    @property
    def suc_chua(self) -> int:
        return self.__suc_chua

    @property
    def gia_phong(self) -> float:
        return self.__gia_phong

    @property
    def gia_co_ban(self) -> float:
        return self.__gia_phong / self.suc_chua

    @property
    def toa_nha(self) -> str:
        return self.__toa_nha

    @property
    def tang(self) -> int:
        return self.__tang

    @suc_chua.setter
    def suc_chua(self, value: int):
        ktra_so(value, lambda x: la_so_duong(x), "Sức chứa phải là số dương")
        self.__suc_chua = value

    @gia_phong.setter
    def gia_phong(self, value: float):
        ktra_so(value, lambda x: la_so_duong(x), "Giá phòng phải là số dương")
        self.__gia_phong = value

class ToaNha(ThucTheCoTen, ThucTheLuuTruDuoc):
    def __init__(self, ma: str, ten: str, so_tang: int):
        ktra_chuoi(ma, lambda x: la_ma_toa_nha(x), "Mã tòa nhà không hợp lệ")
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)

        self.so_tang = so_tang

    @property
    def so_tang(self) -> int:
        return self.__so_tang

    @so_tang.setter
    def so_tang(self, value: int):
        ktra_so(value, lambda x: la_so_duong(x), "Số tầng phải là số dương")
        self.__so_tang = value

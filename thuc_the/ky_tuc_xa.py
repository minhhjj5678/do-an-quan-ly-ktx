from thuc_the.thuc_the_goc import ThucTheCoTen, ThucTheLuuTruDuoc


class SinhVien(ThucTheCoTen, ThucTheLuuTruDuoc):
    def __init__(self, ma: str, ten: str, sdt: str, nam_sinh: int, cccd: str, dia_chi_chi_tiet: str, xa: str, tinh: str):
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)
        self.__nam_sinh = nam_sinh
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
    def dia_chi_chi_tiet(self) -> str | None:
        return self.__dia_chi_chi_tiet

    @property
    def xa(self) -> str | None:
        return self.__xa

    @property
    def tinh(self) -> str | None:
        return self.__tinh

    ## TODO: các setter ném lỗi nếu giá trị không hợp lệ
    @sdt.setter
    def sdt(self, value: str):
        self.__sdt = value

    @phong_hien_tai.setter
    def phong_hien_tai(self, value: str | None):
        self.__phong_hien_tai = value

    @hop_dong.setter
    def hop_dong(self, value: str | None):
        self.__hop_dong = value

    @dia_chi_chi_tiet.setter
    def dia_chi_chi_tiet(self, value: str):
        self.__dia_chi_chi_tiet = value

    @xa.setter
    def xa(self, value: str):
        self.__xa = value

    @tinh.setter
    def tinh(self, value: str):
        self.__tinh = value


class Phong(ThucTheCoTen, ThucTheLuuTruDuoc):
    def __init__(self, ma: str, ten: str, suc_chua: int, gia_phong: float, toa_nha: str, tang: int):
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)
        self.suc_chua = suc_chua
        self.gia_phong = gia_phong
        self.__toa_nha = toa_nha
        self.__tang = tang
        self.__danh_sach_sinh_vien = set()

    @property
    def suc_chua(self) -> int:
        return self.__suc_chua

    @property
    def gia_phong(self) -> float:
        return self.__gia_phong

    @property
    def toa_nha(self) -> str | None:
        return self.__toa_nha

    @property
    def tang(self) -> int | None:
        return self.__tang

    @property
    def danh_sach_sinh_vien(self) -> set[str]:
        return self.__danh_sach_sinh_vien.copy()

    ## TODO: các setter ném lỗi nếu giá trị không hợp lệ
    @suc_chua.setter
    def suc_chua(self, value: int):
        self.__suc_chua = value

    @gia_phong.setter
    def gia_phong(self, value: float):
        self.__gia_phong = value

    # TODO: cần triển khai
    def con_phong(self) -> bool:
        return len(self.danh_sach_sinh_vien) < self.suc_chua

    def them_sinh_vien(self, sinh_vien: SinhVien) -> None:
        """
        Thêm sinh viên vào phòng.
        Ném lỗi hợp lệ khi cần
        """
        pass

    def xoa_sinh_vien(self, sinh_vien: SinhVien | str) -> None:
        """
        Xóa sinh viên khỏi phòng bằng đối tượng hoặc mã sinh viên.
        Ném lỗi hợp lệ khi cần
        """
        pass

class ToaNha(ThucTheCoTen, ThucTheLuuTruDuoc):
    def __init__(self, ma: str, ten: str, so_tang: int):
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)
        self.so_tang = so_tang
        self.__danh_sach_phong = set()

    @property
    def so_tang(self) -> int:
        return self.__so_tang

    @property
    def danh_sach_phong(self) -> set[str]:
        return self.__danh_sach_phong.copy()

    @property
    def so_phong(self) -> int:
        return len(self.__danh_sach_phong)

    ## TODO: các setter ném lỗi nếu giá trị không hợp lệ
    @so_tang.setter
    def so_tang(self, value: int):
        self.__so_tang = value

    def them_phong(self, phong: Phong) -> None:
        """
        Thêm đối tượng phòng vào tòa nhà.
        Ném lỗi hợp lệ khi cần
        """
        pass

    def xoa_phong(self, phong: Phong | str) -> None:
        """
        Xóa phòng bằng mã phòng hoặc đối tượng phòng.
        Ném lỗi hợp lệ khi cần
        """
        pass

from datetime import date

from thuc_the._kiem_tra_ma import ktra_ma_tham_chieu_hop_le
from thuc_the.tai_chinh import TienIchPhong
from thuc_the.thuc_the_goc import ThucTheCoTen, ThucTheLuuTruDuoc
from tien_ich.regex import ktra_chuoi, ktra_so, la_cccd, la_ma_phong, la_ma_sinh_vien, la_ma_toa_nha, la_sdt, la_so_duong


class SinhVien(ThucTheCoTen, ThucTheLuuTruDuoc):
    def __init__(self, ma: str, ten: str, sdt: str, nam_sinh: int, cccd: str, dia_chi_chi_tiet: str, xa: str, tinh: str):
        ktra_chuoi(ma, lambda x: la_ma_sinh_vien(x), "Mã sinh viên không hợp lệ")
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)

        ktra_so(nam_sinh, lambda x: x > date.today().year - 100, "Năm sinh không hợp lệ")
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
    def __init__(self, ma: str, ten: str, suc_chua: int, gia_phong: float, toa_nha: str, tang: int, tien_ich_phong: set[str] | None = None):
        ktra_chuoi(ma, lambda x: la_ma_phong(x), "Mã phòng không hợp lệ")
        ThucTheCoTen.__init__(self, ma, ten)
        ThucTheLuuTruDuoc.__init__(self)

        ktra_ma_tham_chieu_hop_le(toa_nha, "Mã tòa nhà")
        self.__toa_nha = toa_nha

        ktra_so(tang, lambda x: la_so_duong(x), "Tầng phải là số dương")
        self.__tang = tang

        if tien_ich_phong is None:
            tien_ich_phong = set()
        else:
            for tien_ich in tien_ich_phong:
                ktra_ma_tham_chieu_hop_le(tien_ich, 'Mã tiện ích: "' + tien_ich + '"')
        self.__tien_ich_phong = set(tien_ich_phong)

        self.__danh_sach_sinh_vien = set()
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
    def toa_nha(self) -> str | None:
        return self.__toa_nha

    @property
    def tang(self) -> int | None:
        return self.__tang

    @property
    def tien_ich_phong(self) -> set[str]:
        return self.__tien_ich_phong.copy()

    @property
    def danh_sach_sinh_vien(self) -> set[str]:
        return self.__danh_sach_sinh_vien.copy()

    @suc_chua.setter
    def suc_chua(self, value: int):
        ktra_so(value, lambda x: la_so_duong(x), "Sức chứa phải là số dương")
        ktra_so(value, lambda x: x >= len(self.danh_sach_sinh_vien), "Sức chứa không được nhỏ hơn số lượng sinh viên trong phòng")
        self.__suc_chua = value

    @gia_phong.setter
    def gia_phong(self, value: float):
        ktra_so(value, lambda x: la_so_duong(x), "Giá phòng phải là số dương")
        self.__gia_phong = value

    def con_phong(self) -> bool:
        return len(self.danh_sach_sinh_vien) < self.suc_chua

    def them_sinh_vien(self, sinh_vien: SinhVien | str) -> None:
        """
        Thêm sinh viên vào phòng.
        Ném lỗi hợp lệ khi cần
        """
        if not self.con_phong():
            raise ValueError("Phòng đã đầy, không thể thêm sinh viên")
        if isinstance(sinh_vien, SinhVien):
            if sinh_vien.phong_hien_tai is not None:
                raise ValueError(f"Sinh viên {sinh_vien.ma} đã có phòng hiện tại: {sinh_vien.phong_hien_tai}")
            self.__danh_sach_sinh_vien.add(sinh_vien.ma)
        else:
            ktra_ma_tham_chieu_hop_le(sinh_vien, "Mã sinh viên")
            self.__danh_sach_sinh_vien.add(sinh_vien)

    def xoa_sinh_vien(self, sinh_vien: SinhVien | str) -> None:
        """
        Xóa sinh viên khỏi phòng bằng đối tượng hoặc mã sinh viên.
        Ném lỗi hợp lệ khi cần
        """
        if isinstance(sinh_vien, SinhVien):
            if sinh_vien.phong_hien_tai != self.ma or sinh_vien.ma not in self.__danh_sach_sinh_vien:
                raise ValueError(f"Sinh viên {sinh_vien.ma} không ở phòng {self.ma}")
            self.__danh_sach_sinh_vien.remove(sinh_vien.ma)
        else:
            ktra_ma_tham_chieu_hop_le(sinh_vien, "Mã sinh viên")
            if sinh_vien not in self.__danh_sach_sinh_vien:
                raise ValueError(f"Sinh viên {sinh_vien} không ở phòng {self.ma}")
            self.__danh_sach_sinh_vien.remove(sinh_vien)

    def them_tien_ich(self, tien_ich: TienIchPhong | str) -> None:
        """
        Thêm tiện ích vào phòng.
        Ném lỗi hợp lệ khi cần
        """
        ma = tien_ich.ma if isinstance(tien_ich, TienIchPhong) else tien_ich
        ktra_ma_tham_chieu_hop_le(ma, "Mã tiện ích")
        if ma in self.__tien_ich_phong:
            raise ValueError(f"Phòng {self.ma} đã có tiện ích {ma}")
        self.__tien_ich_phong.add(ma)

    def xoa_tien_ich(self, tien_ich: TienIchPhong | str) -> None:
        """
        Xóa tiện ích khỏi phòng bằng đối tượng hoặc mã tiện ích.
        Ném lỗi hợp lệ khi cần
        """
        ma = tien_ich.ma if isinstance(tien_ich, TienIchPhong) else tien_ich
        ktra_ma_tham_chieu_hop_le(ma, "Mã tiện ích")
        if ma not in self.__tien_ich_phong:
            raise ValueError(f"Phòng {self.ma} không có tiện ích {ma}")
        self.__tien_ich_phong.remove(ma)

class ToaNha(ThucTheCoTen, ThucTheLuuTruDuoc):
    def __init__(self, ma: str, ten: str, so_tang: int):
        ktra_chuoi(ma, lambda x: la_ma_toa_nha(x), "Mã tòa nhà không hợp lệ")
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

    @so_tang.setter
    def so_tang(self, value: int):
        ktra_so(value, lambda x: la_so_duong(x), "Số tầng phải là số dương")
        self.__so_tang = value

    def them_phong(self, phong: Phong | str) -> None:
        """
        Thêm đối tượng phòng vào tòa nhà.
        Ném lỗi hợp lệ khi cần
        """
        if isinstance(phong, Phong):
            if phong.toa_nha != self.ma:
                raise ValueError(f"Phòng {phong.ma} không thuộc tòa nhà {self.ma}")
            self.__danh_sach_phong.add(phong.ma)
        else:
            ktra_ma_tham_chieu_hop_le(phong, "Mã phòng")
            self.__danh_sach_phong.add(phong)

    def xoa_phong(self, phong: Phong | str) -> None:
        """
        Xóa phòng bằng mã phòng hoặc đối tượng phòng.
        Ném lỗi hợp lệ khi cần
        """
        if isinstance(phong, Phong):
            if phong.toa_nha != self.ma:
                raise ValueError(f"Phòng {phong.ma} không thuộc tòa nhà {self.ma}")
            self.__danh_sach_phong.remove(phong.ma)
        else:
            ktra_ma_tham_chieu_hop_le(phong, "Mã phòng")
            self.__danh_sach_phong.remove(phong)
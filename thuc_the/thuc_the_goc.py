from abc import ABC, abstractmethod

from thuc_the._kiem_tra_ma import ktra_ma_tham_chieu_hop_le
from tien_ich.regex import ktra_chuoi


class ThucTheGoc(ABC):
    """
    Lớp cơ sở cho tất cả các thực thể trong hệ thống, cung cấp các thuộc tính và phương thức chung.
    
    Thuộc tính:
        - ma: mã định danh duy nhất của thực thể, không được trùng lặp với các thực thể khác.

    Phương thức:
        - __eq__: so sánh hai thực thể có cùng mã hay không.
    """
    @abstractmethod
    def __init__(self, ma: str):
        ktra_ma_tham_chieu_hop_le(ma, "Mã thực thể")
        self.__ma = ma

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ThucTheGoc):
            return False
        return self.ma == other.ma

    @property
    def ma(self):
        return self.__ma

class ThucTheLuuTruDuoc:
    """
    Lớp cơ sở cho tất cả các thực thể có thể lưu trữ trong hệ thống, cung cấp các thuộc tính và phương thức chung.

    Phương thức:
        - luu_tru: đánh dấu thực thể đã được lưu trữ, ví dụ: sinh viên đã tốt nghiệp, phòng đã bị xóa,...
        - con_hoat_dong: kiểm tra thực thể có còn hoạt động hay không, ví dụ: sinh viên đã tốt nghiệp, phòng đã bị xóa,...
    """
    def __init__(self):
        self.__dang_hoat_dong = True

    @property
    def con_hoat_dong(self) -> bool:
        return self.__dang_hoat_dong

    def luu_tru(self) -> None:
        """
        Đánh dấu thực thể đã được lưu trữ hay ngừng hoạt động, ví dụ: sinh viên đã tốt nghiệp, phòng đã bị xóa,...
        """
        self.__dang_hoat_dong = False

    def tai_kich_hoat(self) -> None:
        """
        Đánh dấu thực thể đã hoạt động trở lại hay hết lưu trữ\n
        Dùng khi: sinh viên tạm nghỉ và thuê lại, phòng đã bị xóa nhưng được phục hồi,...
        """
        self.__dang_hoat_dong = True

class ThucTheCoTen(ThucTheGoc):
    """
    Lớp cơ sở cho tất cả các thực thể có tên trong hệ thống, cung cấp các thuộc tính và phương thức chung.

    Thuộc tính:
        - ma: mã định danh duy nhất của thực thể, không được trùng lặp với các thực thể khác.
        - ten: tên của thực thể, không được rỗng.
    
    Phương thức:
        - __eq__: so sánh hai thực thể có cùng mã hay không.
    """
    @abstractmethod
    def __init__(self, ma: str, ten: str):
        super().__init__(ma)
        self.ten = ten

    @property
    def ten(self):
        return self.__ten

    @ten.setter
    def ten(self, value):
        ktra_chuoi(value, lambda x: x.strip() != "", "Tên thực thể không được rỗng")
        self.__ten = value


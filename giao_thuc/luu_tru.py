# Phần C
# Sử dụng api ngoài theo quy định đồ án: https://provinces.open-api.vn/
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from thuc_the.thuc_the_goc import ThucTheGoc


T = TypeVar("T", bound=ThucTheGoc)

class GiaoThucLuuTru(ABC, Generic[T]):
    """
    Giao thức lưu trữ dữ liệu, các tầng nghiệp vụ và giao diện sẽ tương tác với tầng lưu trữ thông qua giao thức này.
    """
    @abstractmethod
<<<<<<< HEAD
    def doc(self) -> list[T]:
        """
        Đọc dữ liệu từ file dữ liệu, nếu không tồn tại thì trả về danh sách rỗng.
=======
    def doc(self) -> dict[str, T]:
        """
        Đọc dữ liệu từ file dữ liệu và trả về dict với key là mã thực thể, nếu không tồn tại/file bị hỏng/mất đồng bộ thì đọc từ file sao lưu, nếu file sao lưu cũng vậy thì trả về dict rỗng.\n
        Đối với api ngoài, khi file dữ liệu và file sao lưu cục bộ hỏng thì đọc dữ liệu trực tiếp từ api.\n
>>>>>>> 4c4d0594e4f71b9578ab0f9ec9e39b6fda39317f
        Ném ValueError nếu file dữ liệu bị hỏng hoặc mất đồng bộ.
        """
        raise NotImplementedError

    @abstractmethod
<<<<<<< HEAD
    def ghi(self, danh_sach: list[T], ghi_de: bool = True) -> None:
        """
        Ghi danh sách thực thể vào file dữ liệu và file sao lưu.\n
        Nếu ghi_de là True thì ghi đè lên file dữ liệu cũ, nếu False thì ghi thêm vào file dữ liệu cũ.
        """
        raise NotImplementedError

    @abstractmethod
    def doc_sao_luu(self) -> list[T]:
        """
        Đọc dữ liệu từ file sao lưu, nếu không tồn tại thì trả về danh sách rỗng.
        Chỉ dùng khi file dữ liệu chính bị hỏng hoặc mất đồng bộ.\n
        Đối với api ngoài, khi file dữ liệu và file sao lưu cục bộ hỏng thì đọc dữ liệu trực tiếp từ api.
=======
    def ghi(self, danh_sach: dict[str, T]) -> None:
        """
        Ghi danh sách thực thể vào file dữ liệu và file sao lưu.
        Luôn ghi đè lên file dữ liệu cũ.
>>>>>>> 4c4d0594e4f71b9578ab0f9ec9e39b6fda39317f
        """
        raise NotImplementedError

    @abstractmethod
    def co_bi_chinh_sua(self) -> bool:
        """
        Kiểm tra file dữ liệu có bị chỉnh sửa ngoài app không, tránh dữ liệu bị hỏng hoặc mất đồng bộ\n
        Lưu dấu thời gian bằng file riêng trong thư mục ``.sao_luu``
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def loai_thuc_the(self) -> type[T]:
        """Trả về loại thực thể mà class kế thừa hỗ trợ đọc/ghi, thực thể phải kế thừa từ ThucTheGoc"""
        raise NotImplementedError

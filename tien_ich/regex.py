# Regex kiểm tra tính hợp lệ của các thuộc tính theo quy định đồ án
# Tầng giao diện gọi khi người dùng nhập dữ liệu
# Tầng nghiệp vụ gọi khi khởi tạo thực thể
from datetime import date
from typing import Callable
import re


def ktra_so(so: float, dieu_kien: Callable[[float], bool], thong_bao_loi: str | None = None) -> bool:
    """
    Kiểm tra số có thỏa mãn điều kiện hay không.

    Tham số:
        - so: số cần kiểm tra
        - dieu_kien: hàm kiểm tra điều kiện
        - thong_bao_loi: thông báo lỗi (nếu có)
    
    Trả về:
        - True nếu thỏa mãn điều kiện
        - False nếu không thỏa mãn điều kiện và không có thông báo lỗi
        - Ném ValueError nếu không thỏa mãn điều kiện và có thông báo lỗi
    
    Ví dụ:
    ```python
        >>> ktra_so(5, lambda x: x > 0)
        True
        >>> ktra_so(-2, lambda x: x > 0, "Số lượng phải lớn hơn 0")
        ValueError: Số lượng phải lớn hơn 0
    ```
    """
    if so is not None and isinstance(so, (int, float)) and dieu_kien(so):
        return True
    if thong_bao_loi is not None:
        raise ValueError(thong_bao_loi)
    return False

def ktra_chuoi(chuoi: str, dieu_kien: Callable[[str], bool], thong_bao_loi: str | None = None) -> bool:
    """
    Kiểm tra chuỗi có thỏa mãn điều kiện hay không.
    
    Tham số:
        - chuoi: chuỗi cần kiểm tra
        - dieu_kien: hàm kiểm tra điều kiện
        - thong_bao_loi: thông báo lỗi (nếu có)
    
    Trả về:
        - True nếu thỏa mãn điều kiện
        - False nếu không thỏa mãn điều kiện và không có thông báo lỗi
        - Ném ValueError nếu không thỏa mãn điều kiện và có thông báo lỗi
    
    Ví dụ:
    ```python
        >>> ktra_chuoi("Hello", lambda x: len(x) > 0)
        True
        >>> ktra_chuoi("", lambda x: len(x) > 0, "Chuỗi không được rỗng")
        ValueError: Chuỗi không được rỗng
    ```
    """
    if chuoi is not None and isinstance(chuoi, str) and chuoi.strip() != "" and dieu_kien(chuoi):
        return True
    if thong_bao_loi is not None:
        raise ValueError(thong_bao_loi)
    return False

def ktra_ngay(ngay: date, dieu_kien: Callable[[date], bool], thong_bao_loi: str | None = None) -> bool:
    """
    Kiểm tra ngày có thỏa mãn điều kiện hay không.
    
    Tham số:
        - ngay: ngày cần kiểm tra
        - dieu_kien: hàm kiểm tra điều kiện
        - thong_bao_loi: thông báo lỗi (nếu có)
    
    Trả về:
        - True nếu thỏa mãn điều kiện
        - False nếu không thỏa mãn điều kiện và không có thông báo lỗi
        - Ném ValueError nếu không thỏa mãn điều kiện và có thông báo lỗi
    
    Ví dụ:
    ```python
        >>> ktra_ngay(date(2023, 1, 1), lambda x: x > date(2022, 12, 31))
        True
        >>> ktra_ngay(date(2022, 12, 31), lambda x: x > date(2022, 12, 31), "Ngày phải sau ngày 31/12/2022")
        ValueError: Ngày phải sau ngày 31/12/2022
    ```
    """
    if ngay is not None and isinstance(ngay, date) and dieu_kien(ngay):
        return True
    if thong_bao_loi is not None:
        raise ValueError(thong_bao_loi)
    return False

def la_so_duong(x: float) -> bool:
    return x > 0

def la_sdt(x: str) -> bool:
    return bool(re.match(r"^(03|05|07|08|09)\d{8}$", x))

def la_cccd(x: str) -> bool:
    return bool(re.match(r"^0\d{11}$", x))

# TODO: dùng regex để kiểm tra mã thực thể
def la_ma_sinh_vien(x: str) -> bool: return True
def la_ma_phong(x: str) -> bool: return True
def la_ma_toa_nha(x: str) -> bool: return True
def la_ma_hoa_don_thang(x: str) -> bool: return True
def la_ma_dich_vu_them(x: str) -> bool: return True
def la_ma_hop_dong(x: str) -> bool: return True
def la_ma_vi_pham(x: str) -> bool: return True
def la_ma_hoc_ky(x: str) -> bool: return True
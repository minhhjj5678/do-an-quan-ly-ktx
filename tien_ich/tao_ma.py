# Phần C
# TODO: tạo bộ sinh mã riêng cho mỗi thực thể, nếu có danh sách hiện tại thì kiểm tra trùng lập trước khi tạo
# TODO: viết thêm các hàm sử dụng thư viện re kiểm tra mã hợp lệ bên file regex.py
def ma_sinh_vien(danh_sach_hien_tai: list | None = None) -> str: return ""
def ma_phong(danh_sach_hien_tai: list | None = None) -> str: return ""
def ma_toa_nha(danh_sach_hien_tai: list | None = None) -> str: return ""
def ma_hoa_don_thang(danh_sach_hien_tai: list | None = None) -> str: return ""
def ma_dich_vu_them(danh_sach_hien_tai: list | None = None) -> str: return ""
def ma_hop_dong(danh_sach_hien_tai: list | None = None) -> str: return ""
def ma_vi_pham(danh_sach_hien_tai: list | None = None) -> str: return ""

# tien_ich/tao_ma.py

def _sinh_ma_tu_dong(tien_to: str, danh_sach_hien_tai: list | None = None) -> str:
    """
    Hàm trợ giúp chung: Tìm số thứ tự lớn nhất hiện tại từ danh sách 
    và sinh mã tiếp theo không trùng lặp (dạng PRE0001).
    """
    if not danh_sach_hien_tai:
        return f"{tien_to}0001"

    # Lấy danh sách mã chuỗi (nếu danh_sach_hien_tai truyền vào là danh sách đối tượng thì lấy thuộc tính .ma)
    cac_ma = []
    for item in danh_sach_hien_tai:
        if isinstance(item, str):
            cac_ma.append(item)
        elif hasattr(item, "ma"):
            cac_ma.append(item.ma)

    # Lọc các mã đúng tiền tố và lấy phần số
    so_thu_tu_list = []
    for ma in cac_ma:
        if ma.startswith(tien_to):
            phan_so = ma[len(tien_to):]
            if phan_so.isdigit():
                so_thu_tu_list.append(int(phan_so))

    if not so_thu_tu_list:
        return f"{tien_to}0001"

    # Sinh mã tiếp theo từ số lớn nhất + 1
    so_moi = max(so_thu_tu_list) + 1
    return f"{tien_to}{so_moi:04d}"


def ma_sinh_vien(danh_sach_hien_tai: list | None = None) -> str:
    return _sinh_ma_tu_dong("SV", danh_sach_hien_tai)

def ma_phong(danh_sach_hien_tai: list | None = None) -> str:
    return _sinh_ma_tu_dong("P", danh_sach_hien_tai)

def ma_toa_nha(danh_sach_hien_tai: list | None = None) -> str:
    return _sinh_ma_tu_dong("TN", danh_sach_hien_tai)

def ma_hoa_don_thang(danh_sach_hien_tai: list | None = None) -> str:
    return _sinh_ma_tu_dong("HDT", danh_sach_hien_tai)

def ma_dich_vu_them(danh_sach_hien_tai: list | None = None) -> str:
    return _sinh_ma_tu_dong("DV", danh_sach_hien_tai)

def ma_hop_dong(danh_sach_hien_tai: list | None = None) -> str:
    return _sinh_ma_tu_dong("HD", danh_sach_hien_tai)

def ma_vi_pham(danh_sach_hien_tai: list | None = None) -> str:
    return _sinh_ma_tu_dong("VP", danh_sach_hien_tai)
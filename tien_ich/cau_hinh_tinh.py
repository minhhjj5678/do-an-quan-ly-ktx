# Cấu hình tĩnh dùng cho toàn bộ project
# Không thay đổi giá trị biến trong file này trong quá trình chạy app, chỉ thay đổi giá trị gốc ở file này
# Các thành viên có thể thay đổi giá trị biến thuộc phạm vi triển khai của mình trong file này trong quá trình phát triển
from dataclasses import dataclass
from enum import Enum
from typing import Final

TEN_APP: Final = "Quản Lý Ký Túc Xá"
KICH_THUOC_MAN_HINH_LON = (1280, 720)
KICH_THUOC_MAN_HINH_POPUP = (400, 400)

@dataclass(frozen=True)
class PhongChu:
    family: str
    size: int
    style: str

class CauHinhPhongChu(Enum):
    TIEU_DE = PhongChu("Arial", 14, "bold")
    NOI_DUNG = PhongChu("Arial", 12, "normal")

@dataclass(frozen=True)
class ChuDe:
    bg: str
    fg: str
    nut: str

class CauHinhChuDe(Enum):
    DARK = ChuDe("#1E1F22", "#BCBEC4", "#3574F0")
    GREY = ChuDe("#F3F4F6", "#1F2937", "#6B7280")
    LIGHT = ChuDe("#FFFFFF", "#000000", "#0078D4")
    DEFAULT = LIGHT

# Data
THU_MUC_DATA = "du_lieu"
FILE_SINH_VIEN = "sinh_vien.json"
FILE_PHONG = "phong.json"
FILE_TOA_NHA = "toa_nha.json"
FILE_HOA_DON_THANG = "hoa_don_thang.json"
FILE_DICH_VU_THEM = "dich_vu_them.json"
FILE_HOP_DONG = "hop_dong.json"
FILE_VI_PHAM = "vi_pham.json"
FILE_TAI_KHOAN = "tai_khoan.json"

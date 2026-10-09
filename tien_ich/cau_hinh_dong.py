# Cấu hình động thay đổi trong quá trình chạy app, có lưu xuống file
# Các thành viên có thể thay đổi giá trị biến thuộc phạm vi triển khai của mình trong file này trong quá trình phát triển
from dataclasses import dataclass

from tien_ich.cau_hinh_tinh import CauHinhChuDe

@dataclass(frozen=True)
class CauHinhDong:
    """Cấu hình toàn cục của hệ thống, được lưu vĩnh viễn xuống file JSON."""

    CHU_DE: CauHinhChuDe = CauHinhChuDe.DEFAULT
    DON_GIA_DIEN: float = 3500.0
    DON_GIA_NUOC: float = 15000.0
    SUC_CHUA_PHONG_MAC_DINH: int = 8
    SO_TIEN_NO_TOI_DA_CHO_PHEP: float = 500000.0
    THOI_HAN_DONG_TIEN_DIEN: int = 5
    TIEN_PHAT_QUA_HAN_NGAY: float = 10000.0


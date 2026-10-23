from dataclasses import dataclass
import warnings

from thuc_the.hoc_vu import HocKy
from thuc_the.ky_tuc_xa import Phong, SinhVien, ToaNha
from thuc_the.tai_chinh import DichVuCoSo, DichVuThem, HoaDonThang, HopDong, TienIchPhong
from thuc_the.tai_khoan import TaiKhoan
from thuc_the.vi_pham import ViPham


def kiem_cheo_du_lieu(kho_du_lieu: "KhoDuLieu" ) -> list[str]:
    """
    Kiểm tra dữ liệu trong kho dữ liệu có hợp lệ hay không.
    Trả về danh sách các lỗi tìm thấy, nếu không có lỗi thì trả về danh sách rỗng.
    """
    warnings.warn("Hàm kiem_cheo_du_lieu chưa được triển khai, luôn trả về danh sách rỗng", stacklevel=2)

    return []

@dataclass
class KhoDuLieu:
    hoc_ky: dict[str, HocKy]
    dich_vu_them: dict[str, DichVuThem]
    tien_ich_phong: dict[str, TienIchPhong]
    toa_nha: dict[str, ToaNha]
    phong: dict[str, Phong]
    sinh_vien: dict[str, SinhVien]
    hop_dong: dict[str, HopDong]
    hoa_don_thang: dict[str, HoaDonThang]
    vi_pham: dict[str, ViPham]
    tai_khoan: dict[str, TaiKhoan]

    def dich_vu_co_so(self) -> dict[str, DichVuCoSo]:
        return {**self.dich_vu_them, **self.tien_ich_phong}
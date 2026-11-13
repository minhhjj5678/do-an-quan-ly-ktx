from thuc_the.tai_chinh import HoaDonThang

from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhHoaDonThang(ManHinhDanhMucCoSo):
    LOAI = HoaDonThang

    TRUONG = [
        "ma_hoa_don",
        "ma_hop_dong",
        "thang",
        "nam",
        "so_tien",
        "trang_thai"
    ]

    BAT_BUOC = [
        "ma_hoa_don",
        "ma_hop_dong",
        "thang",
        "nam"
    ]
from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhHopDong(ManHinhDanhMucCoSo):
    LOAI = "HopDong"

    TRUONG = [
        "ma_hop_dong",
        "ma_sinh_vien",
        "ma_phong",
        "ngay_bat_dau",
        "ngay_ket_thuc",
        "trang_thai"
    ]

    BAT_BUOC = [
        "ma_hop_dong",
        "ma_sinh_vien",
        "ma_phong",
        "ngay_bat_dau"
    ]
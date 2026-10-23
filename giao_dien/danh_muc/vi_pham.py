from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhViPham(ManHinhDanhMucCoSo):
    LOAI = "ViPham"

    TRUONG = [
        "ma_vi_pham",
        "ma_sinh_vien",
        "noi_dung",
        "muc_phat",
        "trang_thai"
    ]

    BAT_BUOC = [
        "ma_vi_pham",
        "ma_sinh_vien",
        "noi_dung"
    ]
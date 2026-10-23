from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhPhong(ManHinhDanhMucCoSo):
    LOAI = "Phong"
    CO_LUU_TRU = True

    TRUONG = [
        "ma_phong",
        "ma_toa_nha",
        "loai_phong",
        "suc_chua",
        "trang_thai"
    ]

    BAT_BUOC = [
        "ma_phong",
        "ma_toa_nha",
        "loai_phong",
        "suc_chua"
    ]
from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhDichVuThem(ManHinhDanhMucCoSo):
    LOAI = "DichVuThem"
    CO_LUU_TRU = True

    TRUONG = [
        "ma_dich_vu",
        "ten_dich_vu",
        "don_gia",
        "don_vi"
    ]

    BAT_BUOC = [
        "ma_dich_vu",
        "ten_dich_vu",
        "don_gia"
    ]
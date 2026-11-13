from thuc_the.ky_tuc_xa import ToaNha

from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhToaNha(ManHinhDanhMucCoSo):
    LOAI = ToaNha
    CO_LUU_TRU = True

    TRUONG = [
        "ma_toa_nha",
        "ten_toa_nha",
        "dia_chi"
    ]

    BAT_BUOC = [
        "ma_toa_nha",
        "ten_toa_nha"
    ]
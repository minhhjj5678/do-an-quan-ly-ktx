from thuc_the.tai_chinh import DichVuThem
from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhDichVuThem(ManHinhDanhMucCoSo):
    LOAI = DichVuThem
    CO_LUU_TRU = True

    TRUONG = [
        "ma",
        "ten",
        "don_gia"
    ]

    BAT_BUOC = [
        "ten",
        "don_gia"
    ]

    TRUONG_GIU_CHUOI = {"ten"}

    KIEU_TRUONG = {
        "don_gia": float
    }

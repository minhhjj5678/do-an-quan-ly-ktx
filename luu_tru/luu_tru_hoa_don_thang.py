# Phần C
# Lưu trữ HoaDonThang xuống file JSON (cau_hinh_tinh.FILE_HOA_DON_THANG).
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson, khoi_phuc_trang_thai
from thuc_the.tai_chinh import HoaDonThang, TrangThaiHoaDon
from tien_ich.cau_hinh_tinh import FILE_HOA_DON_THANG


class LuuTruHoaDonThang(LuuTruJson[HoaDonThang]):
    TEN_FILE = FILE_HOA_DON_THANG
    LOAI = HoaDonThang

    def _sang_dict(self, hd: HoaDonThang) -> dict[str, Any]:
        return {
            "ma": hd.ma,
            "thang": hd.thang,
            "dien_cu": hd.dien_cu,
            "dien_moi": hd.dien_moi,
            "don_gia_dien": hd.don_gia_dien,
            "nuoc_cu": hd.nuoc_cu,
            "nuoc_moi": hd.nuoc_moi,
            "don_gia_nuoc": hd.don_gia_nuoc,
            "phong": hd.phong,  # mã phòng
            "han_chot": hd.han_chot.isoformat(),
            "trang_thai": hd.trang_thai.name,
        }

    def _tu_dict(self, d: dict[str, Any]) -> HoaDonThang:
        hd = HoaDonThang(d["ma"], d["thang"], d["dien_cu"], d["dien_moi"], d["don_gia_dien"],
                         d["nuoc_cu"], d["nuoc_moi"], d["don_gia_nuoc"], d["phong"],
                         date.fromisoformat(d["han_chot"]))
        khoi_phuc_trang_thai(hd, HoaDonThang, TrangThaiHoaDon[d["trang_thai"]])
        return hd
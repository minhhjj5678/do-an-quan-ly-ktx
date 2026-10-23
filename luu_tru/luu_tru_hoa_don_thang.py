# Phần C
# Lưu trữ HoaDonThang xuống file JSON (cau_hinh_tinh.FILE_HOA_DON_THANG).
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson
from thuc_the.hoc_vu import ThangNam
from thuc_the.tai_chinh import HoaDonThang, TrangThaiHoaDon
from tien_ich.cau_hinh_tinh import FILE_HOA_DON_THANG


class LuuTruHoaDonThang(LuuTruJson[HoaDonThang]):
    TEN_FILE = FILE_HOA_DON_THANG
    LOAI = HoaDonThang

    def _sang_dict(self, hd: HoaDonThang) -> dict[str, Any]:
        return {
            "ma": hd.ma,
            "thang_nam": str(hd.thang_nam),  # chuỗi dạng "2026-09" (ThangNam.__str__), đọc lại bằng ThangNam.tu_chuoi
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
        return HoaDonThang(
            ma=d["ma"], thang_nam=ThangNam.tu_chuoi(d["thang_nam"]), dien_cu=d["dien_cu"], dien_moi=d["dien_moi"], don_gia_dien=d["don_gia_dien"],
            nuoc_cu=d["nuoc_cu"], nuoc_moi=d["nuoc_moi"], don_gia_nuoc=d["don_gia_nuoc"], phong=d["phong"],
            han_chot=date.fromisoformat(d["han_chot"]),
            trang_thai=TrangThaiHoaDon[d["trang_thai"]])  # trạng thái truyền thẳng vào hàm khởi tạo
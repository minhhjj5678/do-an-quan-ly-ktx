# Phần C
# Lưu trữ HocKy xuống file JSON (cau_hinh_tinh.FILE_HOC_KY).
# Học kỳ là thực thể nghiệp vụ (hợp đồng và thống kê đều tham chiếu theo mã học kỳ) nên được lưu file như các thực thể khác.
# HocKy không có chức năng lưu trữ/ngừng hoạt động nên không có cờ con_hoat_dong.
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson
from thuc_the.hoc_vu import HocKy
from tien_ich.cau_hinh_tinh import FILE_HOC_KY


class LuuTruHocKy(LuuTruJson[HocKy]):
    TEN_FILE = FILE_HOC_KY
    LOAI = HocKy

    def _sang_dict(self, hk: HocKy) -> dict[str, Any]:
        return {
            "ma": hk.ma,
            "ten": hk.ten,
            # JSON không có kiểu ngày -> lưu chuỗi ISO "2026-09-01", đọc lại bằng date.fromisoformat
            "ngay_bat_dau": hk.ngay_bat_dau.isoformat(),
            "ngay_ket_thuc": hk.ngay_ket_thuc.isoformat(),
        }

    def _tu_dict(self, d: dict[str, Any]) -> HocKy:
        return HocKy(ma=d["ma"], ten=d["ten"],
                     ngay_bat_dau=date.fromisoformat(d["ngay_bat_dau"]),
                     ngay_ket_thuc=date.fromisoformat(d["ngay_ket_thuc"]))
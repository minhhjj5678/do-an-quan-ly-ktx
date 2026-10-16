# Phần C
# Lưu trữ DichVuThem xuống file JSON (cau_hinh_tinh.FILE_DICH_VU_THEM).
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson, khoi_phuc_hoat_dong
from thuc_the.tai_chinh import DichVuThem
from tien_ich.cau_hinh_tinh import FILE_DICH_VU_THEM


class LuuTruDichVuThem(LuuTruJson[DichVuThem]):
    TEN_FILE = FILE_DICH_VU_THEM
    LOAI = DichVuThem

    def _sang_dict(self, dv: DichVuThem) -> dict[str, Any]:
        return {
            "ma": dv.ma,
            "ten": dv.ten,
            "don_gia": dv.don_gia,
            "con_hoat_dong": dv.con_hoat_dong,
        }

    def _tu_dict(self, d: dict[str, Any]) -> DichVuThem:
        dv = DichVuThem(d["ma"], d["ten"], d["don_gia"])
        khoi_phuc_hoat_dong(dv, d["con_hoat_dong"])
        return dv
# Phần C
# Lưu trữ Phong xuống file JSON (cau_hinh_tinh.FILE_PHONG).
# Phong chỉ chứa thông tin của chính nó. Quan hệ với sinh viên (qua HopDong.ma_phong) và với tòa nhà (Phong.toa_nha)
# nằm ở phía còn lại của quan hệ, nên không lưu danh sách nào ở đây.
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson, khoi_phuc_hoat_dong
from thuc_the.ky_tuc_xa import Phong
from tien_ich.cau_hinh_tinh import FILE_PHONG


class LuuTruPhong(LuuTruJson[Phong]):
    TEN_FILE = FILE_PHONG
    LOAI = Phong

    def _sang_dict(self, p: Phong) -> dict[str, Any]:
        return {
            "ma": p.ma,
            "ten": p.ten,
            "suc_chua": p.suc_chua,
            "gia_phong": p.gia_phong,
            "toa_nha": p.toa_nha,  # mã tòa nhà
            "tang": p.tang,
            "con_hoat_dong": p.con_hoat_dong,
        }

    def _tu_dict(self, d: dict[str, Any]) -> Phong:
        p = Phong(d["ma"], d["ten"], d["suc_chua"], d["gia_phong"], d["toa_nha"], d["tang"])
        khoi_phuc_hoat_dong(p, d["con_hoat_dong"])
        return p
# Phần C
# Lưu trữ ViPham xuống file JSON (cau_hinh_tinh.FILE_VI_PHAM).
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson
from thuc_the.vi_pham import TrangThaiViPham, ViPham
from tien_ich.cau_hinh_tinh import FILE_VI_PHAM


class LuuTruViPham(LuuTruJson[ViPham]):
    TEN_FILE = FILE_VI_PHAM
    LOAI = ViPham

    def _sang_dict(self, vp: ViPham) -> dict[str, Any]:
        return {
            "ma": vp.ma,
            "sinh_vien": vp.sinh_vien,  # mã sinh viên
            "ngay_vi_pham": vp.ngay_vi_pham.isoformat(),
            "mo_ta": vp.mo_ta,
            "hinh_thuc_ky_luat": vp.hinh_thuc_ky_luat,
            "trang_thai": vp.trang_thai.name,
        }

    def _tu_dict(self, d: dict[str, Any]) -> ViPham:
        return ViPham(
            ma=d["ma"], sinh_vien=d["sinh_vien"], ngay_vi_pham=date.fromisoformat(d["ngay_vi_pham"]),
            mo_ta=d["mo_ta"], hinh_thuc_ky_luat=d["hinh_thuc_ky_luat"],
            trang_thai=TrangThaiViPham[d["trang_thai"]])  # trạng thái truyền thẳng vào hàm khởi tạo
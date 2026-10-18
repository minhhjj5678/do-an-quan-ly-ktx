# Phần C
# Lưu trữ ViPham xuống file JSON (cau_hinh_tinh.FILE_VI_PHAM).
#
# ViPham có hai class con với thuộc tính riêng:
#   - ViPhamNoiQuy: có hinh_thuc_ky_luat
#   - ViPhamTaiSan: có tien_boi_thuong
# Nếu chỉ lưu chung sẽ mất thông tin "là loại nào" và không dựng lại đúng được, nên mỗi mục
# trong file có thêm khóa "loai" ghi tên loại cụ thể, và khi đọc dùng khóa đó để dựng đúng class.
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson
from thuc_the.vi_pham import TrangThaiViPham, ViPham, ViPhamNoiQuy, ViPhamTaiSan
from tien_ich.cau_hinh_tinh import FILE_VI_PHAM

LOAI_NOI_QUY = "ViPhamNoiQuy"
LOAI_TAI_SAN = "ViPhamTaiSan"


class LuuTruViPham(LuuTruJson[ViPham]):
    TEN_FILE = FILE_VI_PHAM
    LOAI = ViPham  # isinstance(ViPhamNoiQuy(...), ViPham) là True nên ghi được cả hai loại con

    def _sang_dict(self, vp: ViPham) -> dict[str, Any]:
        # Phần thuộc tính chung của mọi loại vi phạm
        d: dict[str, Any] = {
            "ma": vp.ma,
            "sinh_vien": vp.sinh_vien,  # mã sinh viên
            "ngay_vi_pham": vp.ngay_vi_pham.isoformat(),
            "mo_ta": vp.mo_ta,
            "trang_thai": vp.trang_thai.name,
        }
        # Phần riêng theo từng loại + khóa "loai" để đọc lại dựng đúng class
        if isinstance(vp, ViPhamNoiQuy):
            d["loai"] = LOAI_NOI_QUY
            d["hinh_thuc_ky_luat"] = vp.hinh_thuc_ky_luat
        elif isinstance(vp, ViPhamTaiSan):
            d["loai"] = LOAI_TAI_SAN
            d["tien_boi_thuong"] = vp.tien_boi_thuong
        else:
            raise TypeError(f"Chưa hỗ trợ lưu loại vi phạm {type(vp).__name__}")
        return d

    def _tu_dict(self, d: dict[str, Any]) -> ViPham:
        ngay = date.fromisoformat(d["ngay_vi_pham"])
        loai = d["loai"]
        if loai == LOAI_NOI_QUY:
            vp: ViPham = ViPhamNoiQuy(d["ma"], d["sinh_vien"], ngay, d["mo_ta"], d["hinh_thuc_ky_luat"])
        elif loai == LOAI_TAI_SAN:
            vp = ViPhamTaiSan(d["ma"], d["sinh_vien"], ngay, d["mo_ta"], d["tien_boi_thuong"])
        else:
            raise ValueError(f"Loại vi phạm không biết: {loai!r}")
        # ViPham không nhận trạng thái trong hàm khởi tạo nhưng có hàm công khai xu_ly() để chuyển sang "đã xử lý"
        if TrangThaiViPham[d["trang_thai"]] == TrangThaiViPham.DA_XU_LY:
            vp.xu_ly()
        return vp
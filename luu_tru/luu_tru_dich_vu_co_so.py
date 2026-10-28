# Phần C
# Lưu trữ DichVuCoSo xuống MỘT file JSON chung (cau_hinh_tinh.FILE_DICH_VU_THEM) cho cả hai loại con:
#   - DichVuThem: dịch vụ thêm tính theo tháng, thuộc về hợp đồng
#   - TienIchPhong: tiện ích tính theo tháng, thuộc về phòng
# Hai loại dùng chung một kiểu mã (xem tao_ma.ma_dich_vu_them) nên mã không bao giờ trùng nhau và có thể
# nằm chung trong một dict {mã: thực thể}. Mỗi mục trong file có thêm cờ "loai" để khi đọc lên dựng đúng lớp con.
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson, khoi_phuc_hoat_dong
from thuc_the.tai_chinh import DichVuCoSo, DichVuThem, TienIchPhong
from tien_ich.cau_hinh_tinh import FILE_DICH_VU_THEM

# Giá trị của cờ phân loại ghi trong file
LOAI_DICH_VU_THEM = "DichVuThem"
LOAI_TIEN_ICH_PHONG = "TienIchPhong"
_LOP_THEO_LOAI = {LOAI_DICH_VU_THEM: DichVuThem, LOAI_TIEN_ICH_PHONG: TienIchPhong}


class LuuTruDichVuCoSo(LuuTruJson[DichVuCoSo]):
    TEN_FILE = FILE_DICH_VU_THEM
    LOAI = DichVuCoSo  # DichVuThem và TienIchPhong đều là con của DichVuCoSo nên ghi được cả hai

    def _sang_dict(self, dv: DichVuCoSo) -> dict[str, Any]:
        # Kiểm tra từng lớp con để ghi đúng cờ; lớp con lạ (chưa hỗ trợ) thì báo lỗi thay vì ghi sai
        if isinstance(dv, DichVuThem):
            loai = LOAI_DICH_VU_THEM
        elif isinstance(dv, TienIchPhong):
            loai = LOAI_TIEN_ICH_PHONG
        else:
            raise TypeError(f"Chưa hỗ trợ lưu loại dịch vụ {type(dv).__name__}")
        return {
            "loai": loai,
            "ma": dv.ma,
            "ten": dv.ten,
            "don_gia": dv.don_gia,
            "con_hoat_dong": dv.con_hoat_dong,
        }

    def _tu_dict(self, d: dict[str, Any]) -> DichVuCoSo:
        lop = _LOP_THEO_LOAI.get(d["loai"])
        if lop is None:
            raise ValueError(f"Loại dịch vụ không biết: {d['loai']!r}")
        dv = lop(d["ma"], d["ten"], d["don_gia"])  # dựng đúng lớp con theo cờ "loai"
        khoi_phuc_hoat_dong(dv, d["con_hoat_dong"])
        return dv
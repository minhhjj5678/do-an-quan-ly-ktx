# Phần C
# Lưu trữ SinhVien xuống file JSON (tên file lấy từ cau_hinh_tinh.FILE_SINH_VIEN).
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson, khoi_phuc_hoat_dong
from thuc_the.ky_tuc_xa import SinhVien
from tien_ich.cau_hinh_tinh import FILE_SINH_VIEN


class LuuTruSinhVien(LuuTruJson[SinhVien]):
    TEN_FILE = FILE_SINH_VIEN
    LOAI = SinhVien

    def _sang_dict(self, sv: SinhVien) -> dict[str, Any]:
        return {
            "ma": sv.ma,
            "ten": sv.ten,
            "sdt": sv.sdt,
            "nam_sinh": sv.nam_sinh,
            "cccd": sv.cccd,
            "dia_chi_chi_tiet": sv.dia_chi_chi_tiet,
            "xa": sv.xa,
            "tinh": sv.tinh,
            "phong_hien_tai": sv.phong_hien_tai,  # mã phòng hoặc None
            "hop_dong": sv.hop_dong,              # mã hợp đồng hoặc None
            "con_hoat_dong": sv.con_hoat_dong,
        }

    def _tu_dict(self, d: dict[str, Any]) -> SinhVien:
        sv = SinhVien(d["ma"], d["ten"], d["sdt"], d["nam_sinh"], d["cccd"],
                      d["dia_chi_chi_tiet"], d["xa"], d["tinh"])
        # Hai thuộc tính này không nằm trong hàm khởi tạo nên gán qua setter
        sv.phong_hien_tai = d["phong_hien_tai"]
        sv.hop_dong = d["hop_dong"]
        khoi_phuc_hoat_dong(sv, d["con_hoat_dong"])
        return sv
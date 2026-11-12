# Phần C
# Lưu trữ ToaNha xuống file JSON (cau_hinh_tinh.FILE_TOA_NHA).
# ToaNha.them_phong() nhận trực tiếp mã phòng nên lớp này không cần biết gì về file phòng;
# việc kiểm tra chéo "phòng có tồn tại không" thuộc tầng điều phối, không làm ở tầng lưu trữ.
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson, khoi_phuc_hoat_dong
from thuc_the.ky_tuc_xa import ToaNha
from tien_ich.cau_hinh_tinh import FILE_TOA_NHA


class LuuTruToaNha(LuuTruJson[ToaNha]):
    TEN_FILE = FILE_TOA_NHA
    LOAI = ToaNha

    def _sang_dict(self, tn: ToaNha) -> dict[str, Any]:
        return {
            "ma": tn.ma,
            "ten": tn.ten,
            "so_tang": tn.so_tang,
            "danh_sach_phong": sorted(tn.danh_sach_phong),  # mã các phòng, sắp xếp để thứ tự trong file ổn định
            "con_hoat_dong": tn.con_hoat_dong,
        }

    def _tu_dict(self, d: dict[str, Any]) -> ToaNha:
        tn = ToaNha(d["ma"], d["ten"], d["so_tang"])
        for ma_phong in d["danh_sach_phong"]:
            tn.them_phong(ma_phong)  # truyền thẳng mã phòng
        khoi_phuc_hoat_dong(tn, d["con_hoat_dong"])
        return tn
# Phần C
# Lưu trữ Phong xuống file JSON (cau_hinh_tinh.FILE_PHONG).
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
            # Hai tập (set) này JSON không có kiểu tương ứng nên lưu thành list; sorted() để thứ tự trong file ổn định,
            # lần ghi nào cũng ra cùng một nội dung nếu dữ liệu không đổi
            "tien_ich_phong": sorted(p.tien_ich_phong),            # mã các tiện ích
            "danh_sach_sinh_vien": sorted(p.danh_sach_sinh_vien),  # mã các sinh viên đang ở
            "con_hoat_dong": p.con_hoat_dong,
        }

    def _tu_dict(self, d: dict[str, Any]) -> Phong:
        # Tiện ích nhận được ngay trong hàm khởi tạo; danh sách sinh viên thì Phong chỉ cho thêm qua them_sinh_vien()
        p = Phong(d["ma"], d["ten"], d["suc_chua"], d["gia_phong"], d["toa_nha"], d["tang"], set(d["tien_ich_phong"]))
        for ma_sinh_vien in d["danh_sach_sinh_vien"]:
            p.them_sinh_vien(ma_sinh_vien)
        # Lưu trữ phòng đặt SAU CÙNG vì phòng đã ngừng hoạt động có thể không cho thêm sinh viên nữa
        khoi_phuc_hoat_dong(p, d["con_hoat_dong"])
        return p
# Phần C
# Lưu trữ HopDong xuống file JSON (cau_hinh_tinh.FILE_HOP_DONG).
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson
from thuc_the.tai_chinh import HopDong, TrangThaiHopDong
from tien_ich.cau_hinh_tinh import FILE_HOP_DONG


class LuuTruHopDong(LuuTruJson[HopDong]):
    TEN_FILE = FILE_HOP_DONG
    LOAI = HopDong

    def _sang_dict(self, hd: HopDong) -> dict[str, Any]:
        return {
            "ma": hd.ma,
            # JSON không có kiểu ngày -> lưu chuỗi ISO "2026-10-14", đọc lại bằng date.fromisoformat
            "ngay_ky": hd.ngay_ky.isoformat(),
            "ngay_het_han": hd.ngay_het_han.isoformat(),  # hạn giữ chỗ khi chưa thanh toán
            "ngay_bat_dau": hd.ngay_bat_dau.isoformat(),
            "ngay_ket_thuc": hd.ngay_ket_thuc.isoformat(),
            "he_so_thang": hd.he_so_thang,
            "gia_phong": hd.gia_phong,
            "tien_dat_coc": hd.tien_dat_coc,
            "ma_sinh_vien": hd.ma_sinh_vien,
            "ma_phong": hd.ma_phong,
            # Lưu TÊN của enum (CHUA_THANH_TOAN...) thay vì chữ hiển thị, để đổi chữ hiển thị không làm hỏng file cũ
            "trang_thai": hd.trang_thai.name,
        }

    def _tu_dict(self, d: dict[str, Any]) -> HopDong:
        return HopDong(
            ma=d["ma"],
            ngay_ky=date.fromisoformat(d["ngay_ky"]), ngay_het_han=date.fromisoformat(d["ngay_het_han"]),
            ngay_bat_dau=date.fromisoformat(d["ngay_bat_dau"]), ngay_ket_thuc=date.fromisoformat(d["ngay_ket_thuc"]),
            he_so_thang=d["he_so_thang"], gia_phong=d["gia_phong"], tien_dat_coc=d["tien_dat_coc"],
            ma_sinh_vien=d["ma_sinh_vien"], ma_phong=d["ma_phong"],
            trang_thai=TrangThaiHopDong[d["trang_thai"]])  # trạng thái truyền thẳng vào hàm khởi tạo
# Phần C
# Lưu trữ HopDong xuống file JSON (cau_hinh_tinh.FILE_HOP_DONG).
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson, khoi_phuc_trang_thai
from thuc_the.tai_chinh import HopDong, TrangThaiHopDong
from tien_ich.cau_hinh_tinh import FILE_HOP_DONG


class LuuTruHopDong(LuuTruJson[HopDong]):
    TEN_FILE = FILE_HOP_DONG
    LOAI = HopDong

    def _sang_dict(self, hd: HopDong) -> dict[str, Any]:
        return {
            "ma": hd.ma,
            "he_so_thang": hd.he_so_thang,
            # JSON không có kiểu ngày -> lưu chuỗi ISO "2026-10-14", đọc lại bằng date.fromisoformat
            "ngay_bat_dau": hd.ngay_bat_dau.isoformat(),
            "ngay_ket_thuc": hd.ngay_ket_thuc.isoformat(),
            "gia_co_ban": hd.gia_co_ban,
            "tien_dat_coc": hd.tien_dat_coc,
            "ma_sinh_vien": hd.ma_sinh_vien,
            "ma_phong": hd.ma_phong,
            "hoc_ky": hd.hoc_ky,
            "dich_vu_them": hd.dich_vu_them,  # {mã dịch vụ: số lượng/giá}, property trả về bản copy
            "phi_tien_nghi": hd.phi_tien_nghi,
            # Lưu TÊN của enum (CHUA_THANH_TOAN...) thay vì chữ hiển thị, để đổi chữ hiển thị không làm hỏng file cũ
            "trang_thai": hd.trang_thai.name,
        }

    def _tu_dict(self, d: dict[str, Any]) -> HopDong:
        hd = HopDong(d["ma"], d["he_so_thang"],
                     date.fromisoformat(d["ngay_bat_dau"]), date.fromisoformat(d["ngay_ket_thuc"]),
                     d["gia_co_ban"], d["tien_dat_coc"], d["ma_sinh_vien"], d["ma_phong"], d["hoc_ky"],
                     d["dich_vu_them"], d["phi_tien_nghi"])
        # Hàm khởi tạo luôn đặt "chưa thanh toán"; trả về đúng trạng thái đã lưu trong file
        khoi_phuc_trang_thai(hd, HopDong, TrangThaiHopDong[d["trang_thai"]])
        return hd
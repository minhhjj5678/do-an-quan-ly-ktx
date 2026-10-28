# Phần C
# Lưu trữ TaiKhoan xuống file JSON (cau_hinh_tinh.FILE_TAI_KHOAN).
# Chỉ lưu mật khẩu ĐÃ BĂM (mat_khau_bam), không bao giờ lưu mật khẩu gốc.
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson, khoi_phuc_hoat_dong
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from tien_ich.cau_hinh_tinh import FILE_TAI_KHOAN


class LuuTruTaiKhoan(LuuTruJson[TaiKhoan]):
    TEN_FILE = FILE_TAI_KHOAN
    LOAI = TaiKhoan

    def _sang_dict(self, tk: TaiKhoan) -> dict[str, Any]:
        return {
            "ma": tk.ma,  # tên đăng nhập (ma_dang_nhap) chính là mã của tài khoản
            "mat_khau_bam": tk.mat_khau_bam,
            "loai_tai_khoan": tk.loai_tai_khoan.name,
            "ma_chu_the": tk.ma_chu_the,  # mã sinh viên, hoặc None với quản trị viên
            "con_hoat_dong": tk.con_hoat_dong,
        }

    def _tu_dict(self, d: dict[str, Any]) -> TaiKhoan:
        tk = TaiKhoan(d["ma"], d["mat_khau_bam"], LoaiTaiKhoan[d["loai_tai_khoan"]], d["ma_chu_the"])
        khoi_phuc_hoat_dong(tk, d["con_hoat_dong"])
        return tk
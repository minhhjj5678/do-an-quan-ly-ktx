# Phần C
# Lưu trữ HopDong xuống file JSON (FILE_HOP_DONG).
# Ngày lưu dạng chuỗi ISO; trạng thái lưu bằng TÊN enum để đổi chữ hiển thị không làm hỏng file cũ.
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import (LuuTruJson, co_bi_chinh_sua, doc_json, ghi_json, kiem_tra_danh_sach_ghi, kiem_tra_truoc_khi_doc)
from thuc_the.tai_chinh import HopDong, TrangThaiHopDong
from tien_ich.cau_hinh_tinh import FILE_HOP_DONG
from tien_ich.tap_tin import lay_duong_dan_du_lieu, lay_duong_dan_sao_luu


class LuuTruHopDong(LuuTruJson[HopDong]):
    TEN_FILE = FILE_HOP_DONG
    LOAI = HopDong

    def __init__(self) -> None:
        self._da_kiem_tra_khoi_dong = False  # chỉ kiểm tra "bị sửa ngoài app" ở lần doc() đầu

    def _doc_file(self, duong_dan: str) -> dict[str, HopDong]:
        ket_qua: dict[str, HopDong] = {}
        for vi_tri, d in enumerate(doc_json(duong_dan)):
            try:
                thuc_the = HopDong(
                    ma=d["ma"], ngay_ky=date.fromisoformat(d["ngay_ky"]), ngay_het_han=date.fromisoformat(d["ngay_het_han"]),
                    ngay_bat_dau=date.fromisoformat(d["ngay_bat_dau"]), ngay_ket_thuc=date.fromisoformat(d["ngay_ket_thuc"]),
                    he_so_thang=d["he_so_thang"], gia_phong=d["gia_phong"], tien_dat_coc=d["tien_dat_coc"],
                    ma_sinh_vien=d["ma_sinh_vien"], ma_phong=d["ma_phong"], trang_thai=TrangThaiHopDong[d["trang_thai"]])
            except (KeyError, TypeError, AttributeError, ValueError) as loi:
                raise ValueError(f"File {self.TEN_FILE} hỏng ở mục thứ {vi_tri}: {loi!r}") from loi
            if thuc_the.ma in ket_qua:
                raise ValueError(f"File {self.TEN_FILE} có mã trùng lặp: {thuc_the.ma}")
            ket_qua[thuc_the.ma] = thuc_the
        return ket_qua

    def doc(self) -> dict[str, HopDong]:
        kiem_tra_truoc_khi_doc(self.TEN_FILE, self._da_kiem_tra_khoi_dong)
        ket_qua = self._doc_file(lay_duong_dan_du_lieu(self.TEN_FILE))
        self._da_kiem_tra_khoi_dong = True
        return ket_qua

    def doc_sao_luu(self) -> dict[str, HopDong]:
        return self._doc_file(lay_duong_dan_sao_luu(self.TEN_FILE))

    def ghi(self, danh_sach: dict[str, HopDong]) -> None:
        kiem_tra_danh_sach_ghi(danh_sach, HopDong)
        # đổi sang dict TRƯỚC khi đụng file: lỗi ở đây thì file cũ vẫn nguyên
        du_lieu: list[dict[str, Any]] = [{
            "ma": tt.ma, "ngay_ky": tt.ngay_ky.isoformat(), "ngay_het_han": tt.ngay_het_han.isoformat(),
            "ngay_bat_dau": tt.ngay_bat_dau.isoformat(), "ngay_ket_thuc": tt.ngay_ket_thuc.isoformat(),
            "he_so_thang": tt.he_so_thang, "gia_phong": tt.gia_phong, "tien_dat_coc": tt.tien_dat_coc,
            "ma_sinh_vien": tt.ma_sinh_vien, "ma_phong": tt.ma_phong, "trang_thai": tt.trang_thai.name,
        } for tt in danh_sach.values()]
        ghi_json(self.TEN_FILE, du_lieu)
        self._da_kiem_tra_khoi_dong = True

    def co_bi_chinh_sua(self) -> bool:
        return co_bi_chinh_sua(self.TEN_FILE)
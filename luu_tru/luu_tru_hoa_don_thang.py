# Phần C
# Lưu trữ HoaDonThang xuống file JSON (FILE_HOA_DON_THANG).
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import (LuuTruJson, co_bi_chinh_sua, doc_json, ghi_json, kiem_tra_danh_sach_ghi, kiem_tra_truoc_khi_doc)
from thuc_the.tai_chinh import HoaDonThang, ThangNam, TrangThaiHoaDon
from tien_ich.cau_hinh_tinh import FILE_HOA_DON_THANG
from tien_ich.tap_tin import lay_duong_dan_du_lieu, lay_duong_dan_sao_luu


class LuuTruHoaDonThang(LuuTruJson[HoaDonThang]):
    TEN_FILE = FILE_HOA_DON_THANG
    LOAI = HoaDonThang

    def __init__(self) -> None:
        self._da_kiem_tra_khoi_dong = False  # chỉ kiểm tra "bị sửa ngoài app" ở lần doc() đầu

    def _doc_file(self, duong_dan: str) -> dict[str, HoaDonThang]:
        ket_qua: dict[str, HoaDonThang] = {}
        for vi_tri, d in enumerate(doc_json(duong_dan)):
            try:
                thuc_the = HoaDonThang(
                    ma=d["ma"], thang_nam=ThangNam.tu_chuoi(d["thang_nam"]), dien_cu=d["dien_cu"], dien_moi=d["dien_moi"],
                    don_gia_dien=d["don_gia_dien"], nuoc_cu=d["nuoc_cu"], nuoc_moi=d["nuoc_moi"], don_gia_nuoc=d["don_gia_nuoc"],
                    phong=d["phong"], han_chot=date.fromisoformat(d["han_chot"]), trang_thai=TrangThaiHoaDon[d["trang_thai"]])
            except (KeyError, TypeError, AttributeError, ValueError) as loi:
                raise ValueError(f"File {self.TEN_FILE} hỏng ở mục thứ {vi_tri}: {loi!r}") from loi
            if thuc_the.ma in ket_qua:
                raise ValueError(f"File {self.TEN_FILE} có mã trùng lặp: {thuc_the.ma}")
            ket_qua[thuc_the.ma] = thuc_the
        return ket_qua

    def doc(self) -> dict[str, HoaDonThang]:
        kiem_tra_truoc_khi_doc(self.TEN_FILE, self._da_kiem_tra_khoi_dong)
        ket_qua = self._doc_file(lay_duong_dan_du_lieu(self.TEN_FILE))
        self._da_kiem_tra_khoi_dong = True
        return ket_qua

    def doc_sao_luu(self) -> dict[str, HoaDonThang]:
        return self._doc_file(lay_duong_dan_sao_luu(self.TEN_FILE))

    def ghi(self, danh_sach: dict[str, HoaDonThang]) -> None:
        kiem_tra_danh_sach_ghi(danh_sach, HoaDonThang)
        # đổi sang dict TRƯỚC khi đụng file: lỗi ở đây thì file cũ vẫn nguyên
        du_lieu: list[dict[str, Any]] = [{
            "ma": tt.ma, "thang_nam": str(tt.thang_nam),  # dạng "2026-09", đọc lại bằng ThangNam.tu_chuoi
            "dien_cu": tt.dien_cu, "dien_moi": tt.dien_moi, "don_gia_dien": tt.don_gia_dien,
            "nuoc_cu": tt.nuoc_cu, "nuoc_moi": tt.nuoc_moi, "don_gia_nuoc": tt.don_gia_nuoc,
            "phong": tt.phong,  # mã phòng
            "han_chot": tt.han_chot.isoformat(), "trang_thai": tt.trang_thai.name,
        } for tt in danh_sach.values()]
        ghi_json(self.TEN_FILE, du_lieu)
        self._da_kiem_tra_khoi_dong = True

    def co_bi_chinh_sua(self) -> bool:
        return co_bi_chinh_sua(self.TEN_FILE)
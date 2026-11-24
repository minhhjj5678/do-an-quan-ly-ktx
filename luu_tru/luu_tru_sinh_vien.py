# Phần C
# Lưu trữ SinhVien xuống file JSON (FILE_SINH_VIEN).
# SinhVien không ghi phòng hay hợp đồng: quan hệ đó nằm ở HopDong (ma_sinh_vien, ma_phong).
from typing import Any

from luu_tru.luu_tru_json import (LuuTruJson, co_bi_chinh_sua, doc_json, ghi_json, khoi_phuc_hoat_dong, kiem_tra_danh_sach_ghi, kiem_tra_truoc_khi_doc)
from thuc_the.ky_tuc_xa import SinhVien
from tien_ich.cau_hinh_tinh import FILE_SINH_VIEN
from tien_ich.tap_tin import lay_duong_dan_du_lieu, lay_duong_dan_sao_luu


class LuuTruSinhVien(LuuTruJson[SinhVien]):
    TEN_FILE = FILE_SINH_VIEN
    LOAI = SinhVien

    def __init__(self) -> None:
        self._da_kiem_tra_khoi_dong = False  # chỉ kiểm tra "bị sửa ngoài app" ở lần doc() đầu

    def _doc_file(self, duong_dan: str) -> dict[str, SinhVien]:
        ket_qua: dict[str, SinhVien] = {}
        for vi_tri, d in enumerate(doc_json(duong_dan)):
            try:
                thuc_the = SinhVien(d["ma"], d["ten"], d["sdt"], d["nam_sinh"], d["cccd"],
                                   d["dia_chi_chi_tiet"], d["xa"], d["tinh"])
                khoi_phuc_hoat_dong(thuc_the, d["con_hoat_dong"])
            except (KeyError, TypeError, AttributeError, ValueError) as loi:
                raise ValueError(f"File {self.TEN_FILE} hỏng ở mục thứ {vi_tri}: {loi!r}") from loi
            if thuc_the.ma in ket_qua:
                raise ValueError(f"File {self.TEN_FILE} có mã trùng lặp: {thuc_the.ma}")
            ket_qua[thuc_the.ma] = thuc_the
        return ket_qua

    def doc(self) -> dict[str, SinhVien]:
        kiem_tra_truoc_khi_doc(self.TEN_FILE, self._da_kiem_tra_khoi_dong)
        ket_qua = self._doc_file(lay_duong_dan_du_lieu(self.TEN_FILE))
        self._da_kiem_tra_khoi_dong = True
        return ket_qua

    def doc_sao_luu(self) -> dict[str, SinhVien]:
        return self._doc_file(lay_duong_dan_sao_luu(self.TEN_FILE))

    def ghi(self, danh_sach: dict[str, SinhVien]) -> None:
        kiem_tra_danh_sach_ghi(danh_sach, SinhVien)
        # đổi sang dict TRƯỚC khi đụng file: lỗi ở đây thì file cũ vẫn nguyên
        du_lieu: list[dict[str, Any]] = [{
            "ma": tt.ma, "ten": tt.ten, "sdt": tt.sdt, "nam_sinh": tt.nam_sinh, "cccd": tt.cccd,
            "dia_chi_chi_tiet": tt.dia_chi_chi_tiet, "xa": tt.xa, "tinh": tt.tinh,
            "con_hoat_dong": tt.con_hoat_dong,
        } for tt in danh_sach.values()]
        ghi_json(self.TEN_FILE, du_lieu)
        self._da_kiem_tra_khoi_dong = True

    def co_bi_chinh_sua(self) -> bool:
        return co_bi_chinh_sua(self.TEN_FILE)
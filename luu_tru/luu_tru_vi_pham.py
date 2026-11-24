# Phần C
# Lưu trữ ViPham xuống file JSON (FILE_VI_PHAM).
from datetime import date
from typing import Any

from luu_tru.luu_tru_json import (LuuTruJson, co_bi_chinh_sua, doc_json, ghi_json, kiem_tra_danh_sach_ghi, kiem_tra_truoc_khi_doc)
from thuc_the.vi_pham import ViPham, TrangThaiViPham
from tien_ich.cau_hinh_tinh import FILE_VI_PHAM
from tien_ich.tap_tin import lay_duong_dan_du_lieu, lay_duong_dan_sao_luu


class LuuTruViPham(LuuTruJson[ViPham]):
    TEN_FILE = FILE_VI_PHAM
    LOAI = ViPham

    def __init__(self) -> None:
        self._da_kiem_tra_khoi_dong = False  # chỉ kiểm tra "bị sửa ngoài app" ở lần doc() đầu

    def _doc_file(self, duong_dan: str) -> dict[str, ViPham]:
        ket_qua: dict[str, ViPham] = {}
        for vi_tri, d in enumerate(doc_json(duong_dan)):
            try:
                thuc_the = ViPham(ma=d["ma"], sinh_vien=d["sinh_vien"], ngay_vi_pham=date.fromisoformat(d["ngay_vi_pham"]),
                                  mo_ta=d["mo_ta"], hinh_thuc_ky_luat=d["hinh_thuc_ky_luat"],
                                  trang_thai=TrangThaiViPham[d["trang_thai"]])
            except (KeyError, TypeError, AttributeError, ValueError) as loi:
                raise ValueError(f"File {self.TEN_FILE} hỏng ở mục thứ {vi_tri}: {loi!r}") from loi
            if thuc_the.ma in ket_qua:
                raise ValueError(f"File {self.TEN_FILE} có mã trùng lặp: {thuc_the.ma}")
            ket_qua[thuc_the.ma] = thuc_the
        return ket_qua

    def doc(self) -> dict[str, ViPham]:
        kiem_tra_truoc_khi_doc(self.TEN_FILE, self._da_kiem_tra_khoi_dong)
        ket_qua = self._doc_file(lay_duong_dan_du_lieu(self.TEN_FILE))
        self._da_kiem_tra_khoi_dong = True
        return ket_qua

    def doc_sao_luu(self) -> dict[str, ViPham]:
        return self._doc_file(lay_duong_dan_sao_luu(self.TEN_FILE))

    def ghi(self, danh_sach: dict[str, ViPham]) -> None:
        kiem_tra_danh_sach_ghi(danh_sach, ViPham)
        # đổi sang dict TRƯỚC khi đụng file: lỗi ở đây thì file cũ vẫn nguyên
        du_lieu: list[dict[str, Any]] = [{
            "ma": tt.ma, "sinh_vien": tt.sinh_vien,  # mã sinh viên
            "ngay_vi_pham": tt.ngay_vi_pham.isoformat(), "mo_ta": tt.mo_ta,
            "hinh_thuc_ky_luat": tt.hinh_thuc_ky_luat, "trang_thai": tt.trang_thai.name,
        } for tt in danh_sach.values()]
        ghi_json(self.TEN_FILE, du_lieu)
        self._da_kiem_tra_khoi_dong = True

    def co_bi_chinh_sua(self) -> bool:
        return co_bi_chinh_sua(self.TEN_FILE)
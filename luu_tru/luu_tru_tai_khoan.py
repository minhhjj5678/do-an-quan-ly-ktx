# Phần C
# Lưu trữ TaiKhoan xuống file JSON (FILE_TAI_KHOAN).
# Chỉ lưu mật khẩu ĐÃ BĂM (mat_khau_bam), không bao giờ lưu mật khẩu gốc.
from typing import Any

from luu_tru.luu_tru_json import (LuuTruJson, can_tao_file_moi, co_bi_chinh_sua, doc_json, ghi_json, khoi_phuc_hoat_dong, kiem_tra_danh_sach_ghi, kiem_tra_truoc_khi_doc)
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from tien_ich.cau_hinh_tinh import FILE_TAI_KHOAN
from tien_ich.tap_tin import lay_duong_dan_du_lieu, lay_duong_dan_sao_luu


class LuuTruTaiKhoan(LuuTruJson[TaiKhoan]):
    TEN_FILE = FILE_TAI_KHOAN
    LOAI = TaiKhoan

    def __init__(self) -> None:
        self._da_kiem_tra_khoi_dong = False  # chỉ kiểm tra "bị sửa ngoài app" ở lần doc() đầu

    def _doc_file(self, duong_dan: str) -> dict[str, TaiKhoan]:
        ket_qua: dict[str, TaiKhoan] = {}
        for vi_tri, d in enumerate(doc_json(duong_dan)):
            try:
                thuc_the = TaiKhoan(d["ma"], d["mat_khau_bam"], LoaiTaiKhoan[d["loai_tai_khoan"]], d["ma_chu_the"])
                khoi_phuc_hoat_dong(thuc_the, d["con_hoat_dong"])
            except (KeyError, TypeError, AttributeError, ValueError) as loi:
                raise ValueError(f"File {self.TEN_FILE} hỏng ở mục thứ {vi_tri}: {loi!r}") from loi
            if thuc_the.ma in ket_qua:
                raise ValueError(f"File {self.TEN_FILE} có mã trùng lặp: {thuc_the.ma}")
            ket_qua[thuc_the.ma] = thuc_the
        return ket_qua

    def doc(self) -> dict[str, TaiKhoan]:
        kiem_tra_truoc_khi_doc(self.TEN_FILE, self._da_kiem_tra_khoi_dong)
        ket_qua = self._doc_file(lay_duong_dan_du_lieu(self.TEN_FILE))
        self._da_kiem_tra_khoi_dong = True
        return ket_qua

    def doc_sao_luu(self) -> dict[str, TaiKhoan]:
        # Chạy lần đầu (file chính lẫn sao lưu đều chưa có): tạo file rỗng, không báo lỗi
        if can_tao_file_moi(self.TEN_FILE):
            self.ghi({})
            return {}
        return self._doc_file(lay_duong_dan_sao_luu(self.TEN_FILE))

    def ghi(self, danh_sach: dict[str, TaiKhoan]) -> None:
        kiem_tra_danh_sach_ghi(danh_sach, TaiKhoan)
        # đổi sang dict TRƯỚC khi đụng file: lỗi ở đây thì file cũ vẫn nguyên
        du_lieu: list[dict[str, Any]] = [{
            "ma": tt.ma,  # tên đăng nhập chính là mã tài khoản
            "mat_khau_bam": tt.mat_khau_bam,
            "loai_tai_khoan": tt.loai_tai_khoan.name,
            "ma_chu_the": tt.ma_chu_the,  # mã sinh viên, hoặc None với quản trị viên
            "con_hoat_dong": tt.con_hoat_dong,
        } for tt in danh_sach.values()]
        ghi_json(self.TEN_FILE, du_lieu)
        self._da_kiem_tra_khoi_dong = True

    def co_bi_chinh_sua(self) -> bool:
        return co_bi_chinh_sua(self.TEN_FILE)
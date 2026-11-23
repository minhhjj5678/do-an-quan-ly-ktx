# Phần C
# Lưu trữ địa lý (tỉnh và các xã trực thuộc) phục vụ danh_sach_dia_ly.
#
# Nguồn dữ liệu: API công cộng https://provinces.open-api.vn/ (bản v2 = sau sáp nhập 07/2025,
# chỉ còn hai cấp Tỉnh -> Xã/Phường, khớp với dropdown tỉnh -> xã của màn hình sinh viên).
#
# Chiến lược (theo đúng thiết kế trong giao_thuc/luu_tru.py):
#   1. doc(): chỉ đọc file cục bộ du_lieu/dia_ly.json (nhanh, không đụng tới mạng)
#   2. File chính không dùng được -> tầng điều phối gọi doc_sao_luu(): đọc file sao lưu
#   3. Sao lưu cũng hỏng/chưa có -> doc_sao_luu() đọc trực tiếp từ API (có timeout), lưu lại xuống file cho lần sau.
#      Việc gọi mạng có thể mất vài giây nên tầng điều phối phải chạy nó trong luồng phụ (nap_du_lieu_api).
import json
import urllib.request
from typing import Any

from giao_thuc.luu_tru import GiaoThucLuuTru
from luu_tru.luu_tru_json import (co_bi_chinh_sua, doc_json, ghi_json,
                                  kiem_tra_danh_sach_ghi, kiem_tra_truoc_khi_doc)
from thuc_the.dia_ly import Tinh, Xa
from tien_ich.cau_hinh_tinh import FILE_DIA_LY
from tien_ich.tap_tin import lay_duong_dan_du_lieu, lay_duong_dan_sao_luu

# depth=2: mỗi tỉnh kèm luôn danh sách xã, nên chỉ cần MỘT lần gọi cho cả nước
URL_API = "https://provinces.open-api.vn/api/v2/?depth=2"
THOI_GIAN_CHO_GIAY = 20


class LuuTruDiaLy(GiaoThucLuuTru[Tinh]):
    TEN_FILE = FILE_DIA_LY

    def __init__(self) -> None:
        self._da_kiem_tra_khoi_dong = False  # chỉ kiểm tra "bị sửa ngoài app" ở lần doc() đầu

    @property
    def loai_thuc_the(self) -> type[Tinh]:
        return Tinh

    # ---- Đọc / ghi file cục bộ ----
    def _doc_file(self, duong_dan: str) -> dict[str, Tinh]:
        ket_qua: dict[str, Tinh] = {}
        for vi_tri, d in enumerate(doc_json(duong_dan)):
            try:
                thuc_the = Tinh(d["ma"], d["ten"],
                                {x["ma"]: Xa(x["ma"], x["ten"]) for x in d["danh_sach_xa"]})
            except (KeyError, TypeError, AttributeError, ValueError) as loi:
                raise ValueError(f"File {self.TEN_FILE} hỏng ở mục thứ {vi_tri}: {loi!r}") from loi
            if thuc_the.ma in ket_qua:
                raise ValueError(f"File {self.TEN_FILE} có mã trùng lặp: {thuc_the.ma}")
            ket_qua[thuc_the.ma] = thuc_the
        return ket_qua

    def doc(self) -> dict[str, Tinh]:
        kiem_tra_truoc_khi_doc(self.TEN_FILE, self._da_kiem_tra_khoi_dong)
        ket_qua = self._doc_file(lay_duong_dan_du_lieu(self.TEN_FILE))
        self._da_kiem_tra_khoi_dong = True
        return ket_qua

    def ghi(self, danh_sach: dict[str, Tinh]) -> None:
        kiem_tra_danh_sach_ghi(danh_sach, Tinh)
        du_lieu: list[dict[str, Any]] = [{
            "ma": tt.ma,
            "ten": tt.ten,
            "danh_sach_xa": [{"ma": xa.ma, "ten": xa.ten} for xa in tt.danh_sach_xa.values()],
        } for tt in danh_sach.values()]
        ghi_json(self.TEN_FILE, du_lieu)
        self._da_kiem_tra_khoi_dong = True

    def co_bi_chinh_sua(self) -> bool:
        return co_bi_chinh_sua(self.TEN_FILE)

    # ---- Gọi API ----
    def _goi_api(self) -> Any:
        """Gửi GET tới API và trả về JSON đã giải mã. Tách riêng để dễ thay thế khi kiểm thử."""
        yeu_cau = urllib.request.Request(URL_API, headers={"Accept": "application/json"})
        with urllib.request.urlopen(yeu_cau, timeout=THOI_GIAN_CHO_GIAY) as phan_hoi:
            return json.loads(phan_hoi.read().decode("utf-8"))

    @staticmethod
    def _phan_tich_api(du_lieu: Any) -> dict[str, Tinh]:
        """
        Đổi JSON của API thành {mã tỉnh: Tinh}. Mỗi tỉnh có dạng:
            {"name": "Thành phố Hà Nội", "code": 1, ..., "wards": [{"name": "Phường Ba Đình", "code": 4, ...}, ...]}
        Mã trong API là số nguyên, còn ma của thực thể là chuỗi nên đổi bằng str().
        Ném ValueError nếu cấu trúc khác dự kiến.
        """
        if not isinstance(du_lieu, list) or not du_lieu:
            raise ValueError("API địa lý trả về dữ liệu rỗng hoặc sai cấu trúc")
        ket_qua: dict[str, Tinh] = {}
        try:
            for tinh in du_lieu:
                cac_xa = tinh["wards"]
                if not isinstance(cac_xa, list):  # wards = null nghĩa là thiếu depth=2
                    raise ValueError("Thiếu danh sách xã (wards)")
                ma = str(tinh["code"])
                if ma in ket_qua:
                    raise ValueError(f"Mã tỉnh bị trùng: {ma}")
                ket_qua[ma] = Tinh(
                    ma,
                    tinh["name"],
                    {str(xa["code"]): Xa(str(xa["code"]), xa["name"]) for xa in cac_xa},
                )
        except (KeyError, TypeError, ValueError) as loi:
            raise ValueError(f"API địa lý trả về dữ liệu không đúng định dạng: {loi!r}") from loi
        return ket_qua

    def tai_tu_api(self) -> dict[str, Tinh]:
        """Tải tỉnh/xã từ API (không lưu). Ném OSError nếu mất mạng, lỗi HTTP, timeout hoặc dữ liệu sai định dạng."""
        try:
            return self._phan_tich_api(self._goi_api())
        except (OSError, ValueError) as loi:
            raise OSError(f"Không tải được dữ liệu địa lý từ API: {loi}") from loi

    def _tai_va_luu(self) -> dict[str, Tinh]:
        """Tải từ API rồi ghi xuống file chính + sao lưu để lần sau không cần mạng."""
        danh_sach = self.tai_tu_api()
        try:
            self.ghi(danh_sach)
        except OSError:
            pass  # không lưu được (ví dụ ổ đĩa chỉ đọc) thì vẫn dùng dữ liệu vừa tải
        return danh_sach

    def doc_sao_luu(self) -> dict[str, Tinh]:
        """
        Đọc file sao lưu; nếu hỏng hoặc chưa có thì đọc trực tiếp từ API (và lưu lại, khôi phục luôn file chính).
        Ném OSError nếu API cũng không dùng được.
        """
        try:
            danh_sach = self._doc_file(lay_duong_dan_sao_luu(self.TEN_FILE))
            if danh_sach:
                return danh_sach
        except (ValueError, FileNotFoundError):
            pass  # sao lưu hỏng/chưa có -> sang API
        return self._tai_va_luu()
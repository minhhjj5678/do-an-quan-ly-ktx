# Phần C
# Lưu trữ địa lý (tỉnh và các xã trực thuộc) phục vụ danh_sach_dia_ly.
#
# Nguồn dữ liệu: API công cộng https://provinces.open-api.vn/ (bản v2 = sau sáp nhập 07/2025,
# chỉ còn hai cấp Tỉnh -> Xã/Phường, khớp với dropdown tỉnh -> xã của màn hình sinh viên).
#
# Chiến lược (theo đúng thiết kế trong giao_thuc/luu_tru.py):
#   1. doc(): chỉ đọc file cục bộ du_lieu/dia_ly.json (nhanh, không đụng tới mạng), y như các lớp lưu trữ khác
#   2. File chính không dùng được -> tầng điều phối gọi doc_sao_luu(): đọc file sao lưu
#   3. Sao lưu cũng hỏng/chưa có -> doc_sao_luu() đọc trực tiếp từ API (có timeout), lưu lại xuống file cho lần sau.
#      Việc gọi mạng có thể mất vài giây nên tầng điều phối phải chạy nó trong luồng phụ (nap_du_lieu_api).
import json
import urllib.request
from typing import Any

from luu_tru.luu_tru_json import LuuTruJson
from thuc_the.dia_ly import Tinh, Xa
from tien_ich.cau_hinh_tinh import FILE_DIA_LY

# depth=2: mỗi tỉnh kèm luôn danh sách xã của nó, nên chỉ cần MỘT lần gọi cho cả nước
# (tránh gọi 30+ lần, API công cộng yêu cầu không lạm dụng)
URL_API = "https://provinces.open-api.vn/api/v2/?depth=2"
THOI_GIAN_CHO_GIAY = 20


class LuuTruDiaLy(LuuTruJson[Tinh]):
    TEN_FILE = FILE_DIA_LY
    LOAI = Tinh

    # ---- Đổi Tinh <-> dict để lưu JSON ----
    def _sang_dict(self, tinh: Tinh) -> dict[str, Any]:
        return {
            "ma": tinh.ma,
            "ten": tinh.ten,
            "danh_sach_xa": [{"ma": xa.ma, "ten": xa.ten} for xa in tinh.danh_sach_xa],
        }

    def _tu_dict(self, d: dict[str, Any]) -> Tinh:
        return Tinh(d["ma"], d["ten"], [Xa(x["ma"], x["ten"]) for x in d["danh_sach_xa"]])

    # ---- Gọi API ----
    def _goi_api(self) -> Any:
        """Gửi yêu cầu GET tới API và trả về dữ liệu JSON đã giải mã. Tách riêng thành hàm để dễ thay thế khi kiểm thử."""
        yeu_cau = urllib.request.Request(URL_API, headers={"Accept": "application/json"})
        with urllib.request.urlopen(yeu_cau, timeout=THOI_GIAN_CHO_GIAY) as phan_hoi:
            return json.loads(phan_hoi.read().decode("utf-8"))

    @staticmethod
    def _phan_tich_api(du_lieu: Any) -> dict[str, Tinh]:
        """
        Đổi JSON của API thành dict {mã tỉnh: Tinh}. Mỗi tỉnh trong API có dạng:
            {"name": "Thành phố Hà Nội", "code": 1, ..., "wards": [{"name": "Phường Ba Đình", "code": 4, ...}, ...]}
        Mã trong API là số nguyên, còn ma của thực thể là chuỗi nên đổi bằng str().
        Ném ValueError nếu cấu trúc khác dự kiến (ví dụ API đổi định dạng).
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
                ket_qua[ma] = Tinh(ma, tinh["name"], [Xa(str(xa["code"]), xa["name"]) for xa in cac_xa])
        except (KeyError, TypeError, ValueError) as loi:
            raise ValueError(f"API địa lý trả về dữ liệu không đúng định dạng: {loi!r}") from loi
        return ket_qua

    def tai_tu_api(self) -> dict[str, Tinh]:
        """
        Tải danh sách tỉnh/xã từ API (không lưu).
        Ném OSError nếu mất mạng, API trả lỗi, quá thời gian chờ, hoặc API trả dữ liệu sai định dạng.
        """
        try:
            du_lieu = self._goi_api()
            return self._phan_tich_api(du_lieu)
        except (OSError, ValueError) as loi:  # lỗi mạng/HTTP/timeout là OSError; JSON hỏng hoặc sai cấu trúc là ValueError
            raise OSError(f"Không tải được dữ liệu địa lý từ API: {loi}") from loi

    def _tai_va_luu(self) -> dict[str, Tinh]:
        """Tải từ API rồi ghi xuống file chính + sao lưu để lần sau không cần mạng."""
        danh_sach = self.tai_tu_api()
        try:
            self.ghi(danh_sach)
        except OSError:
            pass  # không lưu được (ví dụ ổ đĩa chỉ đọc) thì vẫn dùng dữ liệu vừa tải
        return danh_sach

    # ---- Ghi đè hành vi đọc ----
    # doc() dùng nguyên của lớp cha (chỉ đọc file cục bộ, ném FileNotFoundError/ValueError như giao thức)
    def doc_sao_luu(self) -> dict[str, Tinh]:
        """
        Đọc từ file sao lưu; nếu sao lưu cũng hỏng hoặc chưa có thì đọc trực tiếp từ API (và lưu lại,
        khôi phục luôn cả file chính). Ném OSError nếu API cũng không dùng được.
        """
        try:
            danh_sach = super().doc_sao_luu()
            if danh_sach:
                return danh_sach
        except (ValueError, FileNotFoundError):
            pass  # sao lưu hỏng hoặc chưa có -> chuyển sang API
        return self._tai_va_luu()
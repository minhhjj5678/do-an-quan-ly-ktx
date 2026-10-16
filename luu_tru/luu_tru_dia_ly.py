# Phần C
# Lưu trữ địa lý (tỉnh và các xã trực thuộc) phục vụ danh_sach_dia_ly.
#
# Nguồn dữ liệu: API công cộng https://provinces.open-api.vn/ (bản v2 = sau sáp nhập 07/2025,
# chỉ còn hai cấp Tỉnh -> Xã/Phường, khớp với dropdown tỉnh -> xã của màn hình sinh viên).
#
# Chiến lược (theo đúng thiết kế trong giao_thuc/luu_tru.py):
#   1. Ưu tiên đọc file cục bộ du_lieu/dia_ly.json (nhanh, chạy được khi mất mạng)
#   2. File chính hỏng  -> tầng trên gọi doc_sao_luu() để đọc file sao lưu
#   3. Sao lưu cũng hỏng/chưa có -> đọc trực tiếp từ API, và lưu lại xuống file cho lần sau
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
    def _phan_tich_api(du_lieu: Any) -> list[Tinh]:
        """
        Đổi JSON của API thành danh sách Tinh. Mỗi tỉnh trong API có dạng:
            {"name": "Thành phố Hà Nội", "code": 1, ..., "wards": [{"name": "Phường Ba Đình", "code": 4, ...}, ...]}
        Mã trong API là số nguyên, còn ma của thực thể là chuỗi nên đổi bằng str().
        Ném ValueError nếu cấu trúc khác dự kiến (ví dụ API đổi định dạng).
        """
        if not isinstance(du_lieu, list) or not du_lieu:
            raise ValueError("API địa lý trả về dữ liệu rỗng hoặc sai cấu trúc")
        ket_qua: list[Tinh] = []
        try:
            for tinh in du_lieu:
                cac_xa = tinh["wards"]
                if not isinstance(cac_xa, list):  # wards = null nghĩa là thiếu depth=2
                    raise ValueError("Thiếu danh sách xã (wards)")
                ket_qua.append(Tinh(str(tinh["code"]), tinh["name"],
                                    [Xa(str(xa["code"]), xa["name"]) for xa in cac_xa]))
        except (KeyError, TypeError, ValueError) as loi:
            raise ValueError(f"API địa lý trả về dữ liệu không đúng định dạng: {loi!r}") from loi
        return ket_qua

    def tai_tu_api(self) -> list[Tinh]:
        """Tải danh sách tỉnh/xã từ API (không lưu). Ném ValueError nếu mất mạng, quá thời gian hoặc dữ liệu sai."""
        try:
            du_lieu = self._goi_api()
        except (OSError, ValueError) as loi:  # lỗi mạng/HTTP/timeout là OSError, JSON hỏng là ValueError
            raise ValueError(f"Không tải được dữ liệu địa lý từ API: {loi}") from loi
        return self._phan_tich_api(du_lieu)

    def _tai_va_luu(self) -> list[Tinh]:
        """Tải từ API rồi ghi xuống file chính + sao lưu để lần sau không cần mạng."""
        danh_sach = self.tai_tu_api()
        self.ghi(danh_sach)
        return danh_sach

    # ---- Ghi đè hành vi đọc ----
    def doc(self) -> list[Tinh]:
        """
        Đọc địa lý từ file cục bộ.
        - File hỏng: ném ValueError như giao thức (tầng trên sẽ gọi doc_sao_luu()).
        - File chưa có (lần chạy đầu): tự tải từ API một lần rồi lưu lại. Nếu lúc đó mất mạng
          thì trả về danh sách rỗng, lần gọi sau sẽ thử lại.
        """
        danh_sach = super().doc()
        if danh_sach:
            return danh_sach
        try:
            return self._tai_va_luu()
        except ValueError:
            return []

    def doc_sao_luu(self) -> list[Tinh]:
        """
        Đọc từ file sao lưu; nếu sao lưu cũng hỏng hoặc chưa có thì đọc trực tiếp từ API
        (và lưu lại, khôi phục luôn cả file chính). Ném ValueError nếu API cũng không dùng được.
        """
        try:
            danh_sach = super().doc_sao_luu()
            if danh_sach:
                return danh_sach
        except ValueError:
            pass  # file sao lưu hỏng -> chuyển sang API
        return self._tai_va_luu()
import json
import urllib.request
from typing import List
from luu_tru.luu_tru_co_so import LuuTruCoSo
from thuc_the.dia_ly import Tinh, Xa

API_URL = "https://provinces.open-api.vn/api/?depth=2"

class LuuTruDiaLy(LuuTruCoSo[Tinh]):
    def __init__(self):
        super().__init__("dia_ly.json", Tinh)

    def doc_tu_api(self) -> List[Tinh]:
        try:
            req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                danh_sach_tinh = []
                for item in data:
                    # Lấy danh sách quận/huyện/xã
                    ds_xa = []
                    for w in item.get("districts", []):
                        ds_xa.append(Xa(ma=str(w.get("code")), ten=w.get("name")))
                    danh_sach_tinh.append(Tinh(ma=str(item.get("code")), ten=item.get("name"), danh_sach_xa=ds_xa))
                
                # Lưu vào local sao lưu
                self.ghi(danh_sach_tinh)
                return danh_sach_tinh
        except Exception as e:
            raise ValueError(f"Lỗi khi đọc dữ liệu tỉnh thành từ API: {e}")

    def doc(self) -> List[Tinh]:
        try:
            res = super().doc()
            return res if res else self.doc_tu_api()
        except Exception:
            return self.doc_tu_api()
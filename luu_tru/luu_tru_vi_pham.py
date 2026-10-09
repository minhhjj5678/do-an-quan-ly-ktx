import json
import os
from typing import List
from luu_tru.luu_tru_co_so import LuuTruCoSo
from thuc_the.vi_pham import ViPham, ViPhamNoiQuy, ViPhamTaiSan
from tien_ich.cau_hinh_tinh import FILE_VI_PHAM

class LuuTruViPham(LuuTruCoSo[ViPham]):
    def __init__(self):
        super().__init__(FILE_VI_PHAM, ViPham)

    def doc(self) -> List[ViPham]:
        if not os.path.exists(self.duong_dan_chinh):
            return []
        try:
            with open(self.duong_dan_chinh, "r", encoding="utf-8") as f:
                data = json.load(f)
            danh_sach = []
            for item in data:
                # Phân loại để khởi tạo đúng class con
                if item.get("loai_vi_pham") == "noi_quy" or "hinh_thuc_ky_luat" in item:
                    danh_sach.append(ViPhamNoiQuy.from_dict(item) if hasattr(ViPhamNoiQuy, "from_dict") else item)
                else:
                    danh_sach.append(ViPhamTaiSan.from_dict(item) if hasattr(ViPhamTaiSan, "from_dict") else item)
            return danh_sach
        except Exception:
            return self.doc_sao_luu()
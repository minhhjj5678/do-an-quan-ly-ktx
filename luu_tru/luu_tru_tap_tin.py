import json
import os
from datetime import date, datetime
from enum import Enum
from typing import TypeVar, Generic, List, Type, Any
from giao_thuc.luu_tru import GiaoThucLuuTru
from thuc_the.thuc_the_goc import ThucTheGoc
from tien_ich.tap_tin import lay_duong_dan_du_lieu, lay_duong_dan_sao_luu

T = TypeVar("T", bound=ThucTheGoc)

class CustomEncoder(json.JSONEncoder):
    """Xử lý ép kiểu dữ liệu date và Enum sang dạng có thể ghi vào JSON"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return super().default(obj)

class LuuTruCoSo(GiaoThucLuuTru[T], Generic[T]):
    def __init__(self, ten_file: str, cls_thuc_the: Type[T]):
        self.ten_file = ten_file
        self.cls_thuc_the = cls_thuc_the
        self.duong_dan_chinh = lay_duong_dan_du_lieu(ten_file)
        self.duong_dan_sao_luu = lay_duong_dan_sao_luu(ten_file)
        self.duong_dan_checksum = lay_duong_dan_sao_luu(f"{ten_file}.checksum")

    @property
    def loai_thuc_the(self) -> Type[T]:
        return self.cls_thuc_the

    def _cap_nhat_checksum(self) -> None:
        if os.path.exists(self.duong_dan_chinh):
            mtime = str(os.path.getmtime(self.duong_dan_chinh))
            with open(self.duong_dan_checksum, "w", encoding="utf-8") as f:
                f.write(mtime)

    def co_bi_chinh_sua(self) -> bool:
        if not os.path.exists(self.duong_dan_chinh) or not os.path.exists(self.duong_dan_checksum):
            return False
        with open(self.duong_dan_checksum, "r", encoding="utf-8") as f:
            checksum_da_luu = f.read().strip()
        return checksum_da_luu != str(os.path.getmtime(self.duong_dan_chinh))

    def _object_to_dict(self, obj: Any) -> dict:
        """Tự động chuyển các thuộc tính private __attribute thành dictionary"""
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        res = {}
        for k, v in obj.__dict__.items():
            # Xóa tiền tố name mang tên Class private (__)
            key = k.split("__")[-1] if "__" in k else k.lstrip("_")
            if isinstance(v, (date, datetime)):
                res[key] = v.isoformat()
            elif isinstance(v, Enum):
                res[key] = v.value
            elif isinstance(v, list):
                res[key] = [i.value if isinstance(i, Enum) else (i.isoformat() if isinstance(i, (date, datetime)) else i) for i in v]
            else:
                res[key] = v
        return res

    def doc(self) -> List[T]:
        if not os.path.exists(self.duong_dan_chinh):
            return []
        try:
            with open(self.duong_dan_chinh, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [self.cls_thuc_the.from_dict(item) if hasattr(self.cls_thuc_the, "from_dict") else item for item in data]
        except Exception:
            return self.doc_sao_luu()

    def doc_sao_luu(self) -> List[T]:
        if not os.path.exists(self.duong_dan_sao_luu):
            return []
        with open(self.duong_dan_sao_luu, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [self.cls_thuc_the.from_dict(item) if hasattr(self.cls_thuc_the, "from_dict") else item for item in data]

    def ghi(self, danh_sach: List[T], ghi_de: bool = True) -> None:
        du_lieu_luu = danh_sach if ghi_de else self.doc() + danh_sach
        raw_data = [self._object_to_dict(item) for item in du_lieu_luu]

        with open(self.duong_dan_chinh, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4, cls=CustomEncoder)

        with open(self.duong_dan_sao_luu, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4, cls=CustomEncoder)

        self._cap_nhat_checksum()
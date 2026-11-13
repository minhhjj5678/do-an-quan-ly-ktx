
import re
from datetime import datetime
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, cast



def thanh_dict(obj):
    if isinstance(obj, dict):
        return dict(obj)

    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(cast(Any, obj))

    model_dump = getattr(obj, "model_dump", None)
    if callable(model_dump):
        return model_dump()

    if hasattr(obj, "__dict__"):
        return {
            k: v
            for k, v in vars(obj).items()
            if not k.startswith("_")
        }

    raise TypeError(
        "Không chuyển được đối tượng thành dictionary"
    )


def thanh_danh_sach(data):
    if data is None:
        return []

    if isinstance(data, dict):
        return [
            thanh_dict(v)
            for v in data.values()
        ]

    return [thanh_dict(v) for v in data]


def hien_thi(gia_tri):
    if gia_tri is None:
        return ""

    if isinstance(gia_tri, Enum):
        return str(gia_tri.value)

    return str(gia_tri)


def kiem_tra(truong, gia_tri, bat_buoc=True):
    gia_tri = str(gia_tri).strip()

    if bat_buoc and not gia_tri:
        return f"{truong} không được để trống"

    if not gia_tri:
        return None

    if truong == "email":
        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            gia_tri
        ):
            return "Email không hợp lệ"

    if truong in ("so_dien_thoai", "sdt"):
        if not re.fullmatch(r"0\d{9}", gia_tri):
            return (
                "Số điện thoại phải gồm 10 chữ số, "
                "bắt đầu bằng 0"
            )

    if truong.startswith("ngay_"):
        try:
            datetime.strptime(gia_tri, "%d/%m/%Y")
        except ValueError:
            return f"{truong} phải có dạng dd/mm/yyyy"

    if truong in (
        "suc_chua", "thang", "nam",
        "suc_chua_mac_dinh"
    ):
        try:
            if int(gia_tri) <= 0:
                return f"{truong} phải lớn hơn 0"
        except ValueError:
            return f"{truong} phải là số nguyên"

    if truong in (
        "don_gia", "so_tien", "muc_phat",
        "don_gia_dien", "don_gia_nuoc",
        "han_muc_no"
    ):
        try:
            if float(gia_tri) < 0:
                return f"{truong} không được âm"
        except ValueError:
            return f"{truong} phải là số"

    return None


def chuyen_kieu(truong, gia_tri):
    gia_tri = gia_tri.strip()

    if truong in (
        "suc_chua", "thang", "nam",
        "suc_chua_mac_dinh"
    ):
        return int(gia_tri)

    if truong in (
        "don_gia", "so_tien", "muc_phat",
        "don_gia_dien", "don_gia_nuoc",
        "han_muc_no"
    ):
        return float(gia_tri)

    return gia_tri

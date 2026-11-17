"""Tiện ích hiển thị và kiểm tra cơ bản, không thay quy tắc nghiệp vụ của nhóm."""
import re
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, cast


def thanh_dict(obj):
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(cast(Any, obj))
    model_dump = getattr(obj, 'model_dump', None)
    if callable(model_dump):
        return model_dump()
    if hasattr(obj, '__dict__'):
        return {k: v for k, v in vars(obj).items() if not k.startswith('_')}
    raise TypeError('Đối tượng không hỗ trợ chuyển dictionary')


def thanh_danh_sach(data):
    if data is None:
        return []
    if isinstance(data, dict):
        data = data.values()
    return list(data)


def hien_thi(value):
    if value is None:
        return ''
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, (date, datetime)):
        return value.strftime('%d/%m/%Y') if isinstance(value, date) else str(value)
    return str(value)


def kiem_tra(truong, gia_tri, bat_buoc=True):
    value = str(gia_tri).strip()
    if bat_buoc and not value:
        return f'{truong.replace("_", " ").title()} không được để trống.'
    if not value:
        return None
    if truong in ('email',) and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', value):
        return 'Email không hợp lệ.'
    if truong in ('sdt', 'so_dien_thoai') and not re.fullmatch(r'0\d{9}', value):
        return 'Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0.'
    if truong in ('nam_sinh', 'so_tang', 'tang', 'suc_chua', 'suc_chua_mac_dinh'):
        try:
            so = int(value)
        except ValueError:
            return f'{truong} phải là số nguyên.'
        if so <= 0 and truong != 'nam_sinh':
            return f'{truong} phải lớn hơn 0.'
    if truong in ('don_gia_dien', 'don_gia_nuoc', 'gia_phong', 'don_gia',
                  'muc_phat', 'so_tien', 'han_muc_no'):
        try:
            if float(value) < 0:
                return f'{truong} không được âm.'
        except ValueError:
            return f'{truong} phải là số.'
    return None


def chuyen_kieu(truong, gia_tri):
    # Giữ tương thích với các màn hình khác nếu còn dùng hàm này.
    value = str(gia_tri).strip()
    if truong in ('suc_chua', 'thang', 'nam', 'nam_sinh', 'tang',
                  'so_tang', 'suc_chua_mac_dinh'):
        return int(value)
    if truong in ('don_gia', 'so_tien', 'muc_phat', 'don_gia_dien',
                  'don_gia_nuoc', 'gia_phong', 'han_muc_no'):
        return float(value)
    return value

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


def gan_goi_y_combobox(o_chon, danh_sach: dict[str, str]):
    """Gợi ý tên trong Combobox khi gõ; khi lưu, màn hình đổi nhãn thành mã.

    danh_sach: {"Tên hiển thị (Mã)": "Mã"}. Không tự cho phép nhập mã tự do.
    """
    import unicodedata
    from difflib import SequenceMatcher

    def chuan_hoa(chuoi: str) -> str:
        chuoi = unicodedata.normalize('NFD', chuoi.casefold())
        return ''.join(k for k in chuoi if unicodedata.category(k) != 'Mn').replace('đ', 'd')

    def loc_goi_y():
        tu = chuan_hoa(o_chon.get().strip())
        if not tu or o_chon.get() in danh_sach:
            ket_qua = list(danh_sach)
        else:
            khop = [ten for ten in danh_sach if tu in chuan_hoa(ten)]
            gan = [ten for ten in danh_sach if ten not in khop and
                   any(SequenceMatcher(None, tu, tu_don).ratio() >= 0.65
                       for tu_don in chuan_hoa(ten).replace('(', ' ').replace(')', ' ').split())]
            ket_qua = khop + gan
        o_chon.configure(values=ket_qua)
        return ket_qua

    def khi_go(_event):
        if _event.keysym in ('Up', 'Down', 'Return', 'Escape', 'Tab', 'Left', 'Right'):
            return
        ket_qua = loc_goi_y()
        if ket_qua and o_chon.winfo_exists() and o_chon.focus_get() == o_chon:
            def mo_goi_y():
                try:
                    if o_chon.winfo_exists() and o_chon.focus_get() == o_chon:
                        o_chon.tk.call('ttk::combobox::Post', str(o_chon))
                except Exception:
                    pass
            o_chon.after_idle(mo_goi_y)

    o_chon.configure(values=list(danh_sach), postcommand=loc_goi_y)
    o_chon.bind('<KeyRelease>', khi_go, add='+')
    return danh_sach

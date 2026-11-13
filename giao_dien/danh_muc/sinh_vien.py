from tkinter import ttk

from thuc_the.ky_tuc_xa import SinhVien
from .danh_muc_co_so import ManHinhDanhMucCoSo
from ..dung_chung.ho_tro import hien_thi


class ManHinhSinhVien(ManHinhDanhMucCoSo):
    LOAI = SinhVien
    TIEU_DE = "Quản lý sinh viên"
    MO_TA = "Thông tin sinh viên, số điện thoại và địa chỉ liên hệ."
    CO_LUU_TRU = True
    TRUONG = ['ma', 'ten', 'sdt', 'nam_sinh', 'cccd',
              'dia_chi_chi_tiet', 'tinh', 'xa']
    BAT_BUOC = ['ten', 'sdt', 'nam_sinh', 'cccd',
                'dia_chi_chi_tiet', 'tinh', 'xa']

    def tao_o_nhap(self, parent, truong, gia_tri):
        if truong in ('tinh', 'xa'):
            return ttk.Combobox(parent, state='readonly', width=40)
        return super().tao_o_nhap(parent, truong, gia_tri)

    def cau_hinh_form(self, form, o_nhap, du_lieu):
        cbo_tinh = o_nhap['tinh']
        cbo_xa = o_nhap['xa']
        # Không có class Combobox tự tạo: chỉ lưu ánh xạ trên widget có sẵn.
        ma_tinh_theo_nhan = {}
        ma_xa_theo_nhan = {}
        setattr(cbo_tinh, 'ma_theo_nhan', ma_tinh_theo_nhan)
        setattr(cbo_xa, 'ma_theo_nhan', ma_xa_theo_nhan)

        try:
            ds_tinh = self.adapter.dia_ly()
            # Adapter mới: dict[str, Tinh], Tinh.danh_sach_xa: dict[str, Xa]
            tinh_theo_ma = {str(t.ma): t for t in ds_tinh.values()}
            for ma, tinh in tinh_theo_ma.items():
                ma_tinh_theo_nhan[f'{tinh.ten} ({ma})'] = ma
            cbo_tinh['values'] = list(ma_tinh_theo_nhan)
            ma_cu = hien_thi(du_lieu.get('tinh'))
            for nhan, ma in ma_tinh_theo_nhan.items():
                if ma == ma_cu:
                    cbo_tinh.set(nhan)
                    break
        except Exception as exc:
            ttk.Label(form, text=f'Chưa tải được dữ liệu địa lý: {exc}',
                      foreground='#BD3B31', wraplength=450).pack(anchor='w', pady=8)
            return

        def nap_xa(event=None):
            cbo_xa.set('')
            cbo_xa['values'] = []
            ma_xa_theo_nhan.clear()
            ma_tinh = ma_tinh_theo_nhan.get(cbo_tinh.get())
            if not ma_tinh:
                return
            tinh = tinh_theo_ma[ma_tinh]
            for xa in tinh.danh_sach_xa.values():
                ma = str(xa.ma)
                ma_xa_theo_nhan[f'{xa.ten} ({ma})'] = ma
            cbo_xa['values'] = list(ma_xa_theo_nhan)
            if event is None:
                ma_cu = hien_thi(du_lieu.get('xa'))
                for nhan, ma in ma_xa_theo_nhan.items():
                    if ma == ma_cu:
                        cbo_xa.set(nhan)
                        break

        cbo_tinh.bind('<<ComboboxSelected>>', nap_xa)
        if cbo_tinh.get():
            nap_xa()

    def chuan_hoa_du_lieu_form(self, data, o_nhap):
        data = dict(data)
        for truong in ('tinh', 'xa'):
            widget = o_nhap[truong]
            bang_ma = getattr(widget, 'ma_theo_nhan', {})
            ma = bang_ma.get(data.get(truong, ''))
            if not ma:
                raise ValueError(f'Chưa chọn {"Tỉnh/Thành phố" if truong == "tinh" else "Phường/Xã"} hợp lệ.')
            data[truong] = ma
        return data

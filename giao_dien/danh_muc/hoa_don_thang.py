"""Danh mục hóa đơn tháng: dùng ThangNam, mã HDT tự sinh ở backend."""
import calendar
import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk, messagebox

from thuc_the.ky_tuc_xa import Phong
from thuc_the.tai_chinh import HoaDonThang, ThangNam
from ..dung_chung.ho_tro import gan_goi_y_combobox
from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhHoaDonThang(ManHinhDanhMucCoSo):
    NGHIEP_VU_CHI_TIET = (('Thanh toán hóa đơn', 'thanh_toan_hoa_don_thang'),)
    LOAI = HoaDonThang
    TIEU_DE = 'Quản lý hóa đơn tháng'
    MO_TA = 'Tháng năm YYYY-MM; chọn Chi tiết hóa đơn để thanh toán.'
    TRUONG = [
        'ma', 'thang_nam', 'dien_cu', 'dien_moi', 'don_gia_dien',
        'nuoc_cu', 'nuoc_moi', 'don_gia_nuoc', 'phong', 'han_chot', 'trang_thai',
    ]
    BAT_BUOC = [
        'thang_nam', 'dien_cu', 'dien_moi', 'don_gia_dien',
        'nuoc_cu', 'nuoc_moi', 'don_gia_nuoc', 'phong', 'han_chot',
    ]
    TRUONG_CHI_DOC_KHI_TAO = {'trang_thai'}
    CHO_PHEP_SUA = False  # DieuPhoiKTX cấm cập nhật hóa đơn sau khi tạo

    def thu_tu_truong_form(self):
        return ['phong'] + [t for t in self.TRUONG if t != 'phong']

    def tao_o_nhap(self, parent, truong, gia_tri):
        if truong != 'phong':
            return super().tao_o_nhap(parent, truong, gia_tri)
        ds = self.adapter.lay_tat_ca(Phong)
        self._nhan_phong = {
            f'{phong.ten} ({ma})': str(ma) for ma, phong in
            sorted(ds.items(), key=lambda item: str(item[1].ten).casefold())
        }
        o = ttk.Combobox(parent, state='normal', width=40)
        gan_goi_y_combobox(o, self._nhan_phong)
        if gia_tri:
            o.set(next((nhan for nhan, ma in self._nhan_phong.items()
                        if ma == str(gia_tri)), ''))
        return o

    @staticmethod
    def _khoa_thang(thang_nam):
        """Lấy (năm, tháng) để so hóa đơn, không dựa vào thứ tự chuỗi mã."""
        nam = getattr(thang_nam, 'nam', None)
        thang = getattr(thang_nam, 'thang', None)
        if isinstance(nam, int) and isinstance(thang, int) and 1 <= thang <= 12:
            return nam, thang
        chuoi = str(thang_nam)
        try:
            nam, thang = map(int, chuoi.split('-'))
            if 1 <= thang <= 12:
                return nam, thang
        except (ValueError, TypeError):
            pass
        return None

    def cau_hinh_form(self, form, o_nhap, du_lieu):
        super().cau_hinh_form(form, o_nhap, du_lieu)
        if du_lieu:  # Chỉ tự điền khi tạo, không ghi đè lúc sửa.
            return

        def dien(ten, gia_tri):
            if gia_tri is None or ten not in o_nhap:
                return
            o = o_nhap[ten]
            o.delete(0, tk.END)
            o.insert(0, str(gia_tri))

        hom_nay = date.today()
        dien('thang_nam', f'{hom_nay.year:04d}-{hom_nay.month:02d}')
        try:
            cfg = self.adapter.doc_cau_hinh()
            def gia_tri_cfg(ten: str) -> int | float:
                if isinstance(cfg, dict):
                    gia_tri = cfg.get(ten, cfg.get(ten.lower()))
                else:
                    gia_tri = getattr(cfg, ten, None)
                if isinstance(gia_tri, bool) or not isinstance(gia_tri, (int, float)):
                    raise ValueError(f'Thông số cấu hình {ten} phải là số.')
                return gia_tri
            dien('don_gia_dien', gia_tri_cfg('DON_GIA_DIEN'))
            dien('don_gia_nuoc', gia_tri_cfg('DON_GIA_NUOC'))
            so_ngay = int(gia_tri_cfg('THOI_HAN_DONG_TIEN_DIEN'))
            ngay_cuoi = date(hom_nay.year, hom_nay.month,
                             calendar.monthrange(hom_nay.year, hom_nay.month)[1])
            dien('han_chot', (ngay_cuoi + timedelta(days=so_ngay)).strftime('%d/%m/%Y'))
        except Exception as exc:
            messagebox.showwarning('Không thể đọc cấu hình', str(exc), parent=form.winfo_toplevel())

        o_phong = o_nhap['phong']
        def dien_chi_so_cu(_event=None):
            ma = self._nhan_phong.get(o_phong.get().strip())
            # Không để chỉ số của phòng vừa chọn trước đó dính sang phòng mới.
            dien('dien_cu', '')
            dien('nuoc_cu', '')
            if ma is None:
                return
            try:
                ds = self.adapter.lay_tat_ca(HoaDonThang, lay_luu_tru=True)
                hoa_don = [hd for hd in ds.values()
                           if str(getattr(hd, 'phong', '')) == ma
                           and self._khoa_thang(getattr(hd, 'thang_nam', None)) is not None]
                if not hoa_don:
                    return
                gan_nhat = max(hoa_don, key=lambda hd: self._khoa_thang(hd.thang_nam) or (0, 0))
                dien('dien_cu', gan_nhat.dien_moi)
                dien('nuoc_cu', gan_nhat.nuoc_moi)
            except Exception as exc:
                messagebox.showwarning('Không thể đọc hóa đơn gần nhất', str(exc),
                                       parent=form.winfo_toplevel())

        o_phong.bind('<<ComboboxSelected>>', dien_chi_so_cu, add='+')
        o_phong.bind('<FocusOut>', dien_chi_so_cu, add='+')

    def chuan_hoa_du_lieu_form(self, data, o_nhap):
        data = super().chuan_hoa_du_lieu_form(data, o_nhap)
        ma = self._nhan_phong.get(data.get('phong', ''))
        if not ma:
            raise ValueError('Hãy chọn Phòng từ danh sách theo tên.')
        data['phong'] = ma
        return data

    def _chuyen_kieu(self, truong, value):
        if truong == 'thang_nam':
            try:
                return ThangNam.tu_chuoi(value)
            except (TypeError, ValueError) as exc:
                raise ValueError('Tháng năm phải có dạng YYYY-MM (ví dụ 2026-11).') from exc
        return super()._chuyen_kieu(truong, value)

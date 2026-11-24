"""Danh mục hợp đồng: mã tự sinh bởi DieuPhoiKTX."""
import tkinter as tk
from tkinter import ttk

from thuc_the.ky_tuc_xa import Phong, SinhVien
from thuc_the.tai_chinh import HopDong
from ..dung_chung.ho_tro import gan_goi_y_combobox
from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhHopDong(ManHinhDanhMucCoSo):
    NGHIEP_VU_CHI_TIET = (('Thanh toán hợp đồng', 'thanh_toan_hop_dong'),
                           ('Kết thúc hợp đồng', 'ket_thuc_hop_dong'))
    LOAI = HopDong
    TIEU_DE = 'Quản lý hợp đồng'
    MO_TA = 'Thêm và theo dõi hợp đồng. Chọn hợp đồng và mở Chi tiết để thanh toán hoặc kết thúc.'
    TRUONG = [
        'ma', 'ngay_ky', 'ngay_het_han', 'ngay_bat_dau', 'ngay_ket_thuc',
        'he_so_thang', 'gia_phong', 'tien_dat_coc', 'ma_sinh_vien',
        'ma_phong', 'trang_thai',
    ]
    BAT_BUOC = [
        'ngay_ky', 'ngay_het_han', 'ngay_bat_dau', 'ngay_ket_thuc',
        'he_so_thang', 'gia_phong', 'tien_dat_coc', 'ma_sinh_vien', 'ma_phong',
    ]
    TRUONG_CHI_DOC_KHI_TAO = {'trang_thai'}
    CHO_PHEP_SUA = False  # DieuPhoiKTX cấm cập nhật hợp đồng sau khi tạo

    @staticmethod
    def ten_truong(truong):
        if truong == 'ma_sinh_vien':
            return 'Sinh viên (họ tên - MSSV)'
        if truong == 'ma_phong':
            return 'Phòng (tên - mã)'
        return ManHinhDanhMucCoSo.ten_truong(truong)

    def thu_tu_truong_form(self):
        # Chọn phòng đầu tiên để giá phòng tự điền ngay.
        return ['ma_phong'] + [t for t in self.TRUONG if t != 'ma_phong']

    def tao_o_nhap(self, parent, truong, gia_tri):
        if truong == 'ma_sinh_vien':
            ds_sv = self.app.dieu_phoi.lay_tat_ca(SinhVien)
            self._nhan_sinh_vien = {
                f'{sv.ten} ({ma})': str(ma)
                for ma, sv in sorted(
                    ds_sv.items(), key=lambda item: str(item[1].ten).casefold()
                )
            }
            o = ttk.Combobox(parent, state='normal', width=40)
            gan_goi_y_combobox(o, self._nhan_sinh_vien)
            if gia_tri:
                o.set(next((nhan for nhan, ma in self._nhan_sinh_vien.items()
                            if ma == str(gia_tri)), ''))
            return o

        if truong != 'ma_phong':
            return super().tao_o_nhap(parent, truong, gia_tri)
        ds = self.app.dieu_phoi.lay_tat_ca(Phong)
        self._phong_theo_ma = {str(ma): phong for ma, phong in ds.items()}
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

    def cau_hinh_form(self, form, o_nhap, du_lieu):
        super().cau_hinh_form(form, o_nhap, du_lieu)
        o_gia = o_nhap.get('gia_phong')
        o_phong = o_nhap.get('ma_phong')
        if o_gia is None or o_phong is None:
            return

        def cap_nhat_gia(_event=None):
            ma = self._nhan_phong.get(o_phong.get().strip())
            phong = self._phong_theo_ma.get(ma) if ma else None
            o_gia.configure(state='normal')
            o_gia.delete(0, tk.END)
            if phong is not None:
                o_gia.insert(0, str(phong.gia_phong))
            self._khoa_o(o_gia)

        # Chỉ giá phòng bị khóa; dữ liệu sẽ lấy lại từ phòng lúc lưu.
        o_phong.bind('<<ComboboxSelected>>', cap_nhat_gia, add='+')
        o_phong.bind('<FocusOut>', cap_nhat_gia, add='+')
        cap_nhat_gia()

    def chuan_hoa_du_lieu_form(self, data, o_nhap):
        data = super().chuan_hoa_du_lieu_form(data, o_nhap)
        ma_sinh_vien = self._nhan_sinh_vien.get(data.get('ma_sinh_vien', ''))
        if ma_sinh_vien is None:
            raise ValueError('Hãy chọn Sinh viên từ danh sách theo họ tên hoặc MSSV.')
        data['ma_sinh_vien'] = ma_sinh_vien

        ma = self._nhan_phong.get(data.get('ma_phong', ''))
        phong = self._phong_theo_ma.get(ma) if ma else None
        if phong is None:
            raise ValueError('Hãy chọn Phòng từ danh sách theo tên.')
        data['ma_phong'] = ma
        # Giá thuê luôn theo bản ghi Phòng, không tin giá trị gửi từ ô nhập.
        data['gia_phong'] = str(phong.gia_phong)
        return data

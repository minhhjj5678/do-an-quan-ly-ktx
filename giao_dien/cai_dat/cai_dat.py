"""Cài đặt theo CauHinhDong(frozen=True) thực tế của nhóm."""
from tkinter import ttk, messagebox
from math import isfinite

from tien_ich.cau_hinh_dong import CauHinhDong
from tien_ich.cau_hinh_tinh import CauHinhChuDe


class ManHinhCaiDat(ttk.Frame):
    # (nhãn, thuộc tính CauHinhDong, kiểu dữ liệu, đơn vị)
    THONG_SO = [
        ('Đơn giá điện', 'DON_GIA_DIEN', float, 'đ/kWh'),
        ('Đơn giá nước', 'DON_GIA_NUOC', float, 'đ/m³'),
        ('Sức chứa phòng mặc định', 'SUC_CHUA_PHONG_MAC_DINH', int, 'người'),
        ('Hạn mức nợ tối đa', 'SO_TIEN_NO_TOI_DA_CHO_PHEP', float, 'đồng'),
        ('Hạn đóng tiền điện', 'THOI_HAN_DONG_TIEN_DIEN', int, 'ngày'),
        ('Tiền phạt quá hạn mỗi ngày', 'TIEN_PHAT_QUA_HAN_NGAY', float, 'đ/ngày'),
    ]
    CHU_DE_GIAO_DIEN = ('LIGHT', 'GREY', 'DARK', 'BLUE')

    def __init__(self, parent, adapter, doi_chu_de_callback):
        super().__init__(parent, padding=16)
        self.adapter = adapter
        self.doi_chu_de_callback = doi_chu_de_callback
        self.o_nhap_ts = {}
        self.chi_xem = not self.adapter.la_admin()
        self.tao_giao_dien()
        self.tai_cau_hinh()

    def tao_giao_dien(self):
        dau = ttk.Frame(self, style='KTX.Banner.TFrame', padding=18)
        dau.pack(fill='x', pady=(0, 14))
        ttk.Label(dau, text='CÀI ĐẶT HỆ THỐNG',
                  style='KTX.BannerTitle.TLabel').pack(anchor='w')
        ttk.Label(dau, text='Tùy chỉnh chủ đề và thông số quản lý ký túc xá',
                  style='KTX.BannerSub.TLabel').pack(anchor='w', pady=(5, 0))

        giao_dien = ttk.LabelFrame(self, text='  Giao diện  ', padding=14)
        giao_dien.pack(fill='x', pady=(0, 12))
        ttk.Label(giao_dien, text='Chủ đề màu sắc').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.cbo_chu_de = ttk.Combobox(
            giao_dien, values=self.CHU_DE_GIAO_DIEN, state='readonly', width=18)
        self.cbo_chu_de.grid(row=0, column=1, sticky='w', padx=6)
        ttk.Button(giao_dien, text='Áp dụng màu ngay',
                   command=self.ap_dung_chu_de).grid(row=0, column=2, sticky='w', padx=8)

        # Các thông số chỉ xem của Sinh viên có nền xám rõ ràng.
        style = ttk.Style(self)
        style.configure('KTX.Khoa.TEntry', fieldbackground='#E3E8EF', foreground='#586579')
        style.map('KTX.Khoa.TEntry',
                  fieldbackground=[('readonly', '#E3E8EF'), ('disabled', '#E3E8EF')],
                  foreground=[('readonly', '#586579'), ('disabled', '#586579')])

        tham_so = ttk.LabelFrame(self, text='  Thông số hệ thống  ', padding=14)
        tham_so.pack(fill='x', pady=(0, 12))
        tham_so.columnconfigure(0, weight=1)
        tham_so.columnconfigure(1, weight=1)
        for i, (nhan, ten, _kieu, don_vi) in enumerate(self.THONG_SO):
            khung = ttk.Frame(tham_so)
            khung.grid(row=i // 2, column=i % 2, sticky='ew', padx=8, pady=7)
            khung.columnconfigure(0, weight=1)
            ttk.Label(khung, text=f'{nhan} ({don_vi})').grid(row=0, column=0, sticky='w')
            entry = ttk.Entry(khung, state='readonly' if self.chi_xem else 'normal',
                              style='KTX.Khoa.TEntry' if self.chi_xem else 'TEntry')
            entry.grid(row=1, column=0, sticky='ew', pady=(5, 0))
            self.o_nhap_ts[ten] = entry

        nut = ttk.Frame(self)
        nut.pack(fill='x', pady=(4, 0))
        ttk.Button(nut, text='Lấy lại dữ liệu', command=self.tai_cau_hinh).pack(side='left')
        if self.chi_xem:
            ttk.Label(nut, text='Thông số hệ thống: chỉ xem, không được chỉnh sửa.').pack(side='right')
        else:
            ttk.Button(nut, text='Lưu cấu hình', style='KTX.Primary.TButton',
                       command=self.luu_cau_hinh).pack(side='right')

    @staticmethod
    def _doc_truong_cau_hinh(cfg: object, truong: str) -> object:
        """Backend thật dùng thuộc tính IN HOA; mock cũ dùng dict chữ thường."""
        ten_cu: dict[str, str] = {
            'SUC_CHUA_PHONG_MAC_DINH': 'suc_chua_mac_dinh',
            'SO_TIEN_NO_TOI_DA_CHO_PHEP': 'han_muc_no',
            'THOI_HAN_DONG_TIEN_DIEN': 'thoi_han_dien',
            'TIEN_PHAT_QUA_HAN_NGAY': 'tien_phat_ngay',
        }
        cac_ten: tuple[str, str, str] = (
            truong, ten_cu.get(truong, truong.lower()), truong.lower()
        )
        if isinstance(cfg, dict):
            for ten in cac_ten:
                if ten in cfg:
                    return cfg[ten]
        else:
            for ten in cac_ten:
                if hasattr(cfg, ten):
                    return getattr(cfg, ten)
        # Mock không có đầy đủ thông số; dùng giá trị mặc định đã khai báo
        # trong CauHinhDong thật, không tự tạo số ngẫu nhiên.
        return getattr(CauHinhDong(), truong)

    def tai_cau_hinh(self):
        try:
            cfg = self.adapter.doc_cau_hinh()
            chu_de = self._doc_truong_cau_hinh(cfg, 'CHU_DE')
            ten = str(getattr(chu_de, 'name', chu_de)).split('.')[-1].upper()
            if ten == 'DEFAULT':
                ten = 'LIGHT'
            if self.chi_xem:
                # Sinh viên chỉ đổi màu của phiên đang mở, không sửa cấu hình chung.
                ten = getattr(self.winfo_toplevel(), 'chu_de_hien_tai', ten)
            self.cbo_chu_de.set(ten if ten in self.CHU_DE_GIAO_DIEN else 'LIGHT')
            for _nhan, truong, _kieu, _don_vi in self.THONG_SO:
                entry = self.o_nhap_ts[truong]
                if self.chi_xem:
                    entry.configure(state='normal')
                entry.delete(0, 'end')
                entry.insert(0, str(self._doc_truong_cau_hinh(cfg, truong)))
                if self.chi_xem:
                    entry.configure(state='readonly')
        except Exception as exc:
            messagebox.showerror('Lỗi tải cấu hình', str(exc), parent=self.winfo_toplevel())

    def ap_dung_chu_de(self):
        chu_de = self.cbo_chu_de.get().strip()
        if chu_de not in self.CHU_DE_GIAO_DIEN:
            messagebox.showwarning('Chủ đề', 'Vui lòng chọn chủ đề màu.', parent=self.winfo_toplevel())
            return
        self.doi_chu_de_callback(chu_de)

    def luu_cau_hinh(self):
        if self.chi_xem:
            raise PermissionError('Sinh viên không được thay đổi thông số hệ thống.')
        chon = self.cbo_chu_de.get().strip()
        if chon not in self.CHU_DE_GIAO_DIEN:
            messagebox.showwarning('Chủ đề', 'Vui lòng chọn chủ đề màu.', parent=self.winfo_toplevel())
            return

        cac_chu_de_backend = {loai.name: loai for loai in CauHinhChuDe}
        if chon == 'LIGHT' and 'LIGHT' not in cac_chu_de_backend:
            chu_de = CauHinhChuDe.DEFAULT
        elif chon in cac_chu_de_backend:
            chu_de = cac_chu_de_backend[chon]
        else:
            messagebox.showwarning(
                'Không thể lưu chủ đề',
                f'Backend chưa khai báo CauHinhChuDe.{chon}. '
                'Có thể áp dụng màu ngay, nhưng chưa thể lưu màu này xuống cấu hình.',
                parent=self.winfo_toplevel())
            return

        # Chỉ lưu thông số dạng số; chủ đề enum đã nằm trong biến chu_de.
        du_lieu: dict[str, float | int] = {}
        for nhan, ten, kieu, _don_vi in self.THONG_SO:
            chuoi = self.o_nhap_ts[ten].get().strip()
            if not chuoi:
                messagebox.showwarning('Thiếu thông số', f'Chưa nhập: {nhan}', parent=self.winfo_toplevel())
                return
            try:
                value = kieu(chuoi)
            except ValueError:
                messagebox.showwarning('Thông số không hợp lệ', f'{nhan} phải là số.', parent=self.winfo_toplevel())
                return
            if not isfinite(float(value)) or ((ten in ('SUC_CHUA_PHONG_MAC_DINH', 'THOI_HAN_DONG_TIEN_DIEN') and value <= 0) or value < 0):
                messagebox.showwarning('Thông số không hợp lệ', f'{nhan} không hợp lệ.', parent=self.winfo_toplevel())
                return
            du_lieu[ten] = value

        if not messagebox.askyesno('Xác nhận', 'Lưu cấu hình hệ thống?', parent=self.winfo_toplevel()):
            return
        try:
            # CauHinhDong là frozen dataclass: phải tạo một đối tượng mới.
            cfg_moi = CauHinhDong(
                CHU_DE=chu_de,
                DON_GIA_DIEN=du_lieu['DON_GIA_DIEN'],
                DON_GIA_NUOC=du_lieu['DON_GIA_NUOC'],
                SUC_CHUA_PHONG_MAC_DINH=int(du_lieu['SUC_CHUA_PHONG_MAC_DINH']),
                SO_TIEN_NO_TOI_DA_CHO_PHEP=du_lieu['SO_TIEN_NO_TOI_DA_CHO_PHEP'],
                THOI_HAN_DONG_TIEN_DIEN=int(du_lieu['THOI_HAN_DONG_TIEN_DIEN']),
                TIEN_PHAT_QUA_HAN_NGAY=du_lieu['TIEN_PHAT_QUA_HAN_NGAY'],
            )
            self.adapter.cap_nhat_cau_hinh(cfg_moi)
            self.doi_chu_de_callback(chon)
            messagebox.showinfo('Đã lưu', 'Cấu hình hệ thống đã được lưu.', parent=self.winfo_toplevel())
        except Exception as exc:
            messagebox.showerror('Không thể lưu', str(exc), parent=self.winfo_toplevel())

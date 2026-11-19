import tkinter as tk
from tkinter import ttk, messagebox

from thuc_the.ky_tuc_xa import Phong, ToaNha
from .danh_muc_co_so import ManHinhDanhMucCoSo
from ..dung_chung.ho_tro import hien_thi, gan_goi_y_combobox


class ManHinhPhong(ManHinhDanhMucCoSo):
    LOAI = Phong
    CO_LUU_TRU = True
    TRUONG = ['ten', 'suc_chua', 'gia_phong', 'toa_nha', 'tang']
    BAT_BUOC = ['ten', 'suc_chua', 'gia_phong', 'toa_nha', 'tang']
    TRUONG_CHI_DOC_KHI_SUA = {'toa_nha', 'tang'}

    def cau_hinh_form(self, form, o_nhap, du_lieu):
        super().cau_hinh_form(form, o_nhap, du_lieu)
        # Giá trị mặc định lấy từ CauHinhDong, người dùng vẫn có thể sửa.
        if du_lieu or 'suc_chua' not in o_nhap:
            return
        try:
            cfg = self.adapter.doc_cau_hinh()
            suc_chua = (cfg.get('SUC_CHUA_PHONG_MAC_DINH', cfg.get('suc_chua_phong_mac_dinh'))
                        if isinstance(cfg, dict) else cfg.SUC_CHUA_PHONG_MAC_DINH)
            if suc_chua is not None:
                o = o_nhap['suc_chua']
                o.delete(0, tk.END)
                o.insert(0, str(suc_chua))
        except Exception as exc:
            messagebox.showwarning('Không thể đọc cấu hình', str(exc), parent=form.winfo_toplevel())

    def tao_o_nhap(self, parent, truong, gia_tri):
        if truong != 'toa_nha':
            return super().tao_o_nhap(parent, truong, gia_tri)
        toa_nha = self.adapter.lay_tat_ca(ToaNha)
        lua_chon = {f'{toa.ten} ({ma})': ma for ma, toa in
                    sorted(toa_nha.items(), key=lambda item: str(item[1].ten).casefold())}
        o = ttk.Combobox(parent, state='normal', width=40)
        gan_goi_y_combobox(o, lua_chon)
        self._ma_theo_nhan_toa = lua_chon
        if gia_tri:
            nhan = next((nhan for nhan, ma in lua_chon.items()
                         if ma == str(gia_tri)), '')
            o.set(nhan)
        return o

    def chuan_hoa_du_lieu_form(self, data, o_nhap):
        data = super().chuan_hoa_du_lieu_form(data, o_nhap)
        if 'toa_nha' in data:
            o = o_nhap['toa_nha']
            ma = self._ma_theo_nhan_toa.get(data['toa_nha'])
            if ma is None:
                raise ValueError('Hãy chọn Tòa nhà từ danh sách gợi ý theo tên.')
            data['toa_nha'] = ma
        return data

    def tao_giao_dien(self):
        self._ma_chon = None
        self._tat_ca_phong = []
        self._the_phong = []
        self._so_cot = 0
        self._tao_style()

        dau = tk.Frame(self, bg='#207B68', padx=20, pady=17)
        dau.pack(fill='x', pady=(0, 14))
        ttk.Button(dau, text='+ Thêm phòng', style='KTX.Primary.TButton',
                   command=self.them_moi).pack(side='right')
        tk.Label(dau, text='Quản lý phòng', bg='#207B68', fg='white',
                 font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        tk.Label(dau, text='Xem sức chứa, giá thuê và vị trí từng phòng.',
                 bg='#207B68', fg='#DBF3EB',
                 font=('Segoe UI', 10)).pack(anchor='w', pady=(4, 0))

        thong_ke = ttk.Frame(self)
        thong_ke.pack(fill='x', pady=(0, 12))
        self.so_lieu = {}
        cac_o = (
            ('Tổng số phòng', 'tong', '#2563EB'),
            ('Tổng sức chứa', 'suc_chua', '#059669'),
            ('Số tòa nhà', 'toa', '#7C3AED'),
            ('Giá phòng TB', 'gia', '#B45309'),
        )
        for i, (tieu_de, khoa, mau) in enumerate(cac_o):
            thong_ke.columnconfigure(i, weight=1, uniform='dem')
            nen_o = self._mau_thong_ke[i]
            o = tk.Frame(
                thong_ke, bg=nen_o, padx=14, pady=12,
                highlightthickness=1,
                highlightbackground=self._mau_vien
            )
            o.grid(row=0, column=i, padx=4, sticky='nsew')
            tk.Label(
                o, text=tieu_de, bg=nen_o, fg=self._mau_phu,
                font=('Segoe UI', 10)
            ).pack(anchor='w')
            bien = tk.StringVar(master=self, value='0')
            self.so_lieu[khoa] = bien
            tk.Label(
                o, textvariable=bien, bg=nen_o,
                fg=mau if not self._toi else self._mau_chu,
                font=('Segoe UI', 19, 'bold')
            ).pack(anchor='w', pady=(7, 0))

        thanh = ttk.Frame(self)
        thanh.pack(fill='x', pady=8)
        self.txt_tim = ttk.Entry(thanh)
        self.txt_tim.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.txt_tim.bind('<Return>', lambda _e: self.tim_kiem())
        ttk.Button(thanh, text='Tìm kiếm', command=self.tim_kiem).pack(side='left', padx=4)
        ttk.Button(thanh, text='Làm mới', command=self.lam_moi).pack(side='left', padx=4)

        loc = ttk.Frame(self)
        loc.pack(fill='x', pady=(0, 14))
        ttk.Label(loc, text='Tòa nhà:').pack(side='left', padx=4)
        self.cbo_toa = ttk.Combobox(loc, width=16, state='readonly',
                                    values=['Tất cả tòa nhà'])
        self.cbo_toa.set('Tất cả tòa nhà')
        self.cbo_toa.pack(side='left', padx=4)
        self.cbo_toa.bind('<<ComboboxSelected>>', lambda _e: self.tim_kiem())
        ttk.Label(loc, text='Tầng:').pack(side='left', padx=4)
        self.cbo_tang = ttk.Combobox(loc, width=12, state='readonly', values=['Tất cả tầng'])
        self.cbo_tang.set('Tất cả tầng')
        self.cbo_tang.pack(side='left', padx=4)
        self.cbo_tang.bind('<<ComboboxSelected>>', lambda _e: self.tim_kiem())
        ttk.Checkbutton(loc, text='Bao gồm lưu trữ', variable=self.hien_luu_tru,
                        command=self.tai_du_lieu).pack(side='left', padx=8)

        title = ttk.Frame(self)
        title.pack(fill='x', pady=(0, 6))
        ttk.Label(title, text='Danh sách phòng', style='PhongSection.TLabel').pack(side='left')
        self.lbl_ket_qua = ttk.Label(title, text='0 phòng')
        self.lbl_ket_qua.pack(side='right')

        khung = ttk.Frame(self)
        khung.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(khung, highlightthickness=0,
                                background=self._mau_nen)
        scroll = ttk.Scrollbar(khung, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        self.khung_the = ttk.Frame(self.canvas, padding=4)
        self._id_khung = self.canvas.create_window((0, 0), window=self.khung_the, anchor='nw')
        self.khung_the.bind('<Configure>', lambda _e: self.canvas.configure(
            scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', self._co_gian_the)
        # Sự kiện cuộn do App phân phối, tránh cuộn hai lần.

    def _tao_style(self):
        style = ttk.Style(self)
        self._mau_nen = style.lookup('TFrame', 'background') or '#F4F6FA'
        try:
            rgb = self.winfo_rgb(self._mau_nen)
            self._toi = sum(rgb) / 3 < 32768
        except tk.TclError:
            self._toi = False

        if self._toi:
            self._mau_the = '#303F52'
            self._mau_vien = '#4C637D'
            self._mau_chon = '#32C9A8'
            self._mau_chu = '#F3F7FF'
            self._mau_phu = '#CFD9E7'
            self._mau_thong_ke = (
                '#2B405C', '#294B44', '#403958', '#4B4031'
            )
        else:
            self._mau_the = '#EAF4FF'
            self._mau_vien = '#BAD6F2'
            self._mau_chon = '#0D9488'
            self._mau_chu = '#23354C'
            self._mau_phu = '#526981'
            self._mau_thong_ke = (
                '#E8F1FF', '#E7F6EE', '#F1EDFF', '#FFF1E4'
            )

        style.configure('PhongPage.TLabel', font=('Segoe UI', 20, 'bold'))
        style.configure('PhongSection.TLabel', font=('Segoe UI', 12, 'bold'))

    def tai_du_lieu(self):
        try:
            ket_qua = self.adapter.lay_tat_ca(self.LOAI, lay_luu_tru=self.doc_luu_tru())
            self._tat_ca_phong = list(ket_qua.values())
            self._cap_nhat_bo_loc()
            self._cap_nhat_thong_ke()
            self.tim_kiem()
        except Exception as exc:
            messagebox.showerror('Lỗi tải phòng', str(exc), parent=self.winfo_toplevel())

    def _cap_nhat_bo_loc(self):
        cu_toa, cu_tang = self.cbo_toa.get(), self.cbo_tang.get()
        toa = ['Tất cả tòa nhà'] + sorted({str(p.toa_nha) for p in self._tat_ca_phong})
        tang = ['Tất cả tầng'] + sorted({str(p.tang) for p in self._tat_ca_phong},
                                        key=lambda x: int(x))
        self.cbo_toa.configure(values=toa)
        self.cbo_tang.configure(values=tang)
        self.cbo_toa.set(cu_toa if cu_toa in toa else toa[0])
        self.cbo_tang.set(cu_tang if cu_tang in tang else tang[0])

    def _cap_nhat_thong_ke(self):
        ds = self._tat_ca_phong
        tong = len(ds)
        self.so_lieu['tong'].set(str(tong))
        self.so_lieu['suc_chua'].set(str(sum(p.suc_chua for p in ds)))
        self.so_lieu['toa'].set(str(len({p.toa_nha for p in ds})))
        self.so_lieu['gia'].set(f'{sum(p.gia_phong for p in ds) / tong:,.0f} đ' if tong else '0 đ')

    def tim_kiem(self):
        tu = self.txt_tim.get().strip().casefold()
        toa, tang = self.cbo_toa.get(), self.cbo_tang.get()
        ket_qua = []
        for p in self._tat_ca_phong:
            if toa != 'Tất cả tòa nhà' and str(p.toa_nha) != toa:
                continue
            if tang != 'Tất cả tầng' and str(p.tang) != tang:
                continue
            if tu and not any(tu in hien_thi(getattr(p, k, '')).casefold()
                              for k in self.TRUONG):
                continue
            ket_qua.append(p)
        self.hien_thi_danh_sach(ket_qua)

    def lam_moi(self):
        self.txt_tim.delete(0, 'end')
        self.cbo_toa.set('Tất cả tòa nhà')
        self.cbo_tang.set('Tất cả tầng')
        self.tai_du_lieu()

    def hien_thi_danh_sach(self, data):
        self._ma_chon = None
        self._the_phong.clear()
        for w in self.khung_the.winfo_children():
            w.destroy()
        if isinstance(data, dict):
            data = list(data.values())
        self.lbl_ket_qua.configure(text=f'{len(data)} phòng')
        if not data:
            ttk.Label(self.khung_the, text='Không có phòng phù hợp.',
                      padding=22).grid(row=0, column=0)
            return
        for phong in data:
            card, ma = self._tao_the_phong(phong)
            self._the_phong.append((card, ma))
        self._so_cot = 0
        self._sap_xep_the(self.canvas.winfo_width())

    def _co_gian_the(self, event):
        self.canvas.itemconfigure(self._id_khung, width=event.width)
        self._sap_xep_the(event.width)

    def _sap_xep_the(self, rong):
        so_cot = 3 if rong >= 900 else 2 if rong >= 590 else 1
        if so_cot == self._so_cot:
            return
        self._so_cot = so_cot
        for i in range(3):
            self.khung_the.columnconfigure(i, weight=1 if i < so_cot else 0,
                                           uniform='phong' if i < so_cot else '')
        for i, (the, _) in enumerate(self._the_phong):
            the.grid_forget()
            the.grid(row=i // so_cot, column=i % so_cot,
                     sticky='nsew', padx=6, pady=6)

    def _tao_the_phong(self, p):
        ma = str(p.ma)
        the = tk.Frame(
            self.khung_the, bg=self._mau_the,
            padx=14, pady=14,
            highlightthickness=2,
            highlightbackground=self._mau_vien,
            highlightcolor=self._mau_chon
        )
        nhan = []
        thong_tin = (
            str(p.ten),
            f'Mã phòng: {ma}',
            f'Tòa nhà: {p.toa_nha}',
            f'Tầng: {p.tang}',
            f'Sức chứa: {p.suc_chua} người',
            f'Giá phòng: {p.gia_phong:,.0f} đ'
        )
        for i, noi_dung in enumerate(thong_tin):
            lbl = tk.Label(
                the, text=noi_dung,
                bg=self._mau_the,
                fg=self._mau_chu if i == 0 else self._mau_phu,
                font=('Segoe UI', 13, 'bold') if i == 0 else ('Segoe UI', 10),
                anchor='w', justify='left', wraplength=270
            )
            lbl.pack(anchor='w', fill='x', pady=(2 if i else 0, 4))
            nhan.append(lbl)

        nut = tk.Frame(the, bg=self._mau_the)
        nut.pack(fill='x', pady=(12, 0))
        ttk.Button(
            nut, text='Chi tiết',
            command=lambda m=ma: self._chay_cho_phong(m, self.xem_chi_tiet)
        ).pack(side='left', expand=True, fill='x', padx=(0, 4))
        ttk.Button(
            nut, text='Sửa',
            command=lambda m=ma: self._chay_cho_phong(m, self.chinh_sua)
        ).pack(side='left', expand=True, fill='x', padx=(0, 4))
        
        nut_them = ttk.Menubutton(nut, text='⋯', width=3)
        menu = tk.Menu(nut_them, tearoff=0)
        
        # Gọi tường minh từ ManHinhDanhMucCoSo để khắc phục triệt để cảnh báo Pylance
        for ten, ham in (
            ('Lưu trữ', self.luu_tru),
            ('Tái kích hoạt', lambda: ManHinhDanhMucCoSo.tai_kich_hoat(self)),
            ('Xóa', lambda: ManHinhDanhMucCoSo.xoa(self))
        ):
            menu.add_command(
                label=ten,
                command=lambda h=ham, m=ma: self._chay_cho_phong(m, h)
            )
        nut_them.configure(menu=menu)
        nut_them.pack(side='right')
        
        for w in (the, *nhan):
            w.bind('<Button-1>', lambda _e, m=ma: self._chon_the(m))
        return the, ma

    def _chon_the(self, ma):
        self._ma_chon = ma
        for the, ma_the in self._the_phong:
            the.configure(
                highlightbackground=(
                    self._mau_chon if ma == ma_the else self._mau_vien
                )
            )

    def _chay_cho_phong(self, ma, ham):
        self._chon_the(ma)
        ham()

    def lay_ma_chon(self):
        if self._ma_chon is None:
            messagebox.showwarning('Chưa chọn phòng', 'Hãy chọn một thẻ phòng.',
                                   parent=self.winfo_toplevel())
        return self._ma_chon
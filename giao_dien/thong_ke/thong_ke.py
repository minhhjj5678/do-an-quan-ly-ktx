"""Dashboard thống kê đơn giản, vẽ biểu đồ tròn bằng Tkinter Canvas."""
import tkinter as tk
from tkinter import ttk, messagebox

from ..dung_chung.mau_sac import lay_mau


class ManHinhThongKe(ttk.Frame):
    THONG_KE = [
        ('Số phòng', 'thong_ke_so_phong'),
        ('Tỷ lệ lấp đầy', 'thong_ke_ty_le_lap_day'),
        ('Công nợ', 'thong_ke_cong_no'),
    ]
    NHAN = {
        'hoc_ky': 'Học kỳ',
        'toa_nha': 'Mã tòa nhà',
        'loai_phong': 'Loại phòng',
    }

    def __init__(self, parent, adapter):
        super().__init__(parent, padding=12)
        self.adapter = adapter
        self.ten_hien_tai = 'thong_ke_ty_le_lap_day'
        self.ty_le_bieu_do = None
        self.tao_giao_dien()
        self.after_idle(lambda: self.xem(self.ten_hien_tai))

    def tao_giao_dien(self):
        dau = ttk.Frame(self, style='KTX.Banner.TFrame', padding=18)
        dau.pack(fill='x', pady=(0, 12))
        ttk.Label(dau, text='Thống kê ký túc xá',
                  style='KTX.BannerTitle.TLabel').pack(anchor='w')
        ttk.Label(dau, text='Số liệu rõ ràng, dễ theo dõi hoạt động hằng ngày',
                  style='KTX.BannerSub.TLabel').pack(anchor='w', pady=(5, 0))

        khung_loc = ttk.LabelFrame(self, text='  Lọc dữ liệu  ', padding=12)
        khung_loc.pack(fill='x', pady=(0, 10))
        self.o_loc = {}
        for cot, truong in enumerate(self.NHAN):
            khung_loc.columnconfigure(cot, weight=1)
            o = ttk.Frame(khung_loc)
            o.grid(row=0, column=cot, sticky='ew', padx=(0, 10))
            ttk.Label(o, text=self.NHAN[truong]).pack(anchor='w', pady=(0, 4))
            entry = ttk.Entry(o)
            entry.pack(fill='x')
            self.o_loc[truong] = entry
        ttk.Label(khung_loc, text='Để trống bộ lọc nếu muốn xem toàn bộ dữ liệu.',
                  style='KTX.Muted.TLabel').grid(row=1, column=0,
                                                columnspan=3, sticky='w', pady=(9, 0))

        thanh = ttk.Frame(self)
        thanh.pack(fill='x', pady=(0, 10))
        self.cac_nut = {}
        for nhan, ten in self.THONG_KE:
            nut = ttk.Button(thanh, text=nhan, command=lambda t=ten: self.xem(t))
            nut.pack(side='left', padx=(0, 8))
            self.cac_nut[ten] = nut
        ttk.Button(thanh, text='Làm mới', command=self.lam_moi).pack(side='right')

        khung_ket_qua = ttk.Frame(self)
        khung_ket_qua.pack(fill='both', expand=True)
        khung_ket_qua.columnconfigure(0, weight=1)
        khung_ket_qua.columnconfigure(1, weight=1)
        khung_ket_qua.rowconfigure(0, weight=1)

        ben_trai = ttk.LabelFrame(khung_ket_qua, text='  Biểu đồ tròn  ', padding=12)
        ben_trai.grid(row=0, column=0, sticky='nsew', padx=(0, 7))
        self.bieu_do = tk.Canvas(ben_trai, width=280, height=245,
                                 bd=0, highlightthickness=0)
        self.bieu_do.pack(fill='both', expand=True)
        self.bieu_do.bind('<Configure>', lambda e: self.ve_bieu_do())
        self.lbl_chu_thich = ttk.Label(ben_trai, text='',
                                      style='KTX.Muted.TLabel', wraplength=290,
                                      justify='center')
        self.lbl_chu_thich.pack(pady=(6, 2))

        ben_phai = ttk.LabelFrame(khung_ket_qua, text='  Chi tiết số liệu  ', padding=12)
        ben_phai.grid(row=0, column=1, sticky='nsew', padx=(7, 0))
        ttk.Label(ben_phai, text='Thông tin tổng hợp',
                  style='KTX.CardTitle.TLabel').pack(anchor='w', pady=(0, 10))
        khung_bang = ttk.Frame(ben_phai)
        khung_bang.pack(fill='both', expand=True)
        self.bang = ttk.Treeview(khung_bang, columns=('noi_dung', 'gia_tri'),
                                 show='headings', height=7)
        self.bang.heading('noi_dung', text='Chỉ số')
        self.bang.heading('gia_tri', text='Giá trị')
        self.bang.column('noi_dung', width=175, minwidth=90)
        self.bang.column('gia_tri', width=125, minwidth=80)
        self.bang.pack(side='left', fill='both', expand=True)
        cuon = ttk.Scrollbar(khung_bang, orient='vertical', command=self.bang.yview)
        cuon.pack(side='right', fill='y')
        self.bang.configure(yscrollcommand=cuon.set)
        self.trang_thai = ttk.Label(ben_phai, text='Chọn loại thống kê để xem.',
                                   style='KTX.Muted.TLabel', wraplength=300)
        self.trang_thai.pack(anchor='w', pady=(10, 0))

    @staticmethod
    def _so(value):
        """Đọc số từ backend, không tự suy đoán số liệu."""
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip().replace('%', '').replace(',', '.'))
            except ValueError:
                return None
        return None

    def _ty_le(self, ten_ham, data):
        """Chỉ vẽ khi backend có tỷ lệ lấp đầy hoặc số phòng có cùng đơn vị."""
        if not isinstance(data, dict):
            if ten_ham != 'thong_ke_ty_le_lap_day':
                return None
            so = self._so(data)
            if so is None or so < 0:
                return None
            if isinstance(data, str) and '%' in data:
                return min(100.0, so)
            return min(100.0, so * 100 if so <= 1 else so)
        if ten_ham == 'thong_ke_ty_le_lap_day':
            for key in ('ty_le_lap_day', 'ty_le', 'ti_le_lap_day'):
                if key in data:
                    so = self._so(data[key])
                    if so is None or so < 0:
                        return None
                    # Tỷ lệ có thể là số thập phân 0..1 hoặc phần trăm 0..100.
                    if isinstance(data[key], str) and '%' in data[key]:
                        return min(100.0, so)
                    return min(100.0, so * 100 if 0 <= so <= 1 else so)
        if ten_ham == 'thong_ke_so_phong':
            for da_o, con_trong in (('phong_da_o', 'phong_trong'),
                                   ('so_phong_da_o', 'so_phong_trong'),
                                   ('so_phong_co_nguoi', 'so_phong_trong')):
                if da_o in data and con_trong in data:
                    a, b = self._so(data[da_o]), self._so(data[con_trong])
                    if a is not None and b is not None and a >= 0 and b >= 0 and a + b > 0:
                        return 100 * a / (a + b)
        return None

    def ve_bieu_do(self):
        canvas = self.bieu_do
        canvas.delete('all')
        root = self.winfo_toplevel()
        mau = lay_mau(getattr(root, 'chu_de_hien_tai', 'LIGHT'))
        canvas.configure(bg=mau['the'])
        w = max(canvas.winfo_width(), 200)
        h = max(canvas.winfo_height(), 190)
        radius = max(55, min(w, h) * .36)
        cx, cy = w / 2, h / 2
        x1, y1, x2, y2 = cx - radius, cy - radius, cx + radius, cy + radius
        if self.ty_le_bieu_do is None:
            canvas.create_oval(x1, y1, x2, y2, outline=mau['vien'], width=3,
                               fill=mau['nhat'])
            canvas.create_text(cx, cy, text='Chưa có\ndữ liệu tỷ lệ',
                               justify='center', fill=mau['phu'],
                               font=('Segoe UI', 13, 'bold'))
            return

        pct = max(0, min(100, self.ty_le_bieu_do))
        canvas.create_oval(x1, y1, x2, y2, fill=mau['nhat'], outline=mau['the'])
        if pct > 0:
            canvas.create_arc(x1, y1, x2, y2, start=90,
                              extent=-359.99 if pct >= 100 else -pct * 3.6,
                              fill=mau['chinh'], outline=mau['the'], width=2)
        # Vòng trắng nhỏ tạo cảm giác gọn gàng, hiển thị phần trăm ngay giữa.
        r = radius * .53
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                           fill=mau['the'], outline=mau['the'])
        canvas.create_text(cx, cy, text=f'{pct:.1f}%', fill=mau['chu'],
                           font=('Segoe UI', 17, 'bold'))

    def xem(self, ten_ham):
        bo_loc = {k: o.get().strip() for k, o in self.o_loc.items() if o.get().strip()}
        try:
            data = self.adapter.thong_ke(ten_ham, bo_loc)
        except Exception as exc:
            messagebox.showerror('Lỗi thống kê', str(exc), parent=self.winfo_toplevel())
            return

        self.ten_hien_tai = ten_ham
        for ten, nut in self.cac_nut.items():
            nut.configure(style='KTX.Primary.TButton' if ten == ten_ham else 'TButton')
        self.bang.delete(*self.bang.get_children())
        if isinstance(data, dict):
            for k, v in data.items():
                self.bang.insert('', 'end', values=(k.replace('_', ' ').capitalize(), str(v)))
        else:
            self.bang.insert('', 'end', values=('Kết quả', str(data)))

        self.ty_le_bieu_do = self._ty_le(ten_ham, data)
        if self.ty_le_bieu_do is None:
            self.lbl_chu_thich.configure(text='Biểu đồ xuất hiện khi có dữ liệu tỷ lệ phù hợp.')
        else:
            self.lbl_chu_thich.configure(text='Phần tô màu: đã lấp đầy • Phần nhạt: còn trống')
        self.trang_thai.configure(text='Đã tải kết quả từ hệ thống. Không sử dụng số liệu minh họa.')
        self.ve_bieu_do()

    def lam_moi(self):
        for entry in self.o_loc.values():
            entry.delete(0, 'end')
        self.xem(self.ten_hien_tai)

    def cap_nhat_mau(self):
        self.ve_bieu_do()

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
        'toa_nha': 'Mã tòa nhà',
        'loai_phong': 'Sức chứa phòng',
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

        khung_loc = ttk.LabelFrame(self, text='   Lọc dữ liệu   ', padding=12)
        khung_loc.pack(fill='x', pady=(0, 10))
        self.o_loc = {}
        
        for cot, truong in enumerate(self.NHAN):
            khung_loc.columnconfigure(cot, weight=1)
            o = ttk.Frame(khung_loc)
            o.grid(row=0, column=cot, sticky='ew', padx=(0, 10))
            ttk.Label(o, text=self.NHAN[truong]).pack(anchor='w', pady=(0, 4))
            
            # Thay vì Entry thủ công, dùng ttk.Combobox (thanh ngang sổ xuống)
            values = ['']
            if truong == 'toa_nha':
                try:
                    from thuc_the.ky_tuc_xa import ToaNha
                    ds_toa = self.adapter.lay_tat_ca(ToaNha)
                    values = [''] + [str(t.ma) for t in ds_toa.values()]
                except Exception:
                    values = ['']  # Không tự bịa mã tòa nhà
            elif truong == 'loai_phong':
                values = ['', '2', '4', '6', '8']

            cbo = ttk.Combobox(o, values=values, state='readonly')
            cbo.pack(fill='x')
            cbo.set('')
            self.o_loc[truong] = cbo

        ttk.Label(khung_loc, text='Để trống bộ lọc nếu muốn xem toàn bộ dữ liệu.',
                  style='KTX.Muted.TLabel').grid(row=1, column=0,
                                                 columnspan=2, sticky='w', pady=(9, 0))

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

        ben_trai = ttk.LabelFrame(khung_ket_qua, text='   Biểu đồ tròn   ', padding=12)
        ben_trai.grid(row=0, column=0, sticky='nsew', padx=(0, 7))
        self.bieu_do = tk.Canvas(ben_trai, width=280, height=245,
                                 bd=0, highlightthickness=0)
        self.bieu_do.pack(fill='both', expand=True)
        self.bieu_do.bind('<Configure>', lambda e: self.ve_bieu_do())
        self.lbl_chu_thich = ttk.Label(ben_trai, text='',
                                       style='KTX.Muted.TLabel', wraplength=290,
                                       justify='center')
        self.lbl_chu_thich.pack(pady=(6, 2))

        ben_phai = ttk.LabelFrame(khung_ket_qua, text='   Chi tiết số liệu   ', padding=12)
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
        r = radius * .53
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                           fill=mau['the'], outline=mau['the'])
        canvas.create_text(cx, cy, text=f'{pct:.1f}%', fill=mau['chu'],
                           font=('Segoe UI', 17, 'bold'))

    @staticmethod
    def _lay_truong(du_lieu, *cac_khoa):
        """Đọc thống kê dạng dict của mock; None nghĩa là chưa có số liệu."""
        for khoa in cac_khoa:
            if khoa in du_lieu:
                return du_lieu[khoa]
        return None

    def _so_hop_le(self, gia_tri, ten):
        from math import isfinite
        so = self._so(gia_tri)
        if so is None or not isfinite(so) or so < 0:
            raise ValueError(f"Dữ liệu '{ten}' không hợp lệ: {gia_tri!r}")
        return so

    def xem(self, ten_ham):
        """Hỗ trợ backend thật (tuple/float) và mock cũ (dict)."""
        bo_loc = {k: o.get().strip() for k, o in self.o_loc.items() if o.get().strip()}
        if 'loai_phong' in bo_loc:
            try:
                bo_loc['loai_phong'] = int(bo_loc['loai_phong'])
            except ValueError:
                messagebox.showwarning('Bộ lọc', 'Sức chứa phòng phải là số nguyên.',
                                       parent=self.winfo_toplevel())
                return
        if ten_ham == 'thong_ke_cong_no':
            bo_loc = {}  # Backend thật không nhận bộ lọc công nợ.

        try:
            data = self.adapter.thong_ke(ten_ham, bo_loc)
            self.ty_le_bieu_do = None

            if ten_ham == 'thong_ke_so_phong':
                if isinstance(data, dict):
                    # Mock có thể chỉ trả {'tong_so_phong': ...}; không tự giả định đã có người.
                    tong = self._lay_truong(data, 'tong_so_phong', 'tong', 'tong_phong')
                    trong = self._lay_truong(data, 'phong_trong', 'so_phong_trong')
                    co_nguoi = self._lay_truong(data, 'phong_da_o', 'so_phong_da_o',
                                                'phong_co_nguoi', 'so_phong_co_nguoi')
                    if tong is not None:
                        tong = self._so_hop_le(tong, 'Tổng số phòng')
                    if trong is not None:
                        trong = self._so_hop_le(trong, 'Phòng trống')
                    if co_nguoi is not None:
                        co_nguoi = self._so_hop_le(co_nguoi, 'Phòng có người')
                    if tong is None and trong is not None and co_nguoi is not None:
                        tong = trong + co_nguoi
                    if tong is not None and trong is not None and co_nguoi is None:
                        co_nguoi = tong - trong
                    if tong is not None and co_nguoi is not None and trong is None:
                        trong = tong - co_nguoi
                    if tong is None and trong is None and co_nguoi is None:
                        raise ValueError('Thống kê số phòng không có trường dữ liệu được nhận diện')
                    if tong is not None and trong is not None and co_nguoi is not None:
                        if min(trong, co_nguoi) < 0 or abs((trong + co_nguoi) - tong) > 0.01:
                            raise ValueError('Số phòng trống/có người không khớp tổng số phòng')
                else:
                    if not isinstance(data, (tuple, list)) or len(data) != 3:
                        raise ValueError('Thống kê số phòng phải trả tuple 3 số hoặc dict')
                    trong, co_nguoi, tong = (
                        self._so_hop_le(v, t) for v, t in zip(
                            data, ('Phòng trống', 'Phòng có người', 'Tổng số phòng'))
                    )
                hang = []
                if trong is not None:
                    hang.append(('Phòng trống', f'{trong:g}'))
                if co_nguoi is not None:
                    hang.append(('Phòng có người', f'{co_nguoi:g}'))
                if tong is not None:
                    hang.append(('Tổng số phòng', f'{tong:g}'))
                if tong is not None and co_nguoi is not None:
                    self.ty_le_bieu_do = co_nguoi / tong * 100 if tong else 0.0

            elif ten_ham == 'thong_ke_ty_le_lap_day':
                if isinstance(data, dict):
                    gia_tri = self._lay_truong(data, 'ty_le_lap_day', 'ty_le', 'ti_le_lap_day')
                else:
                    gia_tri = data
                if gia_tri is None:
                    raise ValueError('Không có dữ liệu tỷ lệ lấp đầy')
                so = self._so_hop_le(gia_tri, 'Tỷ lệ lấp đầy')
                # Giao thức thật: 0..1. Một số mock có thể trả tỷ lệ dạng %.
                pct = so * 100 if so <= 1 and not (isinstance(gia_tri, str) and '%' in gia_tri) else so
                if pct > 100:
                    raise ValueError('Tỷ lệ lấp đầy không được vượt quá 100%')
                self.ty_le_bieu_do = pct
                hang = [('Tỷ lệ lấp đầy', f'{pct:.2f}%')]

            elif ten_ham == 'thong_ke_cong_no':
                if isinstance(data, dict):
                    tong_no = self._lay_truong(data, 'tong_tien_no', 'tong_cong_no', 'tong_no')
                    so_sinh_vien = self._lay_truong(data, 'so_sinh_vien_dang_no',
                                                   'so_sinh_vien_no', 'so_nguoi_no')
                elif isinstance(data, (tuple, list)) and len(data) == 2:
                    tong_no, so_sinh_vien = data
                else:
                    raise ValueError('Thống kê công nợ phải trả tuple 2 số hoặc dict')
                if tong_no is None or so_sinh_vien is None:
                    raise ValueError('Dữ liệu công nợ thiếu tổng tiền hoặc số người đang nợ')
                tong_no = self._so_hop_le(tong_no, 'Tổng tiền nợ')
                so_sinh_vien = self._so_hop_le(so_sinh_vien, 'Số người đang nợ')
                hang = [('Tổng tiền nợ', f'{tong_no:,.0f} đ'),
                        ('Số lượng đang nợ', f'{so_sinh_vien:g}')]
            else:
                raise ValueError('Loại thống kê không hỗ trợ')
        except Exception as exc:
            messagebox.showerror('Lỗi thống kê', str(exc), parent=self.winfo_toplevel())
            return

        self.ten_hien_tai = ten_ham
        for ten, nut in self.cac_nut.items():
            nut.configure(style='KTX.Primary.TButton' if ten == ten_ham else 'TButton')
        self.bang.delete(*self.bang.get_children())
        for nhan, value in hang:
            self.bang.insert('', 'end', values=(nhan, str(value)))
        if self.ty_le_bieu_do is None:
            self.lbl_chu_thich.configure(
                text='Chưa có đủ số liệu để vẽ tỷ lệ. Các chỉ số hiện có vẫn được hiển thị.')
        else:
            self.lbl_chu_thich.configure(
                text='Phần tô màu: tỷ lệ đã sử dụng • Phần nhạt: phần còn lại')
        self.trang_thai.configure(text='Đã cập nhật dữ liệu thống kê từ hệ thống.')
        self.ve_bieu_do()

    def lam_moi(self):
        for entry in self.o_loc.values():
            entry.set('')
        self.xem(self.ten_hien_tai)

    def cap_nhat_mau(self):
        self.ve_bieu_do()
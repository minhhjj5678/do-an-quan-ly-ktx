"""Màn hình Tài khoản theo bố cục danh mục.

- Bố cục danh sách: tìm kiếm, thêm mới, chi tiết, chỉnh sửa và xóa.
- Chọn tài khoản trực tiếp trên bảng, không có Hộp tài khoản riêng.
- Quản trị tài khoản vẫn đi qua Adapter/GiaoThucPhienLamViec.
- Đặt lại mật khẩu và thao tác nghiệp vụ chỉ xuất hiện trong cửa sổ Chi tiết.
- Không dùng CRUD thực thể TaiKhoan.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from ..dung_chung.mau_sac import lay_mau


class ManHinhTaiKhoan(ttk.Frame):
    NGHIEP_VU = (
        ('Thanh toán hợp đồng', 'thanh_toan_hop_dong', 'Mã hợp đồng'),
        ('Kết thúc hợp đồng', 'ket_thuc_hop_dong', 'Mã hợp đồng'),
        ('Thanh toán hóa đơn', 'thanh_toan_hoa_don_thang', 'Mã hóa đơn'),
        ('Xử lý vi phạm', 'xu_ly_vi_pham', 'Mã vi phạm'),
    )

    def __init__(self, parent, adapter):
        super().__init__(parent, padding=0)
        self.adapter = adapter
        self.la_quan_tri = bool(self.adapter.la_admin())

        # Dữ liệu tài khoản luôn đọc từ backend thật, không cache giả lập.
        self.ds_tai_khoan = {}
        self.o_ma_nghiep_vu = {}

        self.tao_giao_dien()
        if self.la_quan_tri:
            self.tai_du_lieu()

    # ------------------------------------------------------------------
    # Giao diện chính và thanh cuộn
    # ------------------------------------------------------------------
    def tao_giao_dien(self):
        khung_cuon = ttk.Frame(self)
        khung_cuon.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(khung_cuon, bd=0, highlightthickness=0)
        self.thanh_cuon = ttk.Scrollbar(
            khung_cuon, orient='vertical', command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.thanh_cuon.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.thanh_cuon.pack(side='right', fill='y')

        self.noi_dung = ttk.Frame(self.canvas, padding=12)
        self.id_noi_dung = self.canvas.create_window(
            (0, 0), window=self.noi_dung, anchor='nw'
        )
        self.noi_dung.bind(
            '<Configure>',
            lambda _e: self.canvas.configure(
                scrollregion=self.canvas.bbox('all')
            )
        )
        self.canvas.bind(
            '<Configure>',
            lambda e: self.canvas.itemconfigure(
                self.id_noi_dung, width=e.width
            )
        )
        # Cuộn chuột được App phân phối; không bind_all làm mất cuộn trang khác.

        self.tao_dau_trang()

        if self.la_quan_tri:
            self.tao_thanh_cong_cu_danh_sach()
            self.tao_bang_tai_khoan()
        else:
            self.tao_khu_vuc_nguoi_dung()

    def tao_dau_trang(self):
        dau = ttk.Frame(
            self.noi_dung, style='KTX.Banner.TFrame', padding=18
        )
        dau.pack(fill='x', pady=(0, 12))
        ttk.Label(
            dau, text='Quản lý Tài khoản', style='KTX.BannerTitle.TLabel'
        ).pack(anchor='w')
        ttk.Label(
            dau,
            text='Quản lý thông tin tài khoản và thực hiện các thao tác cần thiết.',
            style='KTX.BannerSub.TLabel'
        ).pack(anchor='w', pady=(4, 0))

    def tao_thanh_cong_cu_danh_sach(self):
        tong = ttk.Frame(self.noi_dung, padding=(14, 10))
        tong.pack(fill='x', pady=(0, 12))
        self.lbl_so_luong = ttk.Label(
            tong, text='Hiển thị 0 tài khoản', font=('Segoe UI', 11, 'bold')
        )
        self.lbl_so_luong.pack(side='left')
        ttk.Button(
            tong, text='+ Thêm mới', style='KTX.Primary.TButton',
            command=self.mo_form_tao_tai_khoan
        ).pack(side='right')

        thanh_tim = ttk.Frame(self.noi_dung)
        thanh_tim.pack(fill='x', pady=(0, 12))
        ttk.Label(thanh_tim, text='Tìm nhanh:').pack(side='left', padx=(0, 7))
        self.txt_tim = ttk.Entry(thanh_tim)
        self.txt_tim.pack(side='left', fill='x', expand=True, padx=(0, 7))
        self.txt_tim.bind('<Return>', lambda _e: self.tim_kiem())
        ttk.Button(
            thanh_tim, text='Tìm kiếm', command=self.tim_kiem
        ).pack(side='left', padx=3)
        ttk.Button(
            thanh_tim, text='Làm mới', command=self.lam_moi
        ).pack(side='left', padx=3)

        hanh_dong = ttk.Frame(self.noi_dung)
        hanh_dong.pack(fill='x', pady=(0, 10))
        ttk.Button(
            hanh_dong, text='Xem chi tiết', command=self.xem_chi_tiet
        ).pack(side='left', padx=(0, 7))
        ttk.Button(
            hanh_dong, text='Đặt lại mật khẩu', command=self.xem_chi_tiet
        ).pack(side='left', padx=(0, 7))
        ttk.Button(
            hanh_dong, text='Xóa', style='KTX.Danger.TButton',
            command=self.xoa_tai_khoan
        ).pack(side='left')
        ttk.Label(
            hanh_dong, text='Nhấp đúp một dòng để xem chi tiết.'
        ).pack(side='right')

    def tao_bang_tai_khoan(self):
        khung_bang = ttk.Frame(self.noi_dung)
        khung_bang.pack(fill='both', expand=True)
        khung_bang.columnconfigure(0, weight=1)
        khung_bang.rowconfigure(0, weight=1)

        cot = ('tai_khoan', 'vai_tro', 'ma_chu_the', 'trang_thai')
        self.bang = ttk.Treeview(
            khung_bang, columns=cot, show='headings',
            selectmode='browse', style='KTX.Treeview'
        )
        tieu_de = {
            'tai_khoan': 'Tên đăng nhập',
            'vai_tro': 'Vai trò',
            'ma_chu_the': 'Mã chủ thể',
            'trang_thai': 'Trạng thái'
        }
        for truong in cot:
            self.bang.heading(truong, text=tieu_de[truong])
            self.bang.column(truong, width=180, minwidth=120, anchor='w')

        self.cap_nhat_mau()
        cuon_y = ttk.Scrollbar(
            khung_bang, orient='vertical', command=self.bang.yview
        )
        cuon_x = ttk.Scrollbar(
            khung_bang, orient='horizontal', command=self.bang.xview
        )
        self.bang.configure(
            yscrollcommand=cuon_y.set, xscrollcommand=cuon_x.set
        )
        self.bang.grid(row=0, column=0, sticky='nsew')
        cuon_y.grid(row=0, column=1, sticky='ns')
        cuon_x.grid(row=1, column=0, sticky='ew')
        self.bang.bind('<Double-1>', lambda _e: self.xem_chi_tiet())

        self.tai_du_lieu()

    def cap_nhat_mau(self):
        """Màu chữ và nền từng dòng phù hợp với chủ đề đang chọn."""
        mau = lay_mau(getattr(self.winfo_toplevel(), 'chu_de_hien_tai', 'LIGHT'))
        if hasattr(self, 'canvas'):
            self.canvas.configure(bg=mau['nen'])
        if hasattr(self, 'bang'):
            self.bang.tag_configure('chan', background=mau['the'], foreground=mau['chu'])
            self.bang.tag_configure('le', background=mau['nhat'], foreground=mau['chu'])

    def tai_du_lieu(self, tu_khoa=''):
        if not hasattr(self, 'bang'):
            return
        try:
            kho = self.adapter.lay_tat_ca(TaiKhoan, lay_luu_tru=True)
        except Exception as exc:
            messagebox.showerror('Lỗi tải tài khoản', str(exc), parent=self.winfo_toplevel())
            return
        self.ds_tai_khoan = {
            ten: {
                'vai_tro': f'{tk.loai_tai_khoan.name} ({tk.loai_tai_khoan.value})',
                'loai_tai_khoan': tk.loai_tai_khoan,
                'ma_chu_the': tk.ma_chu_the,
                'trang_thai': 'Đang hoạt động' if tk.con_hoat_dong else 'Ngưng hoạt động',
            }
            for ten, tk in kho.items()
        }
        self.bang.delete(*self.bang.get_children())
        tu_khoa = tu_khoa.strip().casefold()
        dem = 0
        for ten, thong_tin in self.ds_tai_khoan.items():
            gia_tri = [ten, thong_tin['vai_tro'],
                       thong_tin.get('ma_chu_the') or '', thong_tin['trang_thai']]
            if tu_khoa and not any(tu_khoa in str(x).casefold() for x in gia_tri):
                continue
            self.bang.insert('', 'end', iid=ten, values=gia_tri,
                             tags=('chan' if dem % 2 == 0 else 'le',))
            dem += 1
        self.lbl_so_luong.configure(text=f'Hiển thị {dem} tài khoản')

    def _lay_ten_tai_khoan_dang_chon(self):
        # Chỉ thao tác với tài khoản được chọn trực tiếp trên bảng.
        if not hasattr(self, 'bang'):
            messagebox.showwarning(
                'Chưa có danh sách tài khoản',
                'Danh sách tài khoản hiện không khả dụng.',
                parent=self.winfo_toplevel()
            )
            return None
        chon = self.bang.selection()
        if not chon:
            messagebox.showwarning(
                'Chưa chọn tài khoản',
                'Bạn hãy chọn một tài khoản trong danh sách trước.',
                parent=self.winfo_toplevel()
            )
            return None
        return chon[0]

    def tim_kiem(self):
        self.tai_du_lieu(self.txt_tim.get())

    def lam_moi(self):
        self.txt_tim.delete(0, tk.END)
        self.tai_du_lieu()

    def lay_tai_khoan_chon(self):
        chon = self.bang.selection()
        if not chon:
            messagebox.showwarning(
                'Chưa chọn tài khoản', 'Bạn hãy chọn một tài khoản trong danh sách.',
                parent=self.winfo_toplevel()
            )
            return None
        return chon[0]

    # ------------------------------------------------------------------
    # Người dùng thường: chỉ mở nghiệp vụ trong cửa sổ chi tiết
    # ------------------------------------------------------------------
    def tao_khu_vuc_nguoi_dung(self):
        khung = ttk.LabelFrame(
            self.noi_dung, text='  Thông tin và thao tác  ', padding=18
        )
        khung.pack(fill='x', pady=(0, 12))
        ttk.Label(
            khung,
            text='Các thao tác nghiệp vụ được mở trong cửa sổ chi tiết.'
        ).pack(side='left', fill='x', expand=True)
        ttk.Button(
            khung, text='Chi tiết tài khoản', style='KTX.Primary.TButton',
            command=lambda: self.mo_chi_tiet(None)
        ).pack(side='right')

    # ------------------------------------------------------------------
    # Tạo mới tài khoản
    # ------------------------------------------------------------------
    @staticmethod
    def _tao_o_nhap(parent, hang, nhan, show=''):
        ttk.Label(parent, text=nhan).grid(
            row=hang, column=0, sticky='w', pady=6
        )
        o_nhap = ttk.Entry(parent, show=show)
        o_nhap.grid(
            row=hang, column=1, sticky='ew', padx=12, pady=6
        )
        return o_nhap

    def _lay_bang_vai_tro(self):
        return {f'{loai.name} ({loai.value})': loai for loai in LoaiTaiKhoan}

    def mo_form_tao_tai_khoan(self):
        cua_so = tk.Toplevel(self)
        cua_so.title('Thêm tài khoản mới')
        cua_so.geometry('520x370')
        cua_so.minsize(440, 330)
        cua_so.transient(self.winfo_toplevel())
        cua_so.grab_set()

        khung = ttk.Frame(cua_so, padding=20)
        khung.pack(fill='both', expand=True)
        khung.columnconfigure(1, weight=1)

        ttk.Label(
            khung, text='TẠO TÀI KHOẢN MỚI',
            font=('Segoe UI', 15, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 14))

        txt_ten = self._tao_o_nhap(khung, 1, 'Tên đăng nhập')
        txt_mk = self._tao_o_nhap(khung, 2, 'Mật khẩu', show='*')

        ttk.Label(khung, text='Vai trò / Loại tài khoản').grid(
            row=3, column=0, sticky='w', pady=6
        )
        bang_vai_tro = self._lay_bang_vai_tro()
        cbo_vai_tro = ttk.Combobox(
            khung, state='readonly', values=list(bang_vai_tro)
        )
        cbo_vai_tro.grid(row=3, column=1, sticky='ew', padx=12, pady=6)

        txt_chu_the = self._tao_o_nhap(khung, 4, 'Mã chủ thể (nếu có)')

        def luu():
            ten = txt_ten.get().strip()
            mat_khau = txt_mk.get()
            loai = bang_vai_tro.get(cbo_vai_tro.get())
            ma_chu_the = txt_chu_the.get().strip() or None
            if not ten or not mat_khau or loai is None:
                messagebox.showwarning(
                    'Thiếu thông tin',
                    'Vui lòng nhập tên đăng nhập, mật khẩu và chọn vai trò.',
                    parent=cua_so
                )
                return
            try:
                self.adapter.tao_tai_khoan(ten, mat_khau, loai, ma_chu_the)
                self.tai_du_lieu()
                messagebox.showinfo(
                    'Thành công', f'Đã tạo tài khoản {ten}.', parent=cua_so
                )
                cua_so.destroy()
            except Exception as exc:
                messagebox.showerror('Lỗi tạo tài khoản', str(exc), parent=cua_so)

        nut = ttk.Frame(khung)
        nut.grid(row=5, column=0, columnspan=2, sticky='e', pady=(18, 0))
        ttk.Button(nut, text='Hủy', command=cua_so.destroy).pack(side='right')
        ttk.Button(
            nut, text='Tạo tài khoản', style='KTX.Primary.TButton', command=luu
        ).pack(side='right', padx=(0, 8))

    # ------------------------------------------------------------------
    # Chi tiết: reset mật khẩu + nghiệp vụ chỉ hiện sau khi bấm nút
    # ------------------------------------------------------------------
    def xem_chi_tiet(self):
        ten = self._lay_ten_tai_khoan_dang_chon()
        if ten is not None:
            self.mo_chi_tiet(ten)

    def mo_chi_tiet(self, ten):
        cua_so = tk.Toplevel(self)
        cua_so.title('Chi tiết tài khoản và nghiệp vụ')
        cua_so.geometry('700x720')
        cua_so.minsize(520, 460)
        cua_so.transient(self.winfo_toplevel())
        cua_so.grab_set()

        khung_ngoai = ttk.Frame(cua_so)
        khung_ngoai.pack(fill='both', expand=True)
        canvas = tk.Canvas(khung_ngoai, highlightthickness=0, bd=0)
        cuon = ttk.Scrollbar(khung_ngoai, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=cuon.set)
        canvas.pack(side='left', fill='both', expand=True)
        cuon.pack(side='right', fill='y')
        noi_dung = ttk.Frame(canvas, padding=18)
        item = canvas.create_window((0, 0), window=noi_dung, anchor='nw')
        noi_dung.bind(
            '<Configure>',
            lambda _e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        canvas.bind(
            '<Configure>', lambda e: canvas.itemconfigure(item, width=e.width)
        )

        thong_tin = self.ds_tai_khoan.get(ten, {}) if ten else {}
        ttk.Label(
            noi_dung, text='CHI TIẾT TÀI KHOẢN',
            font=('Segoe UI', 16, 'bold')
        ).pack(anchor='w', pady=(0, 12))
        if ten:
            ttk.Label(noi_dung, text=f'Tên đăng nhập: {ten}').pack(anchor='w', pady=3)
            ttk.Label(
                noi_dung,
                text=f"Vai trò: {thong_tin.get('vai_tro', 'Chưa có dữ liệu vai trò')}"
            ).pack(anchor='w', pady=3)
            ttk.Label(
                noi_dung,
                text=f"Mã chủ thể: {thong_tin.get('ma_chu_the') or 'Không có'}"
            ).pack(anchor='w', pady=3)
            ttk.Label(
                noi_dung,
                text=f"Trạng thái: {thong_tin.get('trang_thai', 'Chưa xác định')}"
            ).pack(anchor='w', pady=3)

        if self.la_quan_tri and ten:
            self.tao_khu_vuc_dat_lai_mat_khau(noi_dung, cua_so, ten)
            self.tao_khu_vuc_trang_thai_tai_khoan(noi_dung, cua_so, ten)

        self.tao_khu_vuc_nghiep_vu(noi_dung, cua_so)

        ttk.Button(
            noi_dung, text='Đóng', command=cua_so.destroy
        ).pack(anchor='e', pady=(16, 2))

    def tao_khu_vuc_dat_lai_mat_khau(self, parent, cua_so, ten):
        khung = ttk.LabelFrame(
            parent, text='  Đặt lại mật khẩu  ', padding=12
        )
        khung.pack(fill='x', pady=(14, 8))
        khung.columnconfigure(1, weight=1)
        ttk.Label(khung, text='Mật khẩu mới').grid(
            row=0, column=0, sticky='w', pady=6
        )
        txt_moi = ttk.Entry(khung, show='*')
        txt_moi.grid(row=0, column=1, sticky='ew', padx=10, pady=6)
        ttk.Label(khung, text='Xác nhận mật khẩu mới').grid(
            row=1, column=0, sticky='w', pady=6
        )
        txt_xac_nhan = ttk.Entry(khung, show='*')
        txt_xac_nhan.grid(row=1, column=1, sticky='ew', padx=10, pady=6)

        def reset():
            mat_khau = txt_moi.get()
            xac_nhan = txt_xac_nhan.get()
            if not mat_khau or not xac_nhan:
                messagebox.showwarning(
                    'Thiếu thông tin', 'Nhập mật khẩu mới và xác nhận.', parent=cua_so
                )
                return
            if mat_khau != xac_nhan:
                messagebox.showwarning(
                    'Mật khẩu không khớp',
                    'Mật khẩu mới và xác nhận không giống nhau.', parent=cua_so
                )
                return
            if not messagebox.askyesno(
                'Xác nhận', f'Đặt lại mật khẩu cho tài khoản {ten}?', parent=cua_so
            ):
                return
            try:
                self.adapter.doi_mat_khau(mat_khau_moi=mat_khau, tai_khoan=ten)
                txt_moi.delete(0, tk.END)
                txt_xac_nhan.delete(0, tk.END)
                messagebox.showinfo(
                    'Thành công', f'Đã đặt lại mật khẩu cho {ten}.', parent=cua_so
                )
            except Exception as exc:
                messagebox.showerror('Lỗi đặt lại mật khẩu', str(exc), parent=cua_so)

        ttk.Button(
            khung, text='Đặt lại mật khẩu', style='KTX.Primary.TButton', command=reset
        ).grid(row=2, column=1, sticky='e', pady=(8, 2))

    def tao_khu_vuc_trang_thai_tai_khoan(self, parent, cua_so, ten):
        khung = ttk.LabelFrame(
            parent, text='  Trạng thái tài khoản  ', padding=12
        )
        khung.pack(fill='x', pady=8)

        def thao_tac(ten_ham, mo_ta, trang_thai):
            if not messagebox.askyesno(
                'Xác nhận', f'Bạn muốn {mo_ta} tài khoản {ten}?', parent=cua_so
            ):
                return
            try:
                getattr(self.adapter, ten_ham)(ten)
                self.tai_du_lieu()
                messagebox.showinfo(
                    'Thành công', f'Đã {mo_ta} tài khoản {ten}.', parent=cua_so
                )
            except Exception as exc:
                messagebox.showerror('Lỗi thao tác tài khoản', str(exc), parent=cua_so)

        hang = ttk.Frame(khung)
        hang.pack(fill='x')
        ttk.Button(
            hang, text='Ngưng hoạt động',
            command=lambda: thao_tac(
                'ngung_tai_khoan', 'ngưng hoạt động', 'Ngưng hoạt động'
            )
        ).pack(side='left', padx=(0, 8))
        ttk.Button(
            hang, text='Kích hoạt lại',
            command=lambda: thao_tac(
                'kich_hoat_lai_tai_khoan', 'kích hoạt lại', 'Đang hoạt động'
            )
        ).pack(side='left')

    def tao_khu_vuc_nghiep_vu(self, parent, cua_so):
        khung = ttk.LabelFrame(
            parent, text='  Thao tác nghiệp vụ  ', padding=12
        )
        khung.pack(fill='x', pady=8)
        khung.columnconfigure(0, weight=1)
        khung.columnconfigure(1, weight=1)

        for i, (tieu_de, ten_ham, nhan_ma) in enumerate(self.NGHIEP_VU):
            the = ttk.LabelFrame(khung, text=f'  {tieu_de}  ', padding=10)
            the.grid(
                row=i // 2, column=i % 2, sticky='nsew', padx=5, pady=5
            )
            the.columnconfigure(0, weight=1)
            ttk.Label(the, text=nhan_ma).grid(
                row=0, column=0, sticky='w', pady=(0, 5)
            )
            o_nhap = ttk.Entry(the)
            o_nhap.grid(row=1, column=0, sticky='ew', pady=(0, 8))
            self.o_ma_nghiep_vu[(cua_so, ten_ham)] = o_nhap
            ttk.Button(
                the, text='Thực hiện', style='KTX.Primary.TButton',
                command=lambda h=ten_ham, t=tieu_de, e=o_nhap:
                    self.thuc_hien_nghiep_vu(h, e.get(), t, cua_so, e)
            ).grid(row=2, column=0, sticky='e')

    def thuc_hien_nghiep_vu(self, ten_ham, ma, tieu_de, cua_so, o_nhap):
        ma = ma.strip()
        if not ma:
            messagebox.showwarning(
                'Thiếu thông tin', 'Vui lòng nhập mã đối tượng.', parent=cua_so
            )
            return
        if not messagebox.askyesno(
            'Xác nhận', f'{tieu_de} cho mã {ma}?', parent=cua_so
        ):
            return
        try:
            self.adapter.nghiep_vu(ten_ham, ma)
            o_nhap.delete(0, tk.END)
            messagebox.showinfo(
                'Thành công', f'Đã thực hiện: {tieu_de}.', parent=cua_so
            )
        except Exception as exc:
            messagebox.showerror('Lỗi nghiệp vụ', str(exc), parent=cua_so)

    # ------------------------------------------------------------------
    # Chỉnh sửa / xóa
    # ------------------------------------------------------------------
    def xoa_tai_khoan(self):
        ten = self._lay_ten_tai_khoan_dang_chon()
        if ten is None:
            return
        if not messagebox.askyesno(
            'Xác nhận xóa', f'Bạn có chắc muốn xóa tài khoản {ten}?',
            parent=self.winfo_toplevel()
        ):
            return
        try:
            self.adapter.xoa_tai_khoan(ten)
            self.tai_du_lieu()
            messagebox.showinfo(
                'Thành công', f'Đã xóa tài khoản {ten}.',
                parent=self.winfo_toplevel()
            )
        except Exception as exc:
            messagebox.showerror('Lỗi xóa tài khoản', str(exc), parent=self.winfo_toplevel())

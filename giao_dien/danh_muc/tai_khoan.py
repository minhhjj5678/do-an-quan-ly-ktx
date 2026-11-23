"""Màn hình Tài khoản theo bố cục danh mục.

- Bố cục danh sách: tìm kiếm, thêm mới, chi tiết, chỉnh sửa và xóa.
- Chọn tài khoản trực tiếp trên bảng, không có Hộp tài khoản riêng.
- Quản trị tài khoản vẫn đi qua Adapter/GiaoThucPhienLamViec.
- Đặt lại mật khẩu mặc định và bật/tắt trạng thái ở cửa sổ Chi tiết.
- Không dùng CRUD thực thể TaiKhoan.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from thuc_the.ky_tuc_xa import SinhVien
from ..dung_chung.ho_tro import gan_goi_y_combobox
from ..dung_chung.mau_sac import lay_mau


class ManHinhTaiKhoan(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=0)
        self.app = app
        self.la_quan_tri = bool(self.app.la_admin())

        # Dữ liệu tài khoản luôn đọc từ backend thật, không cache giả lập.
        self.ds_tai_khoan = {}
        self.hien_luu_tru = tk.BooleanVar(master=self, value=False)

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
            text='Cấp tài khoản, phân quyền và theo dõi trạng thái hoạt động.',
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
        ttk.Checkbutton(
            thanh_tim, text='Bao gồm lưu trữ',
            variable=self.hien_luu_tru,
            command=lambda: self.tai_du_lieu(self.txt_tim.get())
        ).pack(side='right', padx=(12, 0))

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
            'ma_chu_the': 'Sinh viên (MSSV)',
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
            kho = self.app.dieu_phoi.lay_tat_ca(TaiKhoan, lay_luu_tru=self.hien_luu_tru.get())
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
        ttk.Label(khung, text='Quản lý tài khoản chỉ dành cho Quản trị viên.').pack(
            side='left', fill='x', expand=True)
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
        """Chọn vai trò trước; mật khẩu ban đầu dùng tên đăng nhập."""
        cua_so = tk.Toplevel(self)
        cua_so.title('Thêm tài khoản mới')
        cua_so.geometry('610x305')
        cua_so.minsize(510, 285)
        cua_so.transient(self.winfo_toplevel())
        cua_so.grab_set()

        khung = ttk.Frame(cua_so, padding=20)
        khung.pack(fill='both', expand=True)
        khung.columnconfigure(1, weight=1)
        ttk.Label(khung, text='TẠO TÀI KHOẢN MỚI',
                  font=('Segoe UI', 15, 'bold')).grid(
                      row=0, column=0, columnspan=2, sticky='w', pady=(0, 14))

        ttk.Label(khung, text='Vai trò / Loại tài khoản').grid(
            row=1, column=0, sticky='w', pady=7)
        bang_vai_tro = self._lay_bang_vai_tro()
        cbo_vai_tro = ttk.Combobox(khung, state='readonly', values=list(bang_vai_tro))
        cbo_vai_tro.grid(row=1, column=1, sticky='ew', padx=12, pady=7)

        # Style riêng cho ô bị khóa (không sửa), phân biệt rõ với ô đang nhập.
        style = ttk.Style(cua_so)
        style.configure('KTX.Khoa.TEntry', fieldbackground='#E3E8EF', foreground='#586579')
        style.map('KTX.Khoa.TEntry',
                  fieldbackground=[('readonly', '#E3E8EF'), ('disabled', '#E3E8EF')],
                  foreground=[('readonly', '#586579'), ('disabled', '#586579')])
        style.configure('KTX.Khoa.TCombobox', fieldbackground='#E3E8EF',
                        background='#D4DCE6', foreground='#586579')
        style.map('KTX.Khoa.TCombobox',
                  fieldbackground=[('disabled', '#E3E8EF')],
                  foreground=[('disabled', '#586579')])

        txt_ten = self._tao_o_nhap(khung, 2, 'Tên đăng nhập')
        txt_ten.configure(style='KTX.Khoa.TEntry')
        txt_ten.configure(state='disabled')

        ttk.Label(khung, text='Sinh viên (họ tên – MSSV)').grid(
            row=3, column=0, sticky='w', pady=7)
        cbo_sinh_vien = ttk.Combobox(khung, state='disabled', style='KTX.Khoa.TCombobox')
        cbo_sinh_vien.grid(row=3, column=1, sticky='ew', padx=12, pady=7)

        # Cả tài khoản đã ngừng cũng giữ liên kết ma_chu_the, tránh cấp trùng.
        try:
            tk_da_co = self.app.dieu_phoi.lay_tat_ca(TaiKhoan, lay_luu_tru=True)
            ma_da_co = {tk.ma_chu_the for tk in tk_da_co.values() if tk.ma_chu_the}
            sinh_vien = self.app.dieu_phoi.lay_tat_ca(SinhVien)
            sv_chua_co = {f'{sv.ten} ({ma})': ma for ma, sv in
                         sorted(sinh_vien.items(), key=lambda item: str(item[1].ten).casefold())
                         if ma not in ma_da_co}
        except Exception as exc:
            messagebox.showerror('Không thể tải sinh viên', str(exc), parent=cua_so)
            cua_so.destroy()
            return

        gan_goi_y_combobox(cbo_sinh_vien, sv_chua_co)

        def dat_ten_dang_nhap(ten: str, cho_phep_nhap: bool):
            """Hiện MSSV nhưng không cho sửa tay khi là tài khoản Sinh viên."""
            txt_ten.configure(state='normal')
            txt_ten.delete(0, tk.END)
            if ten:
                txt_ten.insert(0, ten)
            txt_ten.configure(style='TEntry' if cho_phep_nhap else 'KTX.Khoa.TEntry',
                              state='normal' if cho_phep_nhap else 'readonly')

        def cap_nhat_sinh_vien(_event=None):
            if bang_vai_tro.get(cbo_vai_tro.get()) == LoaiTaiKhoan.SINH_VIEN:
                ma = sv_chua_co.get(cbo_sinh_vien.get().strip(), '')
                dat_ten_dang_nhap(ma, False)

        def cap_nhat_vai_tro(_event=None):
            loai = bang_vai_tro.get(cbo_vai_tro.get())
            cbo_sinh_vien.set('')
            dat_ten_dang_nhap('', loai == LoaiTaiKhoan.QUAN_TRI_VIEN)
            cbo_sinh_vien.configure(
                state='normal' if loai == LoaiTaiKhoan.SINH_VIEN else 'disabled',
                style='TCombobox' if loai == LoaiTaiKhoan.SINH_VIEN else 'KTX.Khoa.TCombobox'
            )

        cbo_vai_tro.bind('<<ComboboxSelected>>', cap_nhat_vai_tro)
        cbo_sinh_vien.bind('<<ComboboxSelected>>', cap_nhat_sinh_vien)
        cbo_sinh_vien.bind('<KeyRelease>', cap_nhat_sinh_vien, add='+')

        def luu():
            loai = bang_vai_tro.get(cbo_vai_tro.get())
            if loai is None:
                messagebox.showwarning('Thiếu thông tin', 'Hãy chọn vai trò trước.', parent=cua_so)
                return
            ma_chu_the = None
            if loai == LoaiTaiKhoan.SINH_VIEN:
                ma_chu_the = sv_chua_co.get(cbo_sinh_vien.get().strip())
                if ma_chu_the is None:
                    messagebox.showwarning(
                        'Chưa chọn sinh viên',
                        'Hãy chọn đúng tên và MSSV từ danh sách sinh viên chưa có tài khoản.',
                        parent=cua_so
                    )
                    return
                # Tên đăng nhập của Sinh viên luôn bằng mã sinh viên.
                ten = ma_chu_the
            else:
                ten = txt_ten.get().strip()
                if not ten:
                    messagebox.showwarning(
                        'Thiếu thông tin', 'Hãy nhập tên đăng nhập.', parent=cua_so
                    )
                    return
            # PhienLamViec.la_mat_khau yêu cầu mật khẩu tối thiểu 6 ký tự.
            if len(ten) < 6:
                messagebox.showwarning('Tên đăng nhập quá ngắn',
                                       'Do mật khẩu mặc định bằng tên đăng nhập và backend yêu cầu '
                                       'mật khẩu từ 6 ký tự, tên đăng nhập phải có ít nhất 6 ký tự.',
                                       parent=cua_so)
                return
            if not messagebox.askyesno(
                'Xác nhận tạo tài khoản',
                f'Tạo tài khoản {ten}?',
                parent=cua_so
            ):
                return
            try:
                self.app.phien.tao_tai_khoan(ten, ten, loai, ma_chu_the)
                self.tai_du_lieu(self.txt_tim.get())
                messagebox.showinfo('Thành công',
                                    f'Đã tạo tài khoản {ten}.',
                                    parent=cua_so)
                cua_so.destroy()
            except Exception as exc:
                messagebox.showerror('Lỗi tạo tài khoản', str(exc), parent=cua_so)

        nut = ttk.Frame(khung)
        nut.grid(row=4, column=0, columnspan=2, sticky='e', pady=(18, 0))
        ttk.Button(nut, text='Hủy', command=cua_so.destroy).pack(side='right')
        ttk.Button(nut, text='Tạo tài khoản', style='KTX.Primary.TButton',
                   command=luu).pack(side='right', padx=(0, 8))

    # ------------------------------------------------------------------
    # Chi tiết: reset mật khẩu + nghiệp vụ chỉ hiện sau khi bấm nút
    # ------------------------------------------------------------------
    def xem_chi_tiet(self):
        ten = self._lay_ten_tai_khoan_dang_chon()
        if ten is not None:
            self.mo_chi_tiet(ten)

    def mo_chi_tiet(self, ten):
        cua_so = tk.Toplevel(self)
        cua_so.title('Chi tiết tài khoản')
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
        # Khởi tạo trước điều kiện để biến luôn tồn tại khi mở chi tiết.
        bien_trang_thai = tk.StringVar(master=cua_so, value='')
        if ten:
            ttk.Label(noi_dung, text=f'Tên đăng nhập: {ten}').pack(anchor='w', pady=3)
            ttk.Label(
                noi_dung,
                text=f"Vai trò: {thong_tin.get('vai_tro', 'Chưa có dữ liệu vai trò')}"
            ).pack(anchor='w', pady=3)
            ttk.Label(
                noi_dung,
                text=f"Sinh viên (MSSV): {thong_tin.get('ma_chu_the') or 'Không có'}"
            ).pack(anchor='w', pady=3)
            bien_trang_thai.set(
                f"Trạng thái: {thong_tin.get('trang_thai', 'Chưa xác định')}"
            )
            ttk.Label(noi_dung, textvariable=bien_trang_thai).pack(anchor='w', pady=3)

        if self.la_quan_tri and ten:
            self.tao_khu_vuc_dat_lai_mat_khau(noi_dung, cua_so, ten)
            self.tao_khu_vuc_trang_thai_tai_khoan(noi_dung, cua_so, ten, bien_trang_thai)


        ttk.Button(
            noi_dung, text='Đóng', command=cua_so.destroy
        ).pack(anchor='e', pady=(16, 2))

    def tao_khu_vuc_dat_lai_mat_khau(self, parent, cua_so, ten):
        khung = ttk.LabelFrame(parent, text='  Đặt lại mật khẩu  ', padding=12)
        khung.pack(fill='x', pady=(14, 8))
        def reset():
            if len(ten) < 6:
                messagebox.showwarning('Không thể đặt mật khẩu mặc định',
                                       'Tên đăng nhập này ngắn hơn 6 ký tự, không đạt quy tắc '
                                       'mật khẩu của PhienLamViec. Cần thống nhất lại quy tắc '
                                       'với Phần C trước khi đặt lại.', parent=cua_so)
                return
            try:
                self.app.phien.doi_mat_khau(mat_khau_moi=ten, tai_khoan=ten)
                messagebox.showinfo('Thành công', 'Đã đặt lại mật khẩu', parent=cua_so)
            except Exception as exc:
                messagebox.showerror('Lỗi đặt lại mật khẩu', str(exc), parent=cua_so)

        ttk.Button(khung, text='Đặt lại mật khẩu',
                   style='KTX.Primary.TButton', command=reset).pack(anchor='e')

    def tao_khu_vuc_trang_thai_tai_khoan(self, parent, cua_so, ten, bien_trang_thai):
        khung = ttk.LabelFrame(parent, text='  Trạng thái tài khoản  ', padding=12)
        khung.pack(fill='x', pady=8)
        hang = ttk.Frame(khung)
        hang.pack(fill='x')

        def hien_nut():
            for con in hang.winfo_children():
                con.destroy()
            thong_tin = self.ds_tai_khoan.get(ten, {})
            dang_hoat_dong = thong_tin.get('trang_thai') == 'Đang hoạt động'
            ten_ham = 'ngung_tai_khoan' if dang_hoat_dong else 'kich_hoat_lai_tai_khoan'
            mo_ta = 'ngừng hoạt động' if dang_hoat_dong else 'kích hoạt lại'
            nhan_nut = 'Ngừng hoạt động' if dang_hoat_dong else 'Kích hoạt lại'

            def thuc_hien():
                if not messagebox.askyesno('Xác nhận',
                                           f'Bạn muốn {mo_ta} tài khoản {ten}?', parent=cua_so):
                    return
                try:
                    getattr(self.app.phien, ten_ham)(ten)

                    self.tai_du_lieu(self.txt_tim.get())
                    hien_nut()
                    bien_trang_thai.set(
                        f"Trạng thái: {'Ngưng hoạt động' if dang_hoat_dong else 'Đang hoạt động'}"
                    )
                    messagebox.showinfo('Thành công',
                                        f'Đã {mo_ta} tài khoản {ten}.', parent=cua_so)
                except Exception as exc:
                    messagebox.showerror('Lỗi thao tác tài khoản', str(exc), parent=cua_so)

            ttk.Button(hang, text=nhan_nut, command=thuc_hien).pack(side='left')

        hien_nut()

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
            self.app.phien.xoa_tai_khoan(ten)
            self.tai_du_lieu()
            messagebox.showinfo(
                'Thành công', f'Đã xóa tài khoản {ten}.',
                parent=self.winfo_toplevel()
            )
        except Exception as exc:
            messagebox.showerror('Lỗi xóa tài khoản', str(exc), parent=self.winfo_toplevel())

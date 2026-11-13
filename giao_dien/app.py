import tkinter as tk
from tkinter import ttk, messagebox

from .xac_thuc.dang_nhap import ManHinhDangNhap
from .xac_thuc.doi_mat_khau import ManHinhDoiMatKhau
from .xac_thuc.quan_tri_tai_khoan import ManHinhQuanTriTaiKhoan

from .danh_muc.sinh_vien import ManHinhSinhVien
from .danh_muc.phong import ManHinhPhong
from .danh_muc.toa_nha import ManHinhToaNha
from .danh_muc.hop_dong import ManHinhHopDong
from .danh_muc.hoa_don_thang import ManHinhHoaDonThang
#from .danh_muc.dich_vu_them import ManHinhDichVuThem
from .danh_muc.vi_pham import ManHinhViPham
from .danh_muc.tai_khoan import ManHinhTaiKhoan

from .nghiep_vu.nghiep_vu import ManHinhNghiepVu
from .thong_ke.thong_ke import ManHinhThongKe
from .cai_dat.cai_dat import ManHinhCaiDat
from .dung_chung.adapter import Adapter
from .dung_chung.mau_sac import lay_mau


class App(tk.Tk):
    def __init__(self, dieu_phoi, phien):
        super().__init__()

        self.adapter = Adapter(dieu_phoi, phien)
        # Nạp dữ liệu file một lần khi khởi động; nạp API nếu cần sẽ do
        # nghiệp vụ thực hiện trong luồng phụ (không khóa Tkinter).
        self.loi_nap_file = None
        try:
            self.adapter.nap_du_lieu_file()
        except Exception as exc:
            self.loi_nap_file = str(exc)
        self.title("Hệ thống quản lý ký túc xá")
        self.geometry("1280x780")
        self.minsize(900, 580)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.nut_menu = {}
        self.nut_dang_chon = None
        self.ten_man_hinh = tk.StringVar(value="Trang chủ")

        self.doi_chu_de("LIGHT")
        try:
            cau_hinh = self.adapter.doc_cau_hinh()
            chu_de = (cau_hinh.get("chu_de", "LIGHT")
                      if isinstance(cau_hinh, dict)
                      else getattr(cau_hinh, "chu_de", "LIGHT"))
            self.doi_chu_de(str(chu_de))
        except Exception:
            pass
        if self.loi_nap_file:
            self.after(100, lambda: messagebox.showwarning(
                "Dữ liệu chưa sẵn sàng", self.loi_nap_file, parent=self))

        # Con lăn hoạt động ở mọi widget bên trong vùng nội dung.
        self.bind_all("<MouseWheel>", self._xu_ly_cuon_chuot, add="+")
        self.bind_all("<Button-4>", self._xu_ly_cuon_chuot, add="+")
        self.bind_all("<Button-5>", self._xu_ly_cuon_chuot, add="+")
        self.protocol("WM_DELETE_WINDOW", self.xac_nhan_thoat)
        self.hien_thi_dang_nhap()

    def xoa_noi_dung(self):
        for widget in self.winfo_children():
            widget.destroy()

    def hien_thi_dang_nhap(self):
        self.xoa_noi_dung()

        man_hinh = ManHinhDangNhap(
            self,
            self.adapter,
            self.hien_thi_trang_chu
        )
        man_hinh.pack(fill="both", expand=True)

    def hien_thi_trang_chu(self):
        self.xoa_noi_dung()
        self.nut_menu = {}
        self.nut_dang_chon = None

        # Bố cục chính: menu trái + nội dung phải
        self.khung_chinh = ttk.Frame(self)
        self.khung_chinh.pack(fill="both", expand=True)

        self.khung_chinh.columnconfigure(0, weight=0)
        self.khung_chinh.columnconfigure(1, weight=1)
        self.khung_chinh.rowconfigure(0, weight=1)

        self.menu = ttk.Frame(
            self.khung_chinh,
            style="Sidebar.TFrame",
            width=245
        )
        self.menu.grid(row=0, column=0, sticky="nsew")
        self.menu.grid_propagate(False)
        self.menu.pack_propagate(False)

        self.khu_vuc_phai = ttk.Frame(self.khung_chinh)
        self.khu_vuc_phai.grid(
            row=0, column=1, sticky="nsew"
        )
        self.khu_vuc_phai.rowconfigure(1, weight=1)
        self.khu_vuc_phai.columnconfigure(0, weight=1)

        self.tao_menu()
        self.tao_khu_vuc_noi_dung()
        self.hien_thi_chao_mung()
        self.after(60, self._cap_nhat_thanh_cuon_trang)

    def tao_menu(self):
        ttk.Label(
            self.menu,
            text="QUẢN LÝ KTX",
            style="SidebarTitle.TLabel"
        ).pack(fill="x", padx=14, pady=(22, 4))

        vai_tro = (
            "Quản trị viên"
            if self.adapter.la_admin()
            else "Nhân viên"
        )

        ttk.Label(
            self.menu,
            text=vai_tro,
            style="SidebarSubtitle.TLabel"
        ).pack(fill="x", padx=14, pady=(0, 16))

        # Dùng Canvas để menu cuộn được khi cửa sổ thấp
        khung_cuon = ttk.Frame(
            self.menu,
            style="Sidebar.TFrame"
        )
        khung_cuon.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            khung_cuon,
            highlightthickness=0,
            bd=0,
            bg=self.mau_menu
        )
        scrollbar = ttk.Scrollbar(
            khung_cuon,
            orient="vertical",
            command=canvas.yview,
            style="Sidebar.Vertical.TScrollbar"
        )

        self.canvas_menu = canvas

        danh_sach_nut = ttk.Frame(
            canvas,
            style="Sidebar.TFrame"
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=danh_sach_nut,
            anchor="nw"
        )

        danh_sach_nut.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                canvas_window,
                width=event.width
            )
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )
        scrollbar.pack(side="right", fill="y")

        danh_sach = [
            ("Sinh viên", ManHinhSinhVien),
            ("Phòng", ManHinhPhong),
            ("Tòa nhà", ManHinhToaNha),
            ("Hợp đồng", ManHinhHopDong),
            ("Hóa đơn tháng", ManHinhHoaDonThang),
            #("Dịch vụ thêm", ManHinhDichVuThem),
            ("Vi phạm", ManHinhViPham)
        ]

        if self.adapter.la_admin():
            danh_sach.extend([
                ("Tài khoản", ManHinhTaiKhoan),
                ("Quản trị tài khoản",
                 ManHinhQuanTriTaiKhoan)
            ])

        danh_sach.extend([
            ("Nghiệp vụ", ManHinhNghiepVu),
            ("Thống kê", ManHinhThongKe),
            ("Cài đặt", ManHinhCaiDat)
        ])

        for ten, lop in danh_sach:
            nut = ttk.Button(
                danh_sach_nut,
                text=ten,
                style="Sidebar.TButton",
                command=lambda t=ten, c=lop:
                    self.chuyen_man_hinh(c, t)
            )
            nut.pack(
                fill="x",
                padx=12,
                pady=3
            )
            self.nut_menu[ten] = nut

        khung_duoi = ttk.Frame(
            self.menu,
            style="Sidebar.TFrame",
            padding=12
        )
        khung_duoi.pack(side="bottom", fill="x")

        ttk.Separator(
            khung_duoi
        ).pack(fill="x", pady=(0, 12))

        ttk.Button(
            khung_duoi,
            text="Đổi mật khẩu",
            command=self.doi_mat_khau
        ).pack(fill="x", pady=4)

        ttk.Button(
            khung_duoi,
            text="Đăng xuất",
            command=self.dang_xuat
        ).pack(fill="x", pady=4)

    def tao_khu_vuc_noi_dung(self):
        thanh_tieu_de = ttk.Frame(
            self.khu_vuc_phai,
            padding=(22, 16)
        )
        thanh_tieu_de.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        ttk.Label(
            thanh_tieu_de,
            textvariable=self.ten_man_hinh,
            style="PageTitle.TLabel"
        ).pack(side="left")

        ttk.Label(
            thanh_tieu_de,
            text="HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ"
        ).pack(side="right")

        # Không đặt Separator cùng ô grid với thanh tiêu đề.

        # Thanh cuộn CHUNG cho mọi màn hình nằm bên phải.
        # Các bảng Treeview / thẻ Phòng vẫn có thanh cuộn riêng để xem dữ liệu.
        vung_cuon = ttk.Frame(self.khu_vuc_phai)
        vung_cuon.grid(row=1, column=0, sticky="nsew")
        vung_cuon.columnconfigure(0, weight=1)
        vung_cuon.rowconfigure(0, weight=1)

        self.canvas_noi_dung = tk.Canvas(
            vung_cuon, bd=0, highlightthickness=0,
            bg=lay_mau(self.chu_de_hien_tai)["nen"]
        )
        self.thanh_cuon_trang = ttk.Scrollbar(
            vung_cuon, orient="vertical",
            command=self.canvas_noi_dung.yview,
            style="Content.Vertical.TScrollbar"
        )
        self.canvas_noi_dung.configure(
            yscrollcommand=self.thanh_cuon_trang.set
        )
        self.canvas_noi_dung.grid(row=0, column=0, sticky="nsew")
        self.thanh_cuon_trang.grid(row=0, column=1, sticky="ns")

        self.noi_dung = ttk.Frame(self.canvas_noi_dung, padding=16)
        self._id_noi_dung = self.canvas_noi_dung.create_window(
            (0, 0), window=self.noi_dung, anchor="nw"
        )
        self.canvas_noi_dung.bind("<Configure>", self._cap_nhat_thanh_cuon_trang)
        self.noi_dung.bind("<Configure>", self._cap_nhat_thanh_cuon_trang)

        thanh_trang_thai = ttk.Frame(
            self.khu_vuc_phai,
            padding=(16, 8)
        )
        thanh_trang_thai.grid(
            row=2,
            column=0,
            sticky="ew"
        )

        ttk.Label(
            thanh_trang_thai,
            text="Trạng thái: Sẵn sàng"
        ).pack(side="left")

        ttk.Label(
            thanh_trang_thai,
            text="Phiên bản giao diện 1.0"
        ).pack(side="right")

    def _cap_nhat_thanh_cuon_trang(self, event=None):
        """Giữ nội dung rộng bằng cửa sổ; cho cuộn nếu nội dung cao hơn."""
        if not hasattr(self, "canvas_noi_dung"):
            return
        canvas = self.canvas_noi_dung
        if not canvas.winfo_exists():
            return
        rong = max(canvas.winfo_width(), 1)
        cao = max(canvas.winfo_height(), self.noi_dung.winfo_reqheight())
        canvas.itemconfigure(self._id_noi_dung, width=rong, height=cao)
        canvas.configure(scrollregion=canvas.bbox("all"))

    @staticmethod
    def _nam_trong(widget, cha):
        """Kiểm tra widget nằm trong vùng giao diện cha hay không."""
        while widget is not None:
            if widget is cha:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _xu_ly_cuon_chuot(self, event):
        """Cuộn đúng nơi đang trỏ chuột: menu, trang, hoặc bảng/phòng."""
        try:
            if event.widget.winfo_toplevel() is not self:
                return  # Không ảnh hưởng các cửa sổ Toplevel
        except tk.TclError:
            return

        buoc = (-1 if event.delta > 0 else 1) if getattr(event, "delta", 0) else (
            -1 if getattr(event, "num", 0) == 4 else 1)

        if hasattr(self, "canvas_menu") and self._nam_trong(event.widget, self.menu):
            self.canvas_menu.yview_scroll(buoc, "units")
            return "break"

        if not hasattr(self, "noi_dung"):
            return
        if event.widget is self.canvas_noi_dung:
            self.canvas_noi_dung.yview_scroll(buoc, "units")
            return "break"
        if not self._nam_trong(event.widget, self.noi_dung):
            return

        widget = event.widget
        while widget is not self.noi_dung:
            # Chỉ cuộn bảng hoặc Canvas con khi chúng THỰC SỰ có dữ liệu tràn.
            if isinstance(widget, (ttk.Treeview, tk.Text, tk.Listbox)):
                dau, cuoi = widget.yview()
                if cuoi - dau < 0.999:
                    return  # Tkinter có sẵn hành vi cuộn của các widget này
            if isinstance(widget, tk.Canvas) and widget is not self.canvas_noi_dung:
                dau, cuoi = widget.yview()
                if cuoi - dau < 0.999:
                    widget.yview_scroll(buoc, "units")
                    return "break"
            widget = widget.master

        self.canvas_noi_dung.yview_scroll(buoc, "units")
        return "break"

    def hien_thi_chao_mung(self):
        self.ten_man_hinh.set('Trang chủ')
        dau = ttk.Frame(self.noi_dung, style='KTX.Banner.TFrame', padding=28)
        dau.pack(fill='x', pady=(15, 18))
        ttk.Label(dau, text='Chào mừng đến với ký túc xá!',
                  style='KTX.BannerTitle.TLabel').pack(anchor='w')
        ttk.Label(dau, text='Quản lý gọn gàng, mọi thông tin ở một nơi.',
                  style='KTX.BannerSub.TLabel').pack(anchor='w', pady=(10, 0))
        vai_tro = 'Quản trị viên' if self.adapter.la_admin() else 'Nhân viên'
        thong_tin = ttk.Frame(self.noi_dung, style='KTX.Panel.TFrame', padding=22)
        thong_tin.pack(fill='x')
        ttk.Label(thong_tin, text=f'Bạn đang đăng nhập: {vai_tro}',
                  style='KTX.PanelTitle.TLabel').pack(anchor='w')
        ttk.Label(thong_tin, text='Chọn một mục từ thanh bên trái để bắt đầu làm việc.',
                  style='KTX.PanelText.TLabel').pack(anchor='w', pady=(6, 0))

    def chuyen_man_hinh(self, lop, ten=None):
        for widget in self.noi_dung.winfo_children():
            widget.destroy()

        if ten:
            self.ten_man_hinh.set(ten)

        try:
            if lop is ManHinhCaiDat:
                man_hinh = lop(
                    self.noi_dung,
                    self.adapter,
                    self.doi_chu_de
                )
            else:
                man_hinh = lop(
                    self.noi_dung,
                    self.adapter
                )

            man_hinh.pack(fill="both", expand=True)
            self.canvas_noi_dung.yview_moveto(0)
            self.after_idle(self._cap_nhat_thanh_cuon_trang)
            self.after(60, self._cap_nhat_thanh_cuon_trang)

            for ten_nut, nut in self.nut_menu.items():
                nut.configure(
                    style=(
                        "SelectedSidebar.TButton"
                        if ten_nut == ten
                        else "Sidebar.TButton"
                    )
                )

        except Exception as e:
            messagebox.showerror(
                "Lỗi mở màn hình",
                str(e),
                parent=self
            )

    def doi_mat_khau(self):
        ManHinhDoiMatKhau(self, self.adapter)

    def dang_xuat(self):
        if not messagebox.askyesno(
            "Xác nhận đăng xuất",
            "Bạn có chắc chắn muốn đăng xuất?",
            parent=self
        ):
            return

        try:
            ket_qua = self.adapter.dang_xuat()

            if ket_qua is False:
                raise ValueError("Đăng xuất thất bại")

            self.hien_thi_dang_nhap()

        except Exception as e:
            messagebox.showerror(
                "Lỗi đăng xuất",
                str(e),
                parent=self
            )

    def xac_nhan_thoat(self):
        if messagebox.askyesno(
            "Xác nhận thoát",
            "Bạn có chắc chắn muốn thoát ứng dụng?",
            parent=self
        ):
            self.destroy()

    def doi_chu_de(self, chu_de):
        """Áp dụng một bảng màu cho toàn bộ ttk; không đổi dữ liệu nghiệp vụ."""
        self.chu_de_hien_tai = str(chu_de).upper()
        mau = lay_mau(self.chu_de_hien_tai)
        self.mau_menu = mau['menu']
        self.configure(bg=mau['nen'])
        st = self.style
        st.configure('.', font=('Segoe UI', 10))
        st.configure('TFrame', background=mau['nen'])
        st.configure('TLabel', background=mau['nen'], foreground=mau['chu'])
        st.configure('TLabelframe', background=mau['the'],
                     bordercolor=mau['vien'], relief='solid')
        st.configure('TLabelframe.Label', background=mau['nen'],
                     foreground=mau['chu'], font=('Segoe UI', 10, 'bold'))
        st.configure('TButton', padding=(11, 8), background=mau['nut'],
                     foreground=mau['chu'], font=('Segoe UI', 10))
        st.map('TButton', background=[('active', mau['chon'])])
        st.configure('TEntry', padding=6, fieldbackground=mau['the'],
                     foreground=mau['chu'])
        st.configure('TCombobox', padding=6, fieldbackground=mau['the'],
                     background=mau['nut'], foreground=mau['chu'])
        st.map('TCombobox', fieldbackground=[('readonly', mau['the'])],
               foreground=[('readonly', mau['chu'])])
        st.configure('TCheckbutton', background=mau['nen'], foreground=mau['chu'])
        st.configure('Treeview', rowheight=33, background=mau['the'],
                     fieldbackground=mau['the'], foreground=mau['chu'],
                     font=('Segoe UI', 10))
        st.configure('Treeview.Heading', background=mau['nhat'],
                     foreground=mau['chu'], font=('Segoe UI', 10, 'bold'), padding=7)
        st.map('Treeview', background=[('selected', mau['chon'])],
               foreground=[('selected', mau['chu'])])
        st.configure('KTX.Treeview', rowheight=34,
                     background=mau['the'], fieldbackground=mau['the'],
                     foreground=mau['chu'])
        st.map('KTX.Treeview', background=[('selected', mau['chon'])],
               foreground=[('selected', mau['chu'])])
        st.configure('KTX.Treeview.Heading', background=mau['nhat'],
                     foreground=mau['chu'], padding=8,
                     font=('Segoe UI', 10, 'bold'))
        st.configure('Sidebar.Vertical.TScrollbar',
                     background=mau['chinh'], troughcolor=mau['menu'],
                     bordercolor=mau['vien'], arrowcolor=mau['chu'], width=14)
        st.configure('Content.Vertical.TScrollbar',
                     background=mau['chinh'], troughcolor=mau['nen'],
                     bordercolor=mau['vien'], arrowcolor=mau['chu'], width=14)
        st.configure('Sidebar.TFrame', background=mau['menu'])
        st.configure('SidebarTitle.TLabel', background=mau['menu'],
                     foreground=mau['chu'], font=('Segoe UI', 17, 'bold'))
        st.configure('SidebarSubtitle.TLabel', background=mau['menu'],
                     foreground=mau['phu'])
        st.configure('Sidebar.TButton', background=mau['nut'],
                     foreground=mau['chu'], padding=(14, 10), anchor='w')
        st.configure('SelectedSidebar.TButton', background=mau['chon'],
                     foreground=mau['chu'], padding=(14, 10), anchor='w',
                     font=('Segoe UI', 10, 'bold'))
        st.configure('PageTitle.TLabel', font=('Segoe UI', 17, 'bold'))
        st.configure('Welcome.TLabel', font=('Segoe UI', 21, 'bold'))
        st.configure('KTX.Banner.TFrame', background=mau['chinh'])
        st.configure('KTX.BannerTitle.TLabel', background=mau['chinh'],
                     foreground=mau['trang'], font=('Segoe UI', 20, 'bold'))
        st.configure('KTX.BannerSub.TLabel', background=mau['chinh'],
                     foreground='#F0F7FF', font=('Segoe UI', 10))
        st.configure('KTX.Panel.TFrame', background=mau['nhat'])
        st.configure('KTX.PanelTitle.TLabel', background=mau['nhat'],
                     foreground=mau['chu'], font=('Segoe UI', 12, 'bold'))
        st.configure('KTX.PanelText.TLabel', background=mau['nhat'], foreground=mau['chu'])
        st.configure('KTX.CardTitle.TLabel', foreground=mau['chu'],
                     font=('Segoe UI', 12, 'bold'))
        st.configure('KTX.Muted.TLabel', foreground=mau['phu'], font=('Segoe UI', 9))
        st.configure('KTX.Primary.TButton', background=mau['chinh'],
                     foreground='white', padding=(13, 9),
                     font=('Segoe UI', 10, 'bold'))
        st.map('KTX.Primary.TButton',
               background=[('active', mau['chinh_dam'])],
               foreground=[('active', 'white')])
        st.configure('KTX.Light.TButton', background=mau['nut'],
                     foreground=mau['chu'], padding=(12, 8))
        st.configure('KTX.Danger.TButton', background='#FFF0ED',
                     foreground='#A93E38', padding=(12, 8))

        if hasattr(self, "canvas_noi_dung") and self.canvas_noi_dung.winfo_exists():
            self.canvas_noi_dung.configure(bg=mau["nen"])

        # Canvas menu là widget tk, nên cập nhật màu riêng.
        if hasattr(self, 'menu') and self.menu.winfo_exists():
            for widget in self.menu.winfo_children():
                for con in widget.winfo_children():
                    if isinstance(con, tk.Canvas):
                        con.configure(bg=mau['menu'])

        # Các widget tk.Canvas hoặc tk.Frame màu riêng cập nhật qua hook đơn giản.
        if hasattr(self, 'noi_dung') and self.noi_dung.winfo_exists():
            for man_hinh in self.noi_dung.winfo_children():
                ham = getattr(man_hinh, 'cap_nhat_mau', None)
                if callable(ham):
                    ham()

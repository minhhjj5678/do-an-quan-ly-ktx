
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
from .danh_muc.dich_vu_them import ManHinhDichVuThem
from .danh_muc.vi_pham import ManHinhViPham
from .danh_muc.tai_khoan import ManHinhTaiKhoan

from .nghiep_vu.nghiep_vu import ManHinhNghiepVu
from .thong_ke.thong_ke import ManHinhThongKe
from .cai_dat.cai_dat import ManHinhCaiDat
from .dung_chung.adapter import Adapter


class App(tk.Tk):
    def __init__(self, dieu_phoi, phien):
        super().__init__()

        self.adapter = Adapter(dieu_phoi, phien)
        self.title("Hệ thống quản lý ký túc xá")
        self.geometry("1280x780")
        self.minsize(900, 580)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.nut_menu = {}
        self.nut_dang_chon = None
        self.ten_man_hinh = tk.StringVar(value="Trang chủ")

        self.doi_chu_de("LIGHT")

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

        self.khu_vuc_phai = ttk.Frame(self.khung_chinh)
        self.khu_vuc_phai.grid(
            row=0, column=1, sticky="nsew"
        )
        self.khu_vuc_phai.rowconfigure(1, weight=1)
        self.khu_vuc_phai.columnconfigure(0, weight=1)

        self.tao_menu()
        self.tao_khu_vuc_noi_dung()
        self.hien_thi_chao_mung()

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
            command=canvas.yview
        )

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
            ("Dịch vụ thêm", ManHinhDichVuThem),
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

        ttk.Separator(
            self.khu_vuc_phai
        ).grid(row=0, column=0, sticky="sew")

        self.noi_dung = ttk.Frame(
            self.khu_vuc_phai,
            padding=16
        )
        self.noi_dung.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

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

    def hien_thi_chao_mung(self):
        self.ten_man_hinh.set("Trang chủ")

        ttk.Label(
            self.noi_dung,
            text="CHÀO MỪNG ĐẾN HỆ THỐNG",
            style="Welcome.TLabel"
        ).pack(pady=(65, 18))

        vai_tro = (
            "Quản trị viên"
            if self.adapter.la_admin()
            else "Nhân viên"
        )

        ttk.Label(
            self.noi_dung,
            text=f"Bạn đang đăng nhập với vai trò: {vai_tro}"
        ).pack(pady=8)

        ttk.Label(
            self.noi_dung,
            text="Chọn chức năng ở thanh bên trái để bắt đầu."
        ).pack(pady=8)

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
        bang_mau = {
            "LIGHT": {
                "nen": "#F4F6FA",
                "chu": "#253047",
                "menu": "#E8EDF5",
                "nut": "#FFFFFF",
                "chon": "#BFD6FA"
            },
            "GREY": {
                "nen": "#D8DCE2",
                "chu": "#242B35",
                "menu": "#C4CBD5",
                "nut": "#EDF0F3",
                "chon": "#A9B9D1"
            },
            "DARK": {
                "nen": "#252B35",
                "chu": "#F4F6FA",
                "menu": "#1C222B",
                "nut": "#343D4B",
                "chon": "#476A9E"
            }
        }

        mau = bang_mau.get(
            chu_de,
            bang_mau["LIGHT"]
        )

        self.mau_menu = mau["menu"]
        self.configure(bg=mau["nen"])

        self.style.configure(
            ".",
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "TFrame",
            background=mau["nen"]
        )
        self.style.configure(
            "TLabel",
            background=mau["nen"],
            foreground=mau["chu"]
        )
        self.style.configure(
            "TLabelframe",
            background=mau["nen"]
        )
        self.style.configure(
            "TLabelframe.Label",
            background=mau["nen"],
            foreground=mau["chu"]
        )
        self.style.configure(
            "TButton",
            padding=(12, 8),
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "TEntry",
            padding=5
        )
        self.style.configure(
            "TCombobox",
            padding=5
        )
        self.style.configure(
            "Treeview",
            rowheight=30,
            font=("Segoe UI", 10),
            background=mau["nut"],
            foreground=mau["chu"],
            fieldbackground=mau["nut"]
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            padding=7
        )
        self.style.map(
            "Treeview",
            background=[("selected", mau["chon"])],
            foreground=[("selected", mau["chu"])]
        )

        self.style.configure(
            "Sidebar.TFrame",
            background=mau["menu"]
        )
        self.style.configure(
            "SidebarTitle.TLabel",
            background=mau["menu"],
            foreground=mau["chu"],
            font=("Segoe UI", 17, "bold")
        )
        self.style.configure(
            "SidebarSubtitle.TLabel",
            background=mau["menu"],
            foreground=mau["chu"],
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "Sidebar.TButton",
            background=mau["nut"],
            foreground=mau["chu"],
            padding=(14, 10),
            anchor="w"
        )
        self.style.configure(
            "SelectedSidebar.TButton",
            background=mau["chon"],
            foreground=mau["chu"],
            padding=(14, 10),
            anchor="w",
            font=("Segoe UI", 10, "bold")
        )
        self.style.configure(
            "PageTitle.TLabel",
            font=("Segoe UI", 17, "bold")
        )
        self.style.configure(
            "Welcome.TLabel",
            font=("Segoe UI", 21, "bold")
        )

        # Cập nhật Canvas của menu khi đổi chủ đề
        if hasattr(self, "menu") and self.menu.winfo_exists():
            for widget in self.menu.winfo_children():
                for con in widget.winfo_children():
                    if isinstance(con, tk.Canvas):
                        con.configure(bg=self.mau_menu)

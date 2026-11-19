
import tkinter as tk
from threading import Thread
from tkinter import ttk, messagebox
from typing import Callable, cast

from .xac_thuc.dang_nhap import ManHinhDangNhap
from .xac_thuc.doi_mat_khau import ManHinhDoiMatKhau

from .danh_muc.sinh_vien import ManHinhSinhVien
from .danh_muc.phong import ManHinhPhong
from .danh_muc.toa_nha import ManHinhToaNha 
from .danh_muc.hop_dong import ManHinhHopDong
from .danh_muc.hoa_don_thang import ManHinhHoaDonThang
from .danh_muc.vi_pham import ManHinhViPham
from .danh_muc.tai_khoan import ManHinhTaiKhoan
from .dung_chung.ho_tro import hien_thi

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
            # CauHinhDong dùng CHU_DE: Enum, không phải 'chu_de' chữ thường.
            chu_de = getattr(cau_hinh, 'CHU_DE', None)
            ten = getattr(chu_de, 'name', 'DEFAULT').upper()
            self.doi_chu_de(ten if ten in ('LIGHT', 'GREY', 'DARK', 'BLUE') else 'LIGHT')
        except Exception:
            pass
        if self.loi_nap_file:
            self.after(100, lambda: messagebox.showwarning(
                "Dữ liệu chưa sẵn sàng", self.loi_nap_file, parent=self))

        # Cuộn bằng chuột ở menu hoặc vùng nội dung (đăng ký đúng một lần).
        self.bind_all("<MouseWheel>", self._xu_ly_cuon_chuot, add="+")
        self.bind_all("<Button-4>", self._xu_ly_cuon_chuot, add="+")
        self.bind_all("<Button-5>", self._xu_ly_cuon_chuot, add="+")

        self.protocol("WM_DELETE_WINDOW", self.xac_nhan_thoat)
        self.hien_thi_dang_nhap()
        # Quy định của giao thức: nạp dữ liệu địa lý ở luồng phụ.
        self.loi_nap_dia_ly = None
        if self.loi_nap_file is None:
            Thread(target=self._nap_dia_ly_ngam, daemon=True).start()

    def _nap_dia_ly_ngam(self):
        try:
            self.adapter.nap_du_lieu_api()
        except Exception as exc:
            # Không truy cập Tkinter từ luồng phụ.
            self.loi_nap_dia_ly = str(exc)

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
        # Không hiển thị màn hình quản lý khi chưa có phiên đăng nhập hợp lệ.
        if self.adapter.tai_khoan_hien_tai is None:
            self.hien_thi_dang_nhap()
            return
        if not (self.adapter.la_admin() or self.adapter.la_sinh_vien()):
            messagebox.showerror('Vai trò không hợp lệ',
                                 'Hệ thống chỉ hỗ trợ Admin và Sinh viên.', parent=self)
            self.hien_thi_dang_nhap()
            return
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
        if self.adapter.la_admin():
            self.hien_thi_chao_mung()
        else:
            self.hien_thi_trang_sinh_vien('Sinh viên')
        self.after_idle(self._cap_nhat_thanh_cuon_trang)

    def tao_menu(self):
        ttk.Label(
            self.menu,
            text="QUẢN LÝ KTX" if self.adapter.la_admin() else "CỔNG SINH VIÊN",
            style="SidebarTitle.TLabel"
        ).pack(fill="x", padx=14, pady=(22, 4))

        vai_tro = (
            "Quản trị viên"
            if self.adapter.la_admin()
            else "Sinh viên"
        )

        ttk.Label(
            self.menu,
            text=vai_tro,
            style="SidebarSubtitle.TLabel"
        ).pack(fill="x", padx=14, pady=(0, 16))

        # Đặt nút cố định phía dưới TRƯỚC vùng cuộn để không bị che mất.
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
        self.canvas_menu = canvas
        scrollbar = ttk.Scrollbar(
            khung_cuon,
            orient="vertical",
            command=canvas.yview,
            style="Sidebar.Vertical.TScrollbar"
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

        if self.adapter.la_admin():
            danh_sach = [
                ("Sinh viên", ManHinhSinhVien),
                ("Phòng", ManHinhPhong),
                ("Tòa nhà", ManHinhToaNha),
                ("Hợp đồng", ManHinhHopDong),
                ("Hóa đơn tháng", ManHinhHoaDonThang),
                ("Vi phạm", ManHinhViPham),
                ("Tài khoản", ManHinhTaiKhoan),
                ("Thống kê", ManHinhThongKe),
                ("Cài đặt", ManHinhCaiDat),
            ]
        else:
            # Cùng bố cục menu như Admin, nhưng từng mục chỉ hiện dữ liệu của mình.
            danh_sach = [
                ("Sinh viên", None),
                ("Phòng", None),
                ("Tòa nhà", None),
                ("Hợp đồng", None),
                ("Hóa đơn tháng", None),
                ("Vi phạm", None),
                ("Cài đặt", ManHinhCaiDat),
            ]

        for ten, lop in danh_sach:
            nut = ttk.Button(
                danh_sach_nut,
                text=ten,
                style="Sidebar.TButton",
                command=lambda t=ten, c=lop: (
                    self.hien_thi_trang_sinh_vien(t) if c is None
                    else self.chuyen_man_hinh(c, t)
                )
            )
            nut.pack(
                fill="x",
                padx=12,
                pady=3
            )
            self.nut_menu[ten] = nut

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

        # Vùng nội dung cuộn chung cho Thống kê, Cài đặt, các danh mục...
        khung_cuon = ttk.Frame(self.khu_vuc_phai)
        khung_cuon.grid(row=1, column=0, sticky="nsew")
        khung_cuon.rowconfigure(0, weight=1)
        khung_cuon.columnconfigure(0, weight=1)

        self.canvas_noi_dung = tk.Canvas(
            khung_cuon,
            bg=lay_mau(self.chu_de_hien_tai)["nen"],
            highlightthickness=0,
            bd=0
        )
        cuon_trang = ttk.Scrollbar(
            khung_cuon,
            orient="vertical",
            command=self.canvas_noi_dung.yview,
            style="Content.Vertical.TScrollbar"
        )
        self.canvas_noi_dung.configure(yscrollcommand=cuon_trang.set)
        self.canvas_noi_dung.grid(row=0, column=0, sticky="nsew")
        cuon_trang.grid(row=0, column=1, sticky="ns")

        # Màn hình con vẫn nhận self.noi_dung như trước, không cần sửa class.
        self.noi_dung = ttk.Frame(self.canvas_noi_dung, padding=16)
        self._id_noi_dung = self.canvas_noi_dung.create_window(
            (0, 0), window=self.noi_dung, anchor="nw"
        )
        self._kich_thuoc_noi_dung = None
        self.canvas_noi_dung.bind(
            "<Configure>", self._cap_nhat_thanh_cuon_trang
        )
        self.noi_dung.bind(
            "<Configure>", self._cap_nhat_thanh_cuon_trang
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

    def _cap_nhat_thanh_cuon_trang(self, event=None):
        """Giữ trang vừa chiều ngang; cuộn dọc nếu nội dung dài."""
        if not hasattr(self, "canvas_noi_dung"):
            return
        canvas = self.canvas_noi_dung
        if not canvas.winfo_exists():
            return

        # Đảm bảo Tkinter đã tính kích thước yêu cầu của màn hình con.
        self.noi_dung.update_idletasks()
        rong = max(canvas.winfo_width(), 1)
        cao = max(canvas.winfo_height(), self.noi_dung.winfo_reqheight())
        kich_thuoc = (rong, cao)
        if self._kich_thuoc_noi_dung != kich_thuoc:
            self._kich_thuoc_noi_dung = kich_thuoc
            canvas.itemconfigure(self._id_noi_dung, width=rong, height=cao)
        canvas.configure(scrollregion=(0, 0, rong, cao))

    @staticmethod
    def _nam_trong(widget, cha):
        while widget is not None:
            if widget is cha:
                return True
            widget = widget.master
        return False

    def _xu_ly_cuon_chuot(self, event):
        """Cuộn menu hoặc trang theo vị trí chuột, không cướp cuộn của bảng."""
        try:
            if event.widget.winfo_toplevel() is not self:
                return  # Không can thiệp Toplevel đổi mật khẩu
        except tk.TclError:
            return

        delta = getattr(event, "delta", 0)
        if delta:
            buoc = -1 if delta > 0 else 1
        else:
            buoc = -1 if getattr(event, "num", 0) == 4 else 1

        if hasattr(self, "canvas_menu") and self.canvas_menu.winfo_exists():
            if self._nam_trong(event.widget, self.menu):
                self.canvas_menu.yview_scroll(buoc * 2, "units")
                return "break"

        if not hasattr(self, "canvas_noi_dung"):
            return
        if not self.canvas_noi_dung.winfo_exists():
            return
        if not self._nam_trong(event.widget, self.khu_vuc_phai):
            return

        # Treeview/Text/Listbox có cơ chế cuộn dữ liệu riêng.
        widget = event.widget
        while widget is not None and widget is not self.khu_vuc_phai:
            if isinstance(widget, (ttk.Treeview, tk.Text, tk.Listbox)):
                dau, cuoi = widget.yview()
                if cuoi - dau < 0.999:
                    return
            if isinstance(widget, tk.Canvas) and widget is not self.canvas_noi_dung:
                dau, cuoi = widget.yview()
                if cuoi - dau < 0.999:
                    widget.yview_scroll(buoc * 2, "units")
                    return "break"
            widget = widget.master

        self.canvas_noi_dung.yview_scroll(buoc * 2, "units")
        return "break"

    def hien_thi_chao_mung(self):
        self.ten_man_hinh.set('Trang chủ')
        dau = ttk.Frame(self.noi_dung, style='KTX.Banner.TFrame', padding=28)
        dau.pack(fill='x', pady=(15, 18))
        ttk.Label(dau, text='Chào mừng đến với ký túc xá!',
                  style='KTX.BannerTitle.TLabel').pack(anchor='w')
        ttk.Label(dau, text='Quản lý gọn gàng, mọi thông tin ở một nơi.',
                  style='KTX.BannerSub.TLabel').pack(anchor='w', pady=(10, 0))
        vai_tro = 'Quản trị viên' if self.adapter.la_admin() else 'Sinh viên'
        thong_tin = ttk.Frame(self.noi_dung, style='KTX.Panel.TFrame', padding=22)
        thong_tin.pack(fill='x')
        ttk.Label(thong_tin, text=f'Bạn đang đăng nhập: {vai_tro}',
                  style='KTX.PanelTitle.TLabel').pack(anchor='w')
        ttk.Label(thong_tin, text='Chọn một mục từ thanh bên trái để bắt đầu làm việc.',
                  style='KTX.PanelText.TLabel').pack(anchor='w', pady=(6, 0))

    def chuyen_man_hinh(self, lop, ten=None):
        if self.adapter.tai_khoan_hien_tai is None:
            self.hien_thi_dang_nhap()
            return
        # Sinh viên chỉ được mở màn hình Cài đặt (ở chế độ chỉ xem thông số).
        # Mọi màn hình CRUD khác vẫn chỉ dành cho Admin.
        if not self.adapter.la_admin() and not (
            self.adapter.la_sinh_vien() and lop is ManHinhCaiDat
        ):
            messagebox.showerror('Không có quyền',
                                 'Bạn không có quyền mở màn hình quản lý.', parent=self)
            return
        for widget in self.noi_dung.winfo_children():
            widget.destroy()

        if ten:
            self.ten_man_hinh.set(ten)

        try:
            if lop is ManHinhCaiDat:
                # Cài đặt cần thêm callback đổi chủ đề.
                man_hinh = ManHinhCaiDat(
                    self.noi_dung,
                    self.adapter,
                    self.doi_chu_de
                )
            else:
                # Các màn hình quản lý chỉ nhận (parent, adapter).
                tao_man_hinh = cast(Callable[[ttk.Frame, Adapter], ttk.Frame], lop)
                man_hinh = tao_man_hinh(self.noi_dung, self.adapter)

            man_hinh.pack(fill="both", expand=True)
            self.canvas_noi_dung.yview_moveto(0)
            self.after_idle(self._cap_nhat_thanh_cuon_trang)

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

    def hien_thi_ca_nhan(self):
        """Tương thích lời gọi cũ: mở mục Sinh viên của tài khoản đang dùng."""
        self.hien_thi_trang_sinh_vien('Sinh viên')

    @staticmethod
    def _gia_tri_ca_nhan(obj, ten):
        return obj.get(ten) if isinstance(obj, dict) else getattr(obj, ten, None)

    def _ten_tinh_xa_ca_nhan(self, sinh_vien):
        """Đổi mã địa lý trong hồ sơ thành tên, không thay đổi dữ liệu đã lưu."""
        ma_tinh = str(self._gia_tri_ca_nhan(sinh_vien, 'tinh') or '').strip()
        ma_xa = str(self._gia_tri_ca_nhan(sinh_vien, 'xa') or '').strip()
        if not ma_tinh:
            return {'tinh': 'Chưa có thông tin', 'xa': 'Chưa có thông tin'}

        try:
            cac_tinh = self.adapter.dia_ly()
            if not isinstance(cac_tinh, dict):
                raise ValueError('Danh mục tỉnh không hợp lệ')
        except Exception:
            # Dữ liệu địa lý được nạp qua API; không tự đoán tên từ mã.
            return {
                'tinh': f'Chưa tải được tên tỉnh (mã {ma_tinh})',
                'xa': f'Chưa tải được tên xã (mã {ma_xa})' if ma_xa else 'Chưa có thông tin',
            }

        tinh = cac_tinh.get(ma_tinh)
        if tinh is None:
            tinh = next(
                (obj for obj in cac_tinh.values()
                 if str(getattr(obj, 'ma', '')) == ma_tinh), None
            )
        if tinh is None:
            return {
                'tinh': f'Không tìm thấy tỉnh (mã {ma_tinh})',
                'xa': f'Không xác định được xã (mã {ma_xa})' if ma_xa else 'Chưa có thông tin',
            }

        cac_xa = getattr(tinh, 'danh_sach_xa', {})
        xa = cac_xa.get(ma_xa) if isinstance(cac_xa, dict) else None
        if xa is None and isinstance(cac_xa, dict):
            xa = next(
                (obj for obj in cac_xa.values()
                 if str(getattr(obj, 'ma', '')) == ma_xa), None
            )
        return {
            'tinh': str(getattr(tinh, 'ten', ma_tinh)),
            'xa': (str(getattr(xa, 'ten', ma_xa)) if xa is not None
                   else f'Không tìm thấy xã (mã {ma_xa})' if ma_xa
                   else 'Chưa có thông tin'),
        }

    def _cap_nhat_mau_ca_nhan(self):
        mau = lay_mau(self.chu_de_hien_tai)
        for bang in getattr(self, '_bang_sinh_vien', []):
            if bang.winfo_exists():
                bang.tag_configure('chan', background=mau['the'], foreground=mau['chu'])
                bang.tag_configure('le', background=mau['nhat'], foreground=mau['chu'])

    def hien_thi_trang_sinh_vien(self, ten):
        """Một mục menu / một trang chỉ xem; không tạo class giao diện mới."""
        cac_muc = ('Sinh viên', 'Phòng', 'Tòa nhà', 'Hợp đồng',
                   'Hóa đơn tháng', 'Vi phạm')
        if not self.adapter.la_sinh_vien() or ten not in cac_muc:
            messagebox.showerror('Không có quyền',
                                 'Chức năng chỉ dành cho tài khoản Sinh viên.', parent=self)
            return
        ma = self.adapter.ma_sinh_vien_hien_tai()
        if not ma:
            messagebox.showerror('Chưa liên kết hồ sơ',
                                 'Tài khoản chưa được liên kết mã sinh viên.', parent=self)
            return
        for widget in self.noi_dung.winfo_children():
            widget.destroy()
        self._bang_sinh_vien = []
        self.ten_man_hinh.set(ten)

        khung = ttk.Frame(self.noi_dung, padding=14)
        khung.pack(fill='both', expand=True)
        dau = ttk.Frame(khung, style='KTX.Banner.TFrame', padding=18)
        dau.pack(fill='x', pady=(0, 14))
        ttk.Label(dau, text=ten.upper(),
                  style='KTX.BannerTitle.TLabel').pack(anchor='w')
        thong_bao = {
            'Sinh viên': 'Thông tin hồ sơ cá nhân của bạn.',
            'Phòng': 'Phòng bạn đang ở theo hợp đồng còn hiệu lực.',
            'Tòa nhà': 'Thông tin tòa nhà của phòng bạn đang ở.',
            'Hợp đồng': 'Thông tin các hợp đồng của bạn.',
            'Hóa đơn tháng': 'Hóa đơn phòng chưa thanh toán trong thời gian hợp đồng của bạn.',
            'Vi phạm': 'Các vi phạm của bạn chưa được xử lý.',
        }
        ttk.Label(dau, text=thong_bao[ten],
                  style='KTX.BannerSub.TLabel').pack(anchor='w', pady=(7, 0))
        ttk.Button(khung, text='Làm mới',
                   command=lambda: self.hien_thi_trang_sinh_vien(ten)).pack(
                       anchor='e', pady=(0, 10))
        try:
            du_lieu = self.adapter.lay_du_lieu_ca_nhan()
        except Exception as exc:
            messagebox.showerror('Lỗi tải thông tin', str(exc), parent=self)
            return

        if ten == 'Sinh viên':
            sv = du_lieu.get('sinh_vien')
            if sv is None:
                ttk.Label(khung, text='Chưa tìm thấy hồ sơ sinh viên gắn với tài khoản.').pack(anchor='w')
            else:
                thong_tin = ttk.LabelFrame(khung, text='  Hồ sơ của tôi  ', padding=16)
                thong_tin.pack(fill='x')
                cac_truong = (
                    ('Mã sinh viên', 'ma'), ('Họ tên', 'ten'),
                    ('Số điện thoại', 'sdt'), ('Năm sinh', 'nam_sinh'),
                    ('CCCD', 'cccd'), ('Địa chỉ', 'dia_chi_chi_tiet'),
                    ('Tỉnh', 'tinh'), ('Xã', 'xa')
                )
                ten_dia_ly = self._ten_tinh_xa_ca_nhan(sv)
                for i, (nhan, truong) in enumerate(cac_truong):
                    ttk.Label(thong_tin, text=nhan + ':',
                              font=('Segoe UI', 10, 'bold')).grid(
                                  row=i, column=0, sticky='nw', padx=(0, 18), pady=6)
                    gia_tri = (ten_dia_ly[truong] if truong in ten_dia_ly
                               else hien_thi(self._gia_tri_ca_nhan(sv, truong)))
                    ttk.Label(thong_tin,
                              text=gia_tri, wraplength=650).grid(
                                  row=i, column=1, sticky='w', pady=6)
        else:
            cau_hinh_bang = {
                'Phòng': ('phong', (
                    ('ma', 'Mã phòng'), ('ten', 'Tên phòng'),
                    ('toa_nha', 'Mã tòa nhà'), ('tang', 'Tầng'),
                    ('suc_chua', 'Sức chứa'), ('gia_phong', 'Giá phòng'))),
                'Tòa nhà': ('toa_nha', (
                    ('ma', 'Mã tòa nhà'), ('ten', 'Tên tòa nhà'),
                    ('so_tang', 'Số tầng'))),
                'Hợp đồng': ('hop_dong', (
                    ('ma', 'Mã hợp đồng'), ('ma_phong', 'Mã phòng'),
                    ('ngay_ky', 'Ngày ký'), ('ngay_bat_dau', 'Ngày bắt đầu'),
                    ('ngay_ket_thuc', 'Ngày kết thúc'),
                    ('trang_thai', 'Trạng thái'))),
                'Hóa đơn tháng': ('hoa_don', (
                    ('ma', 'Mã hóa đơn'), ('thang_nam', 'Tháng/năm'),
                    ('phong', 'Phòng'), ('han_chot', 'Hạn chót'),
                    ('dien_cu', 'Điện cũ'), ('dien_moi', 'Điện mới'),
                    ('nuoc_cu', 'Nước cũ'), ('nuoc_moi', 'Nước mới'),
                    ('trang_thai', 'Trạng thái'))),
                'Vi phạm': ('vi_pham', (
                    ('ma', 'Mã vi phạm'), ('ngay_vi_pham', 'Ngày vi phạm'),
                    ('mo_ta', 'Mô tả'), ('hinh_thuc_ky_luat', 'Kỷ luật'),
                    ('trang_thai', 'Trạng thái'))),
            }
            khoa, cot = cau_hinh_bang[ten]
            ds = du_lieu.get(khoa, [])
            if not ds:
                ttk.Label(khung, text='Không có dữ liệu phù hợp.',
                          style='KTX.Muted.TLabel').pack(anchor='w', pady=10)
            else:
                vung = ttk.Frame(khung)
                vung.pack(fill='both', expand=True)
                vung.columnconfigure(0, weight=1)
                vung.rowconfigure(0, weight=1)
                truong = tuple(t for t, _ in cot)
                bang = ttk.Treeview(vung, columns=truong, show='headings',
                                    height=12, style='KTX.Treeview', selectmode='browse')
                for t, nhan in cot:
                    bang.heading(t, text=nhan)
                    bang.column(t, width=165, minwidth=105, anchor='w')
                doc = ttk.Scrollbar(vung, orient='vertical', command=bang.yview)
                ngang = ttk.Scrollbar(vung, orient='horizontal', command=bang.xview)
                bang.configure(yscrollcommand=doc.set, xscrollcommand=ngang.set)
                bang.grid(row=0, column=0, sticky='nsew')
                doc.grid(row=0, column=1, sticky='ns')
                ngang.grid(row=1, column=0, sticky='ew')
                self._bang_sinh_vien.append(bang)
                for i, obj in enumerate(ds):
                    bang.insert('', 'end',
                                values=tuple(hien_thi(self._gia_tri_ca_nhan(obj, t))
                                             for t in truong),
                                tags=('chan' if i % 2 == 0 else 'le',))
                self._cap_nhat_mau_ca_nhan()
        for ten_nut, nut in self.nut_menu.items():
            nut.configure(style='SelectedSidebar.TButton' if ten_nut == ten
                          else 'Sidebar.TButton')
        self.canvas_noi_dung.yview_moveto(0)
        self.after_idle(self._cap_nhat_thanh_cuon_trang)

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

        # Hai thanh cuộn hiển thị rõ trên LIGHT/GREY/DARK/BLUE.
        st.configure('Sidebar.Vertical.TScrollbar',
                     background=mau['chinh'], troughcolor=mau['menu'],
                     arrowcolor=mau['chu'])
        st.configure('Content.Vertical.TScrollbar',
                     background=mau['chinh'], troughcolor=mau['nhat'],
                     arrowcolor=mau['chu'])

        if hasattr(self, 'canvas_noi_dung') and self.canvas_noi_dung.winfo_exists():
            self.canvas_noi_dung.configure(bg=mau['nen'])

        # Canvas menu là widget tk, nên cập nhật màu riêng.
        if hasattr(self, 'menu') and self.menu.winfo_exists():
            for widget in self.menu.winfo_children():
                for con in widget.winfo_children():
                    if isinstance(con, tk.Canvas):
                        con.configure(bg=mau['menu'])

        # Các widget tk.Canvas hoặc tk.Frame màu riêng cập nhật qua hook đơn giản.
        if hasattr(self, '_bang_sinh_vien'):
            self._cap_nhat_mau_ca_nhan()
        if hasattr(self, 'noi_dung') and self.noi_dung.winfo_exists():
            for man_hinh in self.noi_dung.winfo_children():
                ham = getattr(man_hinh, 'cap_nhat_mau', None)
                if callable(ham):
                    ham()

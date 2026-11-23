import tkinter as tk
from tkinter import ttk, messagebox


class ManHinhDangNhap(ttk.Frame):
    """Màn hình đăng nhập hai cột, dùng Tkinter thuần."""

    MAU_NEN = "#F0F4F9"
    MAU_XANH_DAM = "#16324B"
    MAU_CHU = "#20364B"
    MAU_PHU = "#68798C"
    MAU_NHAN = "#0F877A"
    MAU_VIEN = "#D9E2EB"

    def __init__(self, parent, app, on_success):
        super().__init__(parent)
        self.app = app
        self.on_success = on_success
        self.tao_giao_dien()

    def tao_giao_dien(self):
        self.columnconfigure(0, weight=4, minsize=310)
        self.columnconfigure(1, weight=6, minsize=500)
        self.rowconfigure(0, weight=1)

        # Nửa trái: giới thiệu hệ thống và hình trang trí đơn giản.
        self.ben_trai = tk.Canvas(
            self, bg=self.MAU_XANH_DAM,
            highlightthickness=0, bd=0
        )
        self.ben_trai.grid(row=0, column=0, sticky="nsew")
        self.ben_trai.bind("<Configure>", self.ve_trang_tri)

        # Nửa phải: form đăng nhập.
        ben_phai = tk.Frame(self, bg=self.MAU_NEN)
        ben_phai.grid(row=0, column=1, sticky="nsew")

        khung = tk.Frame(
            ben_phai,
            bg="white",
            padx=34, pady=30,
            highlightbackground=self.MAU_VIEN,
            highlightthickness=1
        )
        khung.place(relx=0.5, rely=0.49, anchor="center")

        tk.Label(
            khung, text="CỔNG QUẢN LÝ NỘI TRÚ",
            bg="white", fg=self.MAU_NHAN,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        tk.Label(
            khung, text="Chào mừng trở lại",
            bg="white", fg=self.MAU_CHU,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", pady=(9, 3))

        tk.Label(
            khung, text="Đăng nhập để tiếp tục quản lý ký túc xá.",
            bg="white", fg=self.MAU_PHU,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 22))

        tk.Label(
            khung, text="Tài khoản",
            bg="white", fg=self.MAU_CHU,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.txt_tk = tk.Entry(
            khung, width=34,
            font=("Segoe UI", 12),
            bg="#F8FAFC", fg=self.MAU_CHU,
            insertbackground=self.MAU_CHU,
            relief="flat", highlightthickness=1,
            highlightbackground=self.MAU_VIEN,
            highlightcolor=self.MAU_NHAN
        )
        self.txt_tk.pack(fill="x", ipady=9, pady=(6, 16))

        tk.Label(
            khung, text="Mật khẩu",
            bg="white", fg=self.MAU_CHU,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        khung_mat_khau = tk.Frame(
            khung, bg="#F8FAFC",
            highlightbackground=self.MAU_VIEN,
            highlightthickness=1
        )
        khung_mat_khau.pack(fill="x", pady=(6, 19))

        self.txt_mk = tk.Entry(
            khung_mat_khau, show="*",
            font=("Segoe UI", 12),
            bg="#F8FAFC", fg=self.MAU_CHU,
            insertbackground=self.MAU_CHU,
            relief="flat", bd=0
        )
        self.txt_mk.pack(side="left", fill="x", expand=True,
                         padx=(11, 3), ipady=9)

        self.nut_hien = tk.Button(
            khung_mat_khau, text="Hiện",
            command=self.hien_mat_khau,
            bg="#F8FAFC", fg=self.MAU_NHAN,
            activebackground="#F8FAFC",
            activeforeground=self.MAU_NHAN,
            font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0,
            cursor="hand2", padx=9
        )
        self.nut_hien.pack(side="right", padx=4)

        tk.Button(
            khung, text="ĐĂNG NHẬP",
            command=self.dang_nhap,
            bg=self.MAU_NHAN, fg="white",
            activebackground="#0A665D",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat", bd=0,
            cursor="hand2", pady=12
        ).pack(fill="x")

        tk.Label(
            khung,
            text="Sử dụng tài khoản được quản trị viên cấp.",
            bg="white", fg=self.MAU_PHU,
            font=("Segoe UI", 9)
        ).pack(pady=(17, 0))

        tk.Label(
            ben_phai, text="Hệ thống quản lý ký túc xá",
            bg=self.MAU_NEN, fg=self.MAU_PHU,
            font=("Segoe UI", 9)
        ).place(relx=0.5, rely=0.96, anchor="center")

        self.txt_tk.bind("<Return>", lambda event: self.txt_mk.focus_set())
        self.txt_mk.bind("<Return>", lambda event: self.dang_nhap())
        self.after_idle(self.txt_tk.focus_set)

    def ve_trang_tri(self, event):
        """Vẽ vài hình trang trí, tự điều chỉnh khi đổi kích thước."""
        w, h = event.width, event.height
        c = self.ben_trai
        c.delete("all")
        c.create_oval(w - 155, -105, w + 105, 155,
                      outline="#2B526A", width=3)
        c.create_oval(-120, h - 190, 180, h + 110,
                      outline="#2B526A", width=3)
        c.create_oval(w - 88, h - 115, w + 55, h + 28,
                      fill="#1B4960", outline="")

        c.create_rectangle(37, 43, 81, 87,
                           fill="#18B99D", outline="")
        c.create_text(59, 65, text="K", fill="white",
                      font=("Segoe UI", 19, "bold"))
        c.create_text(94, 65, anchor="w", text="KTX  /  QUẢN LÝ",
                      fill="#DCECF3", font=("Segoe UI", 11, "bold"))

        c.create_text(
            38, int(h * 0.40), anchor="w",
            text="QUẢN LÝ\nKÝ TÚC XÁ",
            fill="white", font=("Segoe UI", 26, "bold")
        )
        c.create_text(
            40, int(h * 0.40) + 97, anchor="nw",
            text="Sinh viên  •  Phòng  •  Hợp đồng",
            fill="#BDD4E1", font=("Segoe UI", 11)
        )
        c.create_line(40, h - 82, min(w - 40, 215), h - 82,
                      fill="#18B99D", width=3)
        c.create_text(
            40, h - 62, anchor="nw",
            text="Đơn giản hơn mỗi ngày.",
            fill="#DCECF3", font=("Segoe UI", 11)
        )

    def hien_mat_khau(self):
        if self.txt_mk.cget("show") == "*":
            self.txt_mk.configure(show="")
            self.nut_hien.configure(text="Ẩn")
        else:
            self.txt_mk.configure(show="*")
            self.nut_hien.configure(text="Hiện")

    def dang_nhap(self):
        tai_khoan = self.txt_tk.get().strip()
        mat_khau = self.txt_mk.get()

        if not tai_khoan or not mat_khau:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập tài khoản và mật khẩu.",
                parent=self
            )
            return

        try:
            # Adapter mới trả về None khi thành công, báo lỗi bằng exception.
            self.app.phien.dang_nhap(tai_khoan, mat_khau)
        except Exception as e:
            messagebox.showerror(
                "Đăng nhập thất bại", str(e), parent=self
            )
            return

        self.on_success()

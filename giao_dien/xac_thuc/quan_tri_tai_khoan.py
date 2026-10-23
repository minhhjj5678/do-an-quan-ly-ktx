import tkinter as tk
from tkinter import ttk, messagebox


class ManHinhQuanTriTaiKhoan(ttk.Frame):
    def __init__(self, parent, adapter):
        super().__init__(parent, padding=20)

        self.adapter = adapter
        self.tao_giao_dien()

    def tao_giao_dien(self):
        if not self.adapter.la_admin():
            ttk.Label(
                self,
                text="Bạn không có quyền quản trị tài khoản."
            ).pack(pady=30)
            return

        ttk.Label(
            self,
            text="QUẢN TRỊ TÀI KHOẢN",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=15)

        khung_tao = ttk.LabelFrame(
            self, text="Tạo tài khoản mới", padding=15
        )
        khung_tao.pack(fill="x", pady=10)

        ttk.Label(
            khung_tao, text="Tên tài khoản"
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.txt_tai_khoan = ttk.Entry(
            khung_tao, width=35
        )
        self.txt_tai_khoan.grid(
            row=0, column=1, padx=10, pady=5
        )

        ttk.Label(
            khung_tao, text="Mật khẩu"
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.txt_mat_khau = ttk.Entry(
            khung_tao, width=35, show="*"
        )
        self.txt_mat_khau.grid(
            row=1, column=1, padx=10, pady=5
        )

        self.la_admin = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            khung_tao,
            text="Cấp quyền quản trị viên",
            variable=self.la_admin
        ).grid(row=2, column=1, sticky="w", pady=5)

        ttk.Button(
            khung_tao,
            text="Tạo tài khoản",
            command=self.tao_tai_khoan
        ).grid(row=3, column=1, sticky="e", pady=10)

        khung_reset = ttk.LabelFrame(
            self, text="Reset mật khẩu", padding=15
        )
        khung_reset.pack(fill="x", pady=10)

        ttk.Label(
            khung_reset, text="Tài khoản cần reset"
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.txt_reset_tk = ttk.Entry(
            khung_reset, width=35
        )
        self.txt_reset_tk.grid(
            row=0, column=1, padx=10, pady=5
        )

        ttk.Label(
            khung_reset, text="Mật khẩu mới"
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.txt_reset_mk = ttk.Entry(
            khung_reset, width=35, show="*"
        )
        self.txt_reset_mk.grid(
            row=1, column=1, padx=10, pady=5
        )

        ttk.Button(
            khung_reset,
            text="Reset mật khẩu",
            command=self.reset_mat_khau
        ).grid(row=2, column=1, sticky="e", pady=10)

    def tao_tai_khoan(self):
        if not self.adapter.la_admin():
            messagebox.showerror(
                "Từ chối", "Không có quyền quản trị"
            )
            return

        tai_khoan = self.txt_tai_khoan.get().strip()
        mat_khau = self.txt_mat_khau.get()

        if not tai_khoan or not mat_khau.strip():
            messagebox.showwarning(
                "Thiếu dữ liệu",
                "Vui lòng nhập đầy đủ thông tin"
            )
            return

        try:
            ket_qua = self.adapter.tao_tai_khoan(
                tai_khoan,
                mat_khau,
                self.la_admin.get()
            )

            if ket_qua is False:
                raise ValueError("Tạo tài khoản thất bại")

            messagebox.showinfo(
                "Thành công", "Đã tạo tài khoản"
            )

            self.txt_tai_khoan.delete(0, tk.END)
            self.txt_mat_khau.delete(0, tk.END)
            self.la_admin.set(False)

        except Exception as e:
            messagebox.showerror(
                "Lỗi tạo tài khoản", str(e)
            )

    def reset_mat_khau(self):
        if not self.adapter.la_admin():
            messagebox.showerror(
                "Từ chối", "Không có quyền quản trị"
            )
            return

        tai_khoan = self.txt_reset_tk.get().strip()
        mat_khau_moi = self.txt_reset_mk.get()

        if not tai_khoan or not mat_khau_moi.strip():
            messagebox.showwarning(
                "Thiếu dữ liệu",
                "Vui lòng nhập đầy đủ thông tin"
            )
            return

        if not messagebox.askyesno(
            "Xác nhận",
            f"Bạn chắc chắn muốn reset mật khẩu của {tai_khoan}?"
        ):
            return

        try:
            ket_qua = self.adapter.doi_mat_khau(
                mat_khau_moi=mat_khau_moi,
                tai_khoan=tai_khoan
            )

            if ket_qua is False:
                raise ValueError("Reset mật khẩu thất bại")

            messagebox.showinfo(
                "Thành công",
                "Reset mật khẩu thành công"
            )

            self.txt_reset_tk.delete(0, tk.END)
            self.txt_reset_mk.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror(
                "Lỗi reset mật khẩu", str(e)
            )
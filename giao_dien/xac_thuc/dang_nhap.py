from tkinter import ttk, messagebox


class ManHinhDangNhap(ttk.Frame):
    def __init__(self, parent, adapter, on_success):
        super().__init__(parent, padding=30)
        self.adapter = adapter
        self.on_success = on_success
        self.tao_giao_dien()

    def tao_giao_dien(self):
        khung = ttk.Frame(self, padding=25)
        khung.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            khung,
            text="QUẢN LÝ KÝ TÚC XÁ",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        ttk.Label(khung, text="Tài khoản").pack(anchor="w")
        self.txt_tk = ttk.Entry(khung, width=36)
        self.txt_tk.pack(pady=7)

        ttk.Label(khung, text="Mật khẩu").pack(anchor="w")
        self.txt_mk = ttk.Entry(khung, width=36, show="*")
        self.txt_mk.pack(pady=7)

        ttk.Button(
            khung, text="Đăng nhập",
            command=self.dang_nhap
        ).pack(fill="x", pady=15)

        self.txt_mk.bind(
            "<Return>", lambda event: self.dang_nhap()
        )

    def dang_nhap(self):
        tk = self.txt_tk.get().strip()
        mk = self.txt_mk.get()

        if not tk or not mk:
            messagebox.showwarning(
                "Thiếu dữ liệu",
                "Nhập đầy đủ tài khoản và mật khẩu"
            )
            return

        try:
            ket_qua = self.adapter.dang_nhap(tk, mk)

            if ket_qua is False:
                raise ValueError("Đăng nhập thất bại")

            self.on_success()

        except Exception as e:
            messagebox.showerror(
                "Đăng nhập thất bại", str(e)
            )
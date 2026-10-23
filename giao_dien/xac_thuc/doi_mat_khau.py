import tkinter as tk
from tkinter import ttk, messagebox


class ManHinhDoiMatKhau(tk.Toplevel):
    def __init__(self, parent, adapter):
        super().__init__(parent)

        self.adapter = adapter

        self.title("Đổi mật khẩu")
        self.geometry("420x330")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.tao_giao_dien()

    def tao_giao_dien(self):
        khung = ttk.Frame(self, padding=20)
        khung.pack(fill="both", expand=True)

        ttk.Label(
            khung,
            text="ĐỔI MẬT KHẨU",
            font=("Arial", 17, "bold")
        ).pack(pady=12)

        ttk.Label(
            khung, text="Mật khẩu hiện tại"
        ).pack(anchor="w")

        self.txt_cu = ttk.Entry(khung, show="*")
        self.txt_cu.pack(fill="x", pady=6)

        ttk.Label(
            khung, text="Mật khẩu mới"
        ).pack(anchor="w")

        self.txt_moi = ttk.Entry(khung, show="*")
        self.txt_moi.pack(fill="x", pady=6)

        ttk.Label(
            khung, text="Xác nhận mật khẩu mới"
        ).pack(anchor="w")

        self.txt_xac_nhan = ttk.Entry(khung, show="*")
        self.txt_xac_nhan.pack(fill="x", pady=6)

        ttk.Button(
            khung,
            text="Xác nhận đổi mật khẩu",
            command=self.doi_mat_khau
        ).pack(fill="x", pady=15)

    def doi_mat_khau(self):
        mat_khau_cu = self.txt_cu.get()
        mat_khau_moi = self.txt_moi.get()
        xac_nhan = self.txt_xac_nhan.get()

        if not mat_khau_cu or not mat_khau_moi:
            messagebox.showwarning(
                "Thiếu dữ liệu",
                "Vui lòng nhập đầy đủ mật khẩu",
                parent=self
            )
            return

        if mat_khau_moi != xac_nhan:
            messagebox.showwarning(
                "Lỗi",
                "Mật khẩu xác nhận không khớp",
                parent=self
            )
            return

        try:
            ket_qua = self.adapter.doi_mat_khau(
                mat_khau_cu=mat_khau_cu,
                mat_khau_moi=mat_khau_moi
            )

            if ket_qua is False:
                raise ValueError("Đổi mật khẩu thất bại")

            messagebox.showinfo(
                "Thành công",
                "Đổi mật khẩu thành công!",
                parent=self
            )
            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Lỗi đổi mật khẩu",
                str(e),
                parent=self
            )
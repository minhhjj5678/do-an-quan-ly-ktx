import tkinter as tk
from tkinter import messagebox

from thuc_the.tai_khoan import TaiKhoan

from .danh_muc_co_so import ManHinhDanhMucCoSo
from ..xac_thuc.quan_tri_tai_khoan import ManHinhQuanTriTaiKhoan


class ManHinhTaiKhoan(ManHinhDanhMucCoSo):
    LOAI = TaiKhoan

    TRUONG = [
        "tai_khoan",
        "vai_tro",
        "trang_thai"
    ]

    BAT_BUOC = ["tai_khoan"]

    def them_moi(self):
        if not self.adapter.la_admin():
            messagebox.showerror(
                "Từ chối",
                "Bạn không có quyền tạo tài khoản"
            )
            return

        cua_so = tk.Toplevel(self)
        cua_so.title("Quản trị tài khoản")
        cua_so.geometry("650x600")

        man_hinh = ManHinhQuanTriTaiKhoan(
            cua_so,
            self.adapter
        )
        man_hinh.pack(fill="both", expand=True)

        cua_so.transient(self.winfo_toplevel())
        cua_so.grab_set()

        self.wait_window(cua_so)
        self.tai_du_lieu()
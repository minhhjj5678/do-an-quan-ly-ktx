"""Đổi mật khẩu: không cắt chữ nút, nội dung có thanh cuộn."""
import tkinter as tk
from tkinter import ttk, messagebox


class ManHinhDoiMatKhau(tk.Toplevel):
    def __init__(self, parent, adapter):
        super().__init__(parent)
        self.adapter = adapter
        self.title("Đổi mật khẩu")
        self.geometry("560x610")
        self.minsize(440, 410)
        self.resizable(True, True)
        self.configure(bg="#F5F8F6")
        self.transient(parent.winfo_toplevel())
        self.hien_mk = tk.BooleanVar(master=self, value=False)
        self.tao_giao_dien()
        self.grab_set()
        self.txt_cu.focus_set()

    def tao_giao_dien(self):
        dau = tk.Frame(self, bg="#207D6D", padx=28, pady=21)
        dau.pack(side="top", fill="x")
        tk.Label(dau, text="Đổi mật khẩu", bg="#207D6D", fg="white",
                 anchor="w", font=("Segoe UI", 20, "bold")).pack(fill="x")
        tk.Label(dau, text="Giữ tài khoản của bạn luôn an toàn",
                 bg="#207D6D", fg="#E3F5EF", anchor="w",
                 font=("Segoe UI", 10)).pack(fill="x", pady=(6, 0))

        # Nút nằm CỐ ĐỊNH ở cuối cửa sổ; dùng tk.Button tránh chữ bị cắt
        cuoi = tk.Frame(self, bg="#F5F8F6", padx=28, pady=14)
        cuoi.pack(side="bottom", fill="x")
        tk.Button(cuoi, text="Hủy", command=self.destroy,
                  font=("Segoe UI", 11), bg="#E3EAE6", fg="#26433B",
                  activebackground="#D4DFDA", relief="flat",
                  height=2, width=12, cursor="hand2").pack(side="left")
        tk.Button(cuoi, text="Lưu mật khẩu mới", command=self.doi_mat_khau,
                  font=("Segoe UI", 11, "bold"), bg="#207D6D", fg="white",
                  activebackground="#176657", activeforeground="white",
                  relief="flat", height=2, width=19,
                  cursor="hand2").pack(side="right")

        # Vùng nhập có thanh cuộn, nên thu nhỏ cửa sổ không bị che ô nhập
        vung = tk.Frame(self, bg="#F5F8F6")
        vung.pack(fill="both", expand=True)
        canvas = tk.Canvas(vung, bg="#F5F8F6", bd=0, highlightthickness=0)
        cuon = ttk.Scrollbar(vung, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=cuon.set)
        canvas.pack(side="left", fill="both", expand=True)
        cuon.pack(side="right", fill="y")

        form = tk.Frame(canvas, bg="#F5F8F6", padx=28, pady=22)
        id_form = canvas.create_window((0, 0), window=form, anchor="nw")
        form.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(
            id_form, width=e.width))

        self.txt_cu = self.tao_o_mat_khau(form, "Mật khẩu hiện tại")
        self.txt_moi = self.tao_o_mat_khau(form, "Mật khẩu mới")
        self.txt_xac_nhan = self.tao_o_mat_khau(form, "Nhập lại mật khẩu mới")
        tk.Checkbutton(form, text="Hiển thị mật khẩu",
                       variable=self.hien_mk, command=self.hien_mat_khau,
                       bg="#F5F8F6", fg="#36554B",
                       activebackground="#F5F8F6", font=("Segoe UI", 10)
                       ).pack(anchor="w", pady=(0, 12))

        # Cuộn khi đặt chuột trên cả ô nhập và nhãn
        def cuon_chuot(e):
            buoc = (-1 if e.delta > 0 else 1) if getattr(e, "delta", 0) else (
                -1 if getattr(e, "num", 0) == 4 else 1)
            canvas.yview_scroll(buoc, "units")
            return "break"

        for w in [canvas, form, *form.winfo_children()]:
            w.bind("<MouseWheel>", cuon_chuot)
            w.bind("<Button-4>", cuon_chuot)
            w.bind("<Button-5>", cuon_chuot)

        self.txt_cu.bind("<Return>", lambda e: self.txt_moi.focus_set())
        self.txt_moi.bind("<Return>", lambda e: self.txt_xac_nhan.focus_set())
        self.txt_xac_nhan.bind("<Return>", lambda e: self.doi_mat_khau())

    @staticmethod
    def tao_o_mat_khau(parent, nhan):
        tk.Label(parent, text=nhan, bg="#F5F8F6", fg="#29463D",
                 anchor="w", font=("Segoe UI", 11)).pack(fill="x", pady=(0, 5))
        entry = ttk.Entry(parent, show="*", font=("Segoe UI", 11))
        entry.pack(fill="x", ipady=6, pady=(0, 18))
        return entry

    def hien_mat_khau(self):
        che = "" if self.hien_mk.get() else "*"
        for entry in (self.txt_cu, self.txt_moi, self.txt_xac_nhan):
            entry.configure(show=che)

    def doi_mat_khau(self):
        cu = self.txt_cu.get()
        moi = self.txt_moi.get()
        xac_nhan = self.txt_xac_nhan.get()
        if not cu or not moi or not xac_nhan:
            messagebox.showwarning("Thiếu thông tin", "Nhập đầy đủ ba ô mật khẩu.", parent=self)
            return
        if moi != xac_nhan:
            messagebox.showwarning("Mật khẩu không khớp",
                                   "Mật khẩu xác nhận chưa trùng.", parent=self)
            return
        try:
            self.adapter.doi_mat_khau(mat_khau_moi=moi, mat_khau_cu=cu)
            messagebox.showinfo("Thành công", "Đã đổi mật khẩu.", parent=self)
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Không thể đổi mật khẩu", str(exc), parent=self)

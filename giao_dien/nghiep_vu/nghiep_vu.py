from tkinter import ttk, messagebox


class ManHinhNghiepVu(ttk.Frame):
    DANH_SACH = [
        ("Thanh toán hợp đồng", "thanh_toan_hop_dong"),
        ("Kết thúc hợp đồng", "ket_thuc_hop_dong"),
        ("Thanh toán hóa đơn", "thanh_toan_hoa_don_thang"),
        ("Xử lý vi phạm", "xu_ly_vi_pham")
    ]

    def __init__(self, parent, adapter):
        super().__init__(parent, padding=20)
        self.adapter = adapter
        self.tao_giao_dien()

    def tao_giao_dien(self):
        ttk.Label(
            self, text="THAO TÁC NGHIỆP VỤ",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=15)

        for tieu_de, ten_ham in self.DANH_SACH:
            khung = ttk.LabelFrame(
                self, text=tieu_de, padding=12
            )
            khung.pack(fill="x", pady=8)

            ttk.Label(
                khung, text="Mã đối tượng"
            ).pack(side="left", padx=8)

            entry = ttk.Entry(khung, width=28)
            entry.pack(side="left", padx=8)

            ttk.Button(
                khung,
                text="Thực hiện",
                command=lambda h=ten_ham, e=entry, t=tieu_de:
                    self.thuc_hien(h, e.get(), t)
            ).pack(side="left", padx=8)

    def thuc_hien(self, ten_ham, ma, tieu_de):
        ma = ma.strip()

        if not ma:
            messagebox.showwarning(
                "Thiếu dữ liệu", "Vui lòng nhập mã"
            )
            return

        if not messagebox.askyesno(
            "Xác nhận",
            f"Thực hiện {tieu_de} cho mã {ma}?"
        ):
            return

        try:
            ket_qua = self.adapter.nghiep_vu(
                ten_ham, ma
            )

            if ket_qua is False:
                raise ValueError("Nghiệp vụ không thành công")

            messagebox.showinfo(
                "Thành công", f"Đã thực hiện {tieu_de}"
            )

        except Exception as e:
            messagebox.showerror(
                "Lỗi nghiệp vụ", str(e)
            )
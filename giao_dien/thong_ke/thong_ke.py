import tkinter as tk
from tkinter import ttk, messagebox


class ManHinhThongKe(ttk.Frame):
    THONG_KE = [
        ("Số phòng", "thong_ke_so_phong"),
        ("Tỷ lệ lấp đầy", "thong_ke_ty_le_lap_day"),
        ("Công nợ", "thong_ke_cong_no")
    ]

    def __init__(self, parent, adapter):
        super().__init__(parent, padding=20)
        self.adapter = adapter
        self.tao_giao_dien()

    def tao_giao_dien(self):
        ttk.Label(
            self, text="THỐNG KÊ KÝ TÚC XÁ",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=15)

        khung = ttk.LabelFrame(
            self, text="Bộ lọc", padding=12
        )
        khung.pack(fill="x", pady=10)

        self.o_loc = {}

        for truong in ("hoc_ky", "toa_nha", "loai_phong"):
            ttk.Label(
                khung, text=truong.replace("_", " ").title()
            ).pack(side="left", padx=5)

            entry = ttk.Entry(khung, width=16)
            entry.pack(side="left", padx=5)
            self.o_loc[truong] = entry

        thanh = ttk.Frame(self)
        thanh.pack(fill="x", pady=10)

        for ten, ham in self.THONG_KE:
            ttk.Button(
                thanh, text=ten,
                command=lambda h=ham: self.xem(h)
            ).pack(side="left", padx=6)

        self.ket_qua = tk.Text(
            self, height=18, font=("Consolas", 12),
            state="disabled"
        )
        self.ket_qua.pack(fill="both", expand=True)

    def xem(self, ten_ham):
        bo_loc = {
            ten: entry.get().strip()
            for ten, entry in self.o_loc.items()
            if entry.get().strip()
        }

        try:
            data = self.adapter.thong_ke(
                ten_ham, bo_loc
            )

            self.ket_qua.configure(state="normal")
            self.ket_qua.delete("1.0", tk.END)

            self.ket_qua.insert(
                tk.END, f"{ten_ham.upper()}\n\n"
            )

            if isinstance(data, dict):
                for k, v in data.items():
                    self.ket_qua.insert(
                        tk.END, f"{k}: {v}\n"
                    )
            else:
                self.ket_qua.insert(tk.END, str(data))

            self.ket_qua.configure(state="disabled")

        except Exception as e:
            messagebox.showerror(
                "Lỗi thống kê", str(e)
            )
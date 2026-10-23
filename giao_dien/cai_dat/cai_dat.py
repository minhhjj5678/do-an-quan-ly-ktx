from tkinter import ttk, messagebox

from ..dung_chung.ho_tro import (
    hien_thi,
    thanh_dict,
    kiem_tra,
    chuyen_kieu
)


class ManHinhCaiDat(ttk.Frame):
    TRUONG = [
        "don_gia_dien",
        "don_gia_nuoc",
        "suc_chua_mac_dinh",
        "han_muc_no"
    ]

    def __init__(self, parent, adapter, doi_chu_de):
        super().__init__(parent, padding=20)
        self.adapter = adapter
        self.doi_chu_de = doi_chu_de
        self.tao_giao_dien()
        self.tai_cau_hinh()

    def tao_giao_dien(self):
        ttk.Label(
            self, text="CÀI ĐẶT HỆ THỐNG",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=15)

        ttk.Label(
            self, text="Chủ đề giao diện"
        ).pack(anchor="w")

        self.cbo_chu_de = ttk.Combobox(
            self,
            values=["DARK", "GREY", "LIGHT"],
            state="readonly",
            width=35
        )
        self.cbo_chu_de.pack(anchor="w", pady=8)

        self.o_nhap = {}

        for truong in self.TRUONG:
            ttk.Label(
                self,
                text=truong.replace("_", " ").title()
            ).pack(anchor="w", pady=(10, 2))

            entry = ttk.Entry(self, width=38)
            entry.pack(anchor="w")
            self.o_nhap[truong] = entry

        ttk.Button(
            self, text="Lưu cấu hình",
            command=self.luu
        ).pack(anchor="w", pady=20)

    def tai_cau_hinh(self):
        try:
            data = thanh_dict(
                self.adapter.doc_cau_hinh()
            )

            self.cbo_chu_de.set(
                str(data.get("chu_de", "LIGHT"))
            )

            for truong, entry in self.o_nhap.items():
                entry.delete(0, "end")
                entry.insert(
                    0, str(data.get(truong, ""))
                )
        except Exception as e:
            messagebox.showerror(
                "Lỗi đọc cấu hình", str(e)
            )

    def luu(self):
        data = {
            truong: entry.get().strip()
            for truong, entry in self.o_nhap.items()
        }

        for truong, gia_tri in data.items():
            loi = kiem_tra(truong, gia_tri)
            if loi:
                messagebox.showwarning(
                    "Dữ liệu không hợp lệ", loi
                )
                return

        if not self.cbo_chu_de.get():
            messagebox.showwarning(
                "Lỗi", "Chưa chọn chủ đề"
            )
            return

        try:
            data = {
                k: chuyen_kieu(k, v)
                for k, v in data.items()
            }
            data["chu_de"] = self.cbo_chu_de.get()

            ket_qua = self.adapter.cap_nhat_cau_hinh(
                data
            )
            if ket_qua is False:
                raise ValueError("Không thể lưu cấu hình")

            self.doi_chu_de(data["chu_de"])
            messagebox.showinfo(
                "Thành công", "Đã lưu cấu hình"
            )
        except Exception as e:
            messagebox.showerror(
                "Lỗi cấu hình", str(e)
            )
from tkinter import ttk, messagebox

from .danh_muc_co_so import ManHinhDanhMucCoSo
from ..dung_chung.ho_tro import hien_thi


class ManHinhSinhVien(ManHinhDanhMucCoSo):
    LOAI = "SinhVien"
    CO_LUU_TRU = True

    TRUONG = [
        "ma_sinh_vien",
        "ho_ten",
        "ngay_sinh",
        "email",
        "so_dien_thoai",
        "tinh",
        "xa",
        "dia_chi_chi_tiet"
    ]

    BAT_BUOC = [
        "ma_sinh_vien",
        "ho_ten",
        "ngay_sinh",
        "tinh",
        "xa"
    ]

    def tao_o_nhap(self, parent, truong, gia_tri):
        if truong in ("tinh", "xa"):
            entry = ttk.Combobox(
                parent, state="readonly", width=40
            )
            entry.set(hien_thi(gia_tri))
            return entry

        return super().tao_o_nhap(
            parent, truong, gia_tri
        )

    def cau_hinh_form(self, form, o_nhap, du_lieu):
        cbo_tinh = o_nhap["tinh"]
        cbo_xa = o_nhap["xa"]

        def nap_xa(event=None):
            tinh = cbo_tinh.get()
            if not tinh:
                cbo_xa["values"] = []
                cbo_xa.set("")
                return

            try:
                danh_sach = self.adapter.dia_ly(tinh)
                cbo_xa["values"] = danh_sach

                xa_cu = du_lieu.get("xa", "")
                if xa_cu in danh_sach:
                    cbo_xa.set(xa_cu)
                else:
                    cbo_xa.set("")
            except Exception as e:
                messagebox.showerror("Lỗi địa lý", str(e))

        try:
            cbo_tinh["values"] = self.adapter.dia_ly()
            cbo_tinh.bind(
                "<<ComboboxSelected>>", nap_xa
            )
            if cbo_tinh.get():
                nap_xa()
        except Exception as e:
            messagebox.showerror("Lỗi địa lý", str(e))
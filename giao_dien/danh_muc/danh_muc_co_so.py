import tkinter as tk
from tkinter import ttk, messagebox

from ..dung_chung.ho_tro import (
    thanh_dict, thanh_danh_sach, hien_thi,
    kiem_tra, chuyen_kieu
)


class ManHinhDanhMucCoSo(ttk.Frame):
    LOAI = ""
    TRUONG = []
    BAT_BUOC = []
    CO_LUU_TRU = False
    CHO_PHEP_XOA = True

    def __init__(self, parent, adapter):
        super().__init__(parent, padding=12)
        self.adapter = adapter
        self.tao_giao_dien()
        self.tai_du_lieu()

    def tao_giao_dien(self):
        ttk.Label(
            self,
            text=f"QUẢN LÝ {self.LOAI.upper()}",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=10)

        thanh = ttk.Frame(self)
        thanh.pack(fill="x", pady=8)

        self.txt_tim = ttk.Entry(thanh, width=35)
        self.txt_tim.pack(side="left", padx=4)

        ttk.Button(
            thanh, text="Tìm kiếm",
            command=self.tim_kiem
        ).pack(side="left", padx=4)

        ttk.Button(
            thanh, text="Làm mới",
            command=self.tai_du_lieu
        ).pack(side="left", padx=4)

        ttk.Button(
            thanh, text="Thêm",
            command=self.them_moi
        ).pack(side="right", padx=4)

        khung_bang = ttk.Frame(self)
        khung_bang.pack(fill="both", expand=True)

        self.bang = ttk.Treeview(
            khung_bang,
            columns=self.TRUONG,
            show="headings",
            selectmode="browse"
        )

        for truong in self.TRUONG:
            self.bang.heading(
                truong,
                text=truong.replace("_", " ").title()
            )
            self.bang.column(truong, width=145)

        cuon_y = ttk.Scrollbar(
            khung_bang, orient="vertical",
            command=self.bang.yview
        )
        cuon_x = ttk.Scrollbar(
            khung_bang, orient="horizontal",
            command=self.bang.xview
        )

        self.bang.configure(
            yscrollcommand=cuon_y.set,
            xscrollcommand=cuon_x.set
        )

        self.bang.grid(row=0, column=0, sticky="nsew")
        cuon_y.grid(row=0, column=1, sticky="ns")
        cuon_x.grid(row=1, column=0, sticky="ew")

        khung_bang.columnconfigure(0, weight=1)
        khung_bang.rowconfigure(0, weight=1)

        thanh_nut = ttk.Frame(self)
        thanh_nut.pack(fill="x", pady=10)

        cac_nut = [
            ("Chi tiết", self.xem_chi_tiet),
            ("Chỉnh sửa", self.chinh_sua)
        ]

        if self.CO_LUU_TRU:
            cac_nut.extend([
                ("Lưu trữ", self.luu_tru),
                ("Tái kích hoạt", self.tai_kich_hoat)
            ])

        if self.CHO_PHEP_XOA:
            cac_nut.append(("Xóa", self.xoa))

        for ten, ham in cac_nut:
            ttk.Button(
                thanh_nut, text=ten, command=ham
            ).pack(side="left", padx=4)

    def hien_thi_danh_sach(self, data):
        for item in self.bang.get_children():
            self.bang.delete(item)

        for obj in thanh_danh_sach(data):
            values = [
                hien_thi(obj.get(truong))
                for truong in self.TRUONG
            ]
            self.bang.insert("", "end", values=values)

    def tai_du_lieu(self):
        try:
            data = self.adapter.lay_tat_ca(self.LOAI)
            self.hien_thi_danh_sach(data)
        except Exception as e:
            messagebox.showerror("Lỗi tải dữ liệu", str(e))

    def tim_kiem(self):
        tu_khoa = self.txt_tim.get().strip()

        if not tu_khoa:
            self.tai_du_lieu()
            return

        try:
            data = self.adapter.loc(
                self.LOAI,
                {"tu_khoa": tu_khoa}
            )
            self.hien_thi_danh_sach(data)
        except Exception as e:
            messagebox.showerror("Lỗi tìm kiếm", str(e))

    def lay_ma_chon(self):
        chon = self.bang.selection()

        if not chon:
            messagebox.showwarning(
                "Thông báo", "Hãy chọn một dòng"
            )
            return None

        values = self.bang.item(chon[0], "values")
        return str(values[0])

    def xem_chi_tiet(self):
        ma = self.lay_ma_chon()
        if ma is None:
            return

        try:
            obj = thanh_dict(
                self.adapter.lay_theo_ma(self.LOAI, ma)
            )
            noi_dung = "\n".join(
                f"{k}: {hien_thi(v)}"
                for k, v in obj.items()
            )
            messagebox.showinfo(
                f"Chi tiết {self.LOAI}", noi_dung
            )
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def them_moi(self):
        self.mo_form()

    def chinh_sua(self):
        ma = self.lay_ma_chon()
        if ma is None:
            return

        try:
            data = thanh_dict(
                self.adapter.lay_theo_ma(self.LOAI, ma)
            )
            self.mo_form(data, ma)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def tao_o_nhap(self, parent, truong, gia_tri):
        entry = ttk.Entry(parent, width=42)
        entry.insert(0, hien_thi(gia_tri))
        return entry

    def mo_form(self, du_lieu=None, ma_cu=None):
        sua = ma_cu is not None

        cua_so = tk.Toplevel(self)
        cua_so.title(
            f"{'Sửa' if sua else 'Thêm'} {self.LOAI}"
        )
        cua_so.geometry("540x620")
        cua_so.transient(self.winfo_toplevel())
        cua_so.grab_set()

        khung = ttk.Frame(cua_so, padding=15)
        khung.pack(fill="both", expand=True)

        canvas = tk.Canvas(khung, highlightthickness=0)
        cuon = ttk.Scrollbar(
            khung, orient="vertical",
            command=canvas.yview
        )
        form = ttk.Frame(canvas)

        form.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0), window=form, anchor="nw"
        )
        canvas.configure(yscrollcommand=cuon.set)

        canvas.pack(side="left", fill="both", expand=True)
        cuon.pack(side="right", fill="y")

        du_lieu = du_lieu or {}
        o_nhap = {}

        for truong in self.TRUONG:
            ttk.Label(
                form,
                text=truong.replace("_", " ").title()
            ).pack(anchor="w", pady=(8, 2))

            entry = self.tao_o_nhap(
                form, truong, du_lieu.get(truong, "")
            )
            entry.pack(fill="x")
            o_nhap[truong] = entry

        if sua:
            o_nhap[self.TRUONG[0]].configure(
                state="readonly"
            )

        self.cau_hinh_form(form, o_nhap, du_lieu)

        def luu():
            data = {
                ten: widget.get().strip()
                for ten, widget in o_nhap.items()
            }

            for ten, gia_tri in data.items():
                loi = kiem_tra(
                    ten, gia_tri,
                    bat_buoc=(ten in self.BAT_BUOC)
                )
                if loi:
                    messagebox.showwarning(
                        "Dữ liệu không hợp lệ",
                        loi,
                        parent=cua_so
                    )
                    return

            try:
                data = {
                    k: chuyen_kieu(k, v) if v else None
                    for k, v in data.items()
                }

                if sua:
                    ket_qua = self.adapter.cap_nhat(
                        self.LOAI, ma_cu, data
                    )
                else:
                    ket_qua = self.adapter.them(
                        self.LOAI, data
                    )

                if ket_qua is False:
                    raise ValueError("Không thể lưu dữ liệu")

                messagebox.showinfo(
                    "Thành công",
                    "Đã lưu dữ liệu",
                    parent=cua_so
                )
                cua_so.destroy()
                self.tai_du_lieu()

            except Exception as e:
                messagebox.showerror(
                    "Lỗi nghiệp vụ", str(e),
                    parent=cua_so
                )

        ttk.Button(
            form, text="Lưu dữ liệu",
            command=luu
        ).pack(fill="x", pady=18)

    def cau_hinh_form(self, form, o_nhap, du_lieu):
        """Hook để class con cấu hình thêm widget."""
        return

    def thao_tac_trang_thai(self, ham, mo_ta):
        ma = self.lay_ma_chon()
        if ma is None:
            return

        if not messagebox.askyesno(
            "Xác nhận", f"{mo_ta} mã {ma}?"
        ):
            return

        try:
            ket_qua = getattr(self.adapter, ham)(
                self.LOAI, ma
            )
            if ket_qua is False:
                raise ValueError("Thao tác không thành công")
            self.tai_du_lieu()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def luu_tru(self):
        self.thao_tac_trang_thai(
            "luu_tru", "Lưu trữ"
        )

    def tai_kich_hoat(self):
        self.thao_tac_trang_thai(
            "tai_kich_hoat", "Tái kích hoạt"
        )

    def xoa(self):
        ma = self.lay_ma_chon()
        if ma is None:
            return

        if not messagebox.askyesno(
            "Xác nhận xóa",
            f"Xóa hẳn {self.LOAI} mã {ma}?\n"
            "Thao tác có thể không khôi phục được."
        ):
            return

        ep_xoa = messagebox.askyesno(
            "Ép xóa",
            "Có sử dụng ép xóa không?\n"
            "Chọn Không để xóa thông thường."
        )

        try:
            ket_qua = self.adapter.xoa(
                self.LOAI, ma, ep_xoa
            )
            if ket_qua is False:
                raise ValueError("Không thể xóa")
            self.tai_du_lieu()
        except Exception as e:
            messagebox.showerror("Lỗi xóa", str(e))
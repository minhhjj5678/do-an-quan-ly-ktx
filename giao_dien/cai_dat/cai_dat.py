
"""Màn hình cài đặt: 4 chủ đề và thông số hệ thống."""

import copy
import tkinter as tk
from tkinter import ttk, messagebox

from ..dung_chung.mau_sac import lay_mau


class ManHinhCaiDat(ttk.Frame):
    TRUONG = [
        ("don_gia_dien", "Đơn giá điện", "đ/kWh"),
        ("don_gia_nuoc", "Đơn giá nước", "đ/m³"),
        ("suc_chua_mac_dinh", "Sức chứa mặc định", "người"),
        ("han_muc_no", "Hạn mức nợ", "đồng"),
    ]

    CHU_DE = ("LIGHT", "GREY", "DARK", "BLUE")

    def __init__(self, parent, adapter, doi_chu_de):
        super().__init__(parent, padding=16)

        self.adapter = adapter
        self.doi_chu_de = doi_chu_de
        self.cau_hinh = None
        self.o_nhap = {}

        self.tao_giao_dien()
        self.tai_cau_hinh()

    def tao_giao_dien(self):
        # Tiêu đề
        dau = ttk.Frame(
            self,
            style="KTX.Banner.TFrame",
            padding=16
        )
        dau.pack(fill="x", pady=(0, 14))

        ttk.Label(
            dau,
            text="CÀI ĐẶT HỆ THỐNG",
            style="KTX.BannerTitle.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            dau,
            text="Tùy chỉnh giao diện và các thông số quản lý",
            style="KTX.BannerSub.TLabel"
        ).pack(anchor="w", pady=(6, 0))

        # Thanh nút
        thanh_nut = ttk.Frame(self)
        thanh_nut.pack(
            side="bottom",
            fill="x",
            pady=(12, 0)
        )

        ttk.Button(
            thanh_nut,
            text="Lấy lại dữ liệu",
            command=self.tai_cau_hinh
        ).pack(side="left")

        ttk.Button(
            thanh_nut,
            text="Lưu cấu hình",
            style="KTX.Primary.TButton",
            command=self.luu
        ).pack(side="right")

        # Phần chọn chủ đề
        khung_mau = ttk.LabelFrame(
            self,
            text="  Giao diện  ",
            padding=14
        )
        khung_mau.pack(fill="x", pady=(0, 14))
        khung_mau.columnconfigure(0, weight=1)

        ttk.Label(
            khung_mau,
            text="Chủ đề màu sắc"
        ).grid(row=0, column=0, sticky="w")

        self.cbo_chu_de = ttk.Combobox(
            khung_mau,
            values=self.CHU_DE,
            state="readonly",
            width=26
        )
        self.cbo_chu_de.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=8,
            padx=(0, 10)
        )

        self.cbo_chu_de.bind(
            "<<ComboboxSelected>>",
            self.xem_truoc_mau
        )

        ttk.Button(
            khung_mau,
            text="Áp dụng màu ngay",
            command=self.ap_dung_mau
        ).grid(row=1, column=1, sticky="ew")

        # Khung xem trước màu sắc
        self.khung_xem = tk.Frame(
            khung_mau,
            padx=8,
            pady=8,
            height=56
        )
        self.khung_xem.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew"
        )
        self.khung_xem.pack_propagate(False)

        self.lbl_menu = tk.Label(
            self.khung_xem,
            text="Menu",
            width=13
        )
        self.lbl_menu.pack(
            side="left",
            fill="both",
            padx=(0, 5)
        )

        self.lbl_nen = tk.Label(
            self.khung_xem,
            text="Nền giao diện"
        )
        self.lbl_nen.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        self.lbl_nut = tk.Label(
            self.khung_xem,
            text="Nút bấm",
            width=13
        )
        self.lbl_nut.pack(
            side="left",
            fill="both",
            padx=(5, 0)
        )

        ttk.Label(
            khung_mau,
            text="Áp dụng màu ngay không lưu cấu hình.",
            style="KTX.Muted.TLabel"
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 0)
        )

        # Phần thông số hệ thống
        khung_so = ttk.LabelFrame(
            self,
            text="  Thông số hệ thống  ",
            padding=14
        )
        khung_so.pack(fill="x")
        khung_so.columnconfigure(1, weight=1)

        for i, (truong, nhan, don_vi) in enumerate(self.TRUONG):
            ttk.Label(
                khung_so,
                text=nhan
            ).grid(
                row=i,
                column=0,
                sticky="w",
                pady=7
            )

            entry = ttk.Entry(khung_so)
            entry.grid(
                row=i,
                column=1,
                sticky="ew",
                padx=12,
                pady=7
            )

            ttk.Label(
                khung_so,
                text=don_vi
            ).grid(
                row=i,
                column=2,
                sticky="w",
                pady=7
            )

            self.o_nhap[truong] = entry

    def xem_truoc_mau(self, event=None):
        mau = lay_mau(self.cbo_chu_de.get())

        self.khung_xem.configure(bg=mau["vien"])

        self.lbl_menu.configure(
            bg=mau["menu"],
            fg=mau["chu"]
        )

        self.lbl_nen.configure(
            bg=mau["nen"],
            fg=mau["chu"]
        )

        self.lbl_nut.configure(
            bg=mau["chinh"],
            fg=mau["trang"]
        )

    def ap_dung_mau(self):
        chu_de = self.cbo_chu_de.get()

        if chu_de not in self.CHU_DE:
            messagebox.showwarning(
                "Chủ đề",
                "Hãy chọn một chủ đề.",
                parent=self
            )
            return

        self.doi_chu_de(chu_de)

    def tai_cau_hinh(self):
        try:
            self.cau_hinh = self.adapter.doc_cau_hinh()
            cfg = self.cau_hinh

            if isinstance(cfg, dict):
                gia_tri = lambda ten, mac_dinh="": cfg.get(
                    ten, mac_dinh
                )
            else:
                gia_tri = lambda ten, mac_dinh="": getattr(
                    cfg, ten, mac_dinh
                )

            chu_de = str(
                gia_tri("chu_de", "LIGHT")
            ).upper()

            self.cbo_chu_de.set(
                chu_de if chu_de in self.CHU_DE else "LIGHT"
            )

            self.xem_truoc_mau()

            for truong, entry in self.o_nhap.items():
                entry.delete(0, tk.END)

                value = gia_tri(truong, "")
                entry.insert(
                    0,
                    "" if value is None else str(value)
                )

        except Exception as e:
            messagebox.showerror(
                "Lỗi đọc cấu hình",
                str(e),
                parent=self
            )

    def tao_cau_hinh_moi(self, data):
        cfg = self.cau_hinh

        if cfg is None:
            raise ValueError(
                "Chưa tải được cấu hình từ hệ thống."
            )

        # Nếu cấu hình là dictionary
        if isinstance(cfg, dict):
            return {**cfg, **data}

        # Nếu cấu hình là đối tượng có thể khởi tạo
        # bằng các thuộc tính hiện tại
        try:
            return type(cfg)(
                **{**vars(cfg), **data}
            )

        except (TypeError, AttributeError):
            # Nếu là đối tượng thông thường
            moi = copy.copy(cfg)

            for ten, value in data.items():
                setattr(moi, ten, value)

            return moi

    def luu(self):
        chu_de = self.cbo_chu_de.get()

        if chu_de not in self.CHU_DE:
            messagebox.showwarning(
                "Chủ đề",
                "Hãy chọn một chủ đề.",
                parent=self
            )
            return

        try:
            data = {}

            for truong, entry in self.o_nhap.items():
                value = entry.get().strip()

                if not value:
                    raise ValueError(
                        f"Vui lòng nhập {truong.replace('_', ' ')}."
                    )

                if truong == "suc_chua_mac_dinh":
                    so = int(value)

                    if so <= 0:
                        raise ValueError(
                            "Sức chứa mặc định phải lớn hơn 0."
                        )
                else:
                    so = float(value)

                    if so < 0:
                        raise ValueError(
                            "Đơn giá và hạn mức nợ không được âm."
                        )

                data[truong] = so

            data["chu_de"] = chu_de

            # Tạo cấu hình mới
            moi = self.tao_cau_hinh_moi(data)

            # Xác nhận trước khi lưu
            if not messagebox.askyesno(
                "Xác nhận",
                "Bạn có muốn lưu cấu hình mới?",
                parent=self
            ):
                return

            # Gọi Adapter mới
            self.adapter.cap_nhat_cau_hinh(moi)

            self.cau_hinh = moi
            self.doi_chu_de(chu_de)

            messagebox.showinfo(
                "Thành công",
                "Đã lưu cấu hình.",
                parent=self
            )

        except ValueError as e:
            messagebox.showwarning(
                "Dữ liệu không hợp lệ",
                str(e),
                parent=self
            )

        except Exception as e:
            messagebox.showerror(
                "Lỗi lưu cấu hình",
                str(e),
                parent=self
            )

class MockPhien:
    def __init__(self):
        self.users = {
            "admin": ["123456", True],
            "nhanvien": ["123456", False]
        }
        self.current = None

    def dang_nhap(self, tai_khoan, mat_khau):
        if self.current is not None:
            raise ValueError("Đã có tài khoản đăng nhập")

        if tai_khoan not in self.users:
            raise ValueError("Tài khoản không tồn tại")

        if self.users[tai_khoan][0] != mat_khau:
            raise ValueError("Sai mật khẩu")

        self.current = tai_khoan
        return True

    def dang_xuat(self):
        self.current = None
        return True

    def co_quyen_quan_tri(self):
        return (
            self.current is not None
            and self.users[self.current][1]
        )

    def doi_mat_khau(self, mat_khau_moi,
                     mat_khau_cu=None, tai_khoan=None):
        if tai_khoan is not None:
            if not self.co_quyen_quan_tri():
                raise PermissionError("Không có quyền quản trị")

            if tai_khoan not in self.users:
                raise ValueError("Tài khoản không tồn tại")

            self.users[tai_khoan][0] = mat_khau_moi
        else:
            if self.current is None:
                raise ValueError("Chưa đăng nhập")

            if self.users[self.current][0] != mat_khau_cu:
                raise ValueError("Sai mật khẩu cũ")

            self.users[self.current][0] = mat_khau_moi

        return True

    def tao_tai_khoan(self, tai_khoan, mat_khau,
                      co_quyen_quan_tri=False):
        if not self.co_quyen_quan_tri():
            raise PermissionError("Không có quyền quản trị")

        if tai_khoan in self.users:
            raise ValueError("Tài khoản đã tồn tại")

        self.users[tai_khoan] = [
            mat_khau, co_quyen_quan_tri
        ]
        return True


class MockDieuPhoi:
    def __init__(self):
        self.data = {
            ten: {} for ten in [
                "SinhVien", "Phong", "ToaNha",
                "HopDong", "HoaDonThang",
                "DichVuThem", "ViPham", "TaiKhoan"
            ]
        }

        self.config = {
            "chu_de": "LIGHT",
            "don_gia_dien": 3500,
            "don_gia_nuoc": 12000,
            "suc_chua_mac_dinh": 4,
            "han_muc_no": 500000
        }

    def lay_tat_ca(self, loai):
        return list(self.data[loai].values())

    def loc_theo_dieu_kien(self, loai, dieu_kien):
        tu_khoa = dieu_kien.get("tu_khoa", "").lower()
        return [
            obj for obj in self.lay_tat_ca(loai)
            if tu_khoa in str(obj).lower()
        ]

    def lay_theo_ma(self, loai, ma):
        if ma not in self.data[loai]:
            raise ValueError("Không tìm thấy mã")
        return self.data[loai][ma]

    def them(self, loai, du_lieu):
        ma = str(next(iter(du_lieu.values())))

        if ma in self.data[loai]:
            raise ValueError("Mã đã tồn tại")

        self.data[loai][ma] = dict(du_lieu)
        return True

    def cap_nhat(self, loai, ma, du_lieu):
        self.lay_theo_ma(loai, ma)
        self.data[loai][ma].update(du_lieu)
        return True

    def luu_tru(self, loai, ma):
        self.lay_theo_ma(loai, ma)["luu_tru"] = True
        return True

    def tai_kich_hoat(self, loai, ma):
        self.lay_theo_ma(loai, ma)["luu_tru"] = False
        return True

    def xoa(self, loai, ma, ep_xoa=False):
        self.lay_theo_ma(loai, ma)
        del self.data[loai][ma]
        return True

    def danh_sach_dia_ly(self, tinh=None):
        dia_ly = {
            "TP. Hồ Chí Minh": [
                "Phường Sài Gòn",
                "Phường Bến Thành"
            ],
            "Hà Nội": [
                "Phường Hoàn Kiếm"
            ]
        }

        if tinh is None:
            return list(dia_ly)

        return dia_ly.get(tinh, [])

    def thanh_toan_hop_dong(self, ma):
        self.lay_theo_ma("HopDong", ma)["trang_thai"] = "Đã thanh toán"
        return True

    def ket_thuc_hop_dong(self, ma):
        self.lay_theo_ma("HopDong", ma)["trang_thai"] = "Đã kết thúc"
        return True

    def thanh_toan_hoa_don_thang(self, ma):
        self.lay_theo_ma("HoaDonThang", ma)["trang_thai"] = "Đã thanh toán"
        return True

    def xu_ly_vi_pham(self, ma):
        self.lay_theo_ma("ViPham", ma)["trang_thai"] = "Đã xử lý"
        return True

    def thong_ke_so_phong(self, **bo_loc):
        phong = self.lay_tat_ca("Phong")
        tong = len(phong)
        da_thue = sum(
            p.get("trang_thai") == "Đã thuê"
            for p in phong
        )
        return {
            "tong_so_phong": tong,
            "da_thue": da_thue,
            "phong_trong": tong - da_thue
        }

    def thong_ke_ty_le_lap_day(self, **bo_loc):
        thong_ke = self.thong_ke_so_phong()
        tong = thong_ke["tong_so_phong"]
        return {
            "ty_le_lap_day":
                thong_ke["da_thue"] / tong * 100 if tong else 0
        }

    def thong_ke_cong_no(self, **bo_loc):
        return {
            "tong_tien_no": 0,
            "so_sinh_vien_dang_no": 0
        }

    def doc_cau_hinh(self):
        return dict(self.config)

    def cap_nhat_cau_hinh(self, du_lieu):
        self.config.update(du_lieu)
        return True
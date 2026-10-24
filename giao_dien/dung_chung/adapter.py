class Adapter:
    def __init__(self, dieu_phoi, phien):
        self.dp = dieu_phoi
        self.phien = phien

    def dang_nhap(self, tai_khoan, mat_khau):
        return self.phien.dang_nhap(tai_khoan, mat_khau)

    def dang_xuat(self):
        return self.phien.dang_xuat()

    def la_admin(self):
        quyen = self.phien.co_quyen_quan_tri
        return bool(quyen() if callable(quyen) else quyen)

    def doi_mat_khau(self, mat_khau_moi,
                     mat_khau_cu=None, tai_khoan=None):
        if tai_khoan is not None:
            return self.phien.doi_mat_khau(
                mat_khau_moi=mat_khau_moi,
                tai_khoan=tai_khoan
            )
        return self.phien.doi_mat_khau(
            mat_khau_cu=mat_khau_cu,
            mat_khau_moi=mat_khau_moi
        )

    def tao_tai_khoan(self, tai_khoan, mat_khau, admin):
        return self.phien.tao_tai_khoan(
            tai_khoan=tai_khoan,
            mat_khau=mat_khau,
            co_quyen_quan_tri=admin
        )

    def lay_tat_ca(self, loai):
        return self.dp.lay_tat_ca(loai)

    def loc(self, loai, dieu_kien):
        return self.dp.loc_theo_dieu_kien(loai, dieu_kien)

    def lay_theo_ma(self, loai, ma):
        return self.dp.lay_theo_ma(loai, ma)

    def them(self, loai, du_lieu):
        return self.dp.them(loai, du_lieu)

    def cap_nhat(self, loai, ma, du_lieu):
        return self.dp.cap_nhat(loai, ma, du_lieu)

    def luu_tru(self, loai, ma):
        return self.dp.luu_tru(loai, ma)

    def tai_kich_hoat(self, loai, ma):
        return self.dp.tai_kich_hoat(loai, ma)

    def xoa(self, loai, ma, ep_xoa=False):
        return self.dp.xoa(loai, ma, ep_xoa=ep_xoa)

    def dia_ly(self, tinh=None):
        if tinh is None:
            return self.dp.danh_sach_dia_ly()
        return self.dp.danh_sach_dia_ly(tinh)

    def nghiep_vu(self, ten, ma):
        hop_le = {
            "thanh_toan_hop_dong",
            "ket_thuc_hop_dong",
            "thanh_toan_hoa_don_thang",
            "xu_ly_vi_pham"
        }
        if ten not in hop_le:
            raise ValueError("Nghiệp vụ không hợp lệ")
        return getattr(self.dp, ten)(ma)

    def thong_ke(self, ten, bo_loc):
        hop_le = {
            "thong_ke_so_phong",
            "thong_ke_ty_le_lap_day",
            "thong_ke_cong_no"
        }
        if ten not in hop_le:
            raise ValueError("Thống kê không hợp lệ")
        return getattr(self.dp, ten)(**bo_loc)

    def doc_cau_hinh(self):
        return self.dp.doc_cau_hinh()

    def cap_nhat_cau_hinh(self, data):
        return self.dp.cap_nhat_cau_hinh(data)
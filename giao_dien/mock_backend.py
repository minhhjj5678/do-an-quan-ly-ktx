"""Backend giả lập để chạy thử giao diện Tkinter theo Adapter mới.

Mã thực thể được sinh bằng tien_ich.tao_ma của nhóm.
Đây chỉ là dữ liệu trong bộ nhớ; không ghi vào JSON thật.
"""
from types import SimpleNamespace
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from tien_ich.cau_hinh_dong import CauHinhDong

from tien_ich.tao_ma import (
    ma_sinh_vien,
    ma_phong,
    ma_toa_nha,
    ma_hoa_don_thang,
    ma_hop_dong,
    ma_vi_pham,
    ma_hoc_ky,
)


# Tên class thực thể -> (nhóm mã, hàm sinh mã).
BO_SINH_MA = {
    "SinhVien": ("sinh_vien", ma_sinh_vien),
    "Phong": ("phong", ma_phong),
    "ToaNha": ("toa_nha", ma_toa_nha),
    "HoaDonThang": ("hoa_don_thang", ma_hoa_don_thang),
    "HopDong": ("hop_dong", ma_hop_dong),
    "ViPham": ("vi_pham", ma_vi_pham),
    "HocKy": ("hoc_ky", ma_hoc_ky),
}


class MockPhien:
    def __init__(self, dieu_phoi=None):
        self.users = {'admin': ['123456', True, None, False],
                      'nhanvien': ['123456', False, 'SV0001', False]}
        self._current = None
        if dieu_phoi is not None:
            dieu_phoi.gan_phien(self)

    @property
    def tai_khoan_hien_tai(self):
        if self._current is None:
            return None
        du_lieu = self.users[self._current]
        return SimpleNamespace(
            ma=self._current,
            co_quyen_quan_tri=du_lieu[1],
            loai_tai_khoan=(
                LoaiTaiKhoan.QUAN_TRI_VIEN if du_lieu[1]
                else LoaiTaiKhoan.SINH_VIEN
            ),
            ma_chu_the=du_lieu[2],
        )

    def _la_admin(self):
        return self.tai_khoan_hien_tai is not None and self.tai_khoan_hien_tai.co_quyen_quan_tri

    def dang_nhap(self, tai_khoan, mat_khau):
        if self._current is not None:
            raise ValueError('Đã có tài khoản đăng nhập')
        if tai_khoan not in self.users or self.users[tai_khoan][3]:
            raise ValueError('Tài khoản không tồn tại hoặc đã bị ngưng')
        if self.users[tai_khoan][0] != mat_khau:
            raise ValueError('Sai mật khẩu')
        self._current = tai_khoan

    def dang_xuat(self):
        self._current = None

    def doi_mat_khau(self, mat_khau_moi, mat_khau_cu=None, tai_khoan=None):
        if tai_khoan is None:
            if self._current is None:
                raise ValueError('Chưa đăng nhập')
            if self.users[self._current][0] != mat_khau_cu:
                raise ValueError('Sai mật khẩu cũ')
            tai_khoan = self._current
        elif not self._la_admin():
            raise PermissionError('Không có quyền quản trị')
        if tai_khoan not in self.users:
            raise ValueError('Không có tài khoản này')
        self.users[tai_khoan][0] = mat_khau_moi

    def tao_tai_khoan(self, tai_khoan, mat_khau, loai_tai_khoan, ma_chu_the=None):
        if not self._la_admin():
            raise PermissionError('Không có quyền quản trị')
        if tai_khoan in self.users:
            raise ValueError('Tài khoản đã tồn tại')
        if loai_tai_khoan not in (LoaiTaiKhoan.QUAN_TRI_VIEN, LoaiTaiKhoan.SINH_VIEN):
            raise ValueError('Loại tài khoản không hợp lệ')
        if loai_tai_khoan == LoaiTaiKhoan.SINH_VIEN:
            if not ma_chu_the:
                raise ValueError('Thiếu mã sinh viên')
            if any(u[2] == ma_chu_the for u in self.users.values()):
                raise ValueError('Sinh viên này đã có tài khoản')
        else:
            ma_chu_the = None
        self.users[tai_khoan] = [mat_khau, loai_tai_khoan == LoaiTaiKhoan.QUAN_TRI_VIEN,
                                ma_chu_the, False]

    def ngung_tai_khoan(self, tai_khoan):
        self._kiem_tra_admin(tai_khoan)
        self.users[tai_khoan][3] = True

    def kich_hoat_lai_tai_khoan(self, tai_khoan):
        self._kiem_tra_admin(tai_khoan)
        self.users[tai_khoan][3] = False

    def xoa_tai_khoan(self, tai_khoan):
        self._kiem_tra_admin(tai_khoan)
        del self.users[tai_khoan]

    def _kiem_tra_admin(self, tai_khoan):
        if not self._la_admin():
            raise PermissionError('Không có quyền quản trị')
        if tai_khoan not in self.users:
            raise ValueError('Tài khoản không tồn tại')


class MockDieuPhoi:
    def __init__(self):
        self._phien = None
        self.data = {}
        # Lưu lại mã đã cấp để không cấp lại khi xóa bản ghi trong phiên mock.
        self._ma_da_cap = {}
        # Đồng nhất với backend thật: cấu hình là frozen dataclass CauHinhDong.
        self.config: CauHinhDong = CauHinhDong()
        self._dia_ly = {}

    def nap_du_lieu_file(self):
        # Dữ liệu chỉ dùng để thử Combobox, không phải danh mục địa lý thật.
        def xa(ma, ten): return SimpleNamespace(ma=ma, ten=ten)
        def tinh(ma, ten, cac_xa):
            return SimpleNamespace(ma=ma, ten=ten, danh_sach_xa=cac_xa)
        self._dia_ly = {
            '79': tinh('79', 'TP. Hồ Chí Minh', {
                '79001': xa('79001', 'Phường Sài Gòn'),
                '79002': xa('79002', 'Phường Bến Thành')}),
            '01': tinh('01', 'Hà Nội', {'01001': xa('01001', 'Phường Hoàn Kiếm')})
        }

    def nap_du_lieu_api(self):
        # Không gọi Internet trong bản demo.
        return None

    def danh_sach_dia_ly(self):
        if not self._dia_ly:
            raise ValueError('Chưa nạp dữ liệu địa lý')
        return self._dia_ly.copy()

    def gan_phien(self, phien):
        # Mock phiên và mock điều phối cùng nhìn vào một kho tài khoản.
        self._phien = phien

    def _bang(self, loai):
        return self.data.setdefault(loai, {})

    def lay_tat_ca(self, loai, lay_luu_tru=False):
        if loai is TaiKhoan:
            if self._phien is None:
                return {}
            return {
                ten: SimpleNamespace(
                    ma=ten, ma_dang_nhap=ten,
                    loai_tai_khoan=(LoaiTaiKhoan.QUAN_TRI_VIEN if du_lieu[1]
                                    else LoaiTaiKhoan.SINH_VIEN),
                    ma_chu_the=du_lieu[2],
                    con_hoat_dong=not du_lieu[3],
                    co_quyen_quan_tri=du_lieu[1],
                )
                for ten, du_lieu in self._phien.users.items()
                if lay_luu_tru or not du_lieu[3]
            }
        return {ma: obj for ma, obj in self._bang(loai).items()
                if lay_luu_tru or not getattr(obj, '_mock_luu_tru', False)}

    def loc_theo_dieu_kien(self, loai, predicate, lay_luu_tru=False):
        return {ma: obj for ma, obj in self.lay_tat_ca(loai, lay_luu_tru).items()
                if predicate(obj)}

    def lay_theo_ma(self, loai, ma, lay_luu_tru=False):
        if ma not in self.lay_tat_ca(loai, lay_luu_tru):
            raise ValueError(f'Không tìm thấy mã {ma}')
        return self._bang(loai)[ma]

    def tao_va_them(self, loai, *args, **kwargs):
        """Thêm bản ghi thử với mã do tien_ich.tao_ma sinh."""
        if args:
            raise ValueError("Mock chỉ nhận tham số theo tên")
        if "ma" in kwargs:
            raise ValueError("Không nhập mã: tao_va_them() sẽ tự sinh mã")

        ten_loai = loai.__name__
        if ten_loai not in BO_SINH_MA:
            raise ValueError(f"Chưa có hàm sinh mã cho {ten_loai}")

        nhom_ma, ham_sinh_ma = BO_SINH_MA[ten_loai]

        # Đọc các mã đã cấp để tránh sinh trùng trong phiên Mock.
        cac_ma = {
            ma
            for bang in self.data.values()
            for ma in bang
        }
        cac_ma.update(self._ma_da_cap.get(nhom_ma, set()))

        ma = ham_sinh_ma(cac_ma)
        if ma in cac_ma:
            raise ValueError(f"Mã {ma} đã tồn tại")

        # Mock dùng SimpleNamespace để không phụ thuộc constructor
        # của từng class thực thể. Backend thật tạo đối tượng thật.
        obj = SimpleNamespace(ma=ma, **kwargs)
        self._bang(loai)[ma] = obj
        self._ma_da_cap.setdefault(nhom_ma, set()).add(ma)
        return obj

    def cap_nhat(self, thuc_the):
        # Trong mock, đối tượng đã được sửa trực tiếp bởi Adapter.
        return None

    def luu_tru(self, thuc_the):
        thuc_the._mock_luu_tru = True

    def tai_kich_hoat(self, thuc_the):
        thuc_the._mock_luu_tru = False

    def xoa(self, thuc_the, ep_xoa=False):
        for bang in self.data.values():
            if bang.get(thuc_the.ma) is thuc_the:
                del bang[thuc_the.ma]
                return
        raise ValueError('Không tìm thấy thực thể')

    def thanh_toan_hop_dong(self, thuc_the):
        thuc_the.trang_thai = 'Đã thanh toán'

    def ket_thuc_hop_dong(self, thuc_the):
        thuc_the.trang_thai = 'Đã kết thúc'

    def thanh_toan_hoa_don_thang(self, thuc_the):
        thuc_the.trang_thai = 'Đã thanh toán'

    def xu_ly_vi_pham(self, thuc_the):
        thuc_the.trang_thai = 'Đã xử lý'

    def thong_ke_so_phong(self, toa_nha=None, loai_phong=None) -> tuple[int, int, int]:
        from thuc_the.ky_tuc_xa import Phong
        ds = list(self.lay_tat_ca(Phong).values())
        if toa_nha is not None:
            ma_toa = getattr(toa_nha, 'ma', toa_nha)
            ds = [p for p in ds if getattr(p, 'toa_nha', None) == ma_toa]
        if loai_phong is not None:
            ds = [p for p in ds if getattr(p, 'suc_chua', None) == loai_phong]
        # Mock chưa sinh tình trạng ở phòng: mặc định phòng còn trống.
        return len(ds), 0, len(ds)

    def thong_ke_ty_le_lap_day(self, toa_nha=None, loai_phong=None) -> float:
        return 0.0

    def thong_ke_cong_no(self) -> tuple[float, int]:
        return 0.0, 0

    def doc_cau_hinh(self) -> CauHinhDong:
        return self.config

    def cap_nhat_cau_hinh(self, cau_hinh: CauHinhDong) -> None:
        if not isinstance(cau_hinh, CauHinhDong):
            raise ValueError('Cấu hình phải là CauHinhDong')
        self.config = cau_hinh

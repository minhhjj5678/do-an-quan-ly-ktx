"""
Bản giả lập (in-memory) của GiaoThucDieuPhoi và GiaoThucPhienLamViec để chạy thử giao diện / code khác.

Cách dùng:
    dp = MockDieuPhoi()
    phien = MockPhien(dp)          # có sẵn admin/123456 và sinhvien/123456
    app = Adapter(dp, phien)
    dp.nap_du_lieu_file()

Các giả định (sửa ở đầu file nếu thực thể của bạn khác):
    - Mã của thực thể nằm ở thuộc tính `ma`  -> TEN_THUOC_TINH_MA
    - Hàm khởi tạo thực thể nhận mã làm tham số đầu tiên (đúng như tao_va_them trong giao thức)
"""
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar

from giao_thuc.nghiep_vu import GiaoThucDieuPhoi, GiaoThucPhienLamViec
from thuc_the.dia_ly import Tinh
from thuc_the.ky_tuc_xa import Phong, ToaNha
from thuc_the.tai_chinh import HoaDonThang, HopDong
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from thuc_the.thuc_the_goc import ThucTheGoc, ThucTheLuuTruDuoc
from thuc_the.vi_pham import ViPham
from tien_ich.cau_hinh_dong import CauHinhDong

TEN_THUOC_TINH_MA = "ma"

T = TypeVar("T", bound=ThucTheGoc)
P = ParamSpec("P")

# ThucTheLuuTruDuoc không kế thừa ThucTheGoc nên các hàm trợ giúp phải nhận cả hai
ThucTheBatKy = ThucTheGoc | ThucTheLuuTruDuoc


def _ma(thuc_the: ThucTheBatKy) -> str:
    return getattr(thuc_the, TEN_THUOC_TINH_MA)


def _la_quan_tri(loai: Any) -> bool:
    """Đoán LoaiTaiKhoan là quản trị viên qua tên thành viên enum. Sửa tại đây nếu tên khác."""
    ten = str(getattr(loai, "name", loai)).upper()
    return "QUAN" in ten or "ADMIN" in ten


def _tim_loai(la_quan_tri: bool) -> Any:
    try:
        for thanh_vien in LoaiTaiKhoan:
            if _la_quan_tri(thanh_vien) == la_quan_tri:
                return thanh_vien
    except TypeError:
        pass
    return None


# ======================================================================
class MockDieuPhoi(GiaoThucDieuPhoi):
    """
    Thuộc tính công khai để kịch bản thử chỉnh:
        phong_co_nguoi : set[str]  mã các phòng được coi là có người (cho thống kê)
        cong_no_gia    : tuple[float, int]  kết quả thong_ke_cong_no
        trang_thai     : dict  trạng thái nghiệp vụ giả lập của HopDong/HoaDonThang/ViPham
        loi_api        : bool  True để nap_du_lieu_api ném OSError
    """

    def __init__(self, dia_ly_mau: dict[str, Tinh] | None = None,
                 cau_hinh: CauHinhDong | None = None, loi_api: bool = False):
        self._kho: dict[type, dict[str, ThucTheGoc]] = {}
        self._luu_tru: set[tuple[type, str]] = set()
        self._dem: dict[str, int] = {}
        self._da_nap_file = False
        self._dia_ly_mau = dia_ly_mau or {}
        self._dia_ly: dict[str, Tinh] | None = None
        self._cau_hinh: CauHinhDong | None = cau_hinh
        if self._cau_hinh is None:
            try:
                self._cau_hinh = CauHinhDong()
            except TypeError:
                self._cau_hinh = None  # CauHinhDong cần tham số: truyền vào qua cau_hinh=
        self.loi_api = loi_api
        self.phong_co_nguoi: set[str] = set()
        self.cong_no_gia: tuple[float, int] = (0.0, 0)
        self.trang_thai: dict[tuple[type, str], str] = {}

    # ---------- Nạp dữ liệu ----------
    def nap_du_lieu_file(self) -> None:
        if self._da_nap_file:
            raise RuntimeError("nap_du_lieu_file chỉ được gọi đúng một lần")
        self._da_nap_file = True

    def nap_du_lieu_api(self) -> None:
        if self.loi_api:
            raise OSError("Giả lập: không tải được dữ liệu địa lý")
        self._dia_ly = self._dia_ly_mau

    # ---------- Trợ giúp nội bộ ----------
    def _dang_hoat_dong(self, thuc_the: ThucTheBatKy) -> bool:
        return (type(thuc_the), _ma(thuc_the)) not in self._luu_tru

    def _cua_loai(self, loai: type, lay_luu_tru: bool) -> dict[str, Any]:
        ket_qua: dict[str, Any] = {}
        for kieu, kho in self._kho.items():
            if issubclass(kieu, loai):
                for ma, thuc_the in kho.items():
                    if lay_luu_tru or self._dang_hoat_dong(thuc_the):
                        ket_qua[ma] = thuc_the
        return ket_qua

    def _phai_ton_tai(self, thuc_the: ThucTheBatKy) -> None:
        if _ma(thuc_the) not in self._kho.get(type(thuc_the), {}):
            raise ValueError(f"{type(thuc_the).__name__} mã {_ma(thuc_the)} không tồn tại")

    def _sinh_ma(self, loai: Any) -> str:
        ten = getattr(loai, "__name__", "TT")
        self._dem[ten] = self._dem.get(ten, 0) + 1
        return f"{ten[:3].upper()}{self._dem[ten]:04d}"

    # ---------- CRUD ----------
    def lay_tat_ca(self, loai_thuc_the: type[T], lay_luu_tru: bool = False) -> dict[str, T]:
        return self._cua_loai(loai_thuc_the, lay_luu_tru)

    def them(self, thuc_the: ThucTheGoc) -> None:
        kho = self._kho.setdefault(type(thuc_the), {})
        if _ma(thuc_the) in kho:
            raise ValueError(f"Mã {_ma(thuc_the)} đã tồn tại")
        kho[_ma(thuc_the)] = thuc_the

    def tao_va_them(self, loai_thuc_the: Callable[Concatenate[str, P], T],
                    *args: P.args, **kwargs: P.kwargs) -> T:
        thuc_the = loai_thuc_the(self._sinh_ma(loai_thuc_the), *args, **kwargs)
        self.them(thuc_the)
        return thuc_the

    def xoa(self, thuc_the: ThucTheGoc, ep_xoa: bool = False) -> None:
        # Mock không biết quan hệ giữa các thực thể nên ep_xoa không xóa dây chuyền
        self._phai_ton_tai(thuc_the)
        if isinstance(thuc_the, ThucTheLuuTruDuoc) and self._dang_hoat_dong(thuc_the):
            raise ValueError("Thực thể lưu trữ được đang hoạt động, hãy luu_tru() trước khi xóa")
        del self._kho[type(thuc_the)][_ma(thuc_the)]
        self._luu_tru.discard((type(thuc_the), _ma(thuc_the)))

    def lay_theo_ma(self, loai_thuc_the: type[T], ma: str, lay_luu_tru: bool = False) -> T:
        thuc_the = self._cua_loai(loai_thuc_the, True).get(ma)
        if thuc_the is None:
            raise ValueError(f"Không tìm thấy {loai_thuc_the.__name__} mã {ma}")
        if not lay_luu_tru and not self._dang_hoat_dong(thuc_the):
            raise ValueError(f"{loai_thuc_the.__name__} mã {ma} đã lưu trữ")
        return thuc_the

    def loc_theo_dieu_kien(self, loai_thuc_the: type[T], dieu_kien: Callable[[T], bool],
                           lay_luu_tru: bool = False) -> dict[str, T]:
        return {ma: tt for ma, tt in self._cua_loai(loai_thuc_the, lay_luu_tru).items()
                if dieu_kien(tt)}

    def cap_nhat(self, thuc_the: ThucTheGoc) -> None:
        self._phai_ton_tai(thuc_the)
        self._kho[type(thuc_the)][_ma(thuc_the)] = thuc_the

    def luu_tru(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        self._phai_ton_tai(thuc_the)
        if not self._dang_hoat_dong(thuc_the):
            raise ValueError("Thực thể đã được lưu trữ")
        self._luu_tru.add((type(thuc_the), _ma(thuc_the)))

    def tai_kich_hoat(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        self._phai_ton_tai(thuc_the)
        if self._dang_hoat_dong(thuc_the):
            raise ValueError("Thực thể đang hoạt động")
        self._luu_tru.discard((type(thuc_the), _ma(thuc_the)))

    # ---------- Nghiệp vụ ----------
    def _doi_trang_thai(self, thuc_the: ThucTheBatKy, tu: str | None, den: str,
                        mac_dinh: str, loi: str) -> None:
        """tu=None nghĩa là cho phép từ mọi trạng thái trừ chính `den`."""
        self._phai_ton_tai(thuc_the)
        khoa = (type(thuc_the), _ma(thuc_the))
        hien_tai = self.trang_thai.get(khoa, mac_dinh)
        if (hien_tai != tu) if tu is not None else (hien_tai == den):
            raise ValueError(loi)
        self.trang_thai[khoa] = den

    def thanh_toan_hop_dong(self, hop_dong: HopDong) -> None:
        self._doi_trang_thai(hop_dong, "chua_thanh_toan", "da_thanh_toan",
                             "chua_thanh_toan", "Hợp đồng không ở trạng thái chưa thanh toán")

    def ket_thuc_hop_dong(self, hop_dong: HopDong) -> None:
        self._doi_trang_thai(hop_dong, None, "ket_thuc",
                             "chua_thanh_toan", "Hợp đồng đã kết thúc")

    def thanh_toan_hoa_don_thang(self, hoa_don_thang: HoaDonThang) -> None:
        self._doi_trang_thai(hoa_don_thang, "chua_thanh_toan", "da_thanh_toan",
                             "chua_thanh_toan", "Hóa đơn tháng không ở trạng thái chưa thanh toán")

    def xu_ly_vi_pham(self, vi_pham: ViPham) -> None:
        self._doi_trang_thai(vi_pham, "chua_xu_ly", "da_xu_ly",
                             "chua_xu_ly", "Vi phạm không ở trạng thái chưa xử lý")

    # ---------- Thống kê (bộ lọc toa_nha / loai_phong chưa được áp dụng trong mock) ----------
    def thong_ke_so_phong(self, toa_nha: ToaNha | None = None,
                          loai_phong: int | None = None) -> tuple[int, int, int]:
        phong = self._cua_loai(Phong, False)
        tong = len(phong)
        co_nguoi = sum(1 for ma in phong if ma in self.phong_co_nguoi)
        return tong - co_nguoi, co_nguoi, tong

    def thong_ke_ty_le_lap_day(self, toa_nha: ToaNha | None = None,
                               loai_phong: int | None = None) -> float:
        _, co_nguoi, tong = self.thong_ke_so_phong(toa_nha, loai_phong)
        return co_nguoi / tong if tong else 0.0

    def thong_ke_cong_no(self) -> tuple[float, int]:
        return self.cong_no_gia

    # ---------- Cấu hình / địa lý ----------
    def cap_nhat_cau_hinh(self, cau_hinh: CauHinhDong) -> None:
        self._cau_hinh = cau_hinh

    def doc_cau_hinh(self) -> CauHinhDong:
        if self._cau_hinh is None:
            raise ValueError("Chưa có cấu hình: truyền cau_hinh=... vào MockDieuPhoi")
        return self._cau_hinh

    def danh_sach_dia_ly(self) -> dict[str, Tinh]:
        if self._dia_ly is None:
            raise ValueError("Dữ liệu địa lý chưa được nạp (gọi nap_du_lieu_api trước)")
        return self._dia_ly


# ======================================================================
class TaiKhoanGia:
    """Thay TaiKhoan thật trong mock (không cần biết hàm khởi tạo của TaiKhoan)."""

    def __init__(self, tai_khoan: str, mat_khau: str, la_quan_tri: bool, ma_chu_the: str | None):
        self.ten_dang_nhap = tai_khoan
        self.mat_khau = mat_khau
        self.loai_tai_khoan = _tim_loai(la_quan_tri)
        self.ma_chu_the = ma_chu_the
        self.hoat_dong = True
        self._la_quan_tri = la_quan_tri

    @property
    def co_quyen_quan_tri(self) -> bool:
        return self._la_quan_tri

    def __repr__(self) -> str:
        return f"TaiKhoanGia({self.ten_dang_nhap!r}, quan_tri={self._la_quan_tri}, hoat_dong={self.hoat_dong})"


class MockPhien(GiaoThucPhienLamViec):
    def __init__(self, dieu_phoi: GiaoThucDieuPhoi | None = None, co_san_tai_khoan: bool = True):
        """co_san_tai_khoan=False để thử luồng tạo quản trị viên đầu tiên (chưa đăng nhập)."""
        self.dp = dieu_phoi
        self._tk: dict[str, TaiKhoanGia] = {}
        self._hien_tai: TaiKhoanGia | None = None
        if co_san_tai_khoan:
            self._tk["admin"] = TaiKhoanGia("admin", "123456", True, None)
            self._tk["sinhvien"] = TaiKhoanGia("sinhvien", "123456", False, "SV0001")

    # ---------- Trợ giúp ----------
    def _bat_buoc_admin(self) -> None:
        if self._hien_tai is None:
            raise PermissionError("Chưa đăng nhập")
        if not self._hien_tai.co_quyen_quan_tri:
            raise PermissionError("Không có quyền quản trị")

    def _lay(self, tai_khoan: str) -> TaiKhoanGia:
        if tai_khoan not in self._tk:
            raise ValueError("Tài khoản không tồn tại")
        return self._tk[tai_khoan]

    # ---------- Giao thức ----------
    @property
    def tai_khoan_hien_tai(self) -> TaiKhoan | None:
        return self._hien_tai  # type: ignore[return-value]

    def tao_tai_khoan(self, tai_khoan: str, mat_khau: str, loai_tai_khoan: LoaiTaiKhoan,
                      ma_chu_the: str | None) -> None:
        la_qt = _la_quan_tri(loai_tai_khoan)
        if not any(t.hoat_dong for t in self._tk.values()):
            if not la_qt:
                raise ValueError("Tài khoản đầu tiên phải là quản trị viên")
        else:
            self._bat_buoc_admin()
        if tai_khoan in self._tk:
            raise ValueError("Tài khoản đã tồn tại")
        if not la_qt and not ma_chu_the:
            raise ValueError("Tài khoản sinh viên cần mã sinh viên")
        self._tk[tai_khoan] = TaiKhoanGia(tai_khoan, mat_khau, la_qt, ma_chu_the)

    def dang_nhap(self, tai_khoan: str, mat_khau: str) -> None:
        if self._hien_tai is not None:
            raise ValueError("Đã có tài khoản đăng nhập")
        tk = self._lay(tai_khoan)
        if not tk.hoat_dong:
            raise ValueError("Tài khoản đã ngừng hoạt động")
        if tk.mat_khau != mat_khau:
            raise ValueError("Sai mật khẩu")
        self._hien_tai = tk

    def dang_xuat(self) -> None:
        if self._hien_tai is None:
            raise ValueError("Chưa đăng nhập")
        self._hien_tai = None

    def doi_mat_khau(self, mat_khau_moi: str, mat_khau_cu: str | None = None,
                     tai_khoan: str | None = None) -> None:
        if tai_khoan is not None:
            self._bat_buoc_admin()
            self._lay(tai_khoan).mat_khau = mat_khau_moi
            return
        if self._hien_tai is None:
            raise ValueError("Chưa đăng nhập")
        if mat_khau_cu is None or self._hien_tai.mat_khau != mat_khau_cu:
            raise ValueError("Mật khẩu cũ không đúng")
        self._hien_tai.mat_khau = mat_khau_moi

    def ngung_tai_khoan(self, tai_khoan: str) -> None:
        self._bat_buoc_admin()
        tk = self._lay(tai_khoan)
        if not tk.hoat_dong:
            raise ValueError("Tài khoản đã ngừng hoạt động")
        if tk is self._hien_tai:
            raise ValueError("Không thể ngừng chính tài khoản đang đăng nhập")
        so_admin = sum(1 for t in self._tk.values() if t.hoat_dong and t.co_quyen_quan_tri)
        if tk.co_quyen_quan_tri and so_admin <= 1:
            raise ValueError("Không thể ngừng quản trị viên hoạt động cuối cùng")
        tk.hoat_dong = False

    def kich_hoat_lai_tai_khoan(self, tai_khoan: str) -> None:
        self._bat_buoc_admin()
        tk = self._lay(tai_khoan)
        if tk.hoat_dong:
            raise ValueError("Tài khoản đang hoạt động")
        tk.hoat_dong = True

    def xoa_tai_khoan(self, tai_khoan: str) -> None:
        self._bat_buoc_admin()
        tk = self._lay(tai_khoan)
        if tk.hoat_dong:
            raise ValueError("Chỉ được xóa tài khoản đã ngừng hoạt động")
        if tk is self._hien_tai:
            raise ValueError("Không thể xóa chính tài khoản đang đăng nhập")
        del self._tk[tai_khoan]
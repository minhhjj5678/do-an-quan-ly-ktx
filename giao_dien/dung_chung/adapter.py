from typing import Any, Callable, TypeVar, cast
from datetime import date, datetime
import re

from giao_thuc.nghiep_vu import GiaoThucDieuPhoi, GiaoThucPhienLamViec
from thuc_the.dia_ly import Tinh
from thuc_the.ky_tuc_xa import ToaNha, SinhVien, Phong
from thuc_the.tai_chinh import HoaDonThang, HopDong
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from thuc_the.thuc_the_goc import ThucTheGoc, ThucTheLuuTruDuoc
from thuc_the.vi_pham import ViPham

T = TypeVar("T", bound=ThucTheGoc)


class Adapter:
    _NGHIEP_VU: dict[str, type[ThucTheGoc]] = {
        "thanh_toan_hop_dong": HopDong,
        "ket_thuc_hop_dong": HopDong,
        "thanh_toan_hoa_don_thang": HoaDonThang,
        "xu_ly_vi_pham": ViPham,
    }
    _THONG_KE = {"thong_ke_so_phong", "thong_ke_ty_le_lap_day", "thong_ke_cong_no"}

    def __init__(self, dieu_phoi: GiaoThucDieuPhoi, phien: GiaoThucPhienLamViec):
        self.dp = dieu_phoi
        self.phien = phien

    def nap_du_lieu_file(self) -> None:
        self.dp.nap_du_lieu_file()

    def nap_du_lieu_api(self) -> None:
        self.dp.nap_du_lieu_api()

    @property
    def tai_khoan_hien_tai(self) -> TaiKhoan | None:
        return self.phien.tai_khoan_hien_tai

    def dang_nhap(self, tai_khoan: str, mat_khau: str) -> None:
        self.phien.dang_nhap(tai_khoan, mat_khau)

    def dang_xuat(self) -> None:
        self.phien.dang_xuat()

    def la_admin(self) -> bool:
        tk = self.phien.tai_khoan_hien_tai
        if tk is None:
            return False
        quyen = tk.co_quyen_quan_tri
        return bool(quyen() if callable(quyen) else quyen)

    def la_sinh_vien(self) -> bool:
        """Chỉ nhận đúng vai trò Sinh viên, không mặc định 'không Admin' là Sinh viên."""
        tk = self.tai_khoan_hien_tai
        return tk is not None and tk.loai_tai_khoan == LoaiTaiKhoan.SINH_VIEN

    def ma_sinh_vien_hien_tai(self) -> str | None:
        if not self.la_sinh_vien():
            return None
        tk = self.tai_khoan_hien_tai
        return tk.ma_chu_the if tk is not None else None

    def _yeu_cau_admin(self) -> None:
        """Rào chắn cho các thao tác của giao diện; backend cũng phải kiểm quyền."""
        if self.tai_khoan_hien_tai is None:
            raise PermissionError('Bạn chưa đăng nhập.')
        if not self.la_admin():
            raise PermissionError('Chỉ Quản trị viên được thực hiện thao tác này.')

    def tao_tai_khoan(self, tai_khoan: str, mat_khau: str,
                      loai_tai_khoan: LoaiTaiKhoan, ma_chu_the: str | None = None) -> None:
        self.phien.tao_tai_khoan(tai_khoan, mat_khau, loai_tai_khoan, ma_chu_the)

    def doi_mat_khau(self, mat_khau_moi: str, mat_khau_cu: str | None = None,
                     tai_khoan: str | None = None) -> None:
        self.phien.doi_mat_khau(mat_khau_moi, mat_khau_cu, tai_khoan)

    def ngung_tai_khoan(self, tai_khoan: str) -> None:
        self.phien.ngung_tai_khoan(tai_khoan)

    def kich_hoat_lai_tai_khoan(self, tai_khoan: str) -> None:
        self.phien.kich_hoat_lai_tai_khoan(tai_khoan)

    def xoa_tai_khoan(self, tai_khoan: str) -> None:
        self.phien.xoa_tai_khoan(tai_khoan)

    @staticmethod
    def _cam_tai_khoan(loai: object) -> None:
        if isinstance(loai, type) and issubclass(loai, TaiKhoan):
            raise ValueError("TaiKhoan phải thao tác qua phiên làm việc, không qua CRUD.")

    def lay_tat_ca(self, loai: type[T], lay_luu_tru: bool = False) -> dict[str, T]:
        self._yeu_cau_admin()
        return self.dp.lay_tat_ca(loai, lay_luu_tru)

    def loc(self, loai: type[T], dieu_kien: Callable[[T], bool],
            lay_luu_tru: bool = False) -> dict[str, T]:
        self._yeu_cau_admin()
        return self.dp.loc_theo_dieu_kien(loai, dieu_kien, lay_luu_tru)

    def lay_theo_ma(self, loai: type[T], ma: str, lay_luu_tru: bool = False) -> T:
        self._yeu_cau_admin()
        return self.dp.lay_theo_ma(loai, ma, lay_luu_tru)

    @staticmethod
    def _gia_tri_ca_nhan(obj: object, ten: str):
        return obj.get(ten) if isinstance(obj, dict) else getattr(obj, ten, None)

    @staticmethod
    def _thang_hoa_don(value):
        if isinstance(value, date):
            return value.year, value.month
        nam, thang = getattr(value, 'nam', None), getattr(value, 'thang', None)
        if isinstance(nam, int) and isinstance(thang, int) and 1 <= thang <= 12:
            return nam, thang
        chuoi = str(value)
        ket_qua = re.fullmatch(r'(\d{4})-(\d{1,2})', chuoi)
        if ket_qua:
            nam, thang = int(ket_qua[1]), int(ket_qua[2])
            return (nam, thang) if 1 <= thang <= 12 else None
        ket_qua = re.fullmatch(r'(\d{1,2})/(\d{4})', chuoi)
        if ket_qua:
            thang, nam = int(ket_qua[1]), int(ket_qua[2])
            return (nam, thang) if 1 <= thang <= 12 else None
        return None

    @staticmethod
    def _ngay_hop_dong(gia_tri: object) -> date | None:
        """Đọc ngày từ thực thể thật hoặc dữ liệu giả lập đã được tuần tự hóa."""
        if isinstance(gia_tri, datetime):
            return gia_tri.date()
        if isinstance(gia_tri, date):
            return gia_tri
        if isinstance(gia_tri, str):
            for dinh_dang in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    return datetime.strptime(gia_tri.strip(), dinh_dang).date()
                except ValueError:
                    continue
        return None

    def _ngay_het_hieu_luc(self, hop_dong: object) -> date | None:
        """Ưu tiên ngày hết hạn; ngày kết thúc được dùng khi đã chấm dứt sớm."""
        g = self._gia_tri_ca_nhan
        ngay_het_han = self._ngay_hop_dong(g(hop_dong, 'ngay_het_han'))
        ngay_ket_thuc = self._ngay_hop_dong(g(hop_dong, 'ngay_ket_thuc'))
        trang_thai = self._ten_trang_thai(hop_dong)
        if trang_thai in {'DA_KET_THUC', 'KET_THUC', 'DA_HUY', 'HUY'}:
            if ngay_het_han is not None and ngay_ket_thuc is not None:
                return min(ngay_het_han, ngay_ket_thuc)
            return ngay_ket_thuc or ngay_het_han
        return ngay_het_han or ngay_ket_thuc

    def _hop_dong_dang_o(self, hop_dong: object, hom_nay: date) -> bool:
        """Xác định phòng hiện tại bằng hiệu lực hợp đồng và quy tắc backend."""
        if self._ten_trang_thai(hop_dong) in {
            'DA_KET_THUC', 'KET_THUC', 'DA_HUY', 'HUY'
        }:
            return False
        # Điều phối thật cũng sử dụng HopDong.con_giu_cho() khi xác định phòng có người.
        con_giu_cho = getattr(hop_dong, 'con_giu_cho', None)
        if callable(con_giu_cho) and not con_giu_cho():
            return False
        ngay_bat_dau = self._ngay_hop_dong(
            self._gia_tri_ca_nhan(hop_dong, 'ngay_bat_dau'))
        ngay_het_han = self._ngay_het_hieu_luc(hop_dong)
        return (ngay_bat_dau is not None and ngay_het_han is not None
                and ngay_bat_dau <= hom_nay <= ngay_het_han)

    def _hoa_don_thuoc_hop_dong(self, hoa_don: object, hop_dong: object) -> bool:
        """Hóa đơn của đúng phòng, đúng tháng sinh viên có hợp đồng ở phòng đó."""
        g = self._gia_tri_ca_nhan
        ma_phong_hoa_don = g(hoa_don, 'phong')
        ma_phong_hop_dong = g(hop_dong, 'ma_phong')
        if (not ma_phong_hoa_don or not ma_phong_hop_dong
                or str(ma_phong_hoa_don).strip() != str(ma_phong_hop_dong).strip()):
            return False
        thang = self._thang_hoa_don(g(hoa_don, 'thang_nam'))
        bat_dau = self._ngay_hop_dong(g(hop_dong, 'ngay_bat_dau'))
        het_hieu_luc = self._ngay_het_hieu_luc(hop_dong)
        if thang is None or bat_dau is None or het_hieu_luc is None:
            return False
        return ((bat_dau.year, bat_dau.month) <= thang
                <= (het_hieu_luc.year, het_hieu_luc.month))

    @staticmethod
    def _ten_trang_thai(obj: object) -> str:
        """Hỗ trợ cả trạng thái Enum thật và chuỗi của Mock."""
        import unicodedata
        value = Adapter._gia_tri_ca_nhan(obj, 'trang_thai')
        ten = str(getattr(value, 'name', value) or '').upper()
        ten = ''.join(c for c in unicodedata.normalize('NFD', ten)
                      if unicodedata.category(c) != 'Mn')
        return ten.replace('Đ', 'D').replace(' ', '_').replace('-', '_')

    def lay_du_lieu_ca_nhan(self) -> dict[str, Any]:
        """Chỉ lấy dữ liệu thuộc mã SV trong phiên đăng nhập.

        Phòng/tòa nhà gắn với hợp đồng còn hiệu lực theo backend. Hóa đơn chỉ gồm
        các khoản CHƯA THANH TOÁN trong thời gian hợp đồng; vi phạm chỉ
        gồm những mục CHƯA XỬ LÝ. Không cho phép sửa.
        """
        if not self.la_sinh_vien():
            raise PermissionError('Chỉ Sinh viên được xem dữ liệu qua chức năng này.')
        ma = self.ma_sinh_vien_hien_tai()
        if not ma:
            raise ValueError('Tài khoản chưa liên kết mã sinh viên (ma_chu_the).')
        g = self._gia_tri_ca_nhan
        ma = ma.strip()
        sinh_vien = self.dp.lay_tat_ca(SinhVien, lay_luu_tru=True).get(ma)
        hop_dong = [hd for hd in self.dp.lay_tat_ca(HopDong, lay_luu_tru=True).values()
                    if str(g(hd, 'ma_sinh_vien') or '').strip() == ma]

        # Hợp đồng vẫn hiển thị trong mục Hợp đồng; riêng Phòng/Tòa nhà chỉ
        # lấy hợp đồng giữ chỗ có hiệu lực theo quy tắc của backend.
        hom_nay = date.today()
        hd_hien_tai = [hd for hd in hop_dong if self._hop_dong_dang_o(hd, hom_nay)]
        hd_hien_tai.sort(
            key=lambda hd: self._ngay_hop_dong(g(hd, 'ngay_bat_dau')) or date.min,
            reverse=True,
        )
        ma_phong = None
        if hd_hien_tai:
            ma_phong = str(g(hd_hien_tai[0], 'ma_phong') or '').strip() or None
        phong_hien_tai = (self.dp.lay_tat_ca(Phong, lay_luu_tru=True).get(ma_phong)
                          if ma_phong else None)
        toa_nha = None
        if phong_hien_tai is not None:
            ma_toa_nha = str(g(phong_hien_tai, 'toa_nha') or '').strip()
            toa_nha = self.dp.lay_tat_ca(ToaNha, lay_luu_tru=True).get(ma_toa_nha)

        hoa_don = [hd for hd in self.dp.lay_tat_ca(HoaDonThang, lay_luu_tru=True).values()
                   if self._ten_trang_thai(hd) in ('', 'CHUA_THANH_TOAN')
                   and any(self._hoa_don_thuoc_hop_dong(hd, hop) for hop in hop_dong)]
        vi_pham = [vp for vp in self.dp.lay_tat_ca(ViPham, lay_luu_tru=True).values()
                   if str(g(vp, 'sinh_vien') or '').strip() == ma
                   and self._ten_trang_thai(vp) in ('', 'CHUA_XU_LY')]
        return {
            'sinh_vien': sinh_vien,
            'phong': [phong_hien_tai] if phong_hien_tai else [],
            'toa_nha': [toa_nha] if toa_nha else [],
            'hop_dong': hop_dong,
            'hoa_don': hoa_don,
            'vi_pham': vi_pham,
        }

    def tao_va_them(self, loai: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        self._yeu_cau_admin()
        self._cam_tai_khoan(loai)
        return self.dp.tao_va_them(loai, *args, **kwargs)

    def cap_nhat(self, thuc_the: ThucTheGoc) -> None:
        self._yeu_cau_admin()
        self._cam_tai_khoan(type(thuc_the))
        self.dp.cap_nhat(thuc_the)

    def cap_nhat_truong(self, loai: type[T], ma: str, **du_lieu: Any) -> T:
        self._yeu_cau_admin()
        self._cam_tai_khoan(loai)
        thuc_the = self.dp.lay_theo_ma(loai, ma)
        for truong, gia_tri in du_lieu.items():
            if not hasattr(thuc_the, truong):
                raise ValueError(f"{loai.__name__} không có trường '{truong}'")
            setattr(thuc_the, truong, gia_tri)
        self.dp.cap_nhat(thuc_the)
        return thuc_the

    def _lay_thuc_the_luu_tru_duoc(self, loai: type[ThucTheGoc], ma: str,
                                   lay_luu_tru: bool) -> ThucTheLuuTruDuoc:
        self._cam_tai_khoan(loai)
        if not issubclass(loai, ThucTheLuuTruDuoc):
            raise ValueError(f"{loai.__name__} không phải thực thể lưu trữ được.")
        return cast(ThucTheLuuTruDuoc, self.dp.lay_theo_ma(loai, ma, lay_luu_tru))

    def luu_tru(self, loai: type[ThucTheGoc], ma: str) -> None:
        self._yeu_cau_admin()
        self.dp.luu_tru(self._lay_thuc_the_luu_tru_duoc(loai, ma, lay_luu_tru=False))

    def tai_kich_hoat(self, loai: type[ThucTheGoc], ma: str) -> None:
        self._yeu_cau_admin()
        self.dp.tai_kich_hoat(self._lay_thuc_the_luu_tru_duoc(loai, ma, lay_luu_tru=True))

    def xoa(self, loai: type[ThucTheGoc], ma: str, ep_xoa: bool = False) -> None:
        self._yeu_cau_admin()
        self._cam_tai_khoan(loai)
        self.dp.xoa(self.dp.lay_theo_ma(loai, ma, lay_luu_tru=True), ep_xoa)

    def dia_ly(self, tinh: str | None = None) -> dict[str, Tinh] | Tinh:
        ds = self.dp.danh_sach_dia_ly()
        return ds if tinh is None else ds[tinh]

    def nghiep_vu(self, ten: str, ma: str) -> None:
        self._yeu_cau_admin()
        loai = self._NGHIEP_VU.get(ten)
        if loai is None:
            raise ValueError("Nghiệp vụ không hợp lệ")
        thuc_the = self.dp.lay_theo_ma(loai, ma)
        getattr(self.dp, ten)(thuc_the)

    def thong_ke(self, ten: str, bo_loc: dict[str, Any] | None = None):
        self._yeu_cau_admin()
        if ten not in self._THONG_KE:
            raise ValueError("Thống kê không hợp lệ")
        bo_loc = dict(bo_loc or {})
        if isinstance(bo_loc.get("toa_nha"), str):
            bo_loc["toa_nha"] = self.dp.lay_theo_ma(ToaNha, bo_loc["toa_nha"])
        return getattr(self.dp, ten)(**bo_loc)

    def doc_cau_hinh(self):
        return self.dp.doc_cau_hinh()

    def cap_nhat_cau_hinh(self, cau_hinh) -> None:
        self._yeu_cau_admin()
        self.dp.cap_nhat_cau_hinh(cau_hinh)

from typing import Any, Callable, TypeVar, cast

from giao_thuc.nghiep_vu import GiaoThucDieuPhoi, GiaoThucPhienLamViec
from thuc_the.dia_ly import Tinh
from thuc_the.ky_tuc_xa import ToaNha
from thuc_the.tai_chinh import HoaDonThang, HopDong
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from thuc_the.thuc_the_goc import ThucTheGoc, ThucTheLuuTruDuoc
from thuc_the.vi_pham import ViPham

T = TypeVar("T", bound=ThucTheGoc)


class Adapter:
    # Nghiệp vụ đổi trạng thái: tên hàm -> loại thực thể mà hàm nhận vào
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

    # ---------- Khởi động ----------
    def nap_du_lieu_file(self) -> None:
        """Gọi đúng một lần khi mở app."""
        self.dp.nap_du_lieu_file()

    def nap_du_lieu_api(self) -> None:
        """Phải gọi trong luồng phụ. Ném OSError nếu thất bại, có thể gọi lại."""
        self.dp.nap_du_lieu_api()

    # ---------- Phiên làm việc / tài khoản ----------
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
        quyen = tk.co_quyen_quan_tri  # thuộc tính hoặc phương thức đều xử lý được
        return bool(quyen() if callable(quyen) else quyen)

    def tao_tai_khoan(self, tai_khoan: str, mat_khau: str,
                      loai_tai_khoan: LoaiTaiKhoan, ma_chu_the: str | None = None) -> None:
        # ma_chu_the = mã sinh viên nếu là tài khoản sinh viên, admin thì để None
        self.phien.tao_tai_khoan(tai_khoan, mat_khau, loai_tai_khoan, ma_chu_the)

    def doi_mat_khau(self, mat_khau_moi: str, mat_khau_cu: str | None = None,
                     tai_khoan: str | None = None) -> None:
        # tai_khoan=None: đổi của mình (bắt buộc mat_khau_cu); có tai_khoan: admin reset
        self.phien.doi_mat_khau(mat_khau_moi, mat_khau_cu, tai_khoan)

    def ngung_tai_khoan(self, tai_khoan: str) -> None:
        self.phien.ngung_tai_khoan(tai_khoan)

    def kich_hoat_lai_tai_khoan(self, tai_khoan: str) -> None:
        self.phien.kich_hoat_lai_tai_khoan(tai_khoan)

    def xoa_tai_khoan(self, tai_khoan: str) -> None:
        self.phien.xoa_tai_khoan(tai_khoan)

    # ---------- CRUD ----------
    @staticmethod
    def _cam_tai_khoan(loai: object) -> None:
        # Quy ước: ghi TaiKhoan chỉ đi qua GiaoThucPhienLamViec
        if isinstance(loai, type) and issubclass(loai, TaiKhoan):
            raise ValueError("TaiKhoan phải thao tác qua phiên làm việc, không qua CRUD.")

    def lay_tat_ca(self, loai: type[T], lay_luu_tru: bool = False) -> dict[str, T]:
        return self.dp.lay_tat_ca(loai, lay_luu_tru)

    def loc(self, loai: type[T], dieu_kien: Callable[[T], bool],
            lay_luu_tru: bool = False) -> dict[str, T]:
        return self.dp.loc_theo_dieu_kien(loai, dieu_kien, lay_luu_tru)

    def lay_theo_ma(self, loai: type[T], ma: str, lay_luu_tru: bool = False) -> T:
        return self.dp.lay_theo_ma(loai, ma, lay_luu_tru)

    def tao_va_them(self, loai: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Mã tự sinh, chỉ truyền các tham số còn lại. VD: tao_va_them(SinhVien, ten=..., ...)"""
        self._cam_tai_khoan(loai)
        return self.dp.tao_va_them(loai, *args, **kwargs)

    def cap_nhat(self, thuc_the: ThucTheGoc) -> None:
        """Dùng khi bạn đã sửa thuộc tính trên đối tượng."""
        self._cam_tai_khoan(type(thuc_the))
        self.dp.cap_nhat(thuc_the)

    def cap_nhat_truong(self, loai: type[T], ma: str, **du_lieu: Any) -> T:
        """Lấy thực thể theo mã, gán các trường mới rồi cập nhật."""
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
        self.dp.luu_tru(self._lay_thuc_the_luu_tru_duoc(loai, ma, lay_luu_tru=False))

    def tai_kich_hoat(self, loai: type[ThucTheGoc], ma: str) -> None:
        # thực thể đang lưu trữ nên phải lay_luu_tru=True
        self.dp.tai_kich_hoat(self._lay_thuc_the_luu_tru_duoc(loai, ma, lay_luu_tru=True))

    def xoa(self, loai: type[ThucTheGoc], ma: str, ep_xoa: bool = False) -> None:
        self._cam_tai_khoan(loai)
        self.dp.xoa(self.dp.lay_theo_ma(loai, ma, lay_luu_tru=True), ep_xoa)

    # ---------- Địa lý ----------
    def dia_ly(self, tinh: str | None = None) -> dict[str, Tinh] | Tinh:
        ds = self.dp.danh_sach_dia_ly()  # ném lỗi nếu chưa nạp xong
        return ds if tinh is None else ds[tinh]

    # ---------- Nghiệp vụ ----------
    def nghiep_vu(self, ten: str, ma: str) -> None:
        loai = self._NGHIEP_VU.get(ten)
        if loai is None:
            raise ValueError("Nghiệp vụ không hợp lệ")
        thuc_the = self.dp.lay_theo_ma(loai, ma)
        getattr(self.dp, ten)(thuc_the)

    # ---------- Thống kê ----------
    def thong_ke(self, ten: str, bo_loc: dict[str, Any] | None = None):
        if ten not in self._THONG_KE:
            raise ValueError("Thống kê không hợp lệ")
        bo_loc = dict(bo_loc or {})
        # toa_nha có thể truyền là mã (str) hoặc đối tượng ToaNha
        if isinstance(bo_loc.get("toa_nha"), str):
            bo_loc["toa_nha"] = self.dp.lay_theo_ma(ToaNha, bo_loc["toa_nha"])
        return getattr(self.dp, ten)(**bo_loc)

    # ---------- Cấu hình ----------
    def doc_cau_hinh(self):
        return self.dp.doc_cau_hinh()

    def cap_nhat_cau_hinh(self, cau_hinh) -> None:
        self.dp.cap_nhat_cau_hinh(cau_hinh)
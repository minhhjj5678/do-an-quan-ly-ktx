from typing import Callable, TypeVar, List, dict
from giao_thuc.nghiep_vu import GiaoThucDieuPhoi
from giao_thuc.luu_tru import GiaoThucLuuTru
from thuc_the.thuc_the_goc import ThucTheGoc, ThucTheLuuTruDuoc
from thuc_the.dia_ly import Tinh
from thuc_the.hoc_vu import HocKy
from thuc_the.tai_chinh import HopDong, HoaDonThang, TrangThaiHopDong, TrangThaiHoaDon
from thuc_the.vi_pham import ViPham
from thuc_the.ky_tuc_xa import ToaNha, SinhVien, Phong
from tien_ich.cau_hinh_dong import CauHinhDong
from luu_tru.luu_tru_dia_ly import LuuTruDiaLy

T = TypeVar("T", bound=ThucTheGoc)

class QuanLyDieuPhoi(GiaoThucDieuPhoi):
    def __init__(self, danh_sach_luu_tru: dict[type, GiaoThucLuuTru]):
        # Map từ Type -> Lớp lưu trữ tương ứng
        self._luu_tru = danh_sach_luu_tru
        self._luu_tru_dia_ly = LuuTruDiaLy()
        self._cau_hinh = CauHinhDong()

    def _get_luu_tru(self, loai_thuc_the: type[T]) -> GiaoThucLuuTru[T]:
        if loai_thuc_the not in self._luu_tru:
            raise ValueError(f"Chưa đăng ký lớp lưu trữ cho thực thể {loai_thuc_the.__name__}")
        return self._luu_tru[loai_thuc_the]

    def lay_tat_ca(self, loai_thuc_the: type[T], lay_luu_tru: bool = False) -> list[T]:
        lt = self._get_luu_tru(loai_thuc_the)
        tat_ca = lt.doc()
        if lay_luu_tru:
            return tat_ca
        return [item for item in tat_ca if getattr(item, "con_hoat_dong", True)]

    def lay_theo_ma(self, loai_thuc_the: type[T], ma: str, lay_luu_tru: bool = False) -> T:
        danh_sach = self.lay_tat_ca(loai_thuc_the, lay_luu_tru=lay_luu_tru)
        for item in danh_sach:
            if item.ma == ma:
                return item
        raise ValueError(f"Không tìm thấy thực thể {loai_thuc_the.__name__} với mã '{ma}'.")

    def them(self, loai_thuc_the: type[T], thuc_the: T) -> None:
        lt = self._get_luu_tru(loai_thuc_the)
        tat_ca = lt.doc()
        if any(item.ma == thuc_the.ma for item in tat_ca):
            raise ValueError(f"Mã '{thuc_the.ma}' đã tồn tại trong hệ thống.")
        tat_ca.append(thuc_the)
        lt.ghi(tat_ca)

    def cap_nhat(self, loai_thuc_the: type[T], thuc_the: T) -> None:
        lt = self._get_luu_tru(loai_thuc_the)
        tat_ca = lt.doc()
        index = -1
        for i, item in enumerate(tat_ca):
            if item.ma == thuc_the.ma:
                index = i
                break
        if index == -1:
            raise ValueError(f"Không tìm thấy thực thể cần cập nhật: {thuc_the.ma}")
        tat_ca[index] = thuc_the
        lt.ghi(tat_ca)

    def xoa(self, loai_thuc_the: type[T], thuc_the: T, ep_xoa: bool = False) -> None:
        lt = self._get_luu_tru(loai_thuc_the)
        danh_sach_hd = self.lay_tat_ca(HopDong, lay_luu_tru=True)
        
        # Kiểm tra ràng buộc HopDong
        co_rang_buoc = any(hd.ma_sinh_vien == thuc_the.ma or hd.ma_phong == thuc_the.ma for hd in danh_sach_hd)
        if co_rang_buoc and not ep_xoa:
            raise ValueError(f"Thực thể '{thuc_the.ma}' đang vướng Hợp đồng. Không thể xóa (Dùng ep_xoa=True để xóa đè).")

        if co_rang_buoc and ep_xoa:
            lt_hd = self._get_luu_tru(HopDong)
            ds_hd_moi = [hd for hd in danh_sach_hd if hd.ma_sinh_vien != thuc_the.ma and hd.ma_phong != thuc_the.ma]
            lt_hd.ghi(ds_hd_moi)

        tat_ca = [item for item in lt.doc() if item.ma != thuc_the.ma]
        lt.ghi(tat_ca)

    def loc_theo_dieu_kien(self, loai_thuc_the: type[T], dieu_kien: Callable[[T], bool], lay_luu_tru: bool = False) -> list[T]:
        tat_ca = self.lay_tat_ca(loai_thuc_the, lay_luu_tru=lay_luu_tru)
        return [item for item in tat_ca if dieu_kien(item)]

    def luu_tru(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        if not thuc_the.con_hoat_dong:
            raise ValueError("Thực thể đã ở trạng thái ngừng hoạt động.")
        thuc_the.luu_tru()
        if isinstance(thuc_the, ThucTheGoc):
            self.cap_nhat(type(thuc_the), thuc_the)

    def tai_kich_hoat(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        if thuc_the.con_hoat_dong:
            raise ValueError("Thực thể đang hoạt động bình thường.")
        thuc_the.tai_kich_hoat()
        if isinstance(thuc_the, ThucTheGoc):
            self.cap_nhat(type(thuc_the), thuc_the)

    # Logic Hợp đồng, Hóa đơn, Vi phạm
    def thanh_toan_hop_dong(self, hop_dong: HopDong) -> None:
        hop_dong.thanh_toan()
        self.cap_nhat(HopDong, hop_dong)

    def ket_thuc_hop_dong(self, hop_dong: HopDong) -> None:
        hop_dong.ket_thuc()
        self.cap_nhat(HopDong, hop_dong)

    def thanh_toan_hoa_don_thang(self, hoa_don_thang: HoaDonThang) -> None:
        hoa_don_thang.thanh_toan()
        self.cap_nhat(HoaDonThang, hoa_don_thang)

    def xu_ly_vi_pham(self, vi_pham: ViPham) -> None:
        vi_pham.xu_ly()
        self.cap_nhat(type(vi_pham), vi_pham)

    # Thống kê
    def thong_ke_so_phong(self, hoc_ky: HocKy, toa_nha: ToaNha | None = None, loai_phong: int | None = None) -> tuple[int, int, int]:
        ds_phong = self.lay_tat_ca(Phong)
        if toa_nha:
            ds_phong = [p for p in ds_phong if getattr(p, "ma_toa_nha", "") == toa_nha.ma]
        if loai_phong is not None:
            ds_phong = [p for p in ds_phong if getattr(p, "suc_chua", 0) == loai_phong]

        ds_hd = self.loc_theo_dieu_kien(HopDong, lambda hd: hd.hoc_ky == hoc_ky.ma and hd.trang_thai == TrangThaiHopDong.DA_THANH_TOAN)
        phong_da_thue = {hd.ma_phong for hd in ds_hd}

        tong = len(ds_phong)
        da_thue = sum(1 for p in ds_phong if p.ma in phong_da_thue)
        trong = tong - da_thue
        return trong, da_thue, tong

    def thong_ke_ty_le_lap_day(self, hoc_ky: HocKy, toa_nha: ToaNha | None = None, loai_phong: int | None = None) -> float:
        trong, da_thue, tong = self.thong_ke_so_phong(hoc_ky, toa_nha, loai_phong)
        if tong == 0:
            return 0.0
        return round(da_thue / tong, 4)

    def thong_ke_cong_no(self, hoc_ky: HocKy | None = None) -> tuple[float, int]:
        ds_hd = self.lay_tat_ca(HopDong)
        ds_hd_thang = self.lay_tat_ca(HoaDonThang)

        if hoc_ky:
            ds_hd = [hd for hd in ds_hd if hd.hoc_ky == hoc_ky.ma]

        tong_no = 0.0
        sv_no = set()

        for hd in ds_hd:
            if hd.trang_thai == TrangThaiHopDong.CHUA_THANH_TOAN:
                tong_no += hd.tong_tien()
                sv_no.add(hd.ma_sinh_vien)

        for hdt in ds_hd_thang:
            if hdt.trang_thai == TrangThaiHoaDon.CHUA_THANH_TOAN:
                tong_no += hdt.tong_tien()

        return tong_no, len(sv_no)

    # Cấu hình & Địa lý
    def cap_nhat_cau_hinh(self, cau_hinh: CauHinhDong) -> None:
        self._cau_hinh = cau_hinh

    def doc_cau_hinh(self) -> CauHinhDong:
        return self._cau_hinh

    def danh_sach_dia_ly(self) -> list[Tinh]:
        return self._luu_tru_dia_ly.doc()
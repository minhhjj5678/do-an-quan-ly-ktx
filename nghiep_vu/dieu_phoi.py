import copy
from typing import Callable, Concatenate, cast, Any

from giao_thuc.luu_tru import GiaoThucLuuTru
from giao_thuc.nghiep_vu import GiaoThucDieuPhoi, T, P
from luu_tru.luu_tru_cau_hinh import LuuTruCauHinh
from nghiep_vu.kiem_cheo_du_lieu import KhoDuLieu, kiem_cheo_du_lieu
from thuc_the.dia_ly import Tinh
from thuc_the.ky_tuc_xa import Phong, SinhVien, ToaNha
from thuc_the.tai_chinh import HoaDonThang, HopDong, TrangThaiHopDong
from thuc_the.tai_khoan import TaiKhoan
from thuc_the.thuc_the_goc import ThucTheLuuTruDuoc, ThucTheGoc
from thuc_the.vi_pham import TrangThaiViPham, ViPham
from tien_ich.cau_hinh_dong import CauHinhDong
from tien_ich.tao_ma import ma_hoa_don_thang, ma_hop_dong, ma_sinh_vien, ma_toa_nha, ma_vi_pham, ma_phong


class DieuPhoiKTX(GiaoThucDieuPhoi):
    def __init__(self, kho_luu_tru: dict[type[ThucTheGoc], GiaoThucLuuTru], luu_tru_cau_hinh: LuuTruCauHinh):
        self.__kho_du_lieu: dict[type[ThucTheGoc], dict[str, Any]] = {
            SinhVien: {},
            Phong: {},
            ToaNha: {},
            HopDong: {},
            HoaDonThang: {},
            ViPham: {},
            TaiKhoan: {},
            Tinh: {}
        }
        self.__kho_luu_tru = kho_luu_tru
        self.__luu_tru_cau_hinh = luu_tru_cau_hinh

    def nap_du_lieu_file(self) -> None:
        loi = []
        for loai_thuc_the in self.__kho_du_lieu.keys():
            if loai_thuc_the is Tinh:
                continue
            try:
                kho_luu_tru = self.__kho_luu_tru.get(loai_thuc_the)
                if kho_luu_tru is None:
                    raise ValueError(f"Kho lưu trữ {loai_thuc_the.__name__} chưa được đăng ký trong hàm khởi tạo")

                if kho_luu_tru.co_bi_chinh_sua():
                    self.__kho_du_lieu[loai_thuc_the] = kho_luu_tru.doc_sao_luu()
                else:
                    try:
                        self.__kho_du_lieu[loai_thuc_the] = kho_luu_tru.doc()
                    except (FileNotFoundError, ValueError):
                        self.__kho_du_lieu[loai_thuc_the] = kho_luu_tru.doc_sao_luu()
            except Exception as e:
                loi.append(f"Lỗi xảy ra khi nạp dữ liệu file {loai_thuc_the.__name__}: {e}")

        if not loi:
            loi.extend(self.__kiem_cheo(self.__kho_du_lieu))

        if loi:
            raise ValueError("\n".join(loi))

    def nap_du_lieu_api(self) -> None:
        kho_dl = self.__kho_luu_tru.get(Tinh)
        if kho_dl is not None:
            if not kho_dl.co_bi_chinh_sua():
                try:
                    self.__kho_du_lieu[Tinh] = kho_dl.doc()
                except FileNotFoundError:
                    self.__kho_du_lieu[Tinh] = kho_dl.doc_sao_luu()
            else:
                self.__kho_du_lieu[Tinh] = kho_dl.doc_sao_luu()

            kho_dl.ghi(self.__kho_du_lieu[Tinh])
        else:
            raise ValueError("Kho lưu trữ Tinh chưa được đăng ký trong hàm khởi tạo")


    # các hàm crud
    def lay_tat_ca(self, loai_thuc_the: type[T], lay_luu_tru: bool = False) -> dict[str, T]:
        self.__kiem_tra_loai_thuc_the_hop_le(loai_thuc_the, ghi=False)
        kho = self.__kho_du_lieu[loai_thuc_the]
        if lay_luu_tru:
            return {ma: copy.copy(doi_tuong) for ma, doi_tuong in kho.items()}
        else:
            du_lieu = {ma: cast(T, copy.copy(doi_tuong)) for ma, doi_tuong in kho.items() if (isinstance(doi_tuong, ThucTheLuuTruDuoc) and doi_tuong.con_hoat_dong) or not isinstance(doi_tuong, ThucTheLuuTruDuoc)}
            return du_lieu
        
    def them(self, thuc_the: ThucTheGoc) -> None:
        self.__kiem_tra_loai_thuc_the_hop_le(type(thuc_the))
        kho_tam = self.__kho_du_lieu[type(thuc_the)].copy()
        if thuc_the.ma in kho_tam:
            raise ValueError("Mã thực thể đã tồn tại trong kho lưu trữ")

        kho_can_kiem_tra = self.__kho_du_lieu.copy()
        kho_tam[thuc_the.ma] = copy.copy(thuc_the)
        kho_can_kiem_tra[type(thuc_the)] = kho_tam
        self.__kiem_cheo_nem_loi(kho_can_kiem_tra)

        self.__kho_luu_tru[type(thuc_the)].ghi(kho_tam)
        self.__kho_du_lieu[type(thuc_the)] = kho_tam

    def tao_va_them(self, loai_thuc_the: Callable[Concatenate[str, P], T], *args: P.args, **kwargs: P.kwargs) -> T:
        if not isinstance(loai_thuc_the, type) or not issubclass(loai_thuc_the, ThucTheGoc):
            raise TypeError("loai_thuc_the phải là một lớp")
        self.__kiem_tra_loai_thuc_the_hop_le(loai_thuc_the)

        bang_anh_xa_tao_ma = {
            SinhVien: ma_sinh_vien,
            Phong: ma_phong,
            ToaNha: ma_toa_nha,
            HopDong: ma_hop_dong,
            HoaDonThang: ma_hoa_don_thang,
            ViPham: ma_vi_pham,
        }

        if loai_thuc_the not in bang_anh_xa_tao_ma:
            raise ValueError("Loại thực thể không hợp lệ")
        ma = bang_anh_xa_tao_ma[loai_thuc_the](self.__kho_du_lieu[loai_thuc_the]) # type: ignore
        if ma in self.__kho_du_lieu[loai_thuc_the]:
            raise ValueError(f"Thực thể {loai_thuc_the.__name__} với mã {ma} đã tồn tại")
        doi_tuong = loai_thuc_the(ma, *args, **kwargs)

        kho_tam = self.__kho_du_lieu[loai_thuc_the].copy() # type: ignore
        kho_tam[doi_tuong.ma] = doi_tuong
        kho_can_kiem_tra = self.__kho_du_lieu.copy()
        kho_can_kiem_tra[loai_thuc_the] = kho_tam # type: ignore
        self.__kiem_cheo_nem_loi(kho_can_kiem_tra)

        self.__kho_luu_tru[loai_thuc_the].ghi(kho_tam) # type: ignore
        self.__kho_du_lieu[loai_thuc_the] = kho_tam # type: ignore
        return cast(T, copy.copy(doi_tuong))

    def xoa(self, thuc_the: ThucTheGoc, ep_xoa: bool = False) -> None:
        self.__kiem_tra_loai_thuc_the_hop_le(thuc_the)

        kho_tam = self.__kho_du_lieu[type(thuc_the)].copy()
        kho_tam.pop(thuc_the.ma)
        kho_can_kiem_tra = self.__kho_du_lieu.copy()
        kho_can_kiem_tra[type(thuc_the)] = kho_tam
        self.__kiem_cheo_nem_loi(kho_can_kiem_tra)

        if isinstance(thuc_the, ThucTheLuuTruDuoc) and not ep_xoa:
            raise ValueError("Thực thể này có thể lưu trữ được, việc xóa có thể gây hư hại đến dữ liệu, bạn vẫn muốn xóa?")
        if not ep_xoa:
            raise ValueError("Việc xóa sẽ không thể hoàn tác và có thể gây ảnh hưởng đến dữ liệu, bạn vẫn muốn xóa?")

        self.__kho_luu_tru[type(thuc_the)].ghi(kho_tam)
        self.__kho_du_lieu[type(thuc_the)] = kho_tam

    def lay_theo_ma(self, loai_thuc_the: type[T], ma: str, lay_luu_tru: bool = False) -> T:
        self.__kiem_tra_loai_thuc_the_hop_le(loai_thuc_the, ghi=False)
        kho = self.__kho_du_lieu[loai_thuc_the]
        doi_tuong = kho.get(ma)
        if doi_tuong is None:
            raise ValueError("Thực thể không tồn tại trong cơ sở dữ liệu")

        if not lay_luu_tru and isinstance(doi_tuong, ThucTheLuuTruDuoc) and not doi_tuong.con_hoat_dong:
            raise ValueError("Thực thể không còn hoạt động")

        doi_tuong_ban_sao = copy.copy(doi_tuong)
        return cast(T, doi_tuong_ban_sao)

    def loc_theo_dieu_kien(self, loai_thuc_the: type[T], dieu_kien: Callable[[T], bool], lay_luu_tru: bool = False) -> \
    dict[str, T]:
        kho = self.lay_tat_ca(loai_thuc_the, lay_luu_tru)
        return {ma: doi_tuong for ma, doi_tuong in kho.items() if dieu_kien(doi_tuong)}

    def cap_nhat(self, thuc_the: ThucTheGoc) -> None:
        self.__kiem_tra_loai_thuc_the_hop_le(thuc_the)
        thuc_the_goc = self.__kho_du_lieu[type(thuc_the)][thuc_the.ma]
        if isinstance(thuc_the, ViPham):
            if thuc_the_goc.trang_thai == TrangThaiViPham.DA_XU_LY:
                raise ValueError("Không thể cập nhật vi phạm đã xử lý")
            elif thuc_the.trang_thai != thuc_the_goc.trang_thai:
                raise ValueError("Không thể cập nhật trạng thái vi phạm, hãy dùng hàm nghiệp vụ tương ứng")
        elif isinstance(thuc_the, HopDong):
            raise ValueError("Không thể cập nhật hợp đồng sau khi tạo, vui lòng xóa và tạo lại hợp đồng nếu muốn thay đổi thông tin")
        elif isinstance(thuc_the, HoaDonThang):
            raise ValueError("Không thể cập nhật hóa đơn tháng sau khi tạo, vui lòng xóa và tạo lại hóa đơn nếu muốn thay đổi thông tin")

        if isinstance(thuc_the, ThucTheLuuTruDuoc):
            if thuc_the.con_hoat_dong != thuc_the_goc.con_hoat_dong:
                raise ValueError("Không thể cập nhật trạng thái thực thể lưu trữ được, hãy dùng hàm nghiệp vụ tương ứng")

        kho_tam = self.__kho_du_lieu[type(thuc_the)].copy()
        kho_tam[thuc_the.ma] = copy.copy(thuc_the)
        kho_can_kiem_tra = self.__kho_du_lieu.copy()
        kho_can_kiem_tra[type(thuc_the)] = kho_tam
        self.__kiem_cheo_nem_loi(kho_can_kiem_tra)

        self.__kho_luu_tru[type(thuc_the)].ghi(kho_tam)
        self.__kho_du_lieu[type(thuc_the)] = kho_tam

    def luu_tru(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        self.__kiem_tra_loai_thuc_the_hop_le(thuc_the)
        if not isinstance(thuc_the, ToaNha):
            self.__kiem_cheo_va_ghi(type(thuc_the), thuc_the.ma, lambda tt: tt.luu_tru()) # type: ignore
            return

        kho_can_kiem_tra = {loai: kho.copy() for loai, kho in self.__kho_du_lieu.items()}
        kho_phong_ban_sao = copy.deepcopy(kho_can_kiem_tra[Phong])
        kho_can_kiem_tra[Phong] = kho_phong_ban_sao
        for p in kho_phong_ban_sao.values():
            if p.toa_nha == thuc_the.ma and p.con_hoat_dong: # type: ignore
                p.luu_tru()

        kho_toa_nha_ban_sao = kho_can_kiem_tra[ToaNha]
        kho_can_kiem_tra[ToaNha] = kho_toa_nha_ban_sao

        thuc_the_ban_sao = copy.copy(kho_toa_nha_ban_sao[thuc_the.ma])
        thuc_the_ban_sao.luu_tru()
        kho_toa_nha_ban_sao[thuc_the.ma] = thuc_the_ban_sao
        self.__kiem_cheo_nem_loi(kho_can_kiem_tra)

        self.__kho_luu_tru[Phong].ghi(kho_phong_ban_sao)
        self.__kho_luu_tru[ToaNha].ghi(kho_toa_nha_ban_sao)
        self.__kho_du_lieu[ToaNha] = kho_toa_nha_ban_sao
        self.__kho_du_lieu[Phong] = kho_phong_ban_sao

    def tai_kich_hoat(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        self.__kiem_tra_loai_thuc_the_hop_le(thuc_the)
        self.__kiem_cheo_va_ghi(type(thuc_the), thuc_the.ma, lambda tt: tt.tai_kich_hoat()) # type: ignore


    # các hàm nghiệp vụ
    def thanh_toan_hop_dong(self, hop_dong: HopDong) -> None:
        self.__kiem_tra_loai_thuc_the_hop_le(hop_dong)
        self.__kiem_cheo_va_ghi(HopDong, hop_dong.ma, lambda hd: hd.thanh_toan())

    def ket_thuc_hop_dong(self, hop_dong: HopDong) -> None:
        self.__kiem_tra_loai_thuc_the_hop_le(hop_dong)
        self.__kiem_cheo_va_ghi(HopDong, hop_dong.ma, lambda hd: hd.ket_thuc())

    def thanh_toan_hoa_don_thang(self, hoa_don_thang: HoaDonThang) -> None:
        self.__kiem_tra_loai_thuc_the_hop_le(hoa_don_thang)
        self.__kiem_cheo_va_ghi(HoaDonThang, hoa_don_thang.ma, lambda hd: hd.thanh_toan())

    def xu_ly_vi_pham(self, vi_pham: ViPham) -> None:
        self.__kiem_tra_loai_thuc_the_hop_le(vi_pham)
        self.__kiem_cheo_va_ghi(ViPham, vi_pham.ma, lambda vp: vp.xu_ly())

    def thong_ke_so_phong(self, toa_nha: ToaNha | None = None, loai_phong: int | None = None) -> tuple[int, int, int]:
        if toa_nha is not None and not toa_nha.con_hoat_dong:
            return 0, 0, 0

        ds_phong: list[Phong] = list(self.__kho_du_lieu[Phong].values())
        so_phong_trong = 0
        so_phong_co_nguoi = 0
        tong_so_phong = 0

        for p in ds_phong:
            if not p.con_hoat_dong:
                continue
            toa_nha_can_kiem_tra = toa_nha if toa_nha is not None else self.__kho_du_lieu[ToaNha].get(p.toa_nha)
            if toa_nha_can_kiem_tra is None or not toa_nha_can_kiem_tra.con_hoat_dong:
                continue
            if p.toa_nha == toa_nha_can_kiem_tra.ma:
                if loai_phong is None or p.suc_chua == loai_phong:
                    tong_so_phong += 1
                    if not any(hd.con_giu_cho() and hd.ma_phong == p.ma for hd in self.__kho_du_lieu[HopDong].values()):
                        so_phong_trong += 1
                    else:
                        so_phong_co_nguoi += 1

        return so_phong_trong, so_phong_co_nguoi, tong_so_phong

    def thong_ke_ty_le_lap_day(self, toa_nha: ToaNha | None = None, loai_phong: int | None = None) -> float:
        tong_suc_chua = 0
        tong_hop_dong_giu_cho = 0
        for p in self.__kho_du_lieu[Phong].values():
            if not p.con_hoat_dong:
                continue
            toa_nha_can_kiem_tra = toa_nha if toa_nha is not None else self.__kho_du_lieu[ToaNha].get(p.toa_nha)
            if toa_nha_can_kiem_tra is None or not toa_nha_can_kiem_tra.con_hoat_dong:
                continue
            if p.toa_nha == toa_nha_can_kiem_tra.ma:
                if loai_phong is None or p.suc_chua == loai_phong:
                    tong_suc_chua += p.suc_chua
                    so_hd = sum(hd.con_giu_cho() and hd.ma_phong == p.ma for hd in self.__kho_du_lieu[HopDong].values())
                    if so_hd > 0:
                        tong_hop_dong_giu_cho += so_hd if so_hd <= p.suc_chua else p.suc_chua

        if tong_suc_chua < 1:
            return 0
        else:
            return tong_hop_dong_giu_cho / tong_suc_chua

    def thong_ke_cong_no(self) -> tuple[float, int]:
        tong_cong_no = 0
        so_hop_dong = 0
        for hd in self.__kho_du_lieu[HopDong].values():
            if hd.trang_thai == TrangThaiHopDong.CHUA_THANH_TOAN:
                tong_cong_no += hd.tong_tien()
                so_hop_dong += 1

        return tong_cong_no, so_hop_dong

    def cap_nhat_cau_hinh(self, cau_hinh: CauHinhDong) -> None:
        self.__luu_tru_cau_hinh.cap_nhat_cau_hinh(cau_hinh)

    def doc_cau_hinh(self) -> CauHinhDong:
        return self.__luu_tru_cau_hinh.doc_cau_hinh()

    def danh_sach_dia_ly(self) -> dict[str, Tinh]:
        return self.__kho_du_lieu[Tinh].copy()

    # các hàm hỗ trợ
    def __kiem_tra_loai_thuc_the_hop_le(self, thuc_the: ThucTheGoc | ThucTheLuuTruDuoc | type[ThucTheGoc], ghi = True) -> None:
        loai_thuc_the = thuc_the if isinstance(thuc_the, type) else type(thuc_the)
        if not issubclass(loai_thuc_the, ThucTheGoc) or loai_thuc_the not in self.__kho_du_lieu or loai_thuc_the not in self.__kho_luu_tru:
            raise ValueError("Thực thể không hợp lệ")
        elif loai_thuc_the is Tinh and ghi:
            raise ValueError("Thực thể địa lý chỉ có thể đọc")
        elif isinstance(thuc_the, ThucTheGoc) and thuc_the.ma not in self.__kho_du_lieu[loai_thuc_the]:
            raise ValueError("Thực thể không tồn tại")

    def __kiem_cheo(self, kho: dict[type[ThucTheGoc], dict[str, Any]]) -> list[str]:
        return kiem_cheo_du_lieu(KhoDuLieu(kho[ToaNha], kho[Phong], kho[SinhVien], kho[HopDong], kho[HoaDonThang], kho[ViPham], kho[TaiKhoan]))

    def __kiem_cheo_nem_loi(self, kho: dict[type[ThucTheGoc], dict[str, Any]]) -> None:
        loi_cu = set(self.__kiem_cheo(self.__kho_du_lieu))
        loi_moi = [loi for loi in self.__kiem_cheo(kho) if loi not in loi_cu]
        if loi_moi:
            raise ValueError("\n".join(loi_moi))

    def __kiem_cheo_va_ghi(self, loai_thuc_the: type[T], ma: str, thao_tac: Callable[[T], None]) -> None:
        kho_can_kiem_tra = self.__kho_du_lieu.copy()
        kho_tam = kho_can_kiem_tra[loai_thuc_the].copy()
        ban_sao = copy.copy(kho_tam[ma])
        thao_tac(ban_sao)
        kho_tam[ma] = ban_sao
        kho_can_kiem_tra[loai_thuc_the] = kho_tam
        self.__kiem_cheo_nem_loi(kho_can_kiem_tra)
        self.__kho_luu_tru[loai_thuc_the].ghi(kho_tam)
        self.__kho_du_lieu[loai_thuc_the] = kho_tam


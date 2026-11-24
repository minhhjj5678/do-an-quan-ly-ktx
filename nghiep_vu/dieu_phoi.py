import copy
from datetime import date
from typing import Callable, ParamSpec, TypeVar, cast, Any

from luu_tru.luu_tru_cau_hinh import LuuTruCauHinh
from luu_tru.luu_tru_dia_ly import LuuTruDiaLy
from luu_tru.luu_tru_hoa_don_thang import LuuTruHoaDonThang
from luu_tru.luu_tru_hop_dong import LuuTruHopDong
from luu_tru.luu_tru_phong import LuuTruPhong
from luu_tru.luu_tru_sinh_vien import LuuTruSinhVien
from luu_tru.luu_tru_tai_khoan import LuuTruTaiKhoan
from luu_tru.luu_tru_toa_nha import LuuTruToaNha
from luu_tru.luu_tru_vi_pham import LuuTruViPham
from nghiep_vu.kiem_cheo_du_lieu import KhoDuLieu, kiem_cheo_du_lieu
from thuc_the.dia_ly import Tinh
from thuc_the.ky_tuc_xa import Phong, SinhVien, ToaNha
from thuc_the.tai_chinh import HoaDonThang, HopDong, ThangNam, TrangThaiHopDong
from thuc_the.tai_khoan import TaiKhoan
from thuc_the.thuc_the_goc import ThucTheLuuTruDuoc, ThucTheGoc
from thuc_the.vi_pham import TrangThaiViPham, ViPham
from tien_ich.cau_hinh_dong import CauHinhDong
from tien_ich.tao_ma import ma_hoa_don_thang, ma_hop_dong, ma_sinh_vien, ma_toa_nha, ma_vi_pham, ma_phong

T = TypeVar("T", bound=ThucTheGoc)
P = ParamSpec("P")

class DieuPhoiKTX:
    """
    Quy ước: với TaiKhoan, tầng giao diện không gọi tao_va_them, cap_nhat, luu_tru, tai_kich_hoat, xoa trực tiếp mà chỉ đi qua GiaoThucPhienLamViec (nơi kiểm tra quyền và các luật tài khoản).
    """
    def __init__(self):
        self.__dict_sv: dict[str, SinhVien] = {}
        self.__dict_p: dict[str, Phong] = {}
        self.__dict_tn: dict[str, ToaNha] = {}
        self.__dict_hd: dict[str, HopDong] = {}
        self.__dict_hdt: dict[str, HoaDonThang] = {}
        self.__dict_vp: dict[str, ViPham] = {}
        self.__dict_tk: dict[str, TaiKhoan] = {}
        self.__dict_dl: dict[str, Tinh] = {}

        self.__doc_file_sv = LuuTruSinhVien()
        self.__doc_file_p = LuuTruPhong()
        self.__doc_file_tn = LuuTruToaNha()
        self.__doc_file_hd = LuuTruHopDong()
        self.__doc_file_hdt = LuuTruHoaDonThang()
        self.__doc_file_vp = LuuTruViPham()
        self.__doc_file_tk = LuuTruTaiKhoan()
        self.__doc_file_dl = LuuTruDiaLy()
        self.__doc_file_cau_hinh = LuuTruCauHinh()

    def nap_du_lieu_file(self) -> None:
        """
        Nạp toàn bộ dữ liệu cục bộ vào ram và kiểm chéo. Bắt buộc gọi đúng một lần trước khi sử dụng giao thức.\n
        Ném lỗi nếu dữ liệu hỏng/lệch nhau.
        Không nạp dữ liệu từ api ngoài, chỉ nạp dữ liệu cục bộ.
        """
        loi = []
        for loai_thuc_the in self._kho_du_lieu.keys():
            if loai_thuc_the is Tinh:
                continue
            try:
                doc_file = self._lay_doc_file_theo_loai(loai_thuc_the)
                if doc_file is None:
                    raise ValueError(f"Kho lưu trữ {loai_thuc_the.__name__} chưa được đăng ký trong hàm khởi tạo")

                if doc_file.co_bi_chinh_sua():
                    self._cap_nhat_danh_sach(loai_thuc_the, doc_file.doc_sao_luu())  # type: ignore
                else:
                    try:
                        self._cap_nhat_danh_sach(loai_thuc_the, doc_file.doc()) # type: ignore
                    except (FileNotFoundError, ValueError):
                        self._cap_nhat_danh_sach(loai_thuc_the, doc_file.doc_sao_luu()) # type: ignore
            except Exception as e:
                loi.append(f"Lỗi xảy ra khi nạp dữ liệu file {loai_thuc_the.__name__}: {e}")

        if not loi:
            loi.extend(self.__kiem_cheo(self._kho_du_lieu))

        if loi:
            raise ValueError("\n".join(loi))

    def nap_du_lieu_api(self) -> None:
        """
        Nạp dữ liệu địa lý cục bộ trước, nếu không thành công thì nạp dữ liệu từ api ngoài vào ram.\n
        Bắt buộc phải được gọi trong luồng phụ, chặn màn hình hoặc tải ngầm khi khởi động app.
        Có thể gọi nhiều lần đến khi dữ liệu tải thành công.
        Ném OSError nếu tải dữ liệu không thành công.
        """
        kho_dl = self.__doc_file_dl
        if not kho_dl.co_bi_chinh_sua():
            try:
                self.__dict_dl = kho_dl.doc()
            except FileNotFoundError:
                self.__dict_dl = kho_dl.doc_sao_luu()
        else:
            self.__dict_dl = kho_dl.doc_sao_luu()

        kho_dl.ghi(self.__dict_dl)

    def _lay_danh_sach_theo_loai(self, thuc_the: type[ThucTheGoc] | ThucTheGoc) -> dict:
        thuc_the = type(thuc_the) if isinstance(thuc_the, ThucTheGoc) else thuc_the
        if thuc_the is SinhVien:
            return self.__dict_sv
        elif thuc_the is Phong:
            return self.__dict_p
        elif thuc_the is ToaNha:
            return self.__dict_tn
        elif thuc_the is HopDong:
            return self.__dict_hd
        elif thuc_the is HoaDonThang:
            return self.__dict_hdt
        elif thuc_the is ViPham:
            return self.__dict_vp
        elif thuc_the is TaiKhoan:
            return self.__dict_tk
        elif thuc_the is Tinh:
            return self.__dict_dl
        else:
            raise ValueError(f"Loại thực thể {thuc_the} không hợp lệ.")

    def _cap_nhat_danh_sach(self, thuc_the: type[T] | T, danh_sach_moi: dict[str, T]) -> None:
        thuc_the = type(thuc_the) if isinstance(thuc_the, ThucTheGoc) else thuc_the
        if thuc_the is SinhVien:
            self.__dict_sv = danh_sach_moi # type: ignore
        elif thuc_the is Phong:
            self.__dict_p = danh_sach_moi # type: ignore
        elif thuc_the is ToaNha:
            self.__dict_tn = danh_sach_moi # type: ignore
        elif thuc_the is HopDong:
            self.__dict_hd = danh_sach_moi # type: ignore
        elif thuc_the is HoaDonThang:
            self.__dict_hdt = danh_sach_moi # type: ignore
        elif thuc_the is ViPham:
            self.__dict_vp = danh_sach_moi # type: ignore
        elif thuc_the is TaiKhoan:
            self.__dict_tk = danh_sach_moi # type: ignore
        elif thuc_the is Tinh:
            self.__dict_dl = danh_sach_moi # type: ignore
        else:
            raise ValueError(f"Loại thực thể {thuc_the} không hợp lệ.")

    def _lay_doc_file_theo_loai(self, thuc_the: type[ThucTheGoc] | ThucTheGoc):
        thuc_the = type(thuc_the) if isinstance(thuc_the, ThucTheGoc) else thuc_the
        if thuc_the is SinhVien:
            return self.__doc_file_sv
        elif thuc_the is Phong:
            return self.__doc_file_p
        elif thuc_the is ToaNha:
            return self.__doc_file_tn
        elif thuc_the is HopDong:
            return self.__doc_file_hd
        elif thuc_the is HoaDonThang:
            return self.__doc_file_hdt
        elif thuc_the is ViPham:
            return self.__doc_file_vp
        elif thuc_the is TaiKhoan:
            return self.__doc_file_tk
        elif thuc_the is Tinh:
            return self.__doc_file_dl
        else:
            raise ValueError(f"Loại thực thể {thuc_the} không hợp lệ.")

    @property
    def _kho_du_lieu(self) -> dict[type[ThucTheGoc], dict[str, Any]]:
        return {
            SinhVien: self.__dict_sv,
            Phong: self.__dict_p,
            ToaNha: self.__dict_tn,
            HopDong: self.__dict_hd,
            HoaDonThang: self.__dict_hdt,
            ViPham: self.__dict_vp,
            TaiKhoan: self.__dict_tk,
            Tinh: self.__dict_dl
        }

    # các hàm crud
    def lay_tat_ca(self, loai_thuc_the: type[T], lay_luu_tru: bool = False) -> dict[str, T]:
        """
        Trả về danh sách tất cả các thực thể thuộc loại được chỉ định.\n
        Nếu lay_luu_tru là True thì trả về cả các thực thể đã lưu trữ, ngược lại chỉ trả về các thực thể còn hoạt động.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(loai_thuc_the, ghi=False)
        danh_sach_dict = self._lay_danh_sach_theo_loai(loai_thuc_the)
        if lay_luu_tru:
            return {ma: copy.copy(doi_tuong) for ma, doi_tuong in danh_sach_dict.items()}
        else:
            du_lieu = {ma: cast(T, copy.copy(doi_tuong)) for ma, doi_tuong in danh_sach_dict.items() if (isinstance(doi_tuong, ThucTheLuuTruDuoc) and doi_tuong.con_hoat_dong) or not isinstance(doi_tuong, ThucTheLuuTruDuoc)}
            return du_lieu
        
    def them(self, thuc_the: ThucTheGoc) -> None:
        """
        Thêm một thực thể đã được khởi tạo hoàn chỉnh vào hệ thống.
        Dùng cho các thực thể có mã nhập từ người dùng không cần tự động sinh mã (hiện tại chỉ có TaiKhoan).
        Ném lỗi nếu mã thực thể đã tồn tại hoặc vi phạm dữ liệu chéo.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(type(thuc_the))
        danh_sach_dict_tam = self._lay_danh_sach_theo_loai(type(thuc_the)).copy()
        if thuc_the.ma in danh_sach_dict_tam:
            raise ValueError("Mã thực thể đã tồn tại trong kho lưu trữ")
        self._kiem_cheo_va_luu(thuc_the)

    def tao_va_luu_sinh_vien(self, ten: str, sdt: str, nam_sinh: int, cccd: str, dia_chi_chi_tiet: str, xa: str, tinh: str) -> SinhVien:
        ma = ma_sinh_vien(self.__dict_sv)
        while ma in self.__dict_sv:
            ma = ma_sinh_vien(self.__dict_sv)
        sv = SinhVien(ma, ten, sdt, nam_sinh, cccd, dia_chi_chi_tiet, xa, tinh)
        self._kiem_cheo_va_luu(sv)
        return sv

    def tao_va_luu_phong(self, ten: str, suc_chua: int, gia_phong: float, toa_nha: str, tang: int) -> Phong:
        ma = ma_phong(self.__dict_p)
        while ma in self.__dict_p:
            ma = ma_phong(self.__dict_p)
        phong = Phong(ma, ten, suc_chua, gia_phong, toa_nha, tang)
        self._kiem_cheo_va_luu(phong)
        return phong

    def tao_va_luu_toa_nha(self, ten: str, so_tang: int) -> ToaNha:
        ma = ma_toa_nha(self.__dict_tn)
        while ma in self.__dict_tn:
            ma = ma_toa_nha(self.__dict_tn)
        toa_nha = ToaNha(ma, ten, so_tang)
        self._kiem_cheo_va_luu(toa_nha)
        return toa_nha

    def tao_va_luu_hop_dong(self, ngay_ky: date, ngay_het_han: date, ngay_bat_dau: date, ngay_ket_thuc: date, he_so_thang: int, gia_phong: float, tien_dat_coc: float, ma_sinh_vien: str, ma_phong: str) -> HopDong:
        ma = ma_hop_dong(self.__dict_hd)
        while ma in self.__dict_hd:
            ma = ma_hop_dong(self.__dict_hd)
        hop_dong = HopDong(ma, ngay_ky, ngay_het_han, ngay_bat_dau, ngay_ket_thuc, he_so_thang, gia_phong, tien_dat_coc, ma_sinh_vien, ma_phong)
        self._kiem_cheo_va_luu(hop_dong)
        return hop_dong

    def tao_va_luu_hoa_don_thang(self, thang_nam: ThangNam, dien_cu: int, dien_moi: int, don_gia_dien: float, nuoc_cu: int, nuoc_moi: int, don_gia_nuoc: float, phong: str, han_chot: date) -> HoaDonThang:
        ma = ma_hoa_don_thang(self.__dict_hdt)
        while ma in self.__dict_hdt:
            ma = ma_hoa_don_thang(self.__dict_hdt)
        hoa_don_thang = HoaDonThang(ma, thang_nam, dien_cu, dien_moi, don_gia_dien, nuoc_cu, nuoc_moi, don_gia_nuoc, phong, han_chot)
        self._kiem_cheo_va_luu(hoa_don_thang)
        return hoa_don_thang

    def tao_va_luu_vi_pham(self, sinh_vien: str, ngay_vi_pham: date, mo_ta: str, hinh_thuc_ky_luat: str) -> ViPham:
        ma = ma_vi_pham(self.__dict_vp)
        while ma in self.__dict_vp:
            ma = ma_vi_pham(self.__dict_vp)
        vi_pham = ViPham(ma, sinh_vien, ngay_vi_pham, mo_ta, hinh_thuc_ky_luat)
        self._kiem_cheo_va_luu(vi_pham)
        return vi_pham

    def _kiem_cheo_va_luu(self, thuc_the: ThucTheGoc):
        loai = type(thuc_the)

        # tạo một dict tạm để kiểm tra tính hợp lệ trước khi lưu thật
        danh_sach_dict_tam = self._lay_danh_sach_theo_loai(loai).copy()
        danh_sach_dict_tam[thuc_the.ma] = copy.copy(thuc_the)
        kho_can_kiem_tra = self._kho_du_lieu.copy()
        kho_can_kiem_tra[loai] = danh_sach_dict_tam
        self.__kiem_cheo_nem_loi(kho_can_kiem_tra)

        # gọi tầng đọc file ghi dữ liệu vào file
        self._lay_doc_file_theo_loai(loai).ghi(danh_sach_dict_tam)
        # cập nhật dict trong ram bằng dict tạm
        self._cap_nhat_danh_sach(loai, danh_sach_dict_tam)

    def xoa(self, thuc_the: ThucTheGoc, ep_xoa: bool = False) -> None:
        """
        Xóa thực thể khỏi hệ thống.
        Hạn chế dùng đối với thực thể lưu trữ được, thay bằng luu_tru().
        Nếu ep_xoa = True: Xóa thực thể và **XÓA LUÔN** các thực thể quan hệ yếu phụ thuộc vào thực thể đã xóa.

        - Ném lỗi ValueError nếu:
            - thực thể lưu trữ được (SinhVien, Phong, Tòa Nhà...) và đang còn hoạt động.
            - thực thể còn ràng buộc HopDong, ViPham, HoaDonThang... và ep_xoa = False.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(thuc_the)

        danh_sach_dict_tam = self._kho_du_lieu[type(thuc_the)].copy()
        danh_sach_dict_tam.pop(thuc_the.ma)
        kho_can_kiem_tra = self._kho_du_lieu.copy()
        kho_can_kiem_tra[type(thuc_the)] = danh_sach_dict_tam
        self.__kiem_cheo_nem_loi(kho_can_kiem_tra)

        if isinstance(thuc_the, ThucTheLuuTruDuoc) and not ep_xoa:
            raise ValueError("Thực thể này có thể lưu trữ được, việc xóa có thể gây hư hại đến dữ liệu, bạn vẫn muốn xóa?")
        if not ep_xoa:
            raise ValueError("Việc xóa sẽ không thể hoàn tác và có thể gây ảnh hưởng đến dữ liệu, bạn vẫn muốn xóa?")

        self._lay_doc_file_theo_loai(type(thuc_the)).ghi(danh_sach_dict_tam)
        self._cap_nhat_danh_sach(type(thuc_the), danh_sach_dict_tam)

    def lay_theo_ma(self, loai_thuc_the: type[T], ma: str, lay_luu_tru: bool = False) -> T:
        """
        Lấy thực thể theo mã.\n
        Ném lỗi nếu không tìm thấy thực thể hoặc thực thể đã lưu trữ và lay_luu_tru = False.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(loai_thuc_the, ghi=False)
        danh_sach_dict = self._lay_danh_sach_theo_loai(loai_thuc_the)
        doi_tuong = danh_sach_dict.get(ma)
        if doi_tuong is None:
            raise ValueError("Thực thể không tồn tại trong cơ sở dữ liệu")

        if not lay_luu_tru and isinstance(doi_tuong, ThucTheLuuTruDuoc) and not doi_tuong.con_hoat_dong:
            raise ValueError("Thực thể không còn hoạt động")

        doi_tuong_ban_sao = copy.copy(doi_tuong)
        return cast(T, doi_tuong_ban_sao)

    def loc_theo_dieu_kien(self, loai_thuc_the: type[T], dieu_kien: Callable[[T], bool], lay_luu_tru: bool = False) -> \
    dict[str, T]:
        """
        Lọc danh sách thực thể dựa trên một hàm điều kiện.
        Nếu lay_luu_tru = True thì lọc cả các thực thể đã lưu trữ, ngược lại chỉ lọc các thực thể còn hoạt động.
        """
        kho = self.lay_tat_ca(loai_thuc_the, lay_luu_tru)
        return {ma: doi_tuong for ma, doi_tuong in kho.items() if dieu_kien(doi_tuong)}

    def cap_nhat(self, thuc_the: ThucTheGoc) -> None:
        """
        Cập nhật thông tin của một thực thể.\n
        Ném lỗi nếu thực thể không tồn tại.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(thuc_the)
        danh_sach_dict = self._lay_danh_sach_theo_loai(type(thuc_the))
        thuc_the_goc = danh_sach_dict[thuc_the.ma]
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

        self._kiem_cheo_va_luu(thuc_the)

    def luu_tru(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        """
        Thay đổi trạng thái thực thể thành ngưng hoạt động.\n
        Ném lỗi nếu thực thể đã được lưu trữ hoặc vướng dữ liệu chéo.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(thuc_the)
        if not isinstance(thuc_the, ToaNha):
            self.__kiem_cheo_va_ghi(type(thuc_the), thuc_the.ma, lambda tt: tt.luu_tru()) # type: ignore
            return

        kho_can_kiem_tra = {loai: kho.copy() for loai, kho in self._kho_du_lieu.items()}
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

        self.__doc_file_p.ghi(kho_phong_ban_sao)
        self.__doc_file_tn.ghi(kho_toa_nha_ban_sao)
        self.__dict_tn = kho_toa_nha_ban_sao
        self.__dict_p = kho_phong_ban_sao

    def tai_kich_hoat(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        """
        Thay đổi trạng thái thực thể thành hoạt động.\n
        Ném lỗi nếu thực thể đang hoạt động.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(thuc_the)
        self.__kiem_cheo_va_ghi(type(thuc_the), thuc_the.ma, lambda tt: tt.tai_kich_hoat()) # type: ignore


    # các hàm nghiệp vụ
    def thanh_toan_hop_dong(self, hop_dong: HopDong) -> None:
        """
        Thay đổi trạng thái hợp đồng thành đã thanh toán.
        Cập nhật phòng của sinh viên, danh sách sinh viên của phòng.
        Ném lỗi nếu hợp đồng không ở trạng thái chưa thanh toán hoặc không còn giữ chỗ trong phòng.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(hop_dong)
        self.__kiem_cheo_va_ghi(HopDong, hop_dong.ma, lambda hd: hd.thanh_toan())

    def ket_thuc_hop_dong(self, hop_dong: HopDong) -> None:
        """
        Thay đổi trạng thái hợp đồng thành kết thúc.\n
        Cập nhật phòng của sinh viên, danh sách sinh viên của phòng.
        Ném lỗi nếu hợp đồng đã kết thúc.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(hop_dong)
        self.__kiem_cheo_va_ghi(HopDong, hop_dong.ma, lambda hd: hd.ket_thuc())

    def thanh_toan_hoa_don_thang(self, hoa_don_thang: HoaDonThang) -> None:
        """
        Cập nhật trạng thái thanh toán của hóa đơn tháng thành đã thanh toán.
        Ném lỗi nếu hóa đơn tháng không ở trạng thái thanh toán.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(hoa_don_thang)
        self.__kiem_cheo_va_ghi(HoaDonThang, hoa_don_thang.ma, lambda hd: hd.thanh_toan())

    def xu_ly_vi_pham(self, vi_pham: ViPham) -> None:
        """
        Cập nhật trạng thái xử lý vi phạm thành đã xử lý.
        Ném lỗi nếu vi phạm không ở trạng thái chưa xử lý.
        """
        self.__kiem_tra_loai_thuc_the_hop_le(vi_pham)
        self.__kiem_cheo_va_ghi(ViPham, vi_pham.ma, lambda vp: vp.xu_ly())

    def thong_ke_so_phong(self, toa_nha: ToaNha | None = None, loai_phong: int | None = None) -> tuple[int, int, int]:
        """
        Trả về số lượng phòng trống, số lượng phòng có hợp đồng còn giữ chỗ (có người), tổng số phòng trong tòa nhà.

        Tham số:
            - toa_nha: nếu là None thì thống kê cho tất cả các tòa nhà, nếu là một tòa nhà cụ thể thì thống kê cho tòa nhà đó.
            - loai_phong: sức chứa tối đa của phòng, nếu là None thì thống kê tất cả các loại phòng, nếu là một số nguyên cụ thể thì thống kê cho loại phòng đó.

        Trả về:
            - tuple[int, int, int]: (số phòng trống, số phòng có người, tổng số phòng)
        """
        if toa_nha is not None and not toa_nha.con_hoat_dong:
            return 0, 0, 0

        ds_phong: list[Phong] = list(self.__dict_p.values())
        so_phong_trong = 0
        so_phong_co_nguoi = 0
        tong_so_phong = 0

        for p in ds_phong:
            if not p.con_hoat_dong:
                continue
            toa_nha_can_kiem_tra = toa_nha if toa_nha is not None else self.__dict_tn.get(p.toa_nha)
            if toa_nha_can_kiem_tra is None or not toa_nha_can_kiem_tra.con_hoat_dong:
                continue
            if p.toa_nha == toa_nha_can_kiem_tra.ma:
                if loai_phong is None or p.suc_chua == loai_phong:
                    tong_so_phong += 1
                    if not any(hd.con_giu_cho() and hd.ma_phong == p.ma for hd in self.__dict_hd.values()):
                        so_phong_trong += 1
                    else:
                        so_phong_co_nguoi += 1

        return so_phong_trong, so_phong_co_nguoi, tong_so_phong

    def thong_ke_ty_le_lap_day(self, toa_nha: ToaNha | None = None, loai_phong: int | None = None) -> float:
        """
        Trả về tỷ lệ lấp đầy của tòa nhà.

        Tham số:
            - toa_nha: nếu là None thì thống kê toàn bộ ktx, nếu là một tòa nhà cụ thể thì thống kê tòa nhà đó.
            - loai_phong: sức chứa tối đa của phòng, nếu là None thì thống kê tất cả loại phòng, nếu là số nguyên cụ thể thì thống kê loại phòng đó.

        Trả về:
            - float: tỷ lệ lấp đầy của tòa nhà, giá trị từ 0 đến 1, ví dụ 0.75 nghĩa là 75% sức chứa đã có hợp đồng giữ chỗ."""
        tong_suc_chua = 0
        tong_hop_dong_giu_cho = 0
        for p in self.__dict_p.values():
            if not p.con_hoat_dong:
                continue
            toa_nha_can_kiem_tra = toa_nha if toa_nha is not None else self.__dict_tn.get(p.toa_nha)
            if toa_nha_can_kiem_tra is None or not toa_nha_can_kiem_tra.con_hoat_dong:
                continue
            if p.toa_nha == toa_nha_can_kiem_tra.ma:
                if loai_phong is None or p.suc_chua == loai_phong:
                    tong_suc_chua += p.suc_chua
                    so_hd = sum(hd.con_giu_cho() and hd.ma_phong == p.ma for hd in self.__dict_hd.values())
                    if so_hd > 0:
                        tong_hop_dong_giu_cho += so_hd if so_hd <= p.suc_chua else p.suc_chua

        if tong_suc_chua < 1:
            return 0
        else:
            return tong_hop_dong_giu_cho / tong_suc_chua

    def thong_ke_cong_no(self) -> tuple[float, int]:
        """
        Trả về (Tổng số tiền nợ, Tổng số lượng sinh viên đang nợ).
        Tiền nợ là tiền hợp đồng chưa thanh toán, không tính tiền hóa đơn tháng.
        """
        tong_cong_no = 0
        so_hop_dong = 0
        for hd in self.__dict_hd.values():
            if hd.trang_thai == TrangThaiHopDong.CHUA_THANH_TOAN:
                tong_cong_no += hd.tong_tien()
                so_hop_dong += 1

        return tong_cong_no, so_hop_dong

    def cap_nhat_cau_hinh(self, cau_hinh: CauHinhDong) -> None:
        """
        Thay thế cấu hình hiện tại bằng cấu hình mới.\n
        - cau_hinh: cấu hình mới.
        """
        self.__doc_file_cau_hinh.cap_nhat_cau_hinh(cau_hinh)

    def doc_cau_hinh(self) -> CauHinhDong:
        """
        - Trả về: cấu hình hiện tại.
        """
        return self.__doc_file_cau_hinh.doc_cau_hinh()

    def danh_sach_dia_ly(self) -> dict[str, Tinh]:
        """
        Dùng cho việc nhập địa chỉ thường trú của sinh viên.\n
        - Trả về: danh sách các tỉnh Việt Nam.
        - Ném lỗi nếu dữ liệu địa lý chưa được nạp.
        """
        return self.__dict_dl.copy()

    # các hàm hỗ trợ
    def __kiem_tra_loai_thuc_the_hop_le(self, thuc_the: ThucTheGoc | ThucTheLuuTruDuoc | type[ThucTheGoc], ghi = True) -> None:
        loai_thuc_the = cast(ThucTheGoc, thuc_the if isinstance(thuc_the, type) else type(thuc_the))
        self._lay_doc_file_theo_loai(loai_thuc_the)
        danh_sach_dict = self._lay_danh_sach_theo_loai(loai_thuc_the)
        if loai_thuc_the is Tinh and ghi:
            raise ValueError("Thực thể địa lý chỉ có thể đọc")
        elif isinstance(thuc_the, ThucTheGoc) and thuc_the.ma not in danh_sach_dict:
            raise ValueError("Thực thể không tồn tại")

    def __kiem_cheo(self, kho: dict[type[ThucTheGoc], dict[str, Any]]) -> list[str]:
        return kiem_cheo_du_lieu(KhoDuLieu(kho[ToaNha], kho[Phong], kho[SinhVien], kho[HopDong], kho[HoaDonThang], kho[ViPham], kho[TaiKhoan]))

    def __kiem_cheo_nem_loi(self, kho: dict[type[ThucTheGoc], dict[str, Any]]) -> None:
        loi_cu = set(self.__kiem_cheo(self._kho_du_lieu))
        loi_moi = [loi for loi in self.__kiem_cheo(kho) if loi not in loi_cu]
        if loi_moi:
            raise ValueError("\n".join(loi_moi))

    def __kiem_cheo_va_ghi(self, loai_thuc_the: type[T], ma: str, thao_tac: Callable[[T], None]) -> None:
        # tạo bản sao từ toàn bộ dict gốc để kiểm tra tính hợp lệ trước khi lưu thật
        kho_can_kiem_tra = self._kho_du_lieu.copy()
        # tạo một dict tạm để cập nhật giá trị
        danh_sach_dict_tam = kho_can_kiem_tra[loai_thuc_the].copy()
        # tạo bản sao của đối tượng cần cập nhật
        ban_sao = copy.copy(danh_sach_dict_tam[ma])
        # cập nhật bản sao
        thao_tac(ban_sao)
        danh_sach_dict_tam[ma] = ban_sao
        kho_can_kiem_tra[loai_thuc_the] = danh_sach_dict_tam
        # kiểm tra tính hợp lệ
        self.__kiem_cheo_nem_loi(kho_can_kiem_tra)

        # lưu vào file
        self._lay_doc_file_theo_loai(loai_thuc_the).ghi(danh_sach_dict_tam)
        # cập nhật dict trong ram bằng dict tạm
        self._cap_nhat_danh_sach(loai_thuc_the, danh_sach_dict_tam)


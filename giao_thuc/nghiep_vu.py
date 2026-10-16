from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Concatenate, ParamSpec

from thuc_the.dia_ly import Tinh
from thuc_the.hoc_vu import HocKy
from thuc_the.tai_chinh import HopDong, HoaDonThang
from thuc_the.tai_khoan import TaiKhoan, LoaiTaiKhoan
from thuc_the.vi_pham import ViPham
from tien_ich.cau_hinh_dong import CauHinhDong
from thuc_the.ky_tuc_xa import ToaNha
from thuc_the.thuc_the_goc import ThucTheGoc, ThucTheLuuTruDuoc

T = TypeVar("T", bound=ThucTheGoc)
P = ParamSpec("P")

# Phần B
class GiaoThucDieuPhoi(ABC):
    # CRUD
    @abstractmethod
    def lay_tat_ca(self, loai_thuc_the: type[T], lay_luu_tru: bool = False) -> dict[str, T]:
        """
        Trả về danh sách tất cả các thực thể thuộc loại được chỉ định.\n
        Nếu lay_luu_tru là True thì trả về cả các thực thể đã lưu trữ, ngược lại chỉ trả về các thực thể còn hoạt động.
        """
        raise NotImplementedError

    @abstractmethod
    def tao_va_them(self, loai_thuc_the: Callable[Concatenate[str, P], T], /, *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Tạo và thêm thực thể vào hệ thống.
        Trả về thực thể đã tạo và thêm vào hệ thống.\n
        Ném lỗi nếu logic nội tại hoặc dữ liệu chéo không hợp lệ trước khi thêm thực thể
        """
        raise NotImplementedError

    @abstractmethod
    def xoa(self, loai_thuc_the: type[T], thuc_the: T, ep_xoa: bool = False) -> None:
        """
        Xóa thực thể khỏi hệ thống.
        Hạn chế dùng đối với thực thể lưu trữ được, thay bằng luu_tru().

        - Nếu thực thể lưu trữ được (SinhVien, Phong, Tòa Nhà...) và đang có ràng buộc trong HopDong: Ném lỗi ValueError.
        - Nếu ep_xoa = True: Xóa thực thể và **XÓA LUÔN** các HopDong liên quan.
        """
        raise NotImplementedError

    @abstractmethod
    def lay_theo_ma(self, loai_thuc_the: type[T], ma: str, lay_luu_tru: bool = False) -> T: raise NotImplementedError

    @abstractmethod
    def loc_theo_dieu_kien(self, loai_thuc_the: type[T], dieu_kien: Callable[[T], bool], lay_luu_tru: bool = False) -> dict[str, T]:
        """
        Lọc danh sách thực thể dựa trên một hàm điều kiện.
        """
        raise NotImplementedError

    @abstractmethod
    def cap_nhat(self, loai_thuc_the: type[T], thuc_the: T) -> None:
        """
        Cập nhật thông tin của một thực thể.\n
        Ném lỗi nếu thực thể không tồn tại.
        """
        raise NotImplementedError

    @abstractmethod
    def luu_tru(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        """
        Thay đổi trạng thái thực thể thành ngưng hoạt động.\n
        Ném lỗi nếu thực thể đã được lưu trữ hoặc vướng dữ liệu chéo.
        """
        raise NotImplementedError

    @abstractmethod
    def tai_kich_hoat(self, thuc_the: ThucTheLuuTruDuoc) -> None:
        """
        Thay đổi trạng thái thực thể thành hoạt động.\n
        Ném lỗi nếu thực thể đã được lưu trữ.
        """
        raise NotImplementedError

    # Logic nghiệp vụ
    @abstractmethod
    def thanh_toan_hop_dong(self, hop_dong: HopDong) -> None:
        """
        Thay đổi trạng thái hợp đồng thành đã thanh toán.\n
        Cập nhật phòng của sinh viên, danh sách sinh viên của phòng.
        """
        raise NotImplementedError

    @abstractmethod
    def ket_thuc_hop_dong(self, hop_dong: HopDong) -> None:
        """
        Thay đổi trạng thái hợp đồng thành kết thúc.\n
        Xóa phòng của sinh viên, xóa sinh viên khỏi danh sách sinh viên của phòng.
        """
        raise NotImplementedError

    @abstractmethod
    def thanh_toan_hoa_don_thang(self, hoa_don_thang: HoaDonThang) -> None:
        """
        Cập nhật trạng thái thanh toán của hóa đơn tháng thành đã thanh toán.
        """
        raise NotImplementedError

    @abstractmethod
    def xu_ly_vi_pham(self, vi_pham: ViPham) -> None:
        """
        Cập nhật trạng thái xử lý vi phạm thành đã xử lý.
        """
        raise NotImplementedError

    # Các hàm thống kê
    @abstractmethod
    def thong_ke_so_phong(self, hoc_ky: HocKy, toa_nha: ToaNha | None = None, loai_phong: int | None = None) -> tuple[int, int, int]:
        """
        Trả về số lượng phòng trống, số lượng phòng đã thuê, tổng số phòng trong tòa nhà.
        
        Tham số:
            - hoc_ky: học kỳ hiện tại
            - toa_nha: nếu là None thì thống kê cho tất cả các tòa nhà, nếu là một tòa nhà cụ thể thì thống kê cho tòa nhà đó.
            - loai_phong: sức chứa tối đa của phòng, nếu là None thì thống kê tất cả các loại phòng, nếu là một số nguyên cụ thể thì thống kê cho loại phòng đó.

        Trả về:
            - tuple[int, int, int]: (số phòng trống, số phòng có người, tổng số phòng)
        """
        raise NotImplementedError

    @abstractmethod
    def thong_ke_ty_le_lap_day(self, hoc_ky: HocKy, toa_nha: ToaNha | None = None, loai_phong: int | None = None) -> float:
        """
        Trả về tỷ lệ lấp đầy của tòa nhà.

        Tham số:
            - hoc_ky: học kỳ hiện tại
            - toa_nha: nếu là None thì thống kê toàn bộ ktx, nếu là một tòa nhà cụ thể thì thống kê tòa nhà đó.
            - loai_phong: sức chứa tối đa của phòng, nếu là None thì thống kê tất cả loại phòng, nếu là số nguyên cụ thể thì thống kê loại phòng đó.

        Trả về:
            - float: tỷ lệ lấp đầy của tòa nhà, giá trị từ 0 đến 1, ví dụ 0.75 nghĩa là 75% số phòng đã có người thuê."""
        raise NotImplementedError

    @abstractmethod
    def thong_ke_cong_no(self, hoc_ky: HocKy | None = None) -> tuple[float, int]:
        """
        Trả về (Tổng số tiền nợ, Tổng số lượng sinh viên đang nợ).
        Nếu hoc_ky là None, thống kê công nợ trên toàn hệ thống.
        """
        raise NotImplementedError

    # Logic dữ liệu
    @abstractmethod
    def cap_nhat_cau_hinh(self, cau_hinh: CauHinhDong) -> None:
        """
        Thay thế cấu hình hiện tại bằng cấu hình mới.\n
        - cau_hinh: cấu hình mới.
        """
        raise NotImplementedError

    @abstractmethod
    def doc_cau_hinh(self) -> CauHinhDong:
        """
        - Trả về: cấu hình hiện tại.
        """
        raise NotImplementedError

    @abstractmethod
    def danh_sach_dia_ly(self) -> dict[str, Tinh]:
        """
        Dùng cho việc nhập địa chỉ thường trú của sinh viên.\n
        - Trả về: danh sách các tỉnh Việt Nam.
        """
        raise NotImplementedError

# Phần C
class GiaoThucPhienLamViec(ABC):
    @property
    @abstractmethod
    def tai_khoan_hien_tai(self) -> TaiKhoan | None:
        """
        - Tài khoản đang sử dụng hiện tại.
        """
        raise NotImplementedError

    @abstractmethod
    def tao_tai_khoan(self, tai_khoan: str, mat_khau: str, loai_tai_khoan: LoaiTaiKhoan, ma_chu_the: str | None) -> None:
        """
        Tạo tài khoản mới.

        Thuộc tính:
            - tai_khoan: tên đăng nhập.
            - mat_khau: mật khẩu.
            - loai_tai_khoan: quản trị viên hoặc sinh viên.
            - ma_chu_the: mã sinh viên nếu là loại tài khoản sinh viên.
        """
        raise NotImplementedError

    @abstractmethod
    def dang_nhap(self, tai_khoan: str, mat_khau: str) -> None:
        """
        Đăng nhập tài khoản.\n
        Ném lỗi nếu mật khẩu không hợp lệ hoặc đã đăng nhập.
        """
        raise NotImplementedError

    @abstractmethod
    def dang_xuat(self) -> None:
        """
        Đăng xuất tài khoản hiện tại.\n
        Ném lỗi nếu chưa đăng nhập.
        """
        raise NotImplementedError

    @abstractmethod
    def doi_mat_khau(self, mat_khau_moi: str, mat_khau_cu: str | None = None, tai_khoan: str | None = None) -> None:
        """
        Đổi mật khẩu tài khoản.\n
        - Nếu tai_khoan = None: Đổi mật khẩu cho tài khoản đang đăng nhập hiện tại. BẮT BUỘC có mat_khau_cu.
        - Nếu có tai_khoan: Chức năng dành cho quản trị viên để reset mật khẩu người khác (Không cần mat_khau_cu).
        Ném lỗi nếu: Chưa đăng nhập, không có quyền quản trị, hoặc mật khẩu cũ không đúng.
        """
        raise NotImplementedError
"""Danh mục vi phạm: mã VP tự sinh, xử lý trạng thái qua nghiệp vụ."""
from thuc_the.vi_pham import ViPham
from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhViPham(ManHinhDanhMucCoSo):
    LOAI = ViPham
    TIEU_DE = 'Quản lý vi phạm'
    MO_TA = 'Ghi nhận vi phạm và theo dõi trạng thái xử lý.'
    TRUONG = ['ma', 'sinh_vien', 'ngay_vi_pham', 'mo_ta', 'hinh_thuc_ky_luat', 'trang_thai']
    BAT_BUOC = ['sinh_vien', 'ngay_vi_pham', 'mo_ta', 'hinh_thuc_ky_luat']
    TRUONG_CHI_DOC_KHI_TAO = {'trang_thai'}
    CHO_PHEP_SUA = False  # Các trường của ViPham chỉ có getter trong class thật

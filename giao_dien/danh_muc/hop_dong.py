"""Danh mục hợp đồng: mã tự sinh bởi DieuPhoiKTX."""
from thuc_the.tai_chinh import HopDong
from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhHopDong(ManHinhDanhMucCoSo):
    NGHIEP_VU_CHI_TIET = (('Thanh toán hợp đồng', 'thanh_toan_hop_dong'),
                           ('Kết thúc hợp đồng', 'ket_thuc_hop_dong'))
    LOAI = HopDong
    TIEU_DE = 'Quản lý hợp đồng'
    MO_TA = 'Thêm và theo dõi hợp đồng. Chọn hợp đồng và mở Chi tiết để thanh toán hoặc kết thúc.'
    TRUONG = [
        'ma', 'ngay_ky', 'ngay_het_han', 'ngay_bat_dau', 'ngay_ket_thuc',
        'he_so_thang', 'gia_phong', 'tien_dat_coc', 'ma_sinh_vien',
        'ma_phong', 'trang_thai',
    ]
    BAT_BUOC = [
        'ngay_ky', 'ngay_het_han', 'ngay_bat_dau', 'ngay_ket_thuc',
        'he_so_thang', 'gia_phong', 'tien_dat_coc', 'ma_sinh_vien', 'ma_phong',
    ]
    TRUONG_CHI_DOC_KHI_TAO = {'trang_thai'}
    CHO_PHEP_SUA = False  # DieuPhoiKTX cấm cập nhật hợp đồng sau khi tạo

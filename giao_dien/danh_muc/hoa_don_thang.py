"""Danh mục hóa đơn tháng: dùng ThangNam, mã HDT tự sinh ở backend."""
from thuc_the.tai_chinh import HoaDonThang, ThangNam
from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhHoaDonThang(ManHinhDanhMucCoSo):
    NGHIEP_VU_CHI_TIET = (('Thanh toán hóa đơn', 'thanh_toan_hoa_don_thang'),)
    LOAI = HoaDonThang
    TIEU_DE = 'Quản lý hóa đơn tháng'
    MO_TA = 'Tháng năm YYYY-MM; chọn Chi tiết hóa đơn để thanh toán.'
    TRUONG = [
        'ma', 'thang_nam', 'dien_cu', 'dien_moi', 'don_gia_dien',
        'nuoc_cu', 'nuoc_moi', 'don_gia_nuoc', 'phong', 'han_chot', 'trang_thai',
    ]
    BAT_BUOC = [
        'thang_nam', 'dien_cu', 'dien_moi', 'don_gia_dien',
        'nuoc_cu', 'nuoc_moi', 'don_gia_nuoc', 'phong', 'han_chot',
    ]
    TRUONG_CHI_DOC_KHI_TAO = {'trang_thai'}
    CHO_PHEP_SUA = False  # DieuPhoiKTX cấm cập nhật hóa đơn sau khi tạo

    def _chuyen_kieu(self, truong, value):
        if truong == 'thang_nam':
            try:
                return ThangNam.tu_chuoi(value)
            except (TypeError, ValueError) as exc:
                raise ValueError('Tháng năm phải có dạng YYYY-MM (ví dụ 2026-11).') from exc
        return super()._chuyen_kieu(truong, value)

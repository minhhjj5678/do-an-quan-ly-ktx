from dataclasses import dataclass

from thuc_the.ky_tuc_xa import Phong, SinhVien, ToaNha
from thuc_the.tai_chinh import HoaDonThang, HopDong
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from thuc_the.vi_pham import ViPham


@dataclass
class KhoDuLieu:
    toa_nha: dict[str, ToaNha]
    phong: dict[str, Phong]
    sinh_vien: dict[str, SinhVien]
    hop_dong: dict[str, HopDong]
    hoa_don_thang: dict[str, HoaDonThang]
    vi_pham: dict[str, ViPham]
    tai_khoan: dict[str, TaiKhoan]

def kiem_cheo_du_lieu(kho_du_lieu: KhoDuLieu) -> list[str]:
    """
    Kiểm tra dữ liệu trong kho dữ liệu có hợp lệ hay không.
    Trả về danh sách các lỗi tìm thấy, nếu không có lỗi thì trả về danh sách rỗng.
    """

    danh_sach_loi = []

    # Kiểm tra hợp đồng
    hop_dong_giu_cho_theo_sinh_vien = {}
    hop_dong_giu_cho_theo_phong = {}
    for hop_dong in kho_du_lieu.hop_dong.values():
        hop_dong_hop_le = True
        if hop_dong.ma_sinh_vien not in kho_du_lieu.sinh_vien:
            danh_sach_loi.append(f"Hợp đồng {hop_dong.ma} thuộc về sinh viên {hop_dong.ma_sinh_vien} nhưng sinh viên không tồn tại.")
            hop_dong_hop_le = False

        if hop_dong.ma_phong not in kho_du_lieu.phong:
            danh_sach_loi.append(f"Hợp đồng {hop_dong.ma} thuộc về phòng {hop_dong.ma_phong} nhưng phòng không tồn tại.")
            hop_dong_hop_le = False

        if not hop_dong_hop_le:
            continue

        # chi kiểm tra hợp đồng còn giữ chỗ không được có nhiều hợp đồng cùng thời gian cho một sinh viên hoặc một phòng
        # đối với hợp đồng đã kết thúc, nhiều hợp đồng cùng thời gian cho một sinh viên hoặc một phòng hợp lệ vì sinh viên
        # có thể chuyển phòng hoặc ký hợp đồng mới sau khi hợp đồng cũ kết thúc.
        if hop_dong.con_giu_cho():
            hop_dong_giu_cho_theo_sinh_vien[hop_dong.ma_sinh_vien] = hop_dong_giu_cho_theo_sinh_vien.get(hop_dong.ma_sinh_vien, []) + [hop_dong]
            hop_dong_giu_cho_theo_phong[hop_dong.ma_phong] = hop_dong_giu_cho_theo_phong.get(hop_dong.ma_phong, []) + [hop_dong]

    # Kiểm tra hóa đơn tháng
    danh_sach_hoa_don_theo_phong_va_thang = {}
    for hoa_don in kho_du_lieu.hoa_don_thang.values():
        if hoa_don.phong not in kho_du_lieu.phong:
            danh_sach_loi.append(f"Hóa đơn tháng {hoa_don.ma} thuộc phòng {hoa_don.phong} nhưng phòng không tồn tại.")
            continue

        key_hoa_don = (hoa_don.phong, hoa_don.thang_nam)
        danh_sach_hoa_don_theo_phong_va_thang[key_hoa_don] = danh_sach_hoa_don_theo_phong_va_thang.get(key_hoa_don, []) + [hoa_don.ma]

    # Kiểm tra sinh viên
    for ma_sinh_vien, danh_sach_hop_dong in hop_dong_giu_cho_theo_sinh_vien.items():
        sinh_vien = kho_du_lieu.sinh_vien[ma_sinh_vien]
        if not sinh_vien.con_hoat_dong:
            danh_sach_loi.append(f"Sinh viên {ma_sinh_vien} đã ngừng hoạt động nhưng vẫn có {len(danh_sach_hop_dong)} hợp đồng đang giữ chỗ: {', '.join(hd.ma for hd in danh_sach_hop_dong)}.")
        else:
            hop_dong_qua_gioi_han = tim_hop_dong_vuot_gioi_han(danh_sach_hop_dong, 1)
            if hop_dong_qua_gioi_han:
                danh_sach_loi.append(f"Sinh viên {ma_sinh_vien} có nhiều hợp đồng đang giữ chỗ cùng lúc: {', '.join(hd.ma for hd in hop_dong_qua_gioi_han)}.")

    # Kiểm tra phòng
    for ma_phong, danh_sach_hop_dong in hop_dong_giu_cho_theo_phong.items():
        phong = kho_du_lieu.phong[ma_phong]
        if not phong.con_hoat_dong:
            danh_sach_loi.append(f"Phòng {ma_phong} đã ngừng hoạt động nhưng vẫn có {len(danh_sach_hop_dong)} hợp đồng đang giữ chỗ: {', '.join(hd.ma for hd in danh_sach_hop_dong)}.")
        else:
            hop_dong_qua_gioi_han = tim_hop_dong_vuot_gioi_han(danh_sach_hop_dong, phong.suc_chua)
            if hop_dong_qua_gioi_han:
                danh_sach_loi.append(f"Phòng {ma_phong} có {len(hop_dong_qua_gioi_han)} hợp đồng đang giữ chỗ cùng lúc: {', '.join(hd.ma for hd in hop_dong_qua_gioi_han)}, vượt sức chứa tối đa là {phong.suc_chua}.")

    for (ma_phong, thang_nam), danh_sach_hoa_don in danh_sach_hoa_don_theo_phong_va_thang.items():
        if len(danh_sach_hoa_don) > 1:
            danh_sach_loi.append(f"Phòng {ma_phong} có nhiều hóa đơn trùng kỳ hạn {thang_nam}: {', '.join(danh_sach_hoa_don)}.")

    # Kiểm tra tòa nhà
    for phong in kho_du_lieu.phong.values():
        if phong.toa_nha not in kho_du_lieu.toa_nha:
            danh_sach_loi.append(f"Phòng {phong.ma} thuộc tòa nhà {phong.toa_nha} nhưng tòa nhà không tồn tại.")
            continue

        toa_nha = kho_du_lieu.toa_nha[phong.toa_nha]
        if phong.tang > toa_nha.so_tang:
            danh_sach_loi.append(f"Phòng {phong.ma} thuộc tòa nhà {phong.toa_nha} nhưng tầng {phong.tang} vượt số tầng tối đa là {toa_nha.so_tang}.")
        if not toa_nha.con_hoat_dong and phong.con_hoat_dong:
            danh_sach_loi.append(f"Phòng {phong.ma} thuộc tòa nhà {phong.toa_nha} nhưng tòa nhà đã ngừng hoạt động trong khi phòng vẫn còn hoạt động.")

    # Kiểm tra vi phạm
    for vi_pham in kho_du_lieu.vi_pham.values():
        if vi_pham.sinh_vien not in kho_du_lieu.sinh_vien:
            danh_sach_loi.append(f"Vi phạm {vi_pham.ma} thuộc sinh viên {vi_pham.sinh_vien} nhưng sinh viên không tồn tại.")
            continue

    # Kiểm tra tài khoản
    sinh_vien_da_co_tai_khoan = {}
    for tai_khoan in kho_du_lieu.tai_khoan.values():
        if tai_khoan.loai_tai_khoan == LoaiTaiKhoan.SINH_VIEN and tai_khoan.ma_chu_the is None:
            danh_sach_loi.append(f"Tài khoản {tai_khoan.ma} là sinh viên nhưng không có mã chủ thể.")
        elif tai_khoan.ma_chu_the is not None:
            if tai_khoan.loai_tai_khoan == LoaiTaiKhoan.SINH_VIEN:
                if tai_khoan.ma_chu_the not in kho_du_lieu.sinh_vien:
                    danh_sach_loi.append(f"Tài khoản {tai_khoan.ma} thuộc sinh viên {tai_khoan.ma_chu_the} nhưng sinh viên không tồn tại.")
                sinh_vien_da_co_tai_khoan[tai_khoan.ma_chu_the] = sinh_vien_da_co_tai_khoan.get(tai_khoan.ma_chu_the, []) + [tai_khoan.ma]
                
            elif tai_khoan.loai_tai_khoan == LoaiTaiKhoan.QUAN_TRI_VIEN:
                danh_sach_loi.append(f"Tài khoản {tai_khoan.ma} là quản trị viên nhưng có mã chủ thể {tai_khoan.ma_chu_the}.")

    for ma_sinh_vien, danh_sach_tai_khoan in sinh_vien_da_co_tai_khoan.items():
        if len(danh_sach_tai_khoan) > 1:
            danh_sach_loi.append(f"Sinh viên {ma_sinh_vien} có nhiều hơn một tài khoản: {', '.join(danh_sach_tai_khoan)}.")

    return danh_sach_loi

def tim_hop_dong_vuot_gioi_han(danh_sach_hop_dong: list[HopDong], gioi_han_toi_da: int) -> list[HopDong]:
    """
    Kiểm tra xem danh sách hợp đồng có vượt quá giới hạn tối đa theo khoảng thời gian hay không.
    Nếu ngày kết thúc hiện tại trùng với ngày bắt đầu của hợp đồng tiếp theo thì vẫn được tính là 2 hợp đồng đang giữ.
    """
    if len(danh_sach_hop_dong) <= gioi_han_toi_da:
        return []

    danh_sach_hop_dong_dang_giu_cho: list[HopDong] = []
    for hop_dong_dang_xet in sorted(danh_sach_hop_dong, key=lambda x: x.ngay_bat_dau):
        danh_sach_hop_dong_dang_giu_cho = [hd for hd in danh_sach_hop_dong_dang_giu_cho if hd.ngay_ket_thuc >= hop_dong_dang_xet.ngay_bat_dau]
        danh_sach_hop_dong_dang_giu_cho.append(hop_dong_dang_xet)

        if len(danh_sach_hop_dong_dang_giu_cho) > gioi_han_toi_da:
            return danh_sach_hop_dong_dang_giu_cho
    return []

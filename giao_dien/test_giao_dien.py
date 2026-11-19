"""Chạy thử giao diện KTX bằng Mock, không đọc/ghi dữ liệu thật.

Đặt cùng cấp với mock_backend.py trong thư mục giao_dien/.
Chạy từ thư mục gốc dự án:
    python -m giao_dien.test_giao_dien --chi-test
    python -m giao_dien.test_giao_dien
"""
import argparse
import os
import sys
from datetime import date
from dataclasses import replace
from typing import cast

# Cho phép nhấn Run trong VS Code.
THU_MUC_GIAO_DIEN = os.path.dirname(os.path.abspath(__file__))
THU_MUC_GOC = os.path.dirname(THU_MUC_GIAO_DIEN)
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)

from giao_dien.dung_chung.adapter import Adapter
from giao_dien.mock_backend import MockDieuPhoi, MockPhien
from thuc_the.ky_tuc_xa import SinhVien, Phong, ToaNha
from thuc_the.tai_chinh import HopDong, HoaDonThang
from thuc_the.vi_pham import ViPham
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from tien_ich import tao_ma
from tien_ich.cau_hinh_dong import CauHinhDong
from giao_thuc.nghiep_vu import GiaoThucDieuPhoi, GiaoThucPhienLamViec

ket_qua = []


def kiem_tra(ten, ham):
    try:
        ham()
        print(f'[PASS] {ten}')
        ket_qua.append(True)
    except Exception as loi:
        print(f'[FAIL] {ten}: {type(loi).__name__}: {loi}')
        ket_qua.append(False)


def phai_loi(ham):
    """Kiểm tra thao tác không được phép thực sự bị từ chối."""
    try:
        ham()
    except (ValueError, PermissionError):
        return
    raise AssertionError('Thao tác phải bị từ chối nhưng đã thực hiện thành công')


def tao_he_thong():
    dp = MockDieuPhoi()
    phien = MockPhien(dp)  # Gắn chung kho tài khoản với điều phối Mock.
    # Mock không kế thừa ABC; ép kiểu rõ ràng chỉ tại ranh giới chạy thử.
    adapter = Adapter(cast(GiaoThucDieuPhoi, dp), cast(GiaoThucPhienLamViec, phien))
    adapter.nap_du_lieu_file()
    return adapter


def tao_admin():
    app = tao_he_thong()
    app.dang_nhap('admin', '123456')
    assert app.la_admin() and not app.la_sinh_vien()
    return app


def t_dang_nhap():
    app = tao_he_thong()
    phai_loi(lambda: app.dang_nhap('admin', 'sai'))
    phai_loi(lambda: app.lay_tat_ca(SinhVien))
    app.dang_nhap('admin', '123456')
    assert app.la_admin()
    phai_loi(lambda: app.dang_nhap('admin', '123456'))
    app.dang_xuat()
    assert not app.la_admin()
    app.dang_nhap('nhanvien', '123456')
    # 'nhanvien' chỉ là tên đăng nhập; vai trò thực tế là Sinh viên.
    assert app.la_sinh_vien() and not app.la_admin()
    assert app.ma_sinh_vien_hien_tai() == 'SV0001'
    app.dang_xuat()
    assert app.tai_khoan_hien_tai is None


def t_doi_mat_khau():
    app = tao_admin()
    phai_loi(lambda: app.doi_mat_khau('moi123', 'sai'))
    app.doi_mat_khau('moi123', '123456')
    app.doi_mat_khau('lai123', tai_khoan='nhanvien')
    app.dang_xuat()
    app.dang_nhap('admin', 'moi123')
    app.dang_xuat()
    app.dang_nhap('nhanvien', 'lai123')
    phai_loi(lambda: app.doi_mat_khau('khac123', tai_khoan='admin'))


def t_tai_khoan_va_danh_sach():
    app = tao_he_thong()
    phai_loi(lambda: app.tao_tai_khoan('sv_moi', '123456', LoaiTaiKhoan.SINH_VIEN, 'SV9999'))
    app.dang_nhap('admin', '123456')
    tat_ca = app.lay_tat_ca(TaiKhoan, lay_luu_tru=True)
    assert set(tat_ca) == {'admin', 'nhanvien'}
    assert tat_ca['nhanvien'].loai_tai_khoan == LoaiTaiKhoan.SINH_VIEN

    app.tao_tai_khoan('sv_moi', '123456', LoaiTaiKhoan.SINH_VIEN, 'SV9999')
    tat_ca = app.lay_tat_ca(TaiKhoan, lay_luu_tru=True)
    assert 'sv_moi' in tat_ca and tat_ca['sv_moi'].ma_chu_the == 'SV9999'
    phai_loi(lambda: app.tao_tai_khoan('sv_moi', '654321', LoaiTaiKhoan.QUAN_TRI_VIEN))
    phai_loi(lambda: app.tao_tai_khoan('sv_khac', '123456', LoaiTaiKhoan.SINH_VIEN, 'SV9999'))
    app.dang_xuat()
    app.dang_nhap('sv_moi', '123456')
    assert app.la_sinh_vien()
    phai_loi(lambda: app.tao_tai_khoan('admin2', '123456', LoaiTaiKhoan.QUAN_TRI_VIEN))


def t_quan_tri_tai_khoan():
    app = tao_admin()
    app.ngung_tai_khoan('nhanvien')
    assert not app.lay_tat_ca(TaiKhoan, lay_luu_tru=True)['nhanvien'].con_hoat_dong
    app.dang_xuat()
    phai_loi(lambda: app.dang_nhap('nhanvien', '123456'))

    app.dang_nhap('admin', '123456')
    app.kich_hoat_lai_tai_khoan('nhanvien')
    assert app.lay_tat_ca(TaiKhoan)['nhanvien'].con_hoat_dong
    app.dang_xuat()
    app.dang_nhap('nhanvien', '123456')
    app.dang_xuat()

    app.dang_nhap('admin', '123456')
    app.ngung_tai_khoan('nhanvien')
    app.xoa_tai_khoan('nhanvien')
    assert 'nhanvien' not in app.lay_tat_ca(TaiKhoan, lay_luu_tru=True)


def t_sinh_ma():
    assert tao_ma.ma_sinh_vien(['SV0001', 'SV0008']) == 'SV0009'
    assert tao_ma.ma_hop_dong(['HD0001', 'HDT9999']) == 'HD0002'
    app = tao_admin()
    for loai, tien_to in (
        (SinhVien, 'SV'), (Phong, 'P'), (ToaNha, 'TN'),
        (HopDong, 'HD'), (HoaDonThang, 'HDT'), (ViPham, 'VP'),
    ):
        obj = app.tao_va_them(loai, ten='Dữ liệu thử')
        assert obj.ma == f'{tien_to}0001', (loai.__name__, obj.ma)


def t_crud_sinh_vien():
    app = tao_admin()
    sv = app.tao_va_them(
        SinhVien, ten='Nguyễn An', sdt='0123456789', nam_sinh=2000,
        cccd='123456789012', dia_chi_chi_tiet='123 Đường ABC',
        xa='79001', tinh='79',
    )
    ma = sv.ma
    assert ma == 'SV0001'
    assert app.lay_theo_ma(SinhVien, ma) is sv
    app.cap_nhat_truong(SinhVien, ma, ten='Nguyễn Bình')
    assert app.lay_theo_ma(SinhVien, ma).ten == 'Nguyễn Bình'
    assert len(app.loc(SinhVien, lambda x: 'Bình' in x.ten)) == 1
    phai_loi(lambda: app.cap_nhat_truong(SinhVien, ma, truong_khong_co='x'))
    app.luu_tru(SinhVien, ma)
    assert not app.lay_tat_ca(SinhVien)
    assert ma in app.lay_tat_ca(SinhVien, lay_luu_tru=True)
    app.tai_kich_hoat(SinhVien, ma)
    assert ma in app.lay_tat_ca(SinhVien)
    app.luu_tru(SinhVien, ma)
    app.xoa(SinhVien, ma)
    assert not app.lay_tat_ca(SinhVien, lay_luu_tru=True)
    assert app.tao_va_them(SinhVien, ten='Người khác').ma == 'SV0002'


def t_nghiep_vu():
    app = tao_admin()
    hd = app.tao_va_them(HopDong, ten='Hợp đồng thử')
    app.nghiep_vu('thanh_toan_hop_dong', hd.ma)
    assert hd.trang_thai == 'Đã thanh toán'
    phai_loi(lambda: app.nghiep_vu('khong_ton_tai', hd.ma))


def t_thong_ke_va_cau_hinh():
    app = tao_admin()
    app.tao_va_them(Phong, ten='P101')
    so_phong = app.thong_ke('thong_ke_so_phong')
    lap_day = app.thong_ke('thong_ke_ty_le_lap_day')
    cong_no = app.thong_ke('thong_ke_cong_no')
    # Mock tuân thủ giao thức backend: tuple / float / tuple.
    assert isinstance(so_phong, tuple) and so_phong[2] == 1
    assert isinstance(lap_day, float) and 0.0 <= lap_day <= 1.0
    assert isinstance(cong_no, tuple) and len(cong_no) == 2
    phai_loi(lambda: app.thong_ke('ten_khong_ton_tai'))

    # Cấu hình của backend là CauHinhDong, không phải dictionary.
    cfg = app.doc_cau_hinh()
    assert isinstance(cfg, CauHinhDong)
    cfg_moi = replace(cfg, DON_GIA_DIEN=cfg.DON_GIA_DIEN + 100)
    app.cap_nhat_cau_hinh(cfg_moi)
    assert app.doc_cau_hinh().DON_GIA_DIEN == cfg_moi.DON_GIA_DIEN


def t_phan_quyen_va_ca_nhan():
    app = tao_admin()
    sv1 = app.tao_va_them(SinhVien, ten='Sinh viên 1')
    sv2 = app.tao_va_them(SinhVien, ten='Sinh viên 2')
    p1 = app.tao_va_them(Phong, ten='Phòng 101')
    p2 = app.tao_va_them(Phong, ten='Phòng 102')
    hd1 = app.tao_va_them(HopDong, ma_sinh_vien=sv1.ma, ma_phong=p1.ma,
                          ngay_bat_dau=date(2026, 1, 1), ngay_ket_thuc=date(2026, 12, 31))
    app.tao_va_them(HopDong, ma_sinh_vien=sv2.ma, ma_phong=p2.ma,
                    ngay_bat_dau=date(2026, 1, 1), ngay_ket_thuc=date(2026, 12, 31))
    app.tao_va_them(HoaDonThang, phong=p1.ma, thang_nam='2026-11')
    app.tao_va_them(HoaDonThang, phong=p2.ma, thang_nam='2026-11')
    vp1 = app.tao_va_them(ViPham, sinh_vien=sv1.ma, mo_ta='Vi phạm mẫu')
    app.tao_va_them(ViPham, sinh_vien=sv2.ma, mo_ta='Vi phạm mẫu 2')

    app.dang_xuat()
    app.dang_nhap('nhanvien', '123456')
    assert app.la_sinh_vien() and app.ma_sinh_vien_hien_tai() == sv1.ma
    ca_nhan = app.lay_du_lieu_ca_nhan()
    assert ca_nhan['sinh_vien'].ma == sv1.ma
    assert [p.ma for p in ca_nhan['phong']] == [p1.ma]
    assert [h.ma for h in ca_nhan['hop_dong']] == [hd1.ma]
    assert len(ca_nhan['hoa_don']) == 1
    assert [v.ma for v in ca_nhan['vi_pham']] == [vp1.ma]

    phai_loi(lambda: app.lay_tat_ca(SinhVien))
    phai_loi(lambda: app.lay_theo_ma(SinhVien, sv2.ma))
    phai_loi(lambda: app.tao_va_them(Phong, ten='Phòng trái quyền'))
    phai_loi(lambda: app.thong_ke('thong_ke_cong_no'))
    phai_loi(lambda: app.cap_nhat_cau_hinh(CauHinhDong()))
    phai_loi(lambda: app.nghiep_vu('thanh_toan_hop_dong', hd1.ma))


def t_dia_ly():
    app = tao_he_thong()
    ds = app.dia_ly()
    assert isinstance(ds, dict) and ds
    ma_tinh = next(iter(ds))
    tinh = app.dia_ly(ma_tinh)
    assert not isinstance(tinh, dict)  # Thu hẹp Union cho Pylance.
    assert tinh.ma == ma_tinh
    app.nap_du_lieu_api()


def chay_kiem_tra():
    ket_qua.clear()
    print('=== Kiểm tra Adapter + Mock (Admin / Sinh viên) ===')
    for ten, ham in (
        ('Đăng nhập / đăng xuất / vai trò', t_dang_nhap),
        ('Đổi và reset mật khẩu', t_doi_mat_khau),
        ('Tạo tài khoản + đồng bộ danh sách', t_tai_khoan_va_danh_sach),
        ('Ngừng / kích hoạt / xóa tài khoản', t_quan_tri_tai_khoan),
        ('Sinh mã tự động', t_sinh_ma),
        ('CRUD sinh viên + lưu trữ', t_crud_sinh_vien),
        ('Nghiệp vụ', t_nghiep_vu),
        ('Thống kê + cấu hình Mock', t_thong_ke_va_cau_hinh),
        ('Phân quyền + dữ liệu cá nhân', t_phan_quyen_va_ca_nhan),
        ('Địa lý', t_dia_ly),
    ):
        kiem_tra(ten, ham)
    dat = sum(ket_qua)
    print(f'=== {dat}/{len(ket_qua)} ca đạt ===')
    return dat == len(ket_qua)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chi-test', action='store_true',
                        help='Chỉ chạy kiểm tra, không mở giao diện')
    args = parser.parse_args()
    tat_ca_dat = chay_kiem_tra()
    if args.chi_test:
        sys.exit(0 if tat_ca_dat else 1)
    if not tat_ca_dat:
        print('Có ca kiểm tra chưa đạt; vẫn mở giao diện để xem thử.')

    from giao_dien.app import App
    dp = MockDieuPhoi()
    phien = MockPhien(dp)  # Phải dùng cùng MockDieuPhoi để bảng tài khoản đồng bộ.
    app = App(cast(GiaoThucDieuPhoi, dp), cast(GiaoThucPhienLamViec, phien))
    app.mainloop()


if __name__ == '__main__':
    main()

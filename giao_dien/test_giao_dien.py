import argparse
import os
import sys

# Lấy thư mục cha của giao_dien
thu_muc_hien_tai = os.path.dirname(os.path.abspath(__file__))
thu_muc_goc = os.path.dirname(thu_muc_hien_tai)

# Thêm thư mục gốc vào đường dẫn import
if thu_muc_goc not in sys.path:
    sys.path.insert(0, thu_muc_goc)

from giao_dien.dung_chung.adapter import Adapter
from giao_dien.app import App
from giao_dien.mock_backend import MockDieuPhoi, MockPhien
from thuc_the.ky_tuc_xa import SinhVien
from thuc_the.tai_khoan import LoaiTaiKhoan

ket_qua: list[bool] = []


def kiem_tra(ten, ham):
    try:
        ham()
        print(f"[PASS] {ten}")
        ket_qua.append(True)
    except Exception as loi:
        print(f"[FAIL] {ten}: {type(loi).__name__}: {loi}")
        ket_qua.append(False)


def phai_loi(ham):
    """Mong đợi ham() ném lỗi."""
    try:
        ham()
    except Exception:
        return
    raise AssertionError("mong đợi có lỗi nhưng không có")


def tao_he_thong() -> Adapter:
    dp = MockDieuPhoi()
    phien = MockPhien(dp)
    dp.nap_du_lieu_file()
    return Adapter(dp, phien)


# ---------------- Các ca kiểm tra ----------------
def t_dang_nhap():
    app = tao_he_thong()
    phai_loi(lambda: app.dang_nhap("admin", "sai"))
    app.dang_nhap("admin", "123456")
    assert app.la_admin()
    phai_loi(lambda: app.dang_nhap("admin", "123456"))  # đã đăng nhập
    app.dang_xuat()
    assert not app.la_admin()
    phai_loi(app.dang_xuat)  # chưa đăng nhập


def t_doi_mat_khau():
    app = tao_he_thong()
    app.dang_nhap("admin", "123456")
    phai_loi(lambda: app.doi_mat_khau("moi123", "sai"))
    app.doi_mat_khau("moi123", "123456")
    app.dang_xuat()
    app.dang_nhap("admin", "moi123")
    app.doi_mat_khau("lai123", tai_khoan="sinhvien")  # admin reset người khác
    app.dang_xuat()
    app.dang_nhap("sinhvien", "lai123")
    phai_loi(lambda: app.doi_mat_khau("x", tai_khoan="admin"))  # sinh viên không có quyền


def t_tao_tai_khoan():
    app = tao_he_thong()
    loai_sv = next(m for m in LoaiTaiKhoan if "QUAN" not in m.name.upper())
    phai_loi(lambda: app.tao_tai_khoan("sv_moi", "123456", loai_sv, "SV9999"))  # chưa đăng nhập
    app.dang_nhap("admin", "123456")
    app.tao_tai_khoan("sv_moi", "123456", loai_sv, "SV9999")
    phai_loi(lambda: app.tao_tai_khoan("sv_moi", "123456", loai_sv, "SV9999"))  # trùng
    app.dang_xuat()
    app.dang_nhap("sv_moi", "123456")
    assert not app.la_admin()


def t_ngung_va_xoa_tai_khoan():
    app = tao_he_thong()
    app.dang_nhap("admin", "123456")
    phai_loi(lambda: app.ngung_tai_khoan("admin"))  # chính mình
    phai_loi(lambda: app.xoa_tai_khoan("sinhvien"))  # còn hoạt động
    app.ngung_tai_khoan("sinhvien")
    app.kich_hoat_lai_tai_khoan("sinhvien")
    app.ngung_tai_khoan("sinhvien")
    app.xoa_tai_khoan("sinhvien")
    phai_loi(lambda: app.kich_hoat_lai_tai_khoan("sinhvien"))  # đã xóa


def t_crud_sinh_vien():
    app = tao_he_thong()
    sv = app.tao_va_them(
        SinhVien, ten="A", sdt="0123456789", nam_sinh=2000, cccd="123456789012",
        dia_chi_chi_tiet="123 Đường ABC, Quận XYZ", xa="Xã XYZ", tinh="Tỉnh XYZ",
    )
    ma = sv.ma
    assert len(app.lay_tat_ca(SinhVien)) == 1
    assert app.lay_theo_ma(SinhVien, ma) is sv
    phai_loi(lambda: app.xoa(SinhVien, ma))  # đang hoạt động
    app.luu_tru(SinhVien, ma)
    assert len(app.lay_tat_ca(SinhVien)) == 0
    assert len(app.lay_tat_ca(SinhVien, lay_luu_tru=True)) == 1
    phai_loi(lambda: app.lay_theo_ma(SinhVien, ma))
    app.tai_kich_hoat(SinhVien, ma)
    app.luu_tru(SinhVien, ma)
    app.xoa(SinhVien, ma)
    assert len(app.lay_tat_ca(SinhVien, lay_luu_tru=True)) == 0


def t_thong_ke_va_cau_hinh():
    app = tao_he_thong()
    assert len(app.thong_ke("thong_ke_so_phong")) == 3
    assert 0 <= app.thong_ke("thong_ke_ty_le_lap_day") <= 1
    assert len(app.thong_ke("thong_ke_cong_no")) == 2
    phai_loi(lambda: app.thong_ke("ten_khong_ton_tai"))
    app.doc_cau_hinh()


def t_dia_ly():
    app = tao_he_thong()
    phai_loi(app.dia_ly)  # chưa nạp API
    app.nap_du_lieu_api()
    assert isinstance(app.dia_ly(), dict)


def chay_kiem_tra() -> bool:
    print("=== Tự kiểm tra Adapter + mock ===")
    kiem_tra("Đăng nhập / đăng xuất", t_dang_nhap)
    kiem_tra("Đổi mật khẩu", t_doi_mat_khau)
    kiem_tra("Tạo tài khoản", t_tao_tai_khoan)
    kiem_tra("Ngừng / kích hoạt / xóa tài khoản", t_ngung_va_xoa_tai_khoan)
    kiem_tra("CRUD sinh viên + lưu trữ", t_crud_sinh_vien)
    kiem_tra("Thống kê + cấu hình", t_thong_ke_va_cau_hinh)
    kiem_tra("Địa lý", t_dia_ly)
    dat = sum(ket_qua)
    print(f"=== {dat}/{len(ket_qua)} ca đạt ===\n")
    return dat == len(ket_qua)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chi-test", action="store_true", help="chỉ chạy kiểm tra, không mở giao diện")
    args = parser.parse_args()

    tat_ca_dat = chay_kiem_tra()
    if args.chi_test:
        sys.exit(0 if tat_ca_dat else 1)

    # Hệ thống mới hoàn toàn cho giao diện (mock chỉ cho nạp file một lần)
    # dia_ly_mau: dict[str, Tinh] gồm các đối tượng Tinh thật nếu muốn combobox Tỉnh/Xã có dữ liệu
    dieu_phoi = MockDieuPhoi(dia_ly_mau=None)
    phien = MockPhien(dieu_phoi)
    # Không gọi nap_du_lieu_api ở đây: App tự nạp trong luồng phụ khi khởi động

    app = App(dieu_phoi, phien)
    app.mainloop()


if __name__ == "__main__":
    main()
"""Chạy thử Adapter và giao diện bằng mock_backend (không dùng dữ liệu thật).

Chạy tại thư mục gốc dự án:
    python -m giao_dien.test_giao_dien --chi-test
    python -m giao_dien.test_giao_dien
"""
import argparse
import os
import sys

# Cho phép chạy cả bằng nút Run trong VS Code.
THU_MUC_GIAO_DIEN = os.path.dirname(os.path.abspath(__file__))
THU_MUC_GOC = os.path.dirname(THU_MUC_GIAO_DIEN)
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)

from typing import cast

from giao_thuc.nghiep_vu import GiaoThucDieuPhoi, GiaoThucPhienLamViec
from thuc_the.thuc_the_goc import ThucTheGoc
from giao_dien.dung_chung.adapter import Adapter
from giao_dien.mock_backend import MockDieuPhoi, MockPhien
from thuc_the.ky_tuc_xa import SinhVien, Phong, ToaNha
from thuc_the.tai_chinh import HopDong, HoaDonThang
from thuc_the.vi_pham import ViPham
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from tien_ich import tao_ma


ket_qua = []


def kiem_tra(ten, ham):
    try:
        ham()
        print(f"[PASS] {ten}")
        ket_qua.append(True)
    except Exception as loi:
        print(f"[FAIL] {ten}: {type(loi).__name__}: {loi}")
        ket_qua.append(False)


def phai_loi(ham):
    """Báo lỗi nếu một thao tác lẽ ra bị từ chối lại thực hiện được."""
    try:
        ham()
    except Exception:
        return
    raise AssertionError("Mong đợi có lỗi nhưng thao tác vẫn thành công")


def tao_he_thong():
    dp = MockDieuPhoi()
    phien = MockPhien(dp)  # Cùng kho tài khoản với MockDieuPhoi
    # Mock không khai báo kế thừa giao thức, nhưng cung cấp các hàm Adapter gọi.
    # cast chỉ dùng để Pylance hiểu đây là dữ liệu chạy thử.
    app = Adapter(
        cast(GiaoThucDieuPhoi, dp),
        cast(GiaoThucPhienLamViec, phien),
    )
    app.nap_du_lieu_file()
    return app


def t_dang_nhap():
    app = tao_he_thong()
    phai_loi(lambda: app.dang_nhap("admin", "sai"))
    app.dang_nhap("admin", "123456")
    assert app.la_admin()
    phai_loi(lambda: app.dang_nhap("admin", "123456"))
    app.dang_xuat()
    assert not app.la_admin()
    app.dang_nhap("nhanvien", "123456")
    assert not app.la_admin()
    app.dang_xuat()


def t_doi_mat_khau():
    app = tao_he_thong()
    app.dang_nhap("admin", "123456")
    phai_loi(lambda: app.doi_mat_khau("moi123", "sai"))
    app.doi_mat_khau("moi123", "123456")
    app.doi_mat_khau("lai123", tai_khoan="nhanvien")
    app.dang_xuat()
    app.dang_nhap("admin", "moi123")
    app.dang_xuat()
    app.dang_nhap("nhanvien", "lai123")
    phai_loi(lambda: app.doi_mat_khau("x", tai_khoan="admin"))


def t_tao_tai_khoan():
    app = tao_he_thong()
    loai_thuong = next(
        (x for x in LoaiTaiKhoan
         if "ADMIN" not in x.name.upper() and "QUAN_TRI" not in x.name.upper()),
        None,
    )
    if loai_thuong is None:
        raise ValueError("LoaiTaiKhoan không có loại tài khoản thường để kiểm thử")

    phai_loi(lambda: app.tao_tai_khoan("sv_moi", "123456", loai_thuong, "SV9999"))
    app.dang_nhap("admin", "123456")
    app.tao_tai_khoan("sv_moi", "123456", loai_thuong, "SV9999")
    # Tài khoản vừa tạo phải xuất hiện ngay ở danh sách giao diện.
    ds = app.lay_tat_ca(TaiKhoan, lay_luu_tru=True)
    assert "admin" in ds and "nhanvien" in ds and "sv_moi" in ds
    assert ds["sv_moi"].ma_chu_the == "SV9999"
    assert ds["sv_moi"].con_hoat_dong
    phai_loi(lambda: app.tao_tai_khoan("sv_moi", "123456", loai_thuong, "SV9999"))
    app.dang_xuat()
    app.dang_nhap("sv_moi", "123456")
    assert not app.la_admin()


def t_quan_tri_tai_khoan():
    app = tao_he_thong()
    app.dang_nhap("admin", "123456")
    app.ngung_tai_khoan("nhanvien")
    assert "nhanvien" not in app.lay_tat_ca(TaiKhoan)
    assert not app.lay_tat_ca(TaiKhoan, lay_luu_tru=True)["nhanvien"].con_hoat_dong
    app.dang_xuat()
    phai_loi(lambda: app.dang_nhap("nhanvien", "123456"))

    app.dang_nhap("admin", "123456")
    app.kich_hoat_lai_tai_khoan("nhanvien")
    assert app.lay_tat_ca(TaiKhoan)["nhanvien"].con_hoat_dong
    app.dang_xuat()
    app.dang_nhap("nhanvien", "123456")
    app.dang_xuat()

    app.dang_nhap("admin", "123456")
    app.ngung_tai_khoan("nhanvien")
    app.xoa_tai_khoan("nhanvien")
    assert "nhanvien" not in app.lay_tat_ca(TaiKhoan, lay_luu_tru=True)
    phai_loi(lambda: app.kich_hoat_lai_tai_khoan("nhanvien"))


def t_sinh_ma():
    # Kiểm tra trực tiếp quy tắc trong tien_ich/tao_ma.py.
    assert tao_ma.ma_sinh_vien(["SV0001", "SV0008"]) == "SV0009"
    assert tao_ma.ma_hop_dong(["HD0001", "HDT9999"]) == "HD0002"

    app = tao_he_thong()
    cac_loai: list[tuple[type[ThucTheGoc], str]] = [
        (SinhVien, "SV"), (Phong, "P"), (ToaNha, "TN"),
        (HopDong, "HD"), (HoaDonThang, "HDT"), (ViPham, "VP"),
    ]
    for loai, tien_to in cac_loai:
        obj = app.tao_va_them(loai, ten="Dữ liệu thử")
        assert obj.ma == f"{tien_to}0001", (loai.__name__, obj.ma)

    # Sinh tiếp một mã và bảo đảm không dùng lại mã vừa xóa.
    phong_cu = app.lay_tat_ca(Phong)["P0001"]
    app.xoa(Phong, phong_cu.ma)
    phong_moi = app.tao_va_them(Phong, ten="Phòng mới")
    assert phong_moi.ma == "P0002"


def t_crud_sinh_vien():
    app = tao_he_thong()
    sv = app.tao_va_them(
        SinhVien, ten="Nguyễn An", sdt="0123456789", nam_sinh=2000,
        cccd="123456789012", dia_chi_chi_tiet="123 Đường ABC",
        xa="79001", tinh="79",
    )
    ma = sv.ma
    assert ma == "SV0001"
    assert app.lay_theo_ma(SinhVien, ma) is sv
    assert len(app.lay_tat_ca(SinhVien)) == 1

    app.cap_nhat_truong(SinhVien, ma, ten="Nguyễn Bình")
    assert app.lay_theo_ma(SinhVien, ma).ten == "Nguyễn Bình"
    assert len(app.loc(SinhVien, lambda x: "Bình" in x.ten)) == 1
    phai_loi(lambda: app.cap_nhat_truong(SinhVien, ma, truong_khong_co="x"))

    app.luu_tru(SinhVien, ma)
    assert not app.lay_tat_ca(SinhVien)
    assert ma in app.lay_tat_ca(SinhVien, lay_luu_tru=True)
    phai_loi(lambda: app.lay_theo_ma(SinhVien, ma))
    app.tai_kich_hoat(SinhVien, ma)
    assert ma in app.lay_tat_ca(SinhVien)
    app.luu_tru(SinhVien, ma)
    app.xoa(SinhVien, ma)
    assert not app.lay_tat_ca(SinhVien, lay_luu_tru=True)
    assert app.tao_va_them(SinhVien, ten="Người khác").ma == "SV0002"


def t_nghiep_vu():
    app = tao_he_thong()
    hd = app.tao_va_them(HopDong, ten="Hợp đồng thử")
    app.nghiep_vu("thanh_toan_hop_dong", hd.ma)
    assert hd.trang_thai == "Đã thanh toán"
    phai_loi(lambda: app.nghiep_vu("khong_ton_tai", hd.ma))


def t_thong_ke_va_cau_hinh():
    app = tao_he_thong()
    app.tao_va_them(Phong, ten="P101")
    so_phong = app.thong_ke("thong_ke_so_phong")
    lap_day = app.thong_ke("thong_ke_ty_le_lap_day")
    cong_no = app.thong_ke("thong_ke_cong_no")
    assert so_phong["tong_so_phong"] == 1
    assert 0 <= lap_day["ty_le_lap_day"] <= 1
    assert "tong_tien_no" in cong_no
    phai_loi(lambda: app.thong_ke("ten_khong_ton_tai"))

    # Kiểm thử với MockDieuPhoi: cấu hình trong mock là dictionary.
    # Gán về object vì Adapter thật có thể khai báo trả về CauHinhDong.
    cfg: object = app.doc_cau_hinh()
    assert isinstance(cfg, dict), "Mock phải trả cấu hình dạng dict"
    app.cap_nhat_cau_hinh({**cfg, "chu_de": "BLUE"})

    cfg_sau: object = app.doc_cau_hinh()
    assert isinstance(cfg_sau, dict)
    assert cfg_sau["chu_de"] == "BLUE"


def t_dia_ly():
    app = tao_he_thong()
    # Mock mới nạp tỉnh/xã khi gọi nap_du_lieu_file().
    danh_sach = app.dia_ly()
    assert isinstance(danh_sach, dict) and danh_sach
    ma_tinh = next(iter(danh_sach))
    tinh_duoc_chon = app.dia_ly(ma_tinh)
    assert not isinstance(tinh_duoc_chon, dict)
    assert tinh_duoc_chon.ma == ma_tinh
    app.nap_du_lieu_api()  # Trong mock chỉ là hàm không làm gì


def chay_kiem_tra():
    ket_qua.clear()
    print("=== Kiểm tra Adapter + mock theo tao_ma.py ===")
    kiem_tra("Đăng nhập / đăng xuất", t_dang_nhap)
    kiem_tra("Đổi và reset mật khẩu", t_doi_mat_khau)
    kiem_tra("Tạo tài khoản", t_tao_tai_khoan)
    kiem_tra("Ngừng / kích hoạt / xóa tài khoản", t_quan_tri_tai_khoan)
    kiem_tra("Sinh mã và tránh trùng", t_sinh_ma)
    kiem_tra("CRUD sinh viên + lưu trữ", t_crud_sinh_vien)
    kiem_tra("Nghiệp vụ", t_nghiep_vu)
    kiem_tra("Thống kê + cấu hình", t_thong_ke_va_cau_hinh)
    kiem_tra("Địa lý", t_dia_ly)
    dat = sum(ket_qua)
    print(f"=== {dat}/{len(ket_qua)} ca đạt ===\n")
    return dat == len(ket_qua)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chi-test", action="store_true",
                        help="Chỉ chạy kiểm tra, không mở giao diện")
    args = parser.parse_args()

    tat_ca_dat = chay_kiem_tra()
    if args.chi_test:
        sys.exit(0 if tat_ca_dat else 1)

    if not tat_ca_dat:
        print("Có ca kiểm tra chưa đạt; vẫn mở giao diện để xem thử.")

    # App sẽ tự gọi nap_du_lieu_file(), nên KHÔNG nạp trước tại đây.
    # Import App ở đây để --chi-test không phụ thuộc Tkinter/GUI.
    from giao_dien.app import App

    dieu_phoi = MockDieuPhoi()
    phien = MockPhien(dieu_phoi)
    app = App(
        cast(GiaoThucDieuPhoi, dieu_phoi),
        cast(GiaoThucPhienLamViec, phien),
    )
    app.mainloop()


if __name__ == "__main__":
    main()

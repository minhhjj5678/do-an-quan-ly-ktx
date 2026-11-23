from giao_dien.app import App
from luu_tru.luu_tru_cau_hinh import LuuTruCauHinh
from luu_tru.luu_tru_dia_ly import LuuTruDiaLy
from luu_tru.luu_tru_hoa_don_thang import LuuTruHoaDonThang
from luu_tru.luu_tru_hop_dong import LuuTruHopDong
from luu_tru.luu_tru_phong import LuuTruPhong
from luu_tru.luu_tru_sinh_vien import LuuTruSinhVien
from luu_tru.luu_tru_tai_khoan import LuuTruTaiKhoan
from luu_tru.luu_tru_toa_nha import LuuTruToaNha
from luu_tru.luu_tru_vi_pham import LuuTruViPham
from nghiep_vu.dieu_phoi import DieuPhoiKTX
from nghiep_vu.phien_lam_viec import PhienLamViec
from thuc_the.dia_ly import Tinh
from thuc_the.ky_tuc_xa import Phong, SinhVien, ToaNha
from thuc_the.tai_chinh import HoaDonThang, HopDong
from thuc_the.tai_khoan import TaiKhoan
from thuc_the.vi_pham import ViPham

def main():
    dp = DieuPhoiKTX()
    phien = PhienLamViec(dp)
    app = App(dp, phien)
    app.mainloop()


if __name__ == '__main__':
    main()

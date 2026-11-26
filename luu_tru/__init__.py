# Phần C
# Gom các lớp lưu trữ để có thể import ngắn gọn: from luu_tru import LuuTruSinhVien
# (import đầy đủ như from luu_tru.luu_tru_sinh_vien import LuuTruSinhVien vẫn dùng được).
# Mỗi tên ở đây phải trỏ đúng tên FILE thật trong thư mục luu_tru/.
from .luu_tru_sinh_vien import LuuTruSinhVien
from .luu_tru_phong import LuuTruPhong
from .luu_tru_toa_nha import LuuTruToaNha
from .luu_tru_hop_dong import LuuTruHopDong
from .luu_tru_hoa_don_thang import LuuTruHoaDonThang
from .luu_tru_vi_pham import LuuTruViPham
from .luu_tru_tai_khoan import LuuTruTaiKhoan
from .luu_tru_dia_ly import LuuTruDiaLy
from .luu_tru_cau_hinh import LuuTruCauHinh
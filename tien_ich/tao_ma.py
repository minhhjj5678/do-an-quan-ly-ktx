# Phần C
# TODO: tạo bộ sinh mã riêng cho mỗi thực thể, nếu có danh sách hiện tại thì kiểm tra trùng lập trước khi tạo
# TODO: viết thêm các hàm sử dụng thư viện re kiểm tra mã hợp lệ bên file regex.py
# 
# Bộ sinh mã định danh tự động cho từng loại thực thể.
#
# Định dạng mã: <TIỀN TỐ> + <4 chữ số>, ví dụ: SV0001, P0012, HDT0100.
# Định dạng này được dùng chung với regex.py (các hàm la_ma_*), nên
# tiền tố và số chữ số được khai báo MỘT chỗ duy nhất ở đây để hai file không bao giờ lệch nhau.
import re
from collections.abc import Iterable
from typing import Final

# Số chữ số phần đuôi của mã (SV0001 -> 4 chữ số)
SO_CHU_SO: Final = 4

# Tiền tố của từng loại thực thể.
# Lưu ý: "HD" (hợp đồng) và "HDT" (hóa đơn tháng) bắt đầu giống nhau,
# nhưng không bị nhầm vì sau tiền tố bắt buộc phải là chữ số (HDT0001 không khớp "HD" + 4 chữ số).
TIEN_TO: Final = {
    "sinh_vien": "SV",
    "phong": "P",
    "toa_nha": "TN",
    "hoa_don_thang": "HDT",
    "dich_vu_them": "DV",
    "hop_dong": "HD",
    "vi_pham": "VP",
    "hoc_ky": "HK",
}


def _lay_ma(phan_tu: object) -> str | None:
    """Lấy mã dạng chuỗi từ một phần tử: có thể là chuỗi mã, hoặc đối tượng thực thể có thuộc tính .ma."""
    if isinstance(phan_tu, str):
        return phan_tu
    ma = getattr(phan_tu, "ma", None)
    return ma if isinstance(ma, str) else None


def _sinh_ma_tu_dong(tien_to: str, danh_sach_hien_tai: Iterable[object] | None = None) -> str:
    """
    Hàm dùng chung: tìm số thứ tự lớn nhất đang có rồi sinh mã kế tiếp.

    Tham số:
        - tien_to: tiền tố của loại thực thể, ví dụ "SV".
        - danh_sach_hien_tai: tập các thực thể (hoặc các mã dạng chuỗi) đang có.
          Nhận list, set, tuple hoặc dict đều được: kiểu Iterable là mọi thứ duyệt được bằng vòng for.
          Với dict (ví dụ kết quả lay_tat_ca: {mã: thực thể}) thì for lấy ra các KHÓA, mà khóa chính là mã.

    Trả về:
        - Mã mới, đảm bảo không trùng với bất kỳ mã nào trong danh sách.

    Vì luôn lấy "số lớn nhất + 1" nên mã không bao giờ trùng, kể cả khi có thực thể đã bị xóa
    (mã cũ không bị tái sử dụng).

    Ném ValueError nếu đã dùng hết số (vượt quá 9999).
    """
    # Mẫu khớp đúng một mã của loại này, ví dụ SV\d{4}; nhóm (...) để tách lấy phần số.
    # re.escape để tiền tố có ký tự đặc biệt cũng không làm hỏng regex.
    mau = re.compile(rf"{re.escape(tien_to)}(\d{{{SO_CHU_SO}}})")

    so_lon_nhat = 0
    for phan_tu in danh_sach_hien_tai or []:
        ma = _lay_ma(phan_tu)
        if ma is None:
            continue
        # fullmatch: toàn bộ chuỗi phải khớp, nên "HDT0005" không bị tính vào tiền tố "HD"
        ket_qua = mau.fullmatch(ma)
        if ket_qua:
            so_lon_nhat = max(so_lon_nhat, int(ket_qua.group(1)))

    so_moi = so_lon_nhat + 1
    if so_moi > 10 ** SO_CHU_SO - 1:
        raise ValueError(f"Đã hết mã khả dụng cho tiền tố {tien_to}")

    # :0{SO_CHU_SO}d -> đệm số 0 phía trước cho đủ 4 chữ số (1 -> 0001)
    return f"{tien_to}{so_moi:0{SO_CHU_SO}d}"


def ma_sinh_vien(danh_sach_hien_tai: Iterable[object] | None = None) -> str:
    return _sinh_ma_tu_dong(TIEN_TO["sinh_vien"], danh_sach_hien_tai)

def ma_phong(danh_sach_hien_tai: Iterable[object] | None = None) -> str:
    return _sinh_ma_tu_dong(TIEN_TO["phong"], danh_sach_hien_tai)

def ma_toa_nha(danh_sach_hien_tai: Iterable[object] | None = None) -> str:
    return _sinh_ma_tu_dong(TIEN_TO["toa_nha"], danh_sach_hien_tai)

def ma_hoa_don_thang(danh_sach_hien_tai: Iterable[object] | None = None) -> str:
    return _sinh_ma_tu_dong(TIEN_TO["hoa_don_thang"], danh_sach_hien_tai)

def ma_dich_vu_them(danh_sach_hien_tai: Iterable[object] | None = None) -> str:
    return _sinh_ma_tu_dong(TIEN_TO["dich_vu_them"], danh_sach_hien_tai)

def ma_hop_dong(danh_sach_hien_tai: Iterable[object] | None = None) -> str:
    return _sinh_ma_tu_dong(TIEN_TO["hop_dong"], danh_sach_hien_tai)

def ma_vi_pham(danh_sach_hien_tai: Iterable[object] | None = None) -> str:
    return _sinh_ma_tu_dong(TIEN_TO["vi_pham"], danh_sach_hien_tai)

def ma_hoc_ky(danh_sach_hien_tai: Iterable[object] | None = None) -> str:
    return _sinh_ma_tu_dong(TIEN_TO["hoc_ky"], danh_sach_hien_tai)
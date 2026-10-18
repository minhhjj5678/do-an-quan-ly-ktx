from tien_ich.regex import ktra_chuoi


def ktra_ma_tham_chieu_hop_le(ma: str, ten_truong: str):
    ktra_chuoi(ma, lambda x: x.isalnum(), f"{ten_truong} không được để trống và chỉ được chứa các ký tự chữ và số")
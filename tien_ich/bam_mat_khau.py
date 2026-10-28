# Phần C
# Băm mật khẩu: lưu xuống file chỉ là "mã băm", KHÔNG BAO GIỜ lưu mật khẩu người dùng nhập.
# Băm là phép biến đổi một chiều: từ mã băm không suy ngược ra được mật khẩu, nên lộ file dữ liệu
# cũng không lộ mật khẩu. Khi đăng nhập ta băm mật khẩu vừa nhập rồi so với mã băm đã lưu.
#
# Dùng PBKDF2-HMAC-SHA256 (có sẵn trong thư viện chuẩn hashlib, không cần cài thêm):
#   - "muối" (salt) ngẫu nhiên cho từng mật khẩu: hai người đặt cùng mật khẩu vẫn ra hai mã băm khác nhau
#   - lặp nhiều vòng để mỗi lần thử đoán mật khẩu đều tốn thời gian
# Chuỗi lưu có dạng:  pbkdf2_sha256$<số vòng>$<muối hex>$<mã băm hex>
# Số vòng được ghi kèm trong chuỗi nên sau này tăng số vòng mà mã băm cũ vẫn kiểm tra được.
import hashlib
import hmac
import secrets
from typing import Final

THUAT_TOAN: Final = "pbkdf2_sha256"
SO_VONG_MAC_DINH: Final = 200_000
_SO_VONG_TOI_DA: Final = 5_000_000  # chặn số vòng bất thường trong file hỏng (tránh treo máy khi tính)


def bam_mat_khau(mat_khau: str, so_vong: int = SO_VONG_MAC_DINH) -> str:
    """Băm một mật khẩu, trả về chuỗi gồm thuật toán, số vòng, muối và mã băm để lưu xuống file."""
    muoi = secrets.token_bytes(16)  # secrets dùng nguồn ngẫu nhiên an toàn (random thường thì không)
    ma_bam = hashlib.pbkdf2_hmac("sha256", mat_khau.encode("utf-8"), muoi, so_vong)
    return f"{THUAT_TOAN}${so_vong}${muoi.hex()}${ma_bam.hex()}"


def kiem_tra_mat_khau(mat_khau: str, ma_bam_da_luu: str) -> bool:
    """
    True nếu mật khẩu nhập vào khớp với chuỗi băm đã lưu.
    Chuỗi băm sai định dạng thì trả về False (không ném lỗi).
    """
    try:
        thuat_toan, so_vong_chuoi, muoi_hex, ma_bam_hex = ma_bam_da_luu.split("$")
        so_vong = int(so_vong_chuoi)
        if thuat_toan != THUAT_TOAN or not 1 <= so_vong <= _SO_VONG_TOI_DA:
            return False
        ma_bam_moi = hashlib.pbkdf2_hmac("sha256", mat_khau.encode("utf-8"), bytes.fromhex(muoi_hex), so_vong)
        # compare_digest so sánh trong thời gian không phụ thuộc vị trí byte khác nhau,
        # tránh bị dò mã băm qua chênh lệch thời gian của phép so sánh thường (==)
        return hmac.compare_digest(ma_bam_moi, bytes.fromhex(ma_bam_hex))
    except (ValueError, AttributeError):  # split sai số phần, hex sai, hoặc không phải chuỗi
        return False
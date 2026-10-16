# Phần C
# Làm 2 việc
# 1. Xác định đường dẫn hiện tại của các file json để app hoạt động trong môi trường mã nguồn lẫn môi trường đóng gói
# 2. Tạo thư mục ẩn .sao_luu để lưu trữ các file json phòng trường hợp dữ liệu bị hỏng ngoài ý muốn
import ctypes
import os
import sys

from tien_ich.cau_hinh_tinh import THU_MUC_DATA

# Tên thư mục sao lưu (dấu chấm ở đầu = ẩn trên Linux/macOS; trên Windows phải đặt thêm thuộc tính Hidden)
TEN_THU_MUC_SAO_LUU = ".sao_luu"


def _lay_thu_muc_goc() -> str:
    """
    Trả về thư mục gốc của ứng dụng, nơi chứa thư mục du_lieu.

    - Chạy từ mã nguồn: thư mục gốc dự án (cha của thư mục tien_ich chứa file này).
    - Đã đóng gói (PyInstaller...): thư mục chứa file .exe. KHÔNG dùng __file__ vì khi
      đóng gói kiểu một file, __file__ trỏ vào thư mục tạm bị xóa mỗi lần tắt app,
      dữ liệu sẽ mất theo.
    """
    # PyInstaller đặt sys.frozen = True khi chạy từ bản đóng gói
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


THU_MUC_GOC = _lay_thu_muc_goc()
THU_MUC_DU_LIEU = os.path.join(THU_MUC_GOC, THU_MUC_DATA)
THU_MUC_SAO_LUU = os.path.join(THU_MUC_DU_LIEU, TEN_THU_MUC_SAO_LUU)


def _an_thu_muc(duong_dan: str) -> None:
    """
    Đặt thuộc tính Hidden cho thư mục trên Windows (tên bắt đầu bằng dấu chấm không đủ để ẩn trên Windows).
    Trên hệ điều hành khác không làm gì. Lỗi (nếu có) bị bỏ qua vì ẩn thư mục chỉ là để gọn mắt, không quan trọng.
    """
    if os.name != "nt":
        return
    try:
        FILE_ATTRIBUTE_HIDDEN = 0x02
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        thuoc_tinh = kernel32.GetFileAttributesW(duong_dan)
        if thuoc_tinh == -1:  # -1 = INVALID_FILE_ATTRIBUTES (không đọc được)
            return
        # Dùng | để giữ lại các thuộc tính cũ (ví dụ thuộc tính "là thư mục")
        kernel32.SetFileAttributesW(duong_dan, thuoc_tinh | FILE_ATTRIBUTE_HIDDEN)
    except (OSError, AttributeError):
        pass


def dam_bao_thu_muc() -> None:
    """Tạo thư mục dữ liệu và thư mục ẩn .sao_luu nếu chưa có. Gọi nhiều lần không sao (idempotent)."""
    os.makedirs(THU_MUC_DU_LIEU, exist_ok=True)
    # Chỉ ẩn khi thư mục sao lưu vừa được tạo mới, tránh gọi hệ thống lặp lại mỗi lần lấy đường dẫn
    sao_luu_moi_tao = not os.path.isdir(THU_MUC_SAO_LUU)
    os.makedirs(THU_MUC_SAO_LUU, exist_ok=True)
    if sao_luu_moi_tao:
        _an_thu_muc(THU_MUC_SAO_LUU)


def _kiem_tra_ten_file(ten_file: str) -> None:
    """Chỉ chấp nhận tên file trơn (vd "sinh_vien.json"), chặn các tên như "../x.json" chui ra ngoài thư mục dữ liệu."""
    if not ten_file or os.path.basename(ten_file) != ten_file:
        raise ValueError(f"Tên file không hợp lệ: {ten_file!r}")


def lay_duong_dan_du_lieu(ten_file: str) -> str:
    """Đường dẫn đầy đủ của file dữ liệu chính, ví dụ du_lieu/sinh_vien.json."""
    _kiem_tra_ten_file(ten_file)
    dam_bao_thu_muc()
    return os.path.join(THU_MUC_DU_LIEU, ten_file)


def lay_duong_dan_sao_luu(ten_file: str) -> str:
    """Đường dẫn đầy đủ của file sao lưu tương ứng, ví dụ du_lieu/.sao_luu/sinh_vien.json."""
    _kiem_tra_ten_file(ten_file)
    dam_bao_thu_muc()
    return os.path.join(THU_MUC_SAO_LUU, ten_file)


def lay_duong_dan_dau_thoi_gian(ten_file: str) -> str:
    """
    Đường dẫn file nhỏ lưu "dấu thời gian" của file dữ liệu, ví dụ du_lieu/.sao_luu/sinh_vien.json.thoi_gian.
    Dùng để phát hiện file dữ liệu bị sửa ngoài ứng dụng (xem LuuTruJson.co_bi_chinh_sua).
    """
    _kiem_tra_ten_file(ten_file)
    dam_bao_thu_muc()
    return os.path.join(THU_MUC_SAO_LUU, ten_file + ".thoi_gian")
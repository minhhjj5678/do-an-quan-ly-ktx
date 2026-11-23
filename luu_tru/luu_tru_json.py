# Phần C
# Các hàm dùng chung cho các lớp lưu trữ (không còn là lớp cha):
#   ghi nguyên tử, đọc JSON thô, ghi file chính + sao lưu + dấu thời gian, phát hiện file bị sửa ngoài app.
import json
import os
from typing import Any

from thuc_the.thuc_the_goc import ThucTheGoc, ThucTheLuuTruDuoc
from tien_ich.tap_tin import lay_duong_dan_dau_thoi_gian, lay_duong_dan_du_lieu, lay_duong_dan_sao_luu


def khoi_phuc_hoat_dong(thuc_the: ThucTheLuuTruDuoc, con_hoat_dong: bool) -> None:
    """Thực thể mới tạo luôn hoạt động; nếu file ghi đã lưu trữ thì gọi luu_tru() để đúng trạng thái."""
    if not con_hoat_dong:
        thuc_the.luu_tru()


def ghi_nguyen_tu(duong_dan: str, noi_dung: str) -> None:
    """Ghi ra file tạm rồi os.replace: file đích luôn là bản cũ hoặc bản mới hoàn chỉnh, không bao giờ ghi dở."""
    duong_dan_tam = duong_dan + ".tmp"
    with open(duong_dan_tam, "w", encoding="utf-8") as f:
        f.write(noi_dung)
        f.flush()
        os.fsync(f.fileno())
    os.replace(duong_dan_tam, duong_dan)


def co_bi_chinh_sua(ten_file: str) -> bool:
    """True nếu mtime của file chính khác mtime đã lưu lần ghi cuối (file bị sửa/xóa ngoài app)."""
    duong_dan_dau = lay_duong_dan_dau_thoi_gian(ten_file)
    if not os.path.exists(duong_dan_dau):
        return False  # app chưa từng ghi file này: không có cơ sở kết luận
    try:
        with open(duong_dan_dau, "r", encoding="utf-8") as f:
            da_luu = int(f.read().strip())
    except (OSError, ValueError):
        return True  # file dấu thời gian hỏng -> không còn tin cậy
    duong_dan_chinh = lay_duong_dan_du_lieu(ten_file)
    return not os.path.exists(duong_dan_chinh) or os.stat(duong_dan_chinh).st_mtime_ns != da_luu


def kiem_tra_truoc_khi_doc(ten_file: str, da_kiem_tra_khoi_dong: bool) -> None:
    """Dùng ở đầu doc(): FileNotFoundError nếu chưa có file; ValueError nếu bị sửa ngoài app (chỉ kiểm tra lần đầu)."""
    if not os.path.exists(lay_duong_dan_du_lieu(ten_file)):
        raise FileNotFoundError(f"Không tìm thấy file {ten_file}")
    if not da_kiem_tra_khoi_dong and co_bi_chinh_sua(ten_file):
        raise ValueError(f"File {ten_file} đã bị chỉnh sửa ngoài ứng dụng hoặc bị mất đồng bộ")


def doc_json(duong_dan: str) -> list[Any]:
    """Đọc file JSON thô thành list. FileNotFoundError nếu thiếu file, ValueError nếu hỏng/sai cấu trúc."""
    ten = os.path.basename(duong_dan)
    if not os.path.exists(duong_dan):
        raise FileNotFoundError(f"Không tìm thấy file {ten}")
    try:
        with open(duong_dan, "r", encoding="utf-8") as f:
            du_lieu = json.load(f)
    except (OSError, ValueError) as loi:
        raise ValueError(f"Không đọc được file {ten}: {loi}") from loi
    if not isinstance(du_lieu, list):
        raise ValueError(f"File {ten} sai cấu trúc: phải là một danh sách")
    return du_lieu


def kiem_tra_danh_sach_ghi(danh_sach: dict[str, Any], loai: type[ThucTheGoc]) -> None:
    """TypeError nếu không phải dict/sai loại phần tử; ValueError nếu khóa không khớp mã."""
    if not isinstance(danh_sach, dict):
        raise TypeError("danh_sach phải là dict {mã: thực thể}")
    for ma, thuc_the in danh_sach.items():
        if not isinstance(thuc_the, loai):
            raise TypeError(f"Chỉ ghi được {loai.__name__}, nhận {type(thuc_the).__name__}")
        if ma != thuc_the.ma:
            raise ValueError(f"Khóa {ma!r} không khớp với mã thực thể {thuc_the.ma!r}")


def ghi_json(ten_file: str, danh_sach_dict: list[dict[str, Any]]) -> None:
    """Ghi file chính + file sao lưu + dấu thời gian."""
    noi_dung = json.dumps(danh_sach_dict, ensure_ascii=False, indent=2)
    ghi_nguyen_tu(lay_duong_dan_du_lieu(ten_file), noi_dung)
    ghi_nguyen_tu(lay_duong_dan_sao_luu(ten_file), noi_dung)
    dau = os.stat(lay_duong_dan_du_lieu(ten_file)).st_mtime_ns
    ghi_nguyen_tu(lay_duong_dan_dau_thoi_gian(ten_file), str(dau))
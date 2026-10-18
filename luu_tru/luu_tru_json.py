# Phần C
# Lớp cơ sở dùng chung cho các lớp lưu trữ. Lớp này lo TOÀN BỘ phần việc nặng:
#   - đọc/ghi file JSON an toàn (ghi nguyên tử, không để file nửa chừng)
#   - sao lưu sau mỗi lần ghi, tự rơi về bản sao lưu khi file chính hỏng
#   - phát hiện file bị sửa ngoài ứng dụng bằng dấu thời gian
# Mỗi lớp lưu trữ cụ thể (LuuTruSinhVien, LuuTruPhong...) chỉ cần khai báo:
#   - TEN_FILE: tên file dữ liệu
#   - LOAI: loại thực thể phụ trách
#   - _sang_dict / _tu_dict: đổi thực thể <-> dict để lưu JSON
# Việc đổi qua lại nằm ở tầng lưu trữ nên KHÔNG phải sửa gì trong package thuc_the/ (thuộc phần B).
import json
import os
from abc import abstractmethod
from typing import Any

from giao_thuc.luu_tru import GiaoThucLuuTru, T
from thuc_the.thuc_the_goc import ThucTheGoc, ThucTheLuuTruDuoc
from tien_ich.tap_tin import (
    lay_duong_dan_dau_thoi_gian,
    lay_duong_dan_du_lieu,
    lay_duong_dan_sao_luu,
)


def khoi_phuc_hoat_dong(thuc_the: ThucTheLuuTruDuoc, con_hoat_dong: bool) -> None:
    """Thực thể mới tạo luôn đang hoạt động; nếu trong file ghi đã lưu trữ thì gọi luu_tru() để đưa về đúng trạng thái."""
    if not con_hoat_dong:
        thuc_the.luu_tru()


def ghi_nguyen_tu(duong_dan: str, noi_dung: str) -> None:
    """
    Ghi file theo kiểu "ghi ra file tạm rồi đổi tên".
    Nếu app/máy sập giữa chừng thì file cũ vẫn còn nguyên, không bao giờ có file ghi dở.
    os.replace là thao tác nguyên tử: file đích hoặc là bản cũ, hoặc là bản mới hoàn chỉnh.
    """
    duong_dan_tam = duong_dan + ".tmp"
    with open(duong_dan_tam, "w", encoding="utf-8") as f:
        f.write(noi_dung)
        f.flush()
        os.fsync(f.fileno())  # ép hệ điều hành ghi xuống đĩa thật
    os.replace(duong_dan_tam, duong_dan)


class LuuTruJson(GiaoThucLuuTru[T]):
    # Các lớp con BẮT BUỘC khai báo hai thuộc tính này
    TEN_FILE: str
    LOAI: type[ThucTheGoc]

    def __init__(self) -> None:
        # Kiểm tra "file có bị sửa ngoài app không" chỉ làm MỘT lần ở lần doc() đầu tiên (lúc app khởi động),
        # không theo dõi liên tục trong lúc app chạy. Cờ này nhớ là đã kiểm tra chưa.
        self._da_kiem_tra_khoi_dong = False

    # ---- Hai hàm chuyển đổi: lớp con tự cài ----
    @abstractmethod
    def _sang_dict(self, thuc_the: T) -> dict[str, Any]:
        """Đổi một thực thể thành dict chỉ chứa kiểu JSON hiểu được (str, số, bool, None, list, dict)."""
        raise NotImplementedError

    @abstractmethod
    def _tu_dict(self, du_lieu: dict[str, Any]) -> T:
        """Dựng lại một thực thể từ dict đọc trong file. Thiếu khóa/sai kiểu thì để lỗi KeyError/TypeError nổi lên,
        lớp cha sẽ gói lại thành ValueError."""
        raise NotImplementedError

    # ---- Đường dẫn ----
    @property
    def _duong_dan_chinh(self) -> str:
        return lay_duong_dan_du_lieu(self.TEN_FILE)

    @property
    def _duong_dan_sao_luu(self) -> str:
        return lay_duong_dan_sao_luu(self.TEN_FILE)

    @property
    def _duong_dan_dau_thoi_gian(self) -> str:
        return lay_duong_dan_dau_thoi_gian(self.TEN_FILE)

    @property
    def loai_thuc_the(self) -> type[T]:
        return self.LOAI  # type: ignore[return-value]

    # ---- Đọc ----
    def _doc_file(self, duong_dan: str) -> dict[str, T]:
        """
        Đọc một file JSON và dựng lại dict {mã: thực thể}.
        - File không tồn tại: trả về dict rỗng.
        - File hỏng (không đọc được, sai cấu trúc, thiếu trường, trùng mã): ném ValueError.
        """
        if not os.path.exists(duong_dan):
            return {}

        try:
            with open(duong_dan, "r", encoding="utf-8") as f:
                du_lieu = json.load(f)
        except (OSError, ValueError) as loi:  # JSONDecodeError và UnicodeDecodeError đều là con của ValueError
            raise ValueError(f"Không đọc được file {os.path.basename(duong_dan)}: {loi}") from loi

        if not isinstance(du_lieu, list):
            raise ValueError(f"File {os.path.basename(duong_dan)} sai cấu trúc: phải là một danh sách")

        ket_qua: dict[str, T] = {}
        for vi_tri, muc in enumerate(du_lieu):
            try:
                thuc_the = self._tu_dict(muc)
            except (KeyError, TypeError, AttributeError, ValueError) as loi:
                raise ValueError(f"File {os.path.basename(duong_dan)} hỏng ở mục thứ {vi_tri}: {loi!r}") from loi
            if thuc_the.ma in ket_qua:
                raise ValueError(f"File {os.path.basename(duong_dan)} có mã trùng lặp: {thuc_the.ma}")
            ket_qua[thuc_the.ma] = thuc_the
        return ket_qua

    def doc(self) -> dict[str, T]:
        """
        Đọc dữ liệu, trả về dict với khóa là mã thực thể.

        Thứ tự ưu tiên:
          1. File chính, nếu đọc được và (ở lần đọc đầu tiên) không bị sửa ngoài ứng dụng.
          2. File sao lưu, nếu file chính không tồn tại / hỏng / bị sửa ngoài ứng dụng.
             Dùng được bản sao lưu thì ghi ngược lại để khôi phục file chính.
          3. Dict rỗng, nếu không còn nguồn cục bộ nào dùng được.
        """
        lan_dau = not self._da_kiem_tra_khoi_dong
        self._da_kiem_tra_khoi_dong = True
        chinh, sao_luu = self._duong_dan_chinh, self._duong_dan_sao_luu

        du_lieu_chinh: dict[str, T] | None = None
        if os.path.exists(chinh):
            try:
                du_lieu_chinh = self._doc_file(chinh)
            except ValueError:
                du_lieu_chinh = None  # file hỏng, thử bản sao lưu bên dưới
        # Kiểm tra sửa ngoài app chỉ ở lần đọc đầu; co_bi_chinh_sua() cũng trả True khi file chính bị xóa
        bi_chinh_sua = lan_dau and self.co_bi_chinh_sua()
        if du_lieu_chinh is not None and not bi_chinh_sua:
            return du_lieu_chinh

        du_lieu_sao_luu: dict[str, T] | None = None
        if os.path.exists(sao_luu):
            try:
                du_lieu_sao_luu = self._doc_file(sao_luu)
            except ValueError:
                du_lieu_sao_luu = None  # sao lưu cũng hỏng
        if du_lieu_sao_luu is not None:
            try:
                self.ghi(du_lieu_sao_luu)  # khôi phục file chính (và dấu thời gian) từ bản sao lưu
            except OSError:
                pass  # không ghi được (ví dụ ổ đĩa chỉ đọc) thì vẫn dùng dữ liệu đã đọc
            return du_lieu_sao_luu

        # Không có sao lưu dùng được: file chính chỉ bị đánh dấu "sửa ngoài app" nhưng vẫn đọc được thì giữ dữ liệu đó
        return du_lieu_chinh if du_lieu_chinh is not None else {}

    # ---- Ghi ----
    def ghi(self, danh_sach: dict[str, T]) -> None:
        """
        Ghi toàn bộ dict {mã: thực thể} xuống file chính + file sao lưu + file dấu thời gian.
        Luôn ghi đè lên nội dung cũ.
        Ném TypeError nếu không phải dict hoặc có phần tử sai loại, ValueError nếu khóa không khớp mã thực thể.
        """
        if not isinstance(danh_sach, dict):
            raise TypeError("danh_sach phải là dict {mã: thực thể}")
        for ma, thuc_the in danh_sach.items():
            if not isinstance(thuc_the, self.LOAI):
                raise TypeError(f"{type(self).__name__} chỉ ghi được {self.LOAI.__name__}, nhận {type(thuc_the).__name__}")
            if ma != thuc_the.ma:
                raise ValueError(f"Khóa {ma!r} không khớp với mã thực thể {thuc_the.ma!r}")

        # Đổi sang dict TRƯỚC khi đụng vào file: nếu lỗi ở bước này thì file cũ không bị ảnh hưởng
        # ensure_ascii=False giữ nguyên tiếng Việt, indent=2 để dễ đọc khi mở file
        noi_dung = json.dumps([self._sang_dict(tt) for tt in danh_sach.values()], ensure_ascii=False, indent=2)

        ghi_nguyen_tu(self._duong_dan_chinh, noi_dung)
        ghi_nguyen_tu(self._duong_dan_sao_luu, noi_dung)
        # Lưu dấu thời gian sửa đổi của file chính NGAY SAU khi ghi (đọc từ chính file vừa ghi để so sánh sau này)
        dau_thoi_gian = os.stat(self._duong_dan_chinh).st_mtime_ns
        ghi_nguyen_tu(self._duong_dan_dau_thoi_gian, str(dau_thoi_gian))

        # Vừa ghi xong nghĩa là app đã nắm dữ liệu mới nhất, không cần kiểm tra khởi động nữa
        self._da_kiem_tra_khoi_dong = True

    # ---- Phát hiện sửa ngoài app ----
    def co_bi_chinh_sua(self) -> bool:
        """
        True nếu file chính có dấu hiệu bị sửa/xóa ngoài ứng dụng.

        Cách làm: sau mỗi lần ghi(), ta lưu thời điểm sửa đổi (mtime) của file chính vào file riêng
        trong .sao_luu. Hàm này so mtime hiện tại với giá trị đã lưu: khác nhau nghĩa là có ai đó
        đã mở file bằng chương trình khác và lưu lại.
        """
        duong_dan_dau = self._duong_dan_dau_thoi_gian
        if not os.path.exists(duong_dan_dau):
            # Chưa có dấu thời gian (app chưa từng ghi file này): không có cơ sở để kết luận là bị sửa
            return False
        try:
            with open(duong_dan_dau, "r", encoding="utf-8") as f:
                da_luu = int(f.read().strip())
        except (OSError, ValueError):
            return True  # file dấu thời gian hỏng -> không còn tin cậy được, coi như có vấn đề
        if not os.path.exists(self._duong_dan_chinh):
            return True  # từng ghi mà file chính biến mất -> bị xóa ngoài app
        return os.stat(self._duong_dan_chinh).st_mtime_ns != da_luu
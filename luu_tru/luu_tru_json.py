# Phần C
# Lớp cơ sở dùng chung cho 8 lớp lưu trữ. Lớp này lo TOÀN BỘ phần việc nặng:
#   - đọc/ghi file JSON an toàn (ghi nguyên tử, không để file nửa chừng)
#   - sao lưu sau mỗi lần ghi
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


def khoi_phuc_trang_thai(thuc_the: object, lop_khai_bao: type, gia_tri: object) -> None:
    """
    Gán lại thuộc tính trạng thái (trang_thai) của hợp đồng / hóa đơn / vi phạm khi đọc từ file.

    Vì sao cần: các class này khởi tạo trạng thái mặc định là "chưa thanh toán/chưa xử lý" và
    KHÔNG có setter, trong khi file có thể ghi trạng thái "đã thanh toán". Do không được sửa
    package thuc_the/, ta gán thẳng vào thuộc tính private.

    Python đổi tên thuộc tính private "__trang_thai" khai báo trong class X thành "_X__trang_thai"
    (name mangling), nên phải truyền đúng class đã KHAI BÁO thuộc tính (ví dụ ViPham chứ không phải ViPhamNoiQuy).
    Mọi chỗ gán kiểu này gom về đúng một hàm này để sau này dễ sửa nếu phần B đổi cách lưu trạng thái.
    """
    ten_thuoc_tinh = f"_{lop_khai_bao.__name__}__trang_thai"
    if not hasattr(thuc_the, ten_thuoc_tinh):
        # Phần B đã đổi tên thuộc tính -> báo lỗi rõ ràng thay vì âm thầm đọc sai dữ liệu
        raise ValueError(f"{lop_khai_bao.__name__} không còn thuộc tính {ten_thuoc_tinh}, cần cập nhật khoi_phuc_trang_thai")
    setattr(thuc_the, ten_thuoc_tinh, gia_tri)


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
    def _doc_file(self, duong_dan: str) -> list[T]:
        """
        Đọc một file JSON và dựng lại danh sách thực thể.
        - File không tồn tại: trả về danh sách rỗng.
        - File hỏng (không đọc được, sai cấu trúc, thiếu trường, trùng mã): ném ValueError.
        """
        if not os.path.exists(duong_dan):
            return []

        try:
            with open(duong_dan, "r", encoding="utf-8") as f:
                du_lieu = json.load(f)
        except (OSError, ValueError) as loi:  # JSONDecodeError và UnicodeDecodeError đều là con của ValueError
            raise ValueError(f"Không đọc được file {os.path.basename(duong_dan)}: {loi}") from loi

        if not isinstance(du_lieu, list):
            raise ValueError(f"File {os.path.basename(duong_dan)} sai cấu trúc: phải là một danh sách")

        ket_qua: list[T] = []
        ma_da_thay: set[str] = set()
        for vi_tri, muc in enumerate(du_lieu):
            try:
                thuc_the = self._tu_dict(muc)
            except (KeyError, TypeError, AttributeError, ValueError) as loi:
                raise ValueError(f"File {os.path.basename(duong_dan)} hỏng ở mục thứ {vi_tri}: {loi!r}") from loi
            if thuc_the.ma in ma_da_thay:
                raise ValueError(f"File {os.path.basename(duong_dan)} có mã trùng lặp: {thuc_the.ma}")
            ma_da_thay.add(thuc_the.ma)
            ket_qua.append(thuc_the)
        return ket_qua

    def doc(self) -> list[T]:
        """
        Đọc dữ liệu từ file chính.
        Ném ValueError nếu file hỏng, hoặc (ở lần đọc đầu tiên) nếu file bị sửa ngoài ứng dụng.
        Khi gặp ValueError, tầng trên nên gọi doc_sao_luu() rồi ghi() lại để khôi phục.
        """
        if not self._da_kiem_tra_khoi_dong:
            if self.co_bi_chinh_sua():
                raise ValueError(f"File {self.TEN_FILE} đã bị chỉnh sửa ngoài ứng dụng hoặc bị mất đồng bộ")
            # Chỉ đánh dấu "đã kiểm tra" khi file hợp lệ; nếu chưa khôi phục thì lần doc() sau vẫn báo lỗi tiếp
            self._da_kiem_tra_khoi_dong = True
        return self._doc_file(self._duong_dan_chinh)

    def doc_sao_luu(self) -> list[T]:
        """Đọc từ file sao lưu (trong thư mục .sao_luu). Chỉ dùng khi file chính hỏng."""
        return self._doc_file(self._duong_dan_sao_luu)

    # ---- Ghi ----
    # Dùng lại hàm ghi_nguyen_tu ở đầu file (xem giải thích ở đó)
    _ghi_nguyen_tu = staticmethod(ghi_nguyen_tu)

    def ghi(self, danh_sach: list[T], ghi_de: bool = True) -> None:
        """
        Ghi danh sách thực thể xuống file chính + file sao lưu + file dấu thời gian.

        - ghi_de=True: thay toàn bộ nội dung file bằng danh_sach.
        - ghi_de=False: giữ dữ liệu cũ và ghi thêm danh_sach vào cuối.
        Ném TypeError nếu có phần tử sai loại, ValueError nếu trùng mã (hoặc file cũ hỏng khi ghi thêm).
        """
        moi = list(danh_sach)  # danh_sach có thể là generator/set -> chuyển thành list để duyệt nhiều lần
        for thuc_the in moi:
            if not isinstance(thuc_the, self.LOAI):
                raise TypeError(f"{type(self).__name__} chỉ ghi được {self.LOAI.__name__}, nhận {type(thuc_the).__name__}")

        # Ghi thêm: đọc dữ liệu cũ (đã kiểm tra hợp lệ) rồi nối vào; ghi đè: chỉ dùng dữ liệu mới
        tong = moi if ghi_de else self._doc_file(self._duong_dan_chinh) + moi

        ma_da_thay: set[str] = set()
        for thuc_the in tong:
            if thuc_the.ma in ma_da_thay:
                raise ValueError(f"Mã bị trùng khi ghi {self.TEN_FILE}: {thuc_the.ma}")
            ma_da_thay.add(thuc_the.ma)

        # Đổi sang dict TRƯỚC khi đụng vào file: nếu lỗi ở bước này thì file cũ không bị ảnh hưởng
        # ensure_ascii=False giữ nguyên tiếng Việt, indent=2 để dễ đọc khi mở file
        noi_dung = json.dumps([self._sang_dict(tt) for tt in tong], ensure_ascii=False, indent=2)

        self._ghi_nguyen_tu(self._duong_dan_chinh, noi_dung)
        self._ghi_nguyen_tu(self._duong_dan_sao_luu, noi_dung)
        # Lưu dấu thời gian sửa đổi của file chính NGAY SAU khi ghi (đọc từ chính file vừa ghi để so sánh sau này)
        dau_thoi_gian = os.stat(self._duong_dan_chinh).st_mtime_ns
        self._ghi_nguyen_tu(self._duong_dan_dau_thoi_gian, str(dau_thoi_gian))

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
            return True  # từng ghi nhưng file chính biến mất -> bị xóa ngoài app
        return os.stat(self._duong_dan_chinh).st_mtime_ns != da_luu
# Phần C
# Lưu cấu hình động (CauHinhDong) xuống một file JSON riêng, tách biệt với dữ liệu nghiệp vụ.
# Tên hàm trùng với doc_cau_hinh / cap_nhat_cau_hinh của GiaoThucDieuPhoi để tầng nghiệp vụ chỉ cần gọi thẳng xuống.
#
# CauHinhDong không phải thực thể (không có mã) nên KHÔNG kế thừa GiaoThucLuuTru, chỉ dùng chung
# cách ghi an toàn (ghi file tạm rồi đổi tên) và thư mục sao lưu.
import json
import os
from dataclasses import fields, replace
from typing import Any
from typing import get_type_hints

from luu_tru.luu_tru_json import ghi_nguyen_tu
from tien_ich.cau_hinh_dong import CauHinhDong
from tien_ich.cau_hinh_tinh import FILE_CAU_HINH, CauHinhChuDe
from tien_ich.regex import ktra_so, la_so_duong
from tien_ich.tap_tin import lay_duong_dan_du_lieu, lay_duong_dan_sao_luu


class LuuTruCauHinh:
    TEN_FILE = FILE_CAU_HINH

    # ---- Chuyển đổi CauHinhDong <-> dict ----
    @staticmethod
    def _sang_dict(cau_hinh: CauHinhDong) -> dict[str, Any]:
        """Duyệt mọi trường của dataclass nên khi phần B thêm trường mới, ở đây không phải sửa gì."""
        ket_qua: dict[str, Any] = {}
        for truong in fields(cau_hinh):
            gia_tri = getattr(cau_hinh, truong.name)
            # Enum (chủ đề giao diện) lưu bằng TÊN, ví dụ "DARK"
            ket_qua[truong.name] = gia_tri.name if isinstance(gia_tri, CauHinhChuDe) else gia_tri
        return ket_qua

    @staticmethod
    def _tu_dict(du_lieu: Any) -> CauHinhDong:
        """
        Dựng lại CauHinhDong từ dict. Trường nào thiếu trong file thì lấy giá trị mặc định
        (nên file cũ vẫn đọc được khi có thêm trường mới); khóa lạ bị bỏ qua.
        Ném ValueError nếu giá trị sai kiểu.
        """
        if not isinstance(du_lieu, dict):
            raise ValueError("File cấu hình sai cấu trúc: phải là một đối tượng JSON")
        kieu_thuc = get_type_hints(CauHinhDong)
        gia_tri_moi: dict[str, Any] = {}
        for truong in fields(CauHinhDong):
            if truong.name not in du_lieu:
                continue
            tho = du_lieu[truong.name]
            if truong.type is CauHinhChuDe:
                if tho not in CauHinhChuDe.__members__:
                    raise ValueError(f"Chủ đề không hợp lệ: {tho!r}")
                gia_tri_moi[truong.name] = CauHinhChuDe[tho]
            else:
                # bool là con của int trong Python nên phải loại ra riêng
                if isinstance(tho, bool) or not isinstance(tho, (int, float)):
                    raise ValueError(f"Giá trị {truong.name} phải là số, nhận {tho!r}")
                kieu = kieu_thuc.get(truong.name, truong.type)
                if not isinstance(kieu, type):
                    raise ValueError(f"Không xác định được kiểu số cho {truong.name}")
                gia_tri_moi[truong.name] = kieu(tho)  # ép về int hoặc float đúng như khai báo
        return replace(CauHinhDong(), **gia_tri_moi)  # bắt đầu từ mặc định, đè các trường có trong file

    @staticmethod
    def _kiem_tra(cau_hinh: CauHinhDong) -> None:
        """Từ chối cấu hình vô lý (giá âm, sức chứa 0...) trước khi ghi xuống file."""
        ktra_so(cau_hinh.DON_GIA_DIEN, lambda x: x >= 0, "Đơn giá điện không được âm")
        ktra_so(cau_hinh.DON_GIA_NUOC, lambda x: x >= 0, "Đơn giá nước không được âm")
        ktra_so(cau_hinh.SUC_CHUA_PHONG_MAC_DINH, la_so_duong, "Sức chứa phòng mặc định phải lớn hơn 0")
        ktra_so(cau_hinh.SO_TIEN_NO_TOI_DA_CHO_PHEP, lambda x: x >= 0, "Hạn mức nợ không được âm")
        ktra_so(cau_hinh.THOI_HAN_DONG_TIEN_DIEN, la_so_duong, "Thời hạn đóng tiền điện phải lớn hơn 0")
        ktra_so(cau_hinh.TIEN_PHAT_QUA_HAN_NGAY, lambda x: x >= 0, "Tiền phạt quá hạn không được âm")

    @staticmethod
    def _doc_file(duong_dan: str) -> CauHinhDong:
        with open(duong_dan, "r", encoding="utf-8") as f:
            return LuuTruCauHinh._tu_dict(json.load(f))

    # ---- Hai hàm công khai ----
    def doc_cau_hinh(self) -> CauHinhDong:
        """
        Trả về cấu hình hiện tại.
        Thử lần lượt: file chính -> file sao lưu -> cấu hình mặc định (khi chưa có file hoặc cả hai đều hỏng).
        Cấu hình không quan trọng bằng dữ liệu nghiệp vụ nên không ném lỗi, tránh app không mở được vì một file cài đặt hỏng.
        """
        for duong_dan in (lay_duong_dan_du_lieu(self.TEN_FILE), lay_duong_dan_sao_luu(self.TEN_FILE)):
            if not os.path.exists(duong_dan):
                continue
            try:
                return self._doc_file(duong_dan)
            except (OSError, ValueError):  # JSON hỏng, sai kiểu, không đọc được -> thử nguồn tiếp theo
                continue
        return CauHinhDong()

    def cap_nhat_cau_hinh(self, cau_hinh: CauHinhDong) -> None:
        """Thay cấu hình hiện tại bằng cấu hình mới, ghi vào file chính và file sao lưu. Ném ValueError nếu giá trị không hợp lệ."""
        if not isinstance(cau_hinh, CauHinhDong):
            raise TypeError("cau_hinh phải là CauHinhDong")
        self._kiem_tra(cau_hinh)
        noi_dung = json.dumps(self._sang_dict(cau_hinh), ensure_ascii=False, indent=2)
        ghi_nguyen_tu(lay_duong_dan_du_lieu(self.TEN_FILE), noi_dung)
        ghi_nguyen_tu(lay_duong_dan_sao_luu(self.TEN_FILE), noi_dung)
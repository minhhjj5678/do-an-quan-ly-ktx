# Phần C
# Lưu trữ ToaNha xuống file JSON (cau_hinh_tinh.FILE_TOA_NHA).
#
# ToaNha chỉ cho thêm phòng qua them_phong(phong), và hàm này nhận ĐỐI TƯỢNG Phong chứ không nhận mã.
# Vì vậy khi đọc file, lớp này cần tra các phòng thật từ lớp lưu trữ phòng. Truyền lớp lưu trữ phòng vào hàm
# khởi tạo (nên dùng chung đúng một đối tượng LuuTruPhong với phần còn lại của ứng dụng); không truyền thì tự tạo.
from typing import Any

from giao_thuc.luu_tru import GiaoThucLuuTru
from luu_tru.luu_tru_json import LuuTruJson, khoi_phuc_hoat_dong
from luu_tru.luu_tru_phong import LuuTruPhong
from thuc_the.ky_tuc_xa import Phong, ToaNha
from tien_ich.cau_hinh_tinh import FILE_TOA_NHA


class LuuTruToaNha(LuuTruJson[ToaNha]):
    TEN_FILE = FILE_TOA_NHA
    LOAI = ToaNha

    def __init__(self, luu_tru_phong: GiaoThucLuuTru[Phong] | None = None) -> None:
        super().__init__()
        self._luu_tru_phong = luu_tru_phong if luu_tru_phong is not None else LuuTruPhong()
        self._cac_phong: dict[str, Phong] = {}  # nạp lại mỗi lần đọc file, xem _doc_file

    def _doc_file(self, duong_dan: str) -> dict[str, ToaNha]:
        # Nạp các phòng một lần trước khi dựng từng tòa nhà, để _tu_dict tra được phòng theo mã
        self._cac_phong = self._luu_tru_phong.doc()
        return super()._doc_file(duong_dan)

    def _sang_dict(self, tn: ToaNha) -> dict[str, Any]:
        return {
            "ma": tn.ma,
            "ten": tn.ten,
            "so_tang": tn.so_tang,
            "danh_sach_phong": sorted(tn.danh_sach_phong),  # mã các phòng, thứ tự cố định cho file ổn định
            "con_hoat_dong": tn.con_hoat_dong,
        }

    def _tu_dict(self, d: dict[str, Any]) -> ToaNha:
        tn = ToaNha(d["ma"], d["ten"], d["so_tang"])
        for ma_phong in d["danh_sach_phong"]:
            phong = self._cac_phong.get(ma_phong)
            if phong is None:
                # Tòa nhà ghi phòng mà file phòng không có -> hai file lệch nhau, coi như file hỏng
                raise ValueError(f"Phòng {ma_phong} của tòa {d['ma']} không có trong dữ liệu phòng")
            tn.them_phong(phong)
        khoi_phuc_hoat_dong(tn, d["con_hoat_dong"])
        return tn
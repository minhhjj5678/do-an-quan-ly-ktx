# Phần C
# Sinh dữ liệu mẫu ngẫu nhiên cho toàn bộ 8 loại thực thể (SinhVien, Phong, ToaNha, HopDong,
# HoaDonThang, DichVuThem, ViPham, TaiKhoan) để kiểm thử sau khi ráp ba tầng.
#
# Điểm quan trọng nhất là dữ liệu phải ĐÚNG RÀNG BUỘC CHÉO, ví dụ:
#   - sinh viên có phòng_hiện_tại = P0005 thì phòng P0005 phải tồn tại VÀ có mã sinh viên đó trong danh sách
#   - số sinh viên trong phòng không vượt sức chứa
#   - hợp đồng "đã thanh toán" <=> sinh viên đang ở đúng phòng của hợp đồng đó
#   - thực thể đã lưu trữ (ngừng hoạt động) không được còn hợp đồng đang hiệu lực
# Hàm kiem_tra_rang_buoc() ở cuối file kiểm tra lại toàn bộ các điều kiện này.
#
# Cách dùng:
#   - Trong code:   du_lieu = sinh_du_lieu(so_sinh_vien=80, seed=1);  ghi_du_lieu(du_lieu)
#   - Dòng lệnh:    py -m tien_ich.sinh_du_lieu --so-sinh-vien 80 --seed 1
# Tham số seed cố định thì lần nào chạy cũng ra đúng bộ dữ liệu đó (tiện tái hiện lỗi).
import argparse
import math
import os
import random
from dataclasses import dataclass
from datetime import date

from thuc_the.dia_ly import Tinh
from thuc_the.hoc_vu import HocKy
from thuc_the.ky_tuc_xa import Phong, SinhVien, ToaNha
from thuc_the.tai_chinh import DichVuCoSo, DichVuThem, HoaDonThang, HopDong, TienIchPhong, TrangThaiHoaDon, TrangThaiHopDong
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from thuc_the.vi_pham import ViPham, ViPhamNoiQuy, ViPhamTaiSan
from tien_ich import tao_ma
from tien_ich.bam_mat_khau import SO_VONG_MAC_DINH, bam_mat_khau
from tien_ich.cau_hinh_dong import CauHinhDong
from tien_ich.regex import (
    la_cccd, la_ma_dich_vu_them, la_ma_hoa_don_thang, la_ma_hop_dong, la_ma_phong,
    la_ma_sinh_vien, la_ma_toa_nha, la_ma_vi_pham, la_sdt,
)

# Tài khoản đăng nhập thử được tạo kèm dữ liệu
TEN_ADMIN_MAU = "admin"
MAT_KHAU_ADMIN_MAU = "admin123"
MAT_KHAU_SINH_VIEN_MAU = "123456"
SO_TAI_KHOAN_SINH_VIEN_MAU = 10

# ---- Kho dữ liệu thô để ghép ngẫu nhiên ----
_HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
_DEM_NAM = ["Văn", "Hữu", "Minh", "Quốc", "Đức", "Thành", "Gia", "Anh"]
_DEM_NU = ["Thị", "Ngọc", "Thu", "Khánh", "Phương", "Hồng", "Bảo", "Mai"]
_TEN_NAM = ["Bình", "Cường", "Dũng", "Đạt", "Hải", "Hiếu", "Hùng", "Khoa", "Khang", "Long", "Minh", "Nam", "Phát", "Quân", "Sơn", "Thắng", "Tuấn", "Việt", "Vinh"]
_TEN_NU = ["Chi", "Dung", "Giang", "Hà", "Hạnh", "Hoa", "Hương", "Lan", "Linh", "Ngân", "Nhi", "Phương", "Quỳnh", "Thảo", "Trang", "Uyên", "Vy"]
_DUONG = ["Lê Lợi", "Nguyễn Huệ", "Trần Hưng Đạo", "Hai Bà Trưng", "Lý Thường Kiệt", "Phan Chu Trinh", "Điện Biên Phủ", "Nguyễn Trãi"]
# Dùng khi chưa có dữ liệu địa lý thật (chưa tải từ API); chỉ là dữ liệu mẫu
_DIA_CHI_DU_PHONG = [
    ("Thành phố Hà Nội", "Phường Ba Đình"), ("Thành phố Hồ Chí Minh", "Phường Bến Nghé"),
    ("Thành phố Đà Nẵng", "Phường Hải Châu"), ("Tỉnh Đồng Nai", "Phường Biên Hòa"),
    ("Tỉnh Nghệ An", "Phường Vinh Phú"), ("Tỉnh Lâm Đồng", "Phường Xuân Hương"),
]
_DICH_VU_MAU = [("Giặt ủi", 50_000.0), ("Internet tốc độ cao", 60_000.0), ("Gửi xe máy", 100_000.0),
                ("Dọn vệ sinh phòng", 80_000.0), ("Nước uống đóng bình", 40_000.0)]
_TIEN_ICH_MAU = [("Điều hòa", 400_000.0), ("Bình nóng lạnh", 150_000.0), ("Tủ lạnh mini", 120_000.0), ("Quạt trần", 30_000.0)]
_NOI_QUY = [("Gây ồn sau 23 giờ", "Khiển trách"), ("Về muộn quá giờ quy định", "Nhắc nhở"),
            ("Nấu ăn trong phòng", "Cảnh cáo"), ("Mang người lạ vào phòng", "Cảnh cáo"),
            ("Không dọn vệ sinh phòng", "Nhắc nhở")]
_TAI_SAN = [("Làm vỡ kính cửa sổ", 250_000.0), ("Làm hỏng ổ khóa cửa", 150_000.0),
            ("Hư quạt trần do sử dụng sai", 400_000.0), ("Làm hỏng giường tầng", 800_000.0)]


@dataclass
class DuLieuMau:
    """Toàn bộ dữ liệu mẫu. hoc_ky chỉ để tham chiếu (học kỳ không được lưu xuống file riêng)."""
    hoc_ky: list[HocKy]
    dich_vu_them: list[DichVuThem]
    tien_ich_phong: list[TienIchPhong]
    toa_nha: list[ToaNha]
    phong: list[Phong]
    sinh_vien: list[SinhVien]
    hop_dong: list[HopDong]
    hoa_don_thang: list[HoaDonThang]
    vi_pham: list[ViPham]
    tai_khoan: list[TaiKhoan]

    def dich_vu_co_so(self) -> list[DichVuCoSo]:
        """Dịch vụ thêm và tiện ích phòng gộp chung (hai loại này lưu chung một file, chung kiểu mã)."""
        return [*self.dich_vu_them, *self.tien_ich_phong]


@dataclass
class _KeHoachPhong:
    """Bản nháp của một phòng trong lúc xếp chỗ. Phong thật chưa có hàm thêm sinh viên, nên xếp xong mới dựng Phong."""
    ma: str
    ten: str
    suc_chua: int
    gia: float  # giá cơ bản cho MỖI người mỗi tháng (Phong.gia_phong = gia * suc_chua)
    ma_toa_nha: str
    tang: int
    tien_ich: set[str]
    phi_tien_nghi: float  # tổng giá tiện ích của phòng chia đều cho sức chứa, tức phần mỗi người chịu
    hoat_dong: bool = True
    sinh_vien: list[str] | None = None

    def __post_init__(self) -> None:
        self.sinh_vien = []

    def con_cho(self) -> bool:
        return len(self.sinh_vien) < self.suc_chua  # type: ignore[arg-type]


# ---------------------------------------------------------------- học kỳ
def _sinh_hoc_ky(hom_nay: date) -> list[HocKy]:
    """
    Ba học kỳ gần nhất (đã bắt đầu tính đến hôm nay), xếp từ cũ đến mới; học kỳ cuối là "học kỳ hiện tại".
    Mỗi năm học có HK1 (1/9 - 15/1) và HK2 (1/2 - 15/6).
    """
    cac_ky = []
    for nam in range(hom_nay.year - 2, hom_nay.year + 1):
        cac_ky.append((1, nam, date(nam, 9, 1), date(nam + 1, 1, 15)))
        cac_ky.append((2, nam, date(nam + 1, 2, 1), date(nam + 1, 6, 15)))
    da_bat_dau = [k for k in cac_ky if k[2] <= hom_nay][-3:]
    ket_qua: list[HocKy] = []
    for so_ky, nam, bat_dau, ket_thuc in da_bat_dau:
        ma = tao_ma.ma_hoc_ky([hk.ma for hk in ket_qua])
        ket_qua.append(HocKy(ma=ma, ten=f"Học kỳ {so_ky} năm học {nam}-{nam + 1}", ngay_bat_dau=bat_dau, ngay_ket_thuc=ket_thuc))
    return ket_qua


# ---------------------------------------------------------------- các thực thể độc lập
def _sinh_dich_vu() -> tuple[list[DichVuThem], list[TienIchPhong]]:
    """
    Dịch vụ thêm và tiện ích phòng DÙNG CHUNG một kiểu mã (DV0001...), nên mã được cấp từ danh sách gộp của cả hai
    để không trùng nhau. Mỗi loại có thêm một mục đã ngừng (lưu trữ) và không ai dùng, để thử luu_tru / tai_kich_hoat.
    """
    da_dung: list[str] = []
    cac_dv: list[DichVuThem] = []
    cac_ti: list[TienIchPhong] = []

    def cap_ma() -> str:
        ma = tao_ma.ma_dich_vu_them(da_dung)
        da_dung.append(ma)
        return ma

    for ten, don_gia in _DICH_VU_MAU:
        cac_dv.append(DichVuThem(ma=cap_ma(), ten=ten, don_gia=don_gia))
    dv_cu = DichVuThem(ma=cap_ma(), ten="Giữ xe đạp (đã ngừng)", don_gia=20_000.0)
    dv_cu.luu_tru()
    cac_dv.append(dv_cu)

    for ten, don_gia in _TIEN_ICH_MAU:
        cac_ti.append(TienIchPhong(ma=cap_ma(), ten=ten, don_gia=don_gia))
    ti_cu = TienIchPhong(ma=cap_ma(), ten="Máy sưởi (đã ngừng)", don_gia=200_000.0)
    ti_cu.luu_tru()
    cac_ti.append(ti_cu)
    return cac_dv, cac_ti


def _lap_ke_hoach_phong(rng: random.Random, cac_tien_ich: list[TienIchPhong]) -> tuple[list[tuple[str, str, int]], list[_KeHoachPhong]]:
    """Lập danh sách tòa nhà (mã, tên, số tầng) và các phòng trong từng tòa."""
    cac_toa: list[tuple[str, str, int]] = []
    cac_phong: list[_KeHoachPhong] = []
    gia_theo_suc_chua = {4: 600_000.0, 6: 450_000.0, 8: 350_000.0}  # giá mỗi NGƯỜI mỗi tháng, phòng ít người thì đắt hơn
    for ky_hieu in "ABC":
        ma_toa = tao_ma.ma_toa_nha([t[0] for t in cac_toa])
        so_tang = rng.randint(3, 5)
        cac_toa.append((ma_toa, f"Tòa {ky_hieu}", so_tang))
        for tang in range(1, so_tang + 1):
            for stt in range(1, rng.randint(4, 6) + 1):
                suc_chua = rng.choice([4, 6, 8])
                # Mỗi phòng có 0-3 tiện ích đang hoạt động; phí tiện ích chia đều cho số chỗ, làm tròn đến nghìn đồng
                tien_ich = rng.sample(cac_tien_ich, rng.randint(0, 3))
                phi_tien_nghi = round(sum(ti.don_gia for ti in tien_ich) / suc_chua / 1000) * 1000.0
                cac_phong.append(_KeHoachPhong(
                    ma=tao_ma.ma_phong([p.ma for p in cac_phong]), ten=f"Phòng {ky_hieu}{tang}{stt:02d}",
                    suc_chua=suc_chua, gia=gia_theo_suc_chua[suc_chua], ma_toa_nha=ma_toa, tang=tang,
                    tien_ich={ti.ma for ti in tien_ich}, phi_tien_nghi=phi_tien_nghi,
                    # ~4% phòng ngừng sử dụng; được chọn TRƯỚC khi xếp chỗ nên chắc chắn không có người ở
                    hoat_dong=rng.random() > 0.04))
    return cac_toa, cac_phong


def _sinh_sinh_vien(rng: random.Random, so_luong: int, dia_chi: list[tuple[str, str]]) -> list[SinhVien]:
    cac_sv: list[SinhVien] = []
    da_dung_cccd: set[str] = set()
    da_dung_sdt: set[str] = set()
    for _ in range(so_luong):
        nam = rng.random() < 0.5
        ten = f"{rng.choice(_HO)} {rng.choice(_DEM_NAM if nam else _DEM_NU)} {rng.choice(_TEN_NAM if nam else _TEN_NU)}"
        # CCCD: 12 chữ số bắt đầu bằng 0; SĐT: đầu số hợp lệ + 8 chữ số. Loại trùng để mỗi người có số riêng.
        while (cccd := "0" + "".join(rng.choices("0123456789", k=11))) in da_dung_cccd:
            pass
        while (sdt := rng.choice(["03", "05", "07", "08", "09"]) + "".join(rng.choices("0123456789", k=8))) in da_dung_sdt:
            pass
        da_dung_cccd.add(cccd)
        da_dung_sdt.add(sdt)
        tinh, xa = rng.choice(dia_chi)
        cac_sv.append(SinhVien(
            ma=tao_ma.ma_sinh_vien(cac_sv), ten=ten, sdt=sdt, nam_sinh=rng.randint(2003, 2007), cccd=cccd,
            dia_chi_chi_tiet=f"Số {rng.randint(1, 200)} đường {rng.choice(_DUONG)}", xa=xa, tinh=tinh))
    return cac_sv


# ---------------------------------------------------------------- hợp đồng và xếp chỗ
def _chon_phong_con_cho(rng: random.Random, cac_phong: list[_KeHoachPhong]) -> _KeHoachPhong | None:
    """Chọn phòng đang hoạt động còn chỗ. Ưu tiên (50%) phòng đã có người để có cả phòng đông lẫn phòng trống."""
    con_cho = [p for p in cac_phong if p.hoat_dong and p.con_cho()]
    if not con_cho:
        return None
    da_co_nguoi = [p for p in con_cho if p.sinh_vien]
    return rng.choice(da_co_nguoi if da_co_nguoi and rng.random() < 0.5 else con_cho)


def _tao_hop_dong(rng: random.Random, cac_hd: list[HopDong], sv: SinhVien, phong: _KeHoachPhong, hoc_ky: HocKy,
                  cac_dv_dang_dung: list[DichVuThem], trang_thai: TrangThaiHopDong) -> HopDong:
    so_ngay = (hoc_ky.ngay_ket_thuc - hoc_ky.ngay_bat_dau).days
    # Dịch vụ thêm: lưu {mã dịch vụ: đơn giá tại thời điểm ký}. Chỉ dùng dịch vụ còn hoạt động.
    dich_vu = {dv.ma: dv.don_gia for dv in rng.sample(cac_dv_dang_dung, rng.randint(0, 3))}
    hd = HopDong(
        ma=tao_ma.ma_hop_dong(cac_hd), he_so_thang=round(so_ngay / 30),
        ngay_bat_dau=hoc_ky.ngay_bat_dau, ngay_ket_thuc=hoc_ky.ngay_ket_thuc,
        gia_co_ban=phong.gia, tien_dat_coc=phong.gia,  # đặt cọc một tháng
        ma_sinh_vien=sv.ma, ma_phong=phong.ma, hoc_ky=hoc_ky.ma,
        dich_vu_them=dich_vu, phi_tien_nghi=phong.phi_tien_nghi, trang_thai=trang_thai)
    return hd


def _xep_hop_dong(rng: random.Random, cac_sv: list[SinhVien], cac_phong: list[_KeHoachPhong],
                  cac_hk: list[HocKy], cac_dv: list[DichVuThem]) -> list[HopDong]:
    """
    Mỗi sinh viên rơi vào một kịch bản:
      - "o"   (~60%): đang ở, có hợp đồng ĐÃ THANH TOÁN ở học kỳ hiện tại (có thể kèm hợp đồng cũ đã kết thúc)
      - "cho" (~10%): vừa đăng ký, hợp đồng CHƯA THANH TOÁN, chưa vào ở
      - "cu"  (~15%): chỉ có hợp đồng ĐÃ KẾT THÚC ở các học kỳ trước
      - "moi" (~15%): chưa có hợp đồng nào
    Sinh viên đã lưu trữ (tốt nghiệp) luôn thuộc kịch bản "cu".
    """
    hk_hien_tai, cac_hk_truoc = cac_hk[-1], cac_hk[:-1]
    dv_hoat_dong = [dv for dv in cac_dv if dv.con_hoat_dong]
    cac_hd: list[HopDong] = []
    for sv in cac_sv:
        if rng.random() < 0.10:  # ~10% sinh viên đã tốt nghiệp/rời đi -> lưu trữ
            sv.luu_tru()
            kich_ban = "cu"
        else:
            kich_ban = rng.choices(["o", "cho", "cu", "moi"], weights=[60, 10, 15, 15])[0]

        # Hợp đồng đã kết thúc ở các học kỳ trước (phòng nào cũng được, kể cả phòng nay đã ngừng sử dụng)
        if kich_ban == "cu":
            cac_ky_cu = rng.sample(cac_hk_truoc, rng.randint(1, len(cac_hk_truoc)))
        elif kich_ban in ("o", "cho") and rng.random() < 0.5:
            cac_ky_cu = [cac_hk_truoc[-1]]
        else:
            cac_ky_cu = []
        for hk in cac_ky_cu:
            cac_hd.append(_tao_hop_dong(rng, cac_hd, sv, rng.choice(cac_phong), hk, dv_hoat_dong, TrangThaiHopDong.KET_THUC_HOP_DONG))

        if kich_ban == "o":
            phong = _chon_phong_con_cho(rng, cac_phong)
            if phong is not None:  # hết chỗ thì sinh viên này coi như chưa có hợp đồng hiện tại
                hd = _tao_hop_dong(rng, cac_hd, sv, phong, hk_hien_tai, dv_hoat_dong, TrangThaiHopDong.DA_THANH_TOAN)
                cac_hd.append(hd)
                # Cập nhật cả hai phía của quan hệ: phòng có sinh viên VÀ sinh viên biết phòng/hợp đồng của mình
                phong.sinh_vien.append(sv.ma)  # type: ignore[union-attr]
                sv.phong_hien_tai = phong.ma
                sv.hop_dong = hd.ma
        elif kich_ban == "cho":
            phong = _chon_phong_con_cho(rng, cac_phong)
            if phong is not None:
                cac_hd.append(_tao_hop_dong(rng, cac_hd, sv, phong, hk_hien_tai, dv_hoat_dong, TrangThaiHopDong.CHUA_THANH_TOAN))
    return cac_hd


# ---------------------------------------------------------------- hóa đơn, vi phạm, tài khoản
def _lui_thang(hom_nay: date, so_thang: int) -> tuple[int, int]:
    """Trả về (năm, tháng) của tháng cách hôm nay so_thang tháng về trước."""
    chi_so = hom_nay.year * 12 + (hom_nay.month - 1) - so_thang
    return chi_so // 12, chi_so % 12 + 1


def _sinh_hoa_don(rng: random.Random, cac_phong: list[_KeHoachPhong], hom_nay: date) -> list[HoaDonThang]:
    """
    Hóa đơn 3 tháng gần nhất cho mỗi phòng đang có người ở. Chỉ số điện nước nối tiếp nhau giữa các tháng.
    Tháng cũ phần lớn đã thanh toán; tháng gần nhất còn nhiều hóa đơn chưa thanh toán (để thử thống kê công nợ).
    """
    cau_hinh = CauHinhDong()
    cac_hoa_don: list[HoaDonThang] = []
    for phong in cac_phong:
        if not phong.sinh_vien:
            continue
        dien, nuoc = rng.randint(100, 900), rng.randint(10, 100)  # chỉ số đầu kỳ của tháng đầu tiên
        for so_thang_lui in (3, 2, 1):
            nam, thang = _lui_thang(hom_nay, so_thang_lui)
            nam_han, thang_han = _lui_thang(hom_nay, so_thang_lui - 1)  # hạn chót là ngày N của tháng kế tiếp
            dien_moi = dien + rng.randint(40, 120) * len(phong.sinh_vien)  # dùng nhiều người thì tiêu thụ nhiều
            nuoc_moi = nuoc + rng.randint(3, 8) * len(phong.sinh_vien)
            xac_suat_da_tra = 0.5 if so_thang_lui == 1 else 0.9
            da_tra = rng.random() < xac_suat_da_tra
            cac_hoa_don.append(HoaDonThang(
                ma=tao_ma.ma_hoa_don_thang(cac_hoa_don), thang=thang, dien_cu=dien, dien_moi=dien_moi,
                don_gia_dien=cau_hinh.DON_GIA_DIEN, nuoc_cu=nuoc, nuoc_moi=nuoc_moi,
                don_gia_nuoc=cau_hinh.DON_GIA_NUOC, phong=phong.ma,
                han_chot=date(nam_han, thang_han, min(cau_hinh.THOI_HAN_DONG_TIEN_DIEN, 28)),
                trang_thai=TrangThaiHoaDon.DA_THANH_TOAN if da_tra else TrangThaiHoaDon.CHUA_THANH_TOAN))
            dien, nuoc = dien_moi, nuoc_moi  # chỉ số cuối tháng này là chỉ số đầu tháng sau
    return cac_hoa_don


def _sinh_vi_pham(rng: random.Random, cac_sv: list[SinhVien], hom_nay: date) -> list[ViPham]:
    cac_vp: list[ViPham] = []
    for _ in range(max(1, len(cac_sv) // 6)):
        sv = rng.choice(cac_sv)
        ngay = date.fromordinal(hom_nay.toordinal() - rng.randint(1, 120))
        ma = tao_ma.ma_vi_pham(cac_vp)
        if rng.random() < 0.6:
            mo_ta, ky_luat = rng.choice(_NOI_QUY)
            vp: ViPham = ViPhamNoiQuy(ma=ma, sinh_vien=sv.ma, ngay_vi_pham=ngay, mo_ta=mo_ta, hinh_thuc_ky_luat=ky_luat)
        else:
            mo_ta, tien = rng.choice(_TAI_SAN)
            vp = ViPhamTaiSan(ma=ma, sinh_vien=sv.ma, ngay_vi_pham=ngay, mo_ta=mo_ta, tien_boi_thuong=tien)
        if rng.random() < 0.5:
            vp.xu_ly()
        cac_vp.append(vp)
    return cac_vp


def _sinh_tai_khoan(cac_sv: list[SinhVien], so_vong_bam: int) -> list[TaiKhoan]:
    """Một quản trị viên và tài khoản cho vài sinh viên đang hoạt động đầu danh sách. Mật khẩu được băm như thật."""
    cac_tk = [TaiKhoan(TEN_ADMIN_MAU, bam_mat_khau(MAT_KHAU_ADMIN_MAU, so_vong_bam), LoaiTaiKhoan.QUAN_TRI_VIEN, None)]
    dang_hoat_dong = [sv for sv in cac_sv if sv.con_hoat_dong][:SO_TAI_KHOAN_SINH_VIEN_MAU]
    for sv in dang_hoat_dong:
        # Tên đăng nhập = mã sinh viên viết thường (SV0001 -> sv0001), khớp quy tắc tên đăng nhập trong regex.py
        cac_tk.append(TaiKhoan(sv.ma.lower(), bam_mat_khau(MAT_KHAU_SINH_VIEN_MAU, so_vong_bam), LoaiTaiKhoan.SINH_VIEN, sv.ma))
    return cac_tk


# ---------------------------------------------------------------- hàm chính
def sinh_du_lieu(so_sinh_vien: int = 80, seed: int | None = None, hom_nay: date | None = None,
                 dia_ly: list[Tinh] | None = None, so_vong_bam: int = SO_VONG_MAC_DINH) -> DuLieuMau:
    """
    Sinh một bộ dữ liệu mẫu hoàn chỉnh trong bộ nhớ (chưa ghi file, xem ghi_du_lieu).

    Tham số:
        - so_sinh_vien: số sinh viên cần sinh (tối thiểu 1).
        - seed: hạt giống ngẫu nhiên; cùng seed (và cùng hom_nay) thì cho đúng cùng một bộ dữ liệu.
        - hom_nay: ngày làm mốc cho học kỳ, hóa đơn, vi phạm (mặc định là ngày hiện tại).
        - dia_ly: danh sách tỉnh/xã thật (từ LuuTruDiaLy) để chọn địa chỉ; None thì dùng vài địa chỉ mẫu.
        - so_vong_bam: số vòng băm mật khẩu; giữ mặc định khi dùng thật, chỉ hạ thấp khi cần sinh hàng loạt để test cho nhanh.
    """
    if so_sinh_vien < 1:
        raise ValueError("Số sinh viên phải lớn hơn 0")
    rng = random.Random(seed)
    hom_nay = hom_nay or date.today()

    # Gom địa chỉ thành các cặp (tên tỉnh, tên xã)
    dia_chi = [(t.ten, x.ten) for t in (dia_ly or []) for x in t.danh_sach_xa] or _DIA_CHI_DU_PHONG

    cac_hk = _sinh_hoc_ky(hom_nay)
    cac_dv, cac_ti = _sinh_dich_vu()
    cac_toa, ke_hoach_phong = _lap_ke_hoach_phong(rng, [ti for ti in cac_ti if ti.con_hoat_dong])
    cac_sv = _sinh_sinh_vien(rng, so_sinh_vien, dia_chi)
    cac_hd = _xep_hop_dong(rng, cac_sv, ke_hoach_phong, cac_hk, cac_dv)  # đồng thời xếp sinh viên vào phòng
    cac_hoa_don = _sinh_hoa_don(rng, ke_hoach_phong, hom_nay)

    # Xếp chỗ xong mới dựng Phong và ToaNha thật. Hai class này chỉ cho thêm sinh viên / phòng qua
    # them_sinh_vien() / them_phong(), nên dựng xong rồi mới thêm, và kiểm tra lại kết quả để báo lỗi rõ ràng.
    cac_phong = []
    for p in ke_hoach_phong:
        phong = Phong(ma=p.ma, ten=p.ten, suc_chua=p.suc_chua, gia_phong=p.gia * p.suc_chua, toa_nha=p.ma_toa_nha,
                      tang=p.tang, tien_ich_phong=set(p.tien_ich))
        for ma_sv in p.sinh_vien:  # type: ignore[union-attr]
            phong.them_sinh_vien(ma_sv)
        if phong.danh_sach_sinh_vien != set(p.sinh_vien):  # type: ignore[arg-type]
            raise RuntimeError("Phong.them_sinh_vien() chưa thêm được sinh viên vào phòng (có thể phần B chưa triển khai hàm này)")
        if not p.hoat_dong:  # lưu trữ SAU CÙNG vì phòng ngừng hoạt động có thể không cho thêm sinh viên nữa
            phong.luu_tru()
        cac_phong.append(phong)
    cac_toa_nha = []
    for ma, ten, so_tang in cac_toa:
        toa = ToaNha(ma=ma, ten=ten, so_tang=so_tang)
        for phong in cac_phong:
            if phong.toa_nha == ma:
                toa.them_phong(phong.ma)
        if toa.danh_sach_phong != {p.ma for p in cac_phong if p.toa_nha == ma}:
            raise RuntimeError("ToaNha.them_phong() chưa thêm được phòng vào tòa nhà (có thể phần B chưa triển khai hàm này)")
        cac_toa_nha.append(toa)

    return DuLieuMau(
        hoc_ky=cac_hk, dich_vu_them=cac_dv, tien_ich_phong=cac_ti, toa_nha=cac_toa_nha, phong=cac_phong, sinh_vien=cac_sv,
        hop_dong=cac_hd, hoa_don_thang=cac_hoa_don, vi_pham=_sinh_vi_pham(rng, cac_sv, hom_nay),
        tai_khoan=_sinh_tai_khoan(cac_sv, so_vong_bam))


# ---------------------------------------------------------------- tự kiểm tra ràng buộc chéo
def kiem_tra_rang_buoc(dl: DuLieuMau) -> list[str]:
    """
    Kiểm tra toàn bộ ràng buộc chéo của bộ dữ liệu. Trả về danh sách lỗi (rỗng nghĩa là hợp lệ).
    Dùng được cho cả dữ liệu đọc lại từ file sau khi ghi, để chắc chắn lưu/đọc không làm lệch quan hệ.
    """
    loi: list[str] = []
    sv_theo_ma = {s.ma: s for s in dl.sinh_vien}
    phong_theo_ma = {p.ma: p for p in dl.phong}
    toa_theo_ma = {t.ma: t for t in dl.toa_nha}
    dv_theo_ma = {d.ma: d for d in dl.dich_vu_them}
    ti_theo_ma = {t.ma: t for t in dl.tien_ich_phong}
    ma_hoc_ky = {h.ma for h in dl.hoc_ky}

    # 1. Mã duy nhất và đúng định dạng
    for ten, ds, kiem_tra in [("sinh viên", dl.sinh_vien, la_ma_sinh_vien), ("phòng", dl.phong, la_ma_phong),
                              ("tòa nhà", dl.toa_nha, la_ma_toa_nha), ("hợp đồng", dl.hop_dong, la_ma_hop_dong),
                              ("hóa đơn", dl.hoa_don_thang, la_ma_hoa_don_thang),
                              ("dịch vụ/tiện ích", dl.dich_vu_co_so(), la_ma_dich_vu_them), ("vi phạm", dl.vi_pham, la_ma_vi_pham)]:
        cac_ma = [x.ma for x in ds]
        if len(cac_ma) != len(set(cac_ma)):
            loi.append(f"Mã {ten} bị trùng")
        loi += [f"Mã {ten} sai định dạng: {m}" for m in cac_ma if not kiem_tra(m)]
    for s in dl.sinh_vien:
        if not la_sdt(s.sdt) or not la_cccd(s.cccd):
            loi.append(f"{s.ma}: SĐT hoặc CCCD không hợp lệ")
    if len({s.cccd for s in dl.sinh_vien}) != len(dl.sinh_vien):
        loi.append("CCCD bị trùng giữa các sinh viên")

    # 2. Tòa nhà <-> phòng
    for p in dl.phong:
        t = toa_theo_ma.get(p.toa_nha)
        if t is None:
            loi.append(f"{p.ma}: tòa nhà {p.toa_nha} không tồn tại")
        else:
            if p.ma not in t.danh_sach_phong:
                loi.append(f"{p.ma}: không có trong danh sách phòng của {t.ma}")
            if not 1 <= p.tang <= t.so_tang:
                loi.append(f"{p.ma}: tầng {p.tang} vượt số tầng của {t.ma}")
    for t in dl.toa_nha:
        for ma in t.danh_sach_phong:
            if ma not in phong_theo_ma or phong_theo_ma[ma].toa_nha != t.ma:
                loi.append(f"{t.ma}: phòng {ma} không tồn tại hoặc thuộc tòa khác")

    # 3. Phòng <-> sinh viên (hai chiều), sức chứa
    for p in dl.phong:
        ds = p.danh_sach_sinh_vien
        loi += [f"{p.ma}: tiện ích {m} không tồn tại, đã lưu trữ hoặc không phải tiện ích phòng" for m in p.tien_ich_phong
                if m not in ti_theo_ma or not ti_theo_ma[m].con_hoat_dong]
        if len(ds) > p.suc_chua:
            loi.append(f"{p.ma}: {len(ds)} sinh viên vượt sức chứa {p.suc_chua}")
        if ds and not p.con_hoat_dong:
            loi.append(f"{p.ma}: phòng đã lưu trữ nhưng còn sinh viên")
        for ma in ds:
            if ma not in sv_theo_ma:
                loi.append(f"{p.ma}: sinh viên {ma} không tồn tại")
            elif sv_theo_ma[ma].phong_hien_tai != p.ma:
                loi.append(f"{p.ma}: sinh viên {ma} nhưng {ma} không ghi phòng này")
    for s in dl.sinh_vien:
        if s.phong_hien_tai is not None:
            p = phong_theo_ma.get(s.phong_hien_tai)
            if p is None or s.ma not in p.danh_sach_sinh_vien:
                loi.append(f"{s.ma}: phòng {s.phong_hien_tai} không tồn tại hoặc không có sinh viên này")
            if not s.con_hoat_dong:
                loi.append(f"{s.ma}: đã lưu trữ nhưng vẫn có phòng")

    # 4. Hợp đồng
    da_thanh_toan_cua: dict[str, list[HopDong]] = {}
    for hd in dl.hop_dong:
        if hd.ma_sinh_vien not in sv_theo_ma:
            loi.append(f"{hd.ma}: sinh viên {hd.ma_sinh_vien} không tồn tại")
        if hd.ma_phong not in phong_theo_ma:
            loi.append(f"{hd.ma}: phòng {hd.ma_phong} không tồn tại")
        elif not math.isclose(hd.gia_co_ban, phong_theo_ma[hd.ma_phong].gia_co_ban):
            loi.append(f"{hd.ma}: giá cơ bản không khớp giá cơ bản của phòng {hd.ma_phong}")
        if hd.hoc_ky not in ma_hoc_ky:
            loi.append(f"{hd.ma}: học kỳ {hd.hoc_ky} không tồn tại")
        if hd.ngay_ket_thuc <= hd.ngay_bat_dau:
            loi.append(f"{hd.ma}: ngày kết thúc không sau ngày bắt đầu")
        loi += [f"{hd.ma}: dịch vụ {m} không tồn tại hoặc đã lưu trữ" for m in hd.dich_vu_them
                if m not in dv_theo_ma or not dv_theo_ma[m].con_hoat_dong]
        if hd.trang_thai == TrangThaiHopDong.DA_THANH_TOAN:
            da_thanh_toan_cua.setdefault(hd.ma_sinh_vien, []).append(hd)
            if hd.ma_phong in phong_theo_ma and not phong_theo_ma[hd.ma_phong].con_hoat_dong:
                loi.append(f"{hd.ma}: hợp đồng hiệu lực ở phòng đã lưu trữ")
    for ma_sv, ds in da_thanh_toan_cua.items():
        if len(ds) > 1:
            loi.append(f"{ma_sv}: có {len(ds)} hợp đồng đã thanh toán cùng lúc")
        elif ma_sv in sv_theo_ma:
            s, hd = sv_theo_ma[ma_sv], ds[0]
            if (s.phong_hien_tai, s.hop_dong) != (hd.ma_phong, hd.ma):
                loi.append(f"{ma_sv}: hợp đồng {hd.ma} đã thanh toán nhưng sinh viên không ghi đúng phòng/hợp đồng")
            if not s.con_hoat_dong:
                loi.append(f"{ma_sv}: đã lưu trữ nhưng còn hợp đồng hiệu lực")
    for s in dl.sinh_vien:  # chiều ngược lại: sinh viên ghi phòng/hợp đồng thì phải có hợp đồng đã thanh toán tương ứng
        if (s.phong_hien_tai is None) != (s.hop_dong is None):
            loi.append(f"{s.ma}: phòng hiện tại và hợp đồng không đi đôi với nhau")
        elif s.hop_dong is not None and s.ma not in da_thanh_toan_cua:
            loi.append(f"{s.ma}: ghi hợp đồng {s.hop_dong} nhưng không có hợp đồng đã thanh toán")

    # 5. Hóa đơn tháng
    da_thay: set[tuple[str, int]] = set()
    for h in dl.hoa_don_thang:
        if h.phong not in phong_theo_ma:
            loi.append(f"{h.ma}: phòng {h.phong} không tồn tại")
        if (h.phong, h.thang) in da_thay:
            loi.append(f"{h.ma}: trùng hóa đơn tháng {h.thang} của phòng {h.phong}")
        da_thay.add((h.phong, h.thang))
        if h.dien_moi < h.dien_cu or h.nuoc_moi < h.nuoc_cu:
            loi.append(f"{h.ma}: chỉ số mới nhỏ hơn chỉ số cũ")
        if not 1 <= h.thang <= 12:
            loi.append(f"{h.ma}: tháng {h.thang} không hợp lệ")

    # 6. Vi phạm
    loi += [f"{v.ma}: sinh viên {v.sinh_vien} không tồn tại" for v in dl.vi_pham if v.sinh_vien not in sv_theo_ma]

    # 7. Tài khoản
    ma_chu_the = [t.ma_chu_the for t in dl.tai_khoan if t.loai_tai_khoan == LoaiTaiKhoan.SINH_VIEN]
    if len(ma_chu_the) != len(set(ma_chu_the)):
        loi.append("Có sinh viên có nhiều hơn một tài khoản")
    loi += [f"Tài khoản sinh viên trỏ tới {m} không tồn tại" for m in ma_chu_the if m not in sv_theo_ma]
    if not any(t.co_quyen_quan_tri for t in dl.tai_khoan):
        loi.append("Không có tài khoản quản trị viên nào")
    if any(not t.mat_khau_bam.startswith("pbkdf2_sha256$") for t in dl.tai_khoan):
        loi.append("Có tài khoản chưa băm mật khẩu")
    return loi


# ---------------------------------------------------------------- ghi xuống file
def ghi_du_lieu(dl: DuLieuMau) -> None:
    """Ghi toàn bộ dữ liệu xuống du_lieu/ qua các lớp lưu trữ (có kèm file sao lưu). GHI ĐÈ dữ liệu hiện có."""
    from luu_tru import (LuuTruDichVuCoSo, LuuTruHoaDonThang, LuuTruHopDong, LuuTruPhong,
                         LuuTruSinhVien, LuuTruTaiKhoan, LuuTruToaNha, LuuTruViPham)

    def thanh_dict(danh_sach: list) -> dict:
        """Giao thức lưu trữ nhận dict {mã: thực thể}."""
        return {tt.ma: tt for tt in danh_sach}

    for luu_tru, danh_sach in [(LuuTruSinhVien(), dl.sinh_vien), (LuuTruPhong(), dl.phong), (LuuTruToaNha(), dl.toa_nha),
                               (LuuTruHopDong(), dl.hop_dong), (LuuTruHoaDonThang(), dl.hoa_don_thang),
                               (LuuTruDichVuCoSo(), dl.dich_vu_co_so()),  # dịch vụ thêm + tiện ích phòng: chung một file
                               (LuuTruViPham(), dl.vi_pham), (LuuTruTaiKhoan(), dl.tai_khoan)]:
        luu_tru.ghi(thanh_dict(danh_sach))


def _doc_dia_ly_cuc_bo() -> list[Tinh] | None:
    """Đọc địa lý đã tải sẵn trên máy (không gọi mạng). Chưa có hoặc hỏng thì trả None để dùng địa chỉ mẫu."""
    from luu_tru.luu_tru_dia_ly import LuuTruDiaLy
    from tien_ich.cau_hinh_tinh import FILE_DIA_LY
    from tien_ich.tap_tin import lay_duong_dan_du_lieu
    if not os.path.exists(lay_duong_dan_du_lieu(FILE_DIA_LY)):
        return None
    try:
        return list(LuuTruDiaLy().doc().values()) or None
    except (ValueError, FileNotFoundError):
        return None


def chay(so_sinh_vien: int = 80, seed: int | None = None, cho_phep_ghi_de: bool = False) -> None:
    """Sinh dữ liệu, kiểm tra ràng buộc rồi ghi xuống file. Từ chối nếu đã có dữ liệu mà chưa cho phép ghi đè."""
    from tien_ich import cau_hinh_tinh as cht
    from tien_ich.tap_tin import lay_duong_dan_du_lieu

    cac_file = [cht.FILE_SINH_VIEN, cht.FILE_PHONG, cht.FILE_TOA_NHA, cht.FILE_HOP_DONG,
                cht.FILE_HOA_DON_THANG, cht.FILE_DICH_VU_THEM, cht.FILE_VI_PHAM, cht.FILE_TAI_KHOAN]
    da_co = [f for f in cac_file if os.path.exists(lay_duong_dan_du_lieu(f))]
    if da_co and not cho_phep_ghi_de:
        # Bảo vệ dữ liệu thật: chạy nhầm lệnh này sẽ xóa sạch dữ liệu đang có nên phải chủ động thêm --ghi-de
        raise SystemExit(f"Đã có dữ liệu ({', '.join(da_co)}). Thêm --ghi-de nếu muốn thay toàn bộ bằng dữ liệu mẫu.")

    if seed is None:
        seed = random.randrange(1_000_000)  # tự chọn nhưng in ra để có thể tái hiện đúng bộ dữ liệu này
    dl = sinh_du_lieu(so_sinh_vien, seed, dia_ly=_doc_dia_ly_cuc_bo())
    loi = kiem_tra_rang_buoc(dl)
    if loi:
        raise SystemExit("Dữ liệu sinh ra vi phạm ràng buộc (lỗi của bộ sinh):\n  " + "\n  ".join(loi[:20]))
    ghi_du_lieu(dl)

    dang_o = sum(1 for s in dl.sinh_vien if s.phong_hien_tai)
    print(f"Đã ghi dữ liệu mẫu (seed={seed}): {len(dl.sinh_vien)} sinh viên ({dang_o} đang ở), {len(dl.phong)} phòng, "
          f"{len(dl.toa_nha)} tòa nhà, {len(dl.hop_dong)} hợp đồng, {len(dl.hoa_don_thang)} hóa đơn, "
          f"{len(dl.dich_vu_them)} dịch vụ thêm, {len(dl.tien_ich_phong)} tiện ích phòng, {len(dl.vi_pham)} vi phạm, {len(dl.tai_khoan)} tài khoản.")
    print(f"Đăng nhập thử: {TEN_ADMIN_MAU} / {MAT_KHAU_ADMIN_MAU} (quản trị viên); "
          f"{dl.tai_khoan[1].ma} / {MAT_KHAU_SINH_VIEN_MAU} (sinh viên)" if len(dl.tai_khoan) > 1 else "")


if __name__ == "__main__":
    bo_doc = argparse.ArgumentParser(description="Sinh dữ liệu mẫu cho ứng dụng quản lý ký túc xá")
    bo_doc.add_argument("--so-sinh-vien", type=int, default=80, help="số sinh viên cần sinh (mặc định 80)")
    bo_doc.add_argument("--seed", type=int, default=None, help="hạt giống ngẫu nhiên để tái hiện cùng một bộ dữ liệu")
    bo_doc.add_argument("--ghi-de", action="store_true", help="cho phép thay thế dữ liệu hiện có")
    doi_so = bo_doc.parse_args()
    chay(doi_so.so_sinh_vien, doi_so.seed, doi_so.ghi_de)
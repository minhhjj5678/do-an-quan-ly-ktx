# Phần C
# Sinh dữ liệu mẫu ngẫu nhiên cho toàn bộ thực thể (HocKy, SinhVien, Phong, ToaNha, HopDong, HoaDonThang,
# DichVuThem, TienIchPhong, ViPham, TaiKhoan) để kiểm thử sau khi ráp ba tầng.
#
# Điểm quan trọng nhất là dữ liệu phải ĐÚNG RÀNG BUỘC CHÉO (bộ sinh được viết để luôn thỏa các điều kiện này), ví dụ:
#   - sinh viên có phòng_hiện_tại = P0005 thì phòng P0005 phải tồn tại VÀ có mã sinh viên đó trong danh sách
#   - số sinh viên trong phòng không vượt sức chứa, và số hợp đồng đang giữ chỗ (HopDong.con_giu_cho)
#     của mỗi phòng cũng không vượt sức chứa
#   - hợp đồng "đã thanh toán" <=> sinh viên đang ở đúng phòng của hợp đồng đó
#   - thực thể đã lưu trữ (ngừng hoạt động) không được còn hợp đồng đang hiệu lực
# Việc kiểm tra lại các điều kiện đó do tầng nghiệp vụ đảm nhiệm: chay() gọi nghiep_vu.kiem_cheo_du_lieu.
#
# Cách dùng:
#   - Trong code:   du_lieu = sinh_du_lieu(so_sinh_vien=80, seed=1);  ghi_du_lieu(du_lieu)
#   - Dòng lệnh:    py -m cong_cu.sinh_du_lieu --so-sinh-vien 80 --seed 1
# Tham số seed cố định thì lần nào chạy cũng ra đúng bộ dữ liệu đó (tiện tái hiện lỗi).
import argparse
import os
import random
from dataclasses import dataclass
from datetime import date, timedelta

from thuc_the.dia_ly import Tinh
from nghiep_vu.kiem_cheo_du_lieu import KhoDuLieu, kiem_cheo_du_lieu
from thuc_the.hoc_vu import HocKy, ThangNam
from thuc_the.ky_tuc_xa import Phong, SinhVien, ToaNha
from thuc_the.tai_chinh import DichVuThem, HoaDonThang, HopDong, TienIchPhong, TrangThaiHoaDon, TrangThaiHopDong
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from thuc_the.vi_pham import ViPham, ViPhamNoiQuy, ViPhamTaiSan
from tien_ich import tao_ma
from tien_ich.bam_mat_khau import SO_VONG_MAC_DINH, bam_mat_khau
from tien_ich.cau_hinh_dong import CauHinhDong

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
# (mã tỉnh, mã xã) mẫu, chỉ dùng khi KHÔNG có dữ liệu địa lý thật (chưa có file và không tải được từ API).
# Đây chỉ là mã giả để có giá trị điền vào, không đảm bảo tồn tại trong dữ liệu địa lý thật.
_DIA_CHI_DU_PHONG = [("1", "1"), ("79", "1"), ("48", "1"), ("75", "1"), ("40", "1"), ("68", "1")]
_DICH_VU_MAU = [("Giặt ủi", 50_000.0), ("Internet tốc độ cao", 60_000.0), ("Gửi xe máy", 100_000.0),
                ("Dọn vệ sinh phòng", 80_000.0), ("Nước uống đóng bình", 40_000.0)]
_TIEN_ICH_MAU = [("Điều hòa", 400_000.0), ("Bình nóng lạnh", 150_000.0), ("Tủ lạnh mini", 120_000.0), ("Quạt trần", 30_000.0)]
_NOI_QUY = [("Gây ồn sau 23 giờ", "Khiển trách"), ("Về muộn quá giờ quy định", "Nhắc nhở"),
            ("Nấu ăn trong phòng", "Cảnh cáo"), ("Mang người lạ vào phòng", "Cảnh cáo"),
            ("Không dọn vệ sinh phòng", "Nhắc nhở")]
_TAI_SAN = [("Làm vỡ kính cửa sổ", 250_000.0), ("Làm hỏng ổ khóa cửa", 150_000.0),
            ("Hư quạt trần do sử dụng sai", 400_000.0), ("Làm hỏng giường tầng", 800_000.0)]


@dataclass
class _KeHoachPhong:
    """Bản nháp của một phòng trong lúc xếp chỗ. Xếp xong toàn bộ mới dựng Phong thật từ bản nháp này."""
    ma: str
    ten: str
    suc_chua: int
    gia: float  # giá cơ bản cho MỖI người mỗi tháng (Phong.gia_phong = gia * suc_chua)
    ma_toa_nha: str
    tang: int
    tien_ich: set[str]
    phi_tien_nghi: float  # tổng giá tiện ích của phòng chia đều cho sức chứa, tức phần mỗi người chịu
    hoat_dong: bool = True
    sinh_vien: list[str] | None = None  # sinh viên đang ở (hợp đồng đã thanh toán)
    so_cho_giu: int = 0  # số hợp đồng chưa thanh toán nhưng còn hạn giữ chỗ

    def __post_init__(self) -> None:
        self.sinh_vien = []

    def con_cho(self) -> bool:
        """Còn chỗ khi (người đang ở + chỗ đang được giữ) chưa chạm sức chứa, đúng quy tắc của HopDong.con_giu_cho."""
        return len(self.sinh_vien) + self.so_cho_giu < self.suc_chua  # type: ignore[arg-type]


# ---------------------------------------------------------------- học kỳ
def _sinh_hoc_ky(hom_nay: date) -> list[HocKy]:
    """
    Bốn học kỳ xếp từ cũ đến mới:
      [0], [1]: hai học kỳ đã kết thúc (hợp đồng đã kết thúc, hoặc đăng ký rồi không đóng tiền)
      [2]: học kỳ hiện tại, tức học kỳ đầu tiên chưa kết thúc (đang diễn ra, hoặc sắp bắt đầu nếu đang nghỉ giữa hai kỳ)
      [3]: học kỳ kế tiếp, nơi sinh viên vừa đăng ký và đang giữ chỗ
    Mỗi năm học có HK1 (1/9 - 15/1) và HK2 (1/2 - 15/6).
    """
    cac_ky = []
    for nam in range(hom_nay.year - 2, hom_nay.year + 2):
        cac_ky.append((1, nam, date(nam, 9, 1), date(nam + 1, 1, 15)))
        cac_ky.append((2, nam, date(nam + 1, 2, 1), date(nam + 1, 6, 15)))
    vi_tri_hien_tai = next(i for i, k in enumerate(cac_ky) if k[3] >= hom_nay)
    ket_qua: list[HocKy] = []
    for so_ky, nam, bat_dau, ket_thuc in cac_ky[vi_tri_hien_tai - 2: vi_tri_hien_tai + 2]:
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
    """dia_chi là danh sách (mã tỉnh, mã xã); SinhVien.tinh và SinhVien.xa lưu MÃ chứ không lưu tên."""
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
        ma_tinh, ma_xa = rng.choice(dia_chi)
        cac_sv.append(SinhVien(
            ma=tao_ma.ma_sinh_vien(cac_sv), ten=ten, sdt=sdt, nam_sinh=rng.randint(2003, 2007), cccd=cccd,
            dia_chi_chi_tiet=f"Số {rng.randint(1, 200)} đường {rng.choice(_DUONG)}", xa=ma_xa, tinh=ma_tinh))
    return cac_sv


# ---------------------------------------------------------------- hợp đồng và xếp chỗ
def _chon_phong_con_cho(rng: random.Random, cac_phong: list[_KeHoachPhong]) -> _KeHoachPhong | None:
    """Chọn phòng đang hoạt động còn chỗ. Ưu tiên (50%) phòng đã có người để có cả phòng đông lẫn phòng trống."""
    con_cho = [p for p in cac_phong if p.hoat_dong and p.con_cho()]
    if not con_cho:
        return None
    da_co_nguoi = [p for p in con_cho if p.sinh_vien]
    return rng.choice(da_co_nguoi if da_co_nguoi and rng.random() < 0.5 else con_cho)


def _ngay_ky_va_het_han(rng: random.Random, hoc_ky: HocKy, hom_nay: date, dang_cho: bool) -> tuple[date, date]:
    """
    Trả về (ngày ký, ngày hết hạn giữ chỗ) thỏa quy tắc của HopDong: ngày ký <= ngày hết hạn <= ngày bắt đầu.
      - dang_cho=True: hợp đồng vừa đăng ký cho học kỳ SẮP TỚI và còn hạn giữ chỗ: ký trong 10 ngày qua, hết hạn từ hôm
        nay trở đi (nhưng không quá ngày bắt đầu học kỳ), để HopDong.con_giu_cho là True.
      - dang_cho=False: hợp đồng bình thường ký trước ngày bắt đầu 20-60 ngày, hạn thanh toán là 14 ngày sau khi ký.
    """
    bat_dau = hoc_ky.ngay_bat_dau
    if dang_cho:
        ngay_ky = hom_nay - timedelta(days=rng.randint(0, 10))
        ngay_het_han = min(bat_dau, hom_nay + timedelta(days=rng.randint(1, 14)))
    else:
        ngay_ky = bat_dau - timedelta(days=rng.randint(20, 60))
        ngay_het_han = min(bat_dau, ngay_ky + timedelta(days=14))
    return ngay_ky, ngay_het_han


def _tao_hop_dong(rng: random.Random, cac_hd: list[HopDong], sv: SinhVien, phong: _KeHoachPhong, hoc_ky: HocKy,
                  cac_dv_dang_dung: list[DichVuThem], trang_thai: TrangThaiHopDong, hom_nay: date,
                  dang_cho: bool = False) -> HopDong:
    so_ngay = (hoc_ky.ngay_ket_thuc - hoc_ky.ngay_bat_dau).days
    # Dịch vụ thêm: lưu {mã dịch vụ: đơn giá tại thời điểm ký}. Chỉ dùng dịch vụ còn hoạt động.
    dich_vu = {dv.ma: dv.don_gia for dv in rng.sample(cac_dv_dang_dung, rng.randint(0, 3))}
    ngay_ky, ngay_het_han = _ngay_ky_va_het_han(rng, hoc_ky, hom_nay, dang_cho)
    return HopDong(
        ma=tao_ma.ma_hop_dong(cac_hd), ngay_ky=ngay_ky, ngay_het_han=ngay_het_han, he_so_thang=round(so_ngay / 30),
        ngay_bat_dau=hoc_ky.ngay_bat_dau, ngay_ket_thuc=hoc_ky.ngay_ket_thuc,
        gia_co_ban=phong.gia, tien_dat_coc=phong.gia,  # đặt cọc một tháng
        ma_sinh_vien=sv.ma, ma_phong=phong.ma, hoc_ky=hoc_ky.ma,
        dich_vu_them=dich_vu, phi_tien_nghi=phong.phi_tien_nghi, trang_thai=trang_thai)


def _xep_hop_dong(rng: random.Random, cac_sv: list[SinhVien], cac_phong: list[_KeHoachPhong],
                  cac_hk: list[HocKy], cac_dv: list[DichVuThem], hom_nay: date) -> list[HopDong]:
    """
    Mỗi sinh viên rơi vào một kịch bản (cac_hk = [đã kết thúc, đã kết thúc, hiện tại, kế tiếp]):
      - "o"      (~55%): đang ở, hợp đồng ĐÃ THANH TOÁN ở học kỳ hiện tại (có thể kèm hợp đồng cũ đã kết thúc)
      - "cho"    (~10%): vừa đăng ký học kỳ KẾ TIẾP, hợp đồng CHƯA THANH TOÁN nhưng còn hạn giữ chỗ, chưa vào ở
      - "het_han" (~5%): đăng ký học kỳ trước rồi không đóng tiền, hợp đồng CHƯA THANH TOÁN và đã quá hạn (không giữ chỗ)
      - "cu"     (~15%): chỉ có hợp đồng ĐÃ KẾT THÚC ở các học kỳ trước
      - "moi"    (~15%): chưa có hợp đồng nào
    Sinh viên đã lưu trữ (tốt nghiệp) luôn thuộc kịch bản "cu".
    Mỗi phòng chỉ được xếp thêm khi (người đang ở + hợp đồng đang giữ chỗ) chưa chạm sức chứa.
    """
    cac_hk_truoc, hk_hien_tai, hk_ke_tiep = cac_hk[:2], cac_hk[2], cac_hk[3]
    dv_hoat_dong = [dv for dv in cac_dv if dv.con_hoat_dong]
    cac_hd: list[HopDong] = []

    def tao(sv: SinhVien, phong: _KeHoachPhong, hk: HocKy, trang_thai: TrangThaiHopDong, dang_cho: bool = False) -> HopDong:
        hd = _tao_hop_dong(rng, cac_hd, sv, phong, hk, dv_hoat_dong, trang_thai, hom_nay, dang_cho)
        cac_hd.append(hd)
        return hd

    for sv in cac_sv:
        if rng.random() < 0.10:  # ~10% sinh viên đã tốt nghiệp/rời đi -> lưu trữ
            sv.luu_tru()
            kich_ban = "cu"
        else:
            kich_ban = rng.choices(["o", "cho", "het_han", "cu", "moi"], weights=[55, 10, 5, 15, 15])[0]

        # Hợp đồng đã kết thúc ở các học kỳ trước (phòng nào cũng được, kể cả phòng nay đã ngừng sử dụng)
        if kich_ban == "cu":
            cac_ky_cu = rng.sample(cac_hk_truoc, rng.randint(1, len(cac_hk_truoc)))
        elif kich_ban in ("o", "cho") and rng.random() < 0.5:
            cac_ky_cu = [cac_hk_truoc[-1]]
        else:
            cac_ky_cu = []
        for hk in cac_ky_cu:
            tao(sv, rng.choice(cac_phong), hk, TrangThaiHopDong.KET_THUC_HOP_DONG)

        if kich_ban == "o":
            phong = _chon_phong_con_cho(rng, cac_phong)
            if phong is not None:  # hết chỗ thì sinh viên này coi như chưa có hợp đồng hiện tại
                hd = tao(sv, phong, hk_hien_tai, TrangThaiHopDong.DA_THANH_TOAN)
                # Cập nhật cả hai phía của quan hệ: phòng có sinh viên VÀ sinh viên biết phòng/hợp đồng của mình
                phong.sinh_vien.append(sv.ma)  # type: ignore[union-attr]
                sv.phong_hien_tai = phong.ma
                sv.hop_dong = hd.ma
        elif kich_ban == "cho":
            phong = _chon_phong_con_cho(rng, cac_phong)
            if phong is not None:
                tao(sv, phong, hk_ke_tiep, TrangThaiHopDong.CHUA_THANH_TOAN, dang_cho=True)
                phong.so_cho_giu += 1  # hợp đồng này đang giữ một chỗ của phòng
        elif kich_ban == "het_han":
            # Quá hạn nên không giữ chỗ: phòng nào cũng được, không tính vào sức chứa
            tao(sv, rng.choice(cac_phong), cac_hk_truoc[-1], TrangThaiHopDong.CHUA_THANH_TOAN)
    return cac_hd


# ---------------------------------------------------------------- hóa đơn, vi phạm, tài khoản
def _sinh_hoa_don(rng: random.Random, cac_phong: list[_KeHoachPhong], hom_nay: date) -> list[HoaDonThang]:
    """
    Hóa đơn 3 tháng gần nhất cho mỗi phòng đang có người ở. Chỉ số điện nước nối tiếp nhau giữa các tháng.
    Tháng cũ phần lớn đã thanh toán; tháng gần nhất còn nhiều hóa đơn chưa thanh toán (để thử thống kê công nợ).
    """
    cau_hinh = CauHinhDong()
    hien_tai = ThangNam.tu_ngay(hom_nay)
    cac_hoa_don: list[HoaDonThang] = []
    for phong in cac_phong:
        if not phong.sinh_vien:
            continue
        dien, nuoc = rng.randint(100, 900), rng.randint(10, 100)  # chỉ số đầu kỳ của tháng đầu tiên
        for so_thang_lui in (3, 2, 1):
            thang_nam = hien_tai.lui(so_thang_lui)
            # hạn chót là ngày N của tháng kế tiếp (lui() chỉ nhận số dương nên tháng gần nhất dùng chính tháng hiện tại)
            thang_han = hien_tai.lui(so_thang_lui - 1) if so_thang_lui > 1 else hien_tai
            dien_moi = dien + rng.randint(40, 120) * len(phong.sinh_vien)  # dùng nhiều người thì tiêu thụ nhiều
            nuoc_moi = nuoc + rng.randint(3, 8) * len(phong.sinh_vien)
            xac_suat_da_tra = 0.5 if so_thang_lui == 1 else 0.9
            da_tra = rng.random() < xac_suat_da_tra
            cac_hoa_don.append(HoaDonThang(
                ma=tao_ma.ma_hoa_don_thang(cac_hoa_don), thang_nam=thang_nam, dien_cu=dien, dien_moi=dien_moi,
                don_gia_dien=cau_hinh.DON_GIA_DIEN, nuoc_cu=nuoc, nuoc_moi=nuoc_moi,
                don_gia_nuoc=cau_hinh.DON_GIA_NUOC, phong=phong.ma,
                han_chot=date(thang_han.nam, thang_han.thang, min(cau_hinh.THOI_HAN_DONG_TIEN_DIEN, 28)),
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
def _thanh_dict(danh_sach: list) -> dict:
    """Đổi danh sách thực thể thành dict {mã: thực thể}, đúng dạng KhoDuLieu và giao thức lưu trữ."""
    return {tt.ma: tt for tt in danh_sach}


def sinh_du_lieu(so_sinh_vien: int = 80, seed: int | None = None, hom_nay: date | None = None,
                 dia_ly: list[Tinh] | None = None, so_vong_bam: int = SO_VONG_MAC_DINH) -> KhoDuLieu:
    """
    Sinh một bộ dữ liệu mẫu hoàn chỉnh trong bộ nhớ (chưa ghi file, xem ghi_du_lieu).

    Tham số:
        - so_sinh_vien: số sinh viên cần sinh (tối thiểu 1).
        - seed: hạt giống ngẫu nhiên; cùng seed (và cùng hom_nay) thì cho đúng cùng một bộ dữ liệu.
        - hom_nay: ngày làm mốc cho học kỳ, hóa đơn, vi phạm (mặc định là ngày hiện tại).
        - dia_ly: danh sách tỉnh/xã thật (từ LuuTruDiaLy) để chọn địa chỉ; None thì dùng vài mã địa chỉ mẫu.
        - so_vong_bam: số vòng băm mật khẩu; giữ mặc định khi dùng thật, chỉ hạ thấp khi cần sinh hàng loạt để test cho nhanh.
    """
    if so_sinh_vien < 1:
        raise ValueError("Số sinh viên phải lớn hơn 0")
    rng = random.Random(seed)
    hom_nay = hom_nay or date.today()

    # Gom địa chỉ thành các cặp (mã tỉnh, mã xã)
    dia_chi = [(t.ma, x.ma) for t in (dia_ly or []) for x in t.danh_sach_xa] or _DIA_CHI_DU_PHONG

    cac_hk = _sinh_hoc_ky(hom_nay)
    cac_dv, cac_ti = _sinh_dich_vu()
    cac_toa, ke_hoach_phong = _lap_ke_hoach_phong(rng, [ti for ti in cac_ti if ti.con_hoat_dong])
    cac_sv = _sinh_sinh_vien(rng, so_sinh_vien, dia_chi)
    cac_hd = _xep_hop_dong(rng, cac_sv, ke_hoach_phong, cac_hk, cac_dv, hom_nay)  # đồng thời xếp sinh viên vào phòng
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

    # Kho dữ liệu của tầng nghiệp vụ dùng dict {mã: thực thể} cho mọi loại
    return KhoDuLieu(
        hoc_ky=_thanh_dict(cac_hk), dich_vu_them=_thanh_dict(cac_dv), tien_ich_phong=_thanh_dict(cac_ti),
        toa_nha=_thanh_dict(cac_toa_nha), phong=_thanh_dict(cac_phong), sinh_vien=_thanh_dict(cac_sv),
        hop_dong=_thanh_dict(cac_hd), hoa_don_thang=_thanh_dict(cac_hoa_don),
        vi_pham=_thanh_dict(_sinh_vi_pham(rng, cac_sv, hom_nay)), tai_khoan=_thanh_dict(_sinh_tai_khoan(cac_sv, so_vong_bam)))


# ---------------------------------------------------------------- ghi xuống file
def ghi_du_lieu(kho: KhoDuLieu) -> None:
    """Ghi toàn bộ dữ liệu xuống du_lieu/ qua các lớp lưu trữ (có kèm file sao lưu). GHI ĐÈ dữ liệu hiện có."""
    from luu_tru import (LuuTruDichVuCoSo, LuuTruHoaDonThang, LuuTruHocKy, LuuTruHopDong, LuuTruPhong,
                         LuuTruSinhVien, LuuTruTaiKhoan, LuuTruToaNha, LuuTruViPham)
    for luu_tru, du_lieu in [(LuuTruHocKy(), kho.hoc_ky), (LuuTruSinhVien(), kho.sinh_vien), (LuuTruPhong(), kho.phong),
                             (LuuTruToaNha(), kho.toa_nha), (LuuTruHopDong(), kho.hop_dong),
                             (LuuTruHoaDonThang(), kho.hoa_don_thang),
                             (LuuTruDichVuCoSo(), kho.dich_vu_co_so()),  # dịch vụ thêm + tiện ích phòng: chung một file
                             (LuuTruViPham(), kho.vi_pham), (LuuTruTaiKhoan(), kho.tai_khoan)]:
        luu_tru.ghi(du_lieu)


def _nap_dia_ly() -> list[Tinh] | None:
    """
    Lấy dữ liệu địa lý thật để sinh mã tỉnh/mã xã: ưu tiên file cục bộ, không có thì tải từ API
    (có thể mất vài giây). Không lấy được gì thì trả None để dùng mã địa chỉ mẫu.
    """
    from luu_tru.luu_tru_dia_ly import LuuTruDiaLy
    luu_tru = LuuTruDiaLy()
    try:
        du_lieu = luu_tru.doc()
    except (FileNotFoundError, ValueError):
        du_lieu = {}
    if du_lieu:
        return list(du_lieu.values())
    print("Chưa có dữ liệu địa lý cục bộ, đang đọc từ sao lưu hoặc tải từ API...")
    try:
        return list(luu_tru.doc_sao_luu().values()) or None
    except (FileNotFoundError, ValueError, OSError):
        return None


def chay(so_sinh_vien: int = 80, seed: int | None = None, cho_phep_ghi_de: bool = False) -> None:
    """Sinh dữ liệu, kiểm chéo bằng tầng nghiệp vụ rồi ghi xuống file. Từ chối nếu đã có dữ liệu mà chưa cho phép ghi đè."""
    from tien_ich import cau_hinh_tinh as cht
    from tien_ich.tap_tin import lay_duong_dan_du_lieu

    cac_file = [cht.FILE_HOC_KY, cht.FILE_SINH_VIEN, cht.FILE_PHONG, cht.FILE_TOA_NHA, cht.FILE_HOP_DONG,
                cht.FILE_HOA_DON_THANG, cht.FILE_DICH_VU_THEM, cht.FILE_VI_PHAM, cht.FILE_TAI_KHOAN]
    da_co = [f for f in cac_file if os.path.exists(lay_duong_dan_du_lieu(f))]
    if da_co and not cho_phep_ghi_de:
        # Bảo vệ dữ liệu thật: chạy nhầm lệnh này sẽ xóa sạch dữ liệu đang có nên phải chủ động thêm --ghi-de
        raise SystemExit(f"Đã có dữ liệu ({', '.join(da_co)}). Thêm --ghi-de nếu muốn thay toàn bộ bằng dữ liệu mẫu.")

    if seed is None:
        seed = random.randrange(1_000_000)  # tự chọn nhưng in ra để có thể tái hiện đúng bộ dữ liệu này
    dia_ly = _nap_dia_ly()
    if dia_ly is None:
        print("Cảnh báo: không có dữ liệu địa lý nên mã tỉnh/mã xã của sinh viên là mã mẫu, không khớp dữ liệu địa lý thật.")
    kho = sinh_du_lieu(so_sinh_vien, seed, dia_ly=dia_ly)
    loi = kiem_cheo_du_lieu(kho)
    if loi:
        raise SystemExit("Dữ liệu sinh ra không qua được kiểm chéo:\n  " + "\n  ".join(loi[:20]))
    ghi_du_lieu(kho)

    dang_o = sum(1 for s in kho.sinh_vien.values() if s.phong_hien_tai)
    print(f"Đã ghi dữ liệu mẫu (seed={seed}): {len(kho.sinh_vien)} sinh viên ({dang_o} đang ở), {len(kho.phong)} phòng, "
          f"{len(kho.toa_nha)} tòa nhà, {len(kho.hoc_ky)} học kỳ, {len(kho.hop_dong)} hợp đồng, {len(kho.hoa_don_thang)} hóa đơn, "
          f"{len(kho.dich_vu_them)} dịch vụ thêm, {len(kho.tien_ich_phong)} tiện ích phòng, {len(kho.vi_pham)} vi phạm, "
          f"{len(kho.tai_khoan)} tài khoản.")
    ma_sv = next((t.ma for t in kho.tai_khoan.values() if not t.co_quyen_quan_tri), None)
    print(f"Đăng nhập thử: {TEN_ADMIN_MAU} / {MAT_KHAU_ADMIN_MAU} (quản trị viên)"
          + (f"; {ma_sv} / {MAT_KHAU_SINH_VIEN_MAU} (sinh viên)" if ma_sv else ""))


if __name__ == "__main__":
    bo_doc = argparse.ArgumentParser(description="Sinh dữ liệu mẫu cho ứng dụng quản lý ký túc xá")
    bo_doc.add_argument("--so-sinh-vien", type=int, default=80, help="số sinh viên cần sinh (mặc định 80)")
    bo_doc.add_argument("--seed", type=int, default=None, help="hạt giống ngẫu nhiên để tái hiện cùng một bộ dữ liệu")
    bo_doc.add_argument("--ghi-de", action="store_true", help="cho phép thay thế dữ liệu hiện có")
    doi_so = bo_doc.parse_args()
    chay(doi_so.so_sinh_vien, doi_so.seed, doi_so.ghi_de)
# Phần C
# Sinh dữ liệu mẫu ngẫu nhiên cho toàn bộ thực thể (SinhVien, Phong, ToaNha, HopDong, HoaDonThang, ViPham, TaiKhoan)
# để kiểm thử sau khi ráp ba tầng.
#
# Điểm quan trọng nhất là dữ liệu phải ĐÚNG RÀNG BUỘC CHÉO (bộ sinh được viết để luôn thỏa các điều kiện này), ví dụ:
#   - hợp đồng thuộc về sinh viên và phòng nào thì sinh viên và phòng đó phải thật sự tồn tại
#   - số hợp đồng đang giữ chỗ (HopDong.con_giu_cho) của mỗi phòng không vượt sức chứa
#   - mỗi sinh viên chỉ giữ chỗ nhiều nhất một hợp đồng cùng lúc
#   - thực thể đã lưu trữ (ngừng hoạt động) không còn hợp đồng đang hiệu lực
#   - mỗi phòng thuộc một tòa nhà có tồn tại, tầng không vượt số tầng của tòa nhà
# Việc kiểm tra lại các điều kiện đó do tầng nghiệp vụ đảm nhiệm: chay() gọi nghiep_vu.kiem_cheo_du_lieu.
#
# Cách dùng:
#   - Trong code:   kho = sinh_du_lieu(so_sinh_vien=80, seed=1);  ghi_du_lieu(kho)
#   - Dòng lệnh:    py -m cong_cu.sinh_du_lieu --so-sinh-vien 80 --seed 1
# Tham số seed cố định thì lần nào chạy cũng ra đúng bộ dữ liệu đó (tiện tái hiện lỗi).
import argparse
import os
import random
from dataclasses import dataclass
from datetime import date, timedelta

from nghiep_vu.kiem_cheo_du_lieu import KhoDuLieu, kiem_cheo_du_lieu
from thuc_the.dia_ly import Tinh
from thuc_the.ky_tuc_xa import Phong, SinhVien, ToaNha
from thuc_the.tai_chinh import HoaDonThang, HopDong, ThangNam, TrangThaiHoaDon, TrangThaiHopDong
from thuc_the.tai_khoan import LoaiTaiKhoan, TaiKhoan
from thuc_the.vi_pham import TrangThaiViPham, ViPham
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
# (mô tả vi phạm, hình thức kỷ luật): gồm cả vi phạm nội quy lẫn vi phạm tài sản
_VI_PHAM = [
    ("Gây ồn sau 23 giờ", "Khiển trách"), ("Về muộn quá giờ quy định", "Nhắc nhở"), ("Nấu ăn trong phòng", "Cảnh cáo"),
    ("Mang người lạ vào phòng", "Cảnh cáo"), ("Không dọn vệ sinh phòng", "Nhắc nhở"),
    ("Làm vỡ kính cửa sổ", "Bồi thường 250.000 đồng"), ("Làm hỏng ổ khóa cửa", "Bồi thường 150.000 đồng"),
    ("Hư quạt trần do sử dụng sai", "Bồi thường 400.000 đồng"), ("Làm hỏng giường tầng", "Bồi thường 800.000 đồng"),
]


@dataclass(frozen=True)
class _KyThue:
    """Một đợt thuê phòng (tương ứng một học kỳ). Chỉ dùng nội bộ để chọn ngày cho hợp đồng, không phải thực thể."""
    ngay_bat_dau: date
    ngay_ket_thuc: date


@dataclass
class _KeHoachPhong:
    """Bản nháp của một phòng trong lúc xếp chỗ. Xếp xong toàn bộ mới dựng Phong thật từ bản nháp này."""
    ma: str
    ten: str
    suc_chua: int
    gia: float  # giá cơ bản cho MỖI người mỗi tháng (Phong.gia_phong = gia * suc_chua)
    ma_toa_nha: str
    tang: int
    hoat_dong: bool = True
    sinh_vien: list[str] | None = None  # sinh viên đang ở (hợp đồng đã thanh toán)
    hop_dong: list[HopDong] | None = None  # mọi hợp đồng của phòng này (kể cả đã kết thúc hay quá hạn)

    def __post_init__(self) -> None:
        self.sinh_vien = []
        self.hop_dong = []

    def con_cho(self, hom_nay: date) -> bool:
        """Còn chỗ khi số hợp đồng đang giữ chỗ chưa chạm sức chứa. Việc "đang giữ chỗ" do HopDong.con_giu_cho(hom_nay) quyết định."""
        return sum(1 for hd in self.hop_dong if hd.con_giu_cho(hom_nay)) < self.suc_chua  # type: ignore[union-attr]


# ---------------------------------------------------------------- các đợt thuê
def _sinh_ky_thue(hom_nay: date) -> list[_KyThue]:
    """
    Bốn đợt thuê xếp từ cũ đến mới:
      [0], [1]: hai đợt đã kết thúc (hợp đồng đã kết thúc, hoặc đăng ký rồi không đóng tiền)
      [2]: đợt hiện tại, tức đợt đầu tiên chưa kết thúc (đang diễn ra, hoặc sắp bắt đầu nếu đang nghỉ giữa hai kỳ)
      [3]: đợt kế tiếp, nơi sinh viên vừa đăng ký và đang giữ chỗ
    Mỗi năm học có HK1 (1/9 - 15/1) và HK2 (1/2 - 15/6).
    """
    cac_ky = []
    for nam in range(hom_nay.year - 2, hom_nay.year + 2):
        cac_ky.append(_KyThue(date(nam, 9, 1), date(nam + 1, 1, 15)))
        cac_ky.append(_KyThue(date(nam + 1, 2, 1), date(nam + 1, 6, 15)))
    vi_tri_hien_tai = next(i for i, k in enumerate(cac_ky) if k.ngay_ket_thuc >= hom_nay)
    return cac_ky[vi_tri_hien_tai - 2: vi_tri_hien_tai + 2]


# ---------------------------------------------------------------- tòa nhà, phòng, sinh viên
def _lap_ke_hoach_phong(rng: random.Random) -> tuple[list[tuple[str, str, int]], list[_KeHoachPhong]]:
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
                cac_phong.append(_KeHoachPhong(
                    ma=tao_ma.ma_phong([p.ma for p in cac_phong]), ten=f"Phòng {ky_hieu}{tang}{stt:02d}",
                    suc_chua=suc_chua, gia=gia_theo_suc_chua[suc_chua], ma_toa_nha=ma_toa, tang=tang,
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
def _chon_phong_con_cho(rng: random.Random, cac_phong: list[_KeHoachPhong], hom_nay: date) -> _KeHoachPhong | None:
    """Chọn phòng đang hoạt động còn chỗ. Ưu tiên (50%) phòng đã có người để có cả phòng đông lẫn phòng trống."""
    con_cho = [p for p in cac_phong if p.hoat_dong and p.con_cho(hom_nay)]
    if not con_cho:
        return None
    da_co_nguoi = [p for p in con_cho if p.sinh_vien]
    return rng.choice(da_co_nguoi if da_co_nguoi and rng.random() < 0.5 else con_cho)


def _ngay_ky_va_het_han(rng: random.Random, ky: _KyThue, hom_nay: date, dang_cho: bool) -> tuple[date, date]:
    """
    Trả về (ngày ký, ngày hết hạn giữ chỗ) thỏa quy tắc của HopDong: ngày ký <= ngày hết hạn <= ngày bắt đầu.
      - dang_cho=True: hợp đồng vừa đăng ký cho đợt SẮP TỚI và còn hạn giữ chỗ: ký trong 10 ngày qua, hết hạn từ hôm
        nay trở đi (nhưng không quá ngày bắt đầu đợt), để HopDong.con_giu_cho là True.
      - dang_cho=False: hợp đồng bình thường ký trước ngày bắt đầu 20-60 ngày, hạn thanh toán là 14 ngày sau khi ký.
    """
    bat_dau = ky.ngay_bat_dau
    if dang_cho:
        ngay_ky = hom_nay - timedelta(days=rng.randint(0, 10))
        ngay_het_han = min(bat_dau, hom_nay + timedelta(days=rng.randint(1, 14)))
    else:
        ngay_ky = bat_dau - timedelta(days=rng.randint(20, 60))
        ngay_het_han = min(bat_dau, ngay_ky + timedelta(days=14))
    return ngay_ky, ngay_het_han


def _tao_hop_dong(rng: random.Random, cac_hd: list[HopDong], sv: SinhVien, phong: _KeHoachPhong, ky: _KyThue,
                  trang_thai: TrangThaiHopDong, hom_nay: date, dang_cho: bool = False) -> HopDong:
    so_ngay = (ky.ngay_ket_thuc - ky.ngay_bat_dau).days
    ngay_ky, ngay_het_han = _ngay_ky_va_het_han(rng, ky, hom_nay, dang_cho)
    return HopDong(
        ma=tao_ma.ma_hop_dong(cac_hd), ngay_ky=ngay_ky, ngay_het_han=ngay_het_han,
        ngay_bat_dau=ky.ngay_bat_dau, ngay_ket_thuc=ky.ngay_ket_thuc, he_so_thang=round(so_ngay / 30),
        gia_phong=phong.gia, tien_dat_coc=phong.gia,  # giá mỗi người mỗi tháng; đặt cọc một tháng
        ma_sinh_vien=sv.ma, ma_phong=phong.ma, trang_thai=trang_thai)


def _xep_hop_dong(rng: random.Random, cac_sv: list[SinhVien], cac_phong: list[_KeHoachPhong],
                  cac_ky: list[_KyThue], hom_nay: date) -> list[HopDong]:
    """
    Mỗi sinh viên rơi vào một kịch bản (cac_ky = [đã kết thúc, đã kết thúc, hiện tại, kế tiếp]):
      - "o"      (~55%): đang ở, hợp đồng ĐÃ THANH TOÁN ở đợt hiện tại (có thể kèm hợp đồng cũ đã kết thúc)
      - "cho"    (~10%): vừa đăng ký đợt KẾ TIẾP, hợp đồng CHƯA THANH TOÁN nhưng còn hạn giữ chỗ, chưa vào ở
      - "het_han" (~5%): đăng ký đợt trước rồi không đóng tiền, hợp đồng CHƯA THANH TOÁN và đã quá hạn (không giữ chỗ)
      - "cu"     (~15%): chỉ có hợp đồng ĐÃ KẾT THÚC ở các đợt trước
      - "moi"    (~15%): chưa có hợp đồng nào
    Sinh viên đã lưu trữ (tốt nghiệp) luôn thuộc kịch bản "cu".
    Mỗi phòng chỉ được xếp thêm khi số hợp đồng đang giữ chỗ (HopDong.con_giu_cho) chưa chạm sức chứa.
    """
    cac_ky_truoc, ky_hien_tai, ky_ke_tiep = cac_ky[:2], cac_ky[2], cac_ky[3]
    cac_hd: list[HopDong] = []

    def tao(sv: SinhVien, phong: _KeHoachPhong, ky: _KyThue, trang_thai: TrangThaiHopDong, dang_cho: bool = False) -> HopDong:
        hd = _tao_hop_dong(rng, cac_hd, sv, phong, ky, trang_thai, hom_nay, dang_cho)
        cac_hd.append(hd)
        phong.hop_dong.append(hd)  # type: ignore[union-attr]  # để con_cho() đếm được bằng HopDong.con_giu_cho
        return hd

    for sv in cac_sv:
        if rng.random() < 0.10:  # ~10% sinh viên đã tốt nghiệp/rời đi -> lưu trữ
            sv.luu_tru()
            kich_ban = "cu"
        else:
            kich_ban = rng.choices(["o", "cho", "het_han", "cu", "moi"], weights=[55, 10, 5, 15, 15])[0]

        # Hợp đồng đã kết thúc ở các đợt trước (phòng nào cũng được, kể cả phòng nay đã ngừng sử dụng)
        if kich_ban == "cu":
            cac_ky_cu = rng.sample(cac_ky_truoc, rng.randint(1, len(cac_ky_truoc)))
        elif kich_ban in ("o", "cho") and rng.random() < 0.5:
            cac_ky_cu = [cac_ky_truoc[-1]]
        else:
            cac_ky_cu = []
        for ky in cac_ky_cu:
            tao(sv, rng.choice(cac_phong), ky, TrangThaiHopDong.KET_THUC_HOP_DONG)

        if kich_ban == "o":
            phong = _chon_phong_con_cho(rng, cac_phong, hom_nay)
            if phong is not None:  # hết chỗ thì sinh viên này coi như chưa có hợp đồng hiện tại
                tao(sv, phong, ky_hien_tai, TrangThaiHopDong.DA_THANH_TOAN)
                # SinhVien không còn ghi phòng/hợp đồng của mình (quan hệ nằm ở HopDong); bản nháp phòng chỉ nhớ
                # người đang ở để biết phòng nào có người mà lập hóa đơn
                phong.sinh_vien.append(sv.ma)  # type: ignore[union-attr]
        elif kich_ban == "cho":
            phong = _chon_phong_con_cho(rng, cac_phong, hom_nay)
            if phong is not None:
                tao(sv, phong, ky_ke_tiep, TrangThaiHopDong.CHUA_THANH_TOAN, dang_cho=True)
        elif kich_ban == "het_han":
            # Quá hạn nên không giữ chỗ: phòng nào cũng được, không tính vào sức chứa
            tao(sv, rng.choice(cac_phong), cac_ky_truoc[-1], TrangThaiHopDong.CHUA_THANH_TOAN)
    return cac_hd


# ---------------------------------------------------------------- hóa đơn, vi phạm, tài khoản
def _sinh_hoa_don(rng: random.Random, cac_phong: list[_KeHoachPhong], hom_nay: date) -> list[HoaDonThang]:
    """
    Hóa đơn 3 tháng gần nhất cho mỗi phòng đang có người ở. Chỉ số điện nước nối tiếp nhau giữa các tháng.
    Tháng cũ phần lớn đã thanh toán; tháng gần nhất còn nhiều hóa đơn chưa thanh toán.
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
        mo_ta, hinh_thuc = rng.choice(_VI_PHAM)
        da_xu_ly = rng.random() < 0.5
        cac_vp.append(ViPham(
            ma=tao_ma.ma_vi_pham(cac_vp), sinh_vien=sv.ma, ngay_vi_pham=ngay, mo_ta=mo_ta, hinh_thuc_ky_luat=hinh_thuc,
            trang_thai=TrangThaiViPham.DA_XU_LY if da_xu_ly else TrangThaiViPham.CHUA_XU_LY))
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
        - hom_nay: ngày làm mốc cho hợp đồng, hóa đơn, vi phạm và cho HopDong.con_giu_cho(hom_nay)
          (mặc định là ngày hiện tại; không cần đúng ngày chạy, miễn là cả bộ dữ liệu bám cùng một mốc).
        - dia_ly: danh sách tỉnh/xã thật (từ LuuTruDiaLy) để chọn địa chỉ; None thì dùng vài mã địa chỉ mẫu.
        - so_vong_bam: số vòng băm mật khẩu; giữ mặc định khi dùng thật, chỉ hạ thấp khi cần sinh hàng loạt để test cho nhanh.
    """
    if so_sinh_vien < 1:
        raise ValueError("Số sinh viên phải lớn hơn 0")
    rng = random.Random(seed)
    hom_nay = hom_nay or date.today()

    # Gom địa chỉ thành các cặp (mã tỉnh, mã xã)
    dia_chi = [(t.ma, x.ma)
    for t in (dia_ly.values() 
              if isinstance(dia_ly, dict) 
              else 
                (dia_ly or []))
    for x in t.danh_sach_xa.values()
    ] or _DIA_CHI_DU_PHONG

    cac_ky = _sinh_ky_thue(hom_nay)
    cac_toa, ke_hoach_phong = _lap_ke_hoach_phong(rng)
    cac_sv = _sinh_sinh_vien(rng, so_sinh_vien, dia_chi)
    cac_hd = _xep_hop_dong(rng, cac_sv, ke_hoach_phong, cac_ky, hom_nay)  # đồng thời gán phòng/hợp đồng cho sinh viên
    cac_hoa_don = _sinh_hoa_don(rng, ke_hoach_phong, hom_nay)

    # Xếp chỗ xong mới dựng Phong và ToaNha thật từ bản nháp
    cac_phong = []
    for p in ke_hoach_phong:
        phong = Phong(ma=p.ma, ten=p.ten, suc_chua=p.suc_chua, gia_phong=p.gia * p.suc_chua, toa_nha=p.ma_toa_nha, tang=p.tang)
        if not p.hoat_dong:
            phong.luu_tru()
        cac_phong.append(phong)
    cac_toa_nha = [ToaNha(ma=ma, ten=ten, so_tang=so_tang) for ma, ten, so_tang in cac_toa]

    # Kho dữ liệu của tầng nghiệp vụ dùng dict {mã: thực thể} cho mọi loại
    return KhoDuLieu(
        toa_nha=_thanh_dict(cac_toa_nha), phong=_thanh_dict(cac_phong), sinh_vien=_thanh_dict(cac_sv),
        hop_dong=_thanh_dict(cac_hd), hoa_don_thang=_thanh_dict(cac_hoa_don),
        vi_pham=_thanh_dict(_sinh_vi_pham(rng, cac_sv, hom_nay)), tai_khoan=_thanh_dict(_sinh_tai_khoan(cac_sv, so_vong_bam)))


# ---------------------------------------------------------------- ghi xuống file
def ghi_du_lieu(kho: KhoDuLieu) -> None:
    """Ghi toàn bộ dữ liệu xuống du_lieu/ qua các lớp lưu trữ (có kèm file sao lưu). GHI ĐÈ dữ liệu hiện có."""
    from luu_tru import (LuuTruHoaDonThang, LuuTruHopDong, LuuTruPhong, LuuTruSinhVien,
                         LuuTruTaiKhoan, LuuTruToaNha, LuuTruViPham)
    for luu_tru, du_lieu in [(LuuTruSinhVien(), kho.sinh_vien), (LuuTruPhong(), kho.phong), (LuuTruToaNha(), kho.toa_nha),
                             (LuuTruHopDong(), kho.hop_dong), (LuuTruHoaDonThang(), kho.hoa_don_thang),
                             (LuuTruViPham(), kho.vi_pham), (LuuTruTaiKhoan(), kho.tai_khoan)]:
        luu_tru.ghi(du_lieu)


def _kiem_tra_tai_khoan_mau(kho: KhoDuLieu) -> list[str]:
    """Chắc chắn các tài khoản đăng nhập thử in ra ở cuối thực sự dùng được, bằng chính TaiKhoan.kiem_tra()."""
    loi = []
    admin = kho.tai_khoan.get(TEN_ADMIN_MAU)
    if admin is None or not admin.kiem_tra(MAT_KHAU_ADMIN_MAU):
        loi.append(f"Tài khoản {TEN_ADMIN_MAU} không đăng nhập được bằng mật khẩu mẫu")
    for tk in kho.tai_khoan.values():
        if not tk.co_quyen_quan_tri and not tk.kiem_tra(MAT_KHAU_SINH_VIEN_MAU):
            loi.append(f"Tài khoản {tk.ma} không đăng nhập được bằng mật khẩu mẫu")
    return loi


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

    cac_file = [cht.FILE_SINH_VIEN, cht.FILE_PHONG, cht.FILE_TOA_NHA, cht.FILE_HOP_DONG,
                cht.FILE_HOA_DON_THANG, cht.FILE_VI_PHAM, cht.FILE_TAI_KHOAN]
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
    loi += _kiem_tra_tai_khoan_mau(kho)
    if loi:
        raise SystemExit("Dữ liệu sinh ra không qua được kiểm chéo:\n  " + "\n  ".join(loi[:20]))
    ghi_du_lieu(kho)

    # "Đang ở" suy ra từ hợp đồng: có hợp đồng đã thanh toán và còn giữ chỗ
    dang_o = len({hd.ma_sinh_vien for hd in kho.hop_dong.values() if hd.trang_thai == TrangThaiHopDong.DA_THANH_TOAN and hd.con_giu_cho()})
    print(f"Đã ghi dữ liệu mẫu (seed={seed}): {len(kho.sinh_vien)} sinh viên ({dang_o} đang ở), {len(kho.phong)} phòng, "
          f"{len(kho.toa_nha)} tòa nhà, {len(kho.hop_dong)} hợp đồng, {len(kho.hoa_don_thang)} hóa đơn, "
          f"{len(kho.vi_pham)} vi phạm, {len(kho.tai_khoan)} tài khoản.")
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
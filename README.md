# Quản Lý Ký Túc Xá

File này giải thích kiến trúc tổng thể của dự án và liệt kê chi tiết các tính năng cần triển khai cho Phần A giao diện và Phần C lưu trữ và tiện ích dựa trên khung mã nguồn.

## 1. Tổng quan

Đây là ứng dụng quản lý ký túc xá, bao gồm các tính năng chính: quản lý sinh viên, phòng, tòa nhà, hợp đồng thuê, hóa đơn điện nước hàng tháng, dịch vụ thêm, vi phạm nội quy/tài sản, và tài khoản đăng nhập (quản trị viên hoặc sinh viên).

Dự án được chia thành 3 phần công việc, ứng với 3 người:

* Phần A: Giao diện người dùng.
* Phần B: Thực thể và nghiệp vụ (điều phối, xử lý logic, ràng buộc dữ liệu).
* Phần C: Lưu trữ dữ liệu, quản lý tài khoản và các tiện ích hỗ trợ.

## 2. Kiến trúc tổng thể

Dự án áp dụng kiến trúc phân tầng, các tầng không phụ thuộc trực tiếp vào nhau mà giao tiếp thông qua các giao thức được định nghĩa trong thư mục `giao_thuc/`.

Sơ đồ luồng phụ thuộc:

```
     ┌────────────────────────────── Tầng giao diện <──── giao_dien (triển khai cụ thể - phần A)
     │      sử dụng                         |
     ↓                                      | gọi
┌──────────┐                                |
│ tien_ich │                                v
│    &     │ <──────────── GiaoThucDieuPhoi / GiaoThucPhienLamViec  <────  nghiep_vu (triển khai cụ thể - phần B, C)
│ thuc_the │   sử dụng                      |
└──────────┘                                | gọi
     ↑                                      |
     │      sử dụng                         v
     └─────────────────────────────── GiaoThucLuuTru  <────  luu_tru (triển khai cụ thể - phần C)
```

* `giao_dien` (Phần A) chỉ gọi các phương thức đã định nghĩa trong `GiaoThucDieuPhoi` và `GiaoThucPhienLamViec`, không được gọi thẳng `luu_tru`.
* `nghiep_vu` (Phần B) triển khai cụ thể `GiaoThucDieuPhoi` để xử lý toàn bộ logic nghiệp vụ và kiểm tra dữ liệu chéo giữa các thực thể.
* `luu_tru` (Phần C) triển khai cụ thể `GiaoThucLuuTru` để thực hiện đọc/ghi dữ liệu xuống file và đảm bảo dữ liệu không hỏng/mất.

Ba người có thể phát triển song song: A dựng giao diện dựa trên các hàm có sẵn (nếu B chưa code xong thì có thể dùng dữ liệu giả), C viết phần đọc ghi độc lập, B ráp nối logic ở giữa.

## 3. Cấu trúc thư mục

```
Dự án
├── main.py                      Điểm khởi động ứng dụng
├── giao_dien/                   Giao diện người dùng (A)
├── giao_thuc/
│   ├── luu_tru.py               Giao thức GiaoThucLuuTru (B)
│   │
│   └── nghiep_vu.py             Giao thức GiaoThucDieuPhoi (B) và GiaoThucPhienLamViec (C)
│
├── thuc_the/                    Phần B — định nghĩa các class thực thể
│   │
│   ├── thuc_the_goc.py          Các class cơ sở dùng chung (xem mục 4)
│   │
│   ├── dia_ly.py                Xa, Tinh
│   │
│   ├── hoc_vu.py                HocKy
│   │
│   ├── ky_tuc_xa.py             SinhVien, Phong, ToaNha
│   │
│   ├── tai_chinh.py             DichVuThem, HopDong, HoaDonThang
│   │
│   ├── tai_khoan.py             TaiKhoan, LoaiTaiKhoan
│   │
│   └── vi_pham.py               ViPham, ViPhamNoiQuy, ViPhamTaiSan
│
├── nghiep_vu/                   Phần B, C — triển khai cụ thể GiaoThucDieuPhoi và GiaoThucPhienLamViec
│
├── luu_tru/                     Phần C — triển khai cụ thể GiaoThucLuuTru cho từng loại thực thể
│
├── du_lieu/                     Phần C — chứa các file dữ liệu JSON khi chạy app
│
└── tien_ich/                    Phần C — các hàm và cấu hình dùng chung
    │
    ├── cau_hinh_tinh.py         Cấu hình tĩnh: tên app, kích thước cửa sổ, font, theme, tên file dữ liệu
    │
    ├── cau_hinh_dong.py         Cấu hình động: đơn giá điện nước, sức chứa phòng mặc định,... 
    │
    ├── regex.py                 Các hàm kiểm tra tính hợp lệ dữ liệu, dùng bởi giao diện và nghiệp vụ
    │
    ├── tao_ma.py                Sinh mã định danh tự động cho từng loại thực thể
    │
    ├── tap_tin.py               Xác định đường dẫn file dữ liệu, quản lý thư mục sao lưu ẩn
    │
    └── sinh_du_lieu.py          Sinh dữ liệu mẫu để kiểm thử
```

## 4. Mô hình thực thể cơ sở

Ba class trong `thuc_the/thuc_the_goc.py` dùng để làm class cơ sở cho toàn bộ thực thể, mỗi class phụ trách một phần riêng:

* `ThucTheGoc`: mọi thực thể đều có `ma` (mã định danh duy nhất) và so sánh bằng nhau qua `ma` (`__eq__`).
* `ThucTheCoTen`: bổ sung thuộc tính `ten` cho các thực thể có tên (kế thừa thêm từ `ThucTheGoc`).
* `ThucTheLuuTruDuoc`: bổ sung khả năng lưu trữ/ngừng hoạt động (`luu_tru`, `tai_kich_hoat`, `con_hoat_dong`) cho các thực thể có thể bị xóa mềm thay vì xóa hẳn (sinh viên tốt nghiệp, phòng ngừng sử dụng...).

Một thực thể cụ thể sẽ kế thừa các class phù hợp, ví dụ `SinhVien(ThucTheCoTen, ThucTheLuuTruDuoc)` vừa có tên vừa lưu trữ được, còn `HopDong(ThucTheGoc)` chỉ có mã không tên và không lưu trữ được (vì hợp đồng dùng trạng thái riêng qua `TrangThaiHopDong`).

## 5. Quy trình làm việc với Git

### 5.1. Quy tắc chung
* Không đẩy code trực tiếp lên nhánh `main`. Nhánh `main` luôn phải chạy được và không chứa code đang viết dở.
* Mỗi tính năng hoặc nhiệm vụ nhỏ được làm trên một nhánh riêng, tạo ra từ `main` mới nhất, và chỉ gộp lại vào `main` thông qua pull request trên GitHub.

### 5.2. Đặt tên nhánh
Đặt tên nhánh theo mẫu `phan-<a|c>/<mo-ta-ngan-khong-dau>`, ví dụ:
* `phan-a/man-hinh-dang-nhap`
* `phan-c/luu-tru-sinh-vien`

### 5.3. Các bước thực hiện trên VS Code / PyCharm
1. **Đồng bộ code:** Sang nhánh `main` và nhấn nút `Pull` / `Fetch` để lấy code mới nhất về máy.
2. **Tạo nhánh mới:** Trong mục source control của phần mềm, chọn `Create Branch` từ `main` rồi đặt tên theo quy tắc.
3. **Commit code:** Viết code cho tính năng, tick chọn các file thay đổi, ghi mô tả ngắn gọn (ví dụ: "Thêm form đăng nhập") và nhấn `Commit`.
4. **Đẩy code:** Nhấn `Publish Branch` hoặc `Push` để đẩy nhánh lên GitHub.
5. **Gộp code:** Lên trang GitHub của dự án, bấm nút `Compare & pull request`. Tag tui xem qua trước khi xác nhận gộp vào `main`.
6. **Dọn dẹp:** Gộp xong rồi muốn thì (nên) xóa nhánh vừa làm trên GitHub và trên máy cá nhân cho project gọn.

### 5.4. Xử lý xung đột
* Thường xuyên cập nhật code: chuyển sang nhánh `main` để kéo code mới về rồi chuyển lại nhánh đang làm và chọn tính năng `Merge main into current branch` trên IDE.
* Nếu IDE báo xung đột thì mở các file bị đánh dấu đỏ tìm các chỗ xung đột rồi chọn `Accept Current Change` để giữ code của mình hoặc `Accept Incoming Change` để lấy code mới, xong rồi thì commit và push lại.

## 6. Việc cần triển khai — Phần A giao diện

Toàn bộ màn hình chỉ được sử dụng `GiaoThucDieuPhoi` (nghiệp vụ) và `GiaoThucPhienLamViec` (đăng nhập, phiên làm việc). Danh sách công việc chính:

### 6.1. Đăng nhập và tài khoản
* Màn hình đăng nhập (gọi `dang_nhap`), báo lỗi khi sai mật khẩu hoặc đã đăng nhập.
* Chức năng đăng xuất (`dang_xuat`).
* Màn hình đổi mật khẩu cho tài khoản hiện tại (`doi_mat_khau` không kèm `tai_khoan`).
* Màn hình quản trị viên tạo tài khoản mới (`tao_tai_khoan`) và reset mật khẩu tài khoản khác (`doi_mat_khau` có kèm `tai_khoan`).
* Ẩn/hiện chức năng theo `co_quyen_quan_tri` của tài khoản đang đăng nhập.

### 6.2. Quản lý danh mục (áp dụng cho từng loại trong 8 loại thực thể)

Với mỗi loại: SinhVien, Phong, ToaNha, HopDong, HoaDonThang, DichVuThem, ViPham, TaiKhoan, cần có:
* Màn hình danh sách thì gọi `lay_tat_ca` hoặc `loc_theo_dieu_kien` để tìm kiếm/lọc.
* Màn hình xem chi tiết một thực thể (`lay_theo_ma`).
* Form thêm mới thì gọi `them`, hiện lỗi trả về khi dữ liệu không hợp lệ hoặc vi phạm ràng buộc chéo.
* Form chỉnh sửa thì gọi `cap_nhat`.
* Với thực thể lưu trữ được (SinhVien, Phong, ToaNha, DichVuThem): nút lưu trữ/tái kích hoạt thay cho xóa hẳn (`luu_tru`, `tai_kich_hoat`), và một lựa chọn xóa hẳn có xác nhận rõ ràng khi cần (`xoa`, cân nhắc tham số `ep_xoa`).
* Nhập địa chỉ thường trú của sinh viên cần dùng `danh_sach_dia_ly` để hiển thị danh sách tỉnh/xã dạng chọn lựa (dropdown liên động tỉnh → xã).

### 6.3. Thao tác nghiệp vụ riêng
* Thanh toán hợp đồng (`thanh_toan_hop_dong`) để thêm sinh viên vào phòng.
* Kết thúc hợp đồng (`ket_thuc_hop_dong`) để sửa thuộc tính phòng và sinh viên liên quan.
* Thanh toán hóa đơn tháng (`thanh_toan_hoa_don_thang`).
* Xử lý vi phạm (`xu_ly_vi_pham`).

### 6.4. Thống kê
* Màn hình thống kê số phòng trống/đã thuê/tổng số theo tòa nhà và loại phòng (`thong_ke_so_phong`), có thể lọc theo học kỳ, tòa nhà, loại phòng.
* Màn hình tỷ lệ lấp đầy (`thong_ke_ty_le_lap_day`), nên hiển thị dạng phần trăm hoặc biểu đồ.
* Màn hình công nợ (`thong_ke_cong_no`) để hiển thị tổng tiền nợ và số sinh viên đang nợ.

### 6.5. Cài đặt
* Màn hình gọi `cap_nhat_cau_hinh` và `doc_cau_hinh` để đổi giao diện theo `CauHinhChuDe` (DARK, GREY, LIGHT) và các thông số trong `CauHinhDong` (đơn giá điện, nước, sức chứa phòng mặc định, hạn mức nợ...).

### 6.6. Lưu ý khi triển khai
* Toàn bộ input người dùng cần kiểm tra hợp lệ ngay tại tầng giao diện bằng các hàm trong `tien_ich/regex.py` trước khi gửi xuống tầng nghiệp vụ, để báo lỗi ngay tại form thay vì đợi lỗi ném từ tầng dưới.

## 7. Việc cần triển khai — Phần C lưu trữ và tiện ích

### 7.1. Cài đặt GiaoThucLuuTru cho từng loại thực thể

Cần class cài đặt cụ thể `GiaoThucLuuTru[T]` cho 8 loại thực thể (SinhVien, Phong, ToaNha, HopDong, HoaDonThang, DichVuThem, ViPham, TaiKhoan) cần:
* `doc`: đọc danh sách thực thể từ file JSON tương ứng (tên file đã định nghĩa sẵn trong `tien_ich/cau_hinh_tinh.py`), trả về danh sách rỗng nếu file chưa tồn tại, ném `ValueError` nếu file hỏng hoặc dữ liệu mất đồng bộ.
* `ghi`: ghi danh sách thực thể xuống file dữ liệu và file sao lưu, hỗ trợ cả ghi đè và ghi thêm.
* `doc_sao_luu`: đọc từ file sao lưu, chỉ dùng khi file chính hỏng.
* `co_bi_chinh_sua`: kiểm tra file dữ liệu có bị sửa ngoài ứng dụng hay không, bằng cách lưu một dấu thời gian vào một file riêng trong thư mục `.sao_luu` ngay sau mỗi lần ghi, rồi so sánh lại dấu thời gian đó khi đọc dữ liệu. Chỉ cần thực hiện kiểm tra này một lần khi ứng dụng khởi động, không cần theo dõi liên tục trong lúc ứng dụng đang chạy.
* `loai_thuc_the`: trả về loại thực thể mà class đang phụ trách.

Lưu ý riêng cho `ViPham`: class này có hai class con (`ViPhamNoiQuy`, `ViPhamTaiSan`) với thuộc tính riêng. Khi ghi JSON cần lưu kèm thông tin phân loại cụ thể (`ViPhamNoiQuy` hoặc `ViPhamTaiSan`), và khi đọc lại phải dựng đúng loại tương ứng thay vì dựng chung một kiểu `ViPham`.

### 7.2. Địa lý
* Gọi API ngoài (`https://provinces.open-api.vn/`) để lấy danh sách tỉnh và các xã trực thuộc, phục vụ `danh_sach_dia_ly`.
* Theo đúng thiết kế trong `giao_thuc/luu_tru.py`: nếu cả file dữ liệu và file sao lưu cục bộ hỏng thì đọc trực tiếp từ API.

### 7.3. Cấu hình động
* Triển khai `cap_nhat_cau_hinh` và `doc_cau_hinh`, đọc/ghi đối tượng `CauHinhDong` xuống một file JSON riêng, tách biệt với dữ liệu nghiệp vụ.

### 7.4. Phiên làm việc và tài khoản
* `tai_khoan_hien_tai`: theo dõi tài khoản đang đăng nhập trong phiên hiện tại.
* `tao_tai_khoan`: tạo tài khoản mới, băm mật khẩu trước khi lưu chứ không lưu thẳng mật khẩu người dùng nhập.
* `dang_nhap`/`dang_xuat`: xác thực bằng cách so khớp mật khẩu đã băm, quản lý trạng thái đăng nhập.
* `doi_mat_khau`: xử lý cả hai trường hợp tự đổi mật khẩu (yêu cầu mật khẩu cũ) và quản trị viên reset mật khẩu người khác (yêu cầu quyền quản trị, không cần mật khẩu cũ).

### 7.5. Tiện ích
* `tao_ma.py`: viết bộ sinh mã riêng cho từng loại thực thể và phải kiểm tra trùng lặp với danh sách hiện tại nếu được truyền vào.
* `regex.py`: hoàn thiện các hàm kiểm tra đang trả về `True` và phải khớp với định dạng mã do `tao_ma.py` sinh ra.
* `tap_tin.py`: xác định đường dẫn thư mục dữ liệu đúng trong cả môi trường chạy mã nguồn lẫn môi trường đã đóng gói thành file thực thi và phải tạo thư mục ẩn `.sao_luu` để chứa các file sao lưu.
* `sinh_du_lieu.py`: sinh dữ liệu mẫu ngẫu nhiên cho toàn bộ 8 loại thực thể, đảm bảo đúng ràng buộc chéo giữa chúng (ví dụ: sinh viên có mã phòng thì phòng đó phải thật sự tồn tại và có sinh viên đó trong danh sách) để kiểm thử sau khi các phần được tích hợp.

## 8. Cơ chế lắp ráp tại `main.py`

File `main.py` là nơi duy nhất trong dự án biết sự tồn tại của cả 3 tầng. Để đảm bảo các tầng không bị dính chặt vào nhau, dự án này xài kỹ thuật **Tiêm phụ thuộc**. 

Hàm khởi tạo của tầng cấp cao sẽ yêu cầu truyền vào một đối tượng thuộc giao thức của tầng thấp hơn. 

Dưới đây là mã giả minh họa cách `main.py` sẽ ráp code của 3 người lại với nhau:

```python
# main.py

# Import các lớp triển khai CỤ THỂ của cả 3 phần
from luu_tru.luu_tru_sinh_vien import LuuTruSinhVien
# ... (import các class lưu trữ khác)
from nghiep_vu.dieu_phoi import DieuPhoiNghiepVu
from giao_dien.ung_dung import UngDungGUI

def main():
    # BƯỚC 1: Khởi tạo các đối tượng của Phần C
    # Các đối tượng này triển khai GiaoThucLuuTru
    luu_tru_sv = LuuTruSinhVien()
    # luu_tru_phong = LuuTruPhong()
    # ...

    # BƯỚC 2: Khởi tạo đối tượng của Phần B
    # Tầng nghiệp vụ yêu cầu truyền vào các đối tượng lưu trữ thông qua hàm khởi tạo
    # Phần B có thể gọi xuống Phần C thông qua giao thức
    he_thong_nghiep_vu = DieuPhoiNghiepVu(
        luu_tru_sinh_vien=luu_tru_sv,
        # luu_tru_phong=luu_tru_phong,
        # ...
    )

    # BƯỚC 3: Khởi tạo đối tượng của Phần A
    # Tầng giao diện yêu cầu truyền vào đối tượng nghiệp vụ (GiaoThucDieuPhoi / GiaoThucPhienLamViec)
    app = UngDungGUI(dieu_phoi=he_thong_nghiep_vu)

    # BƯỚC 4: Chạy ứng dụng
    app.chay_ung_dung()

if __name__ == "__main__":
    main()
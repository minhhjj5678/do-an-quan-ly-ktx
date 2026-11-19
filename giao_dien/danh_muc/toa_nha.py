from thuc_the.ky_tuc_xa import ToaNha
from .danh_muc_co_so import ManHinhDanhMucCoSo


class ManHinhToaNha(ManHinhDanhMucCoSo):
    LOAI = ToaNha
    TIEU_DE = 'Quản lý tòa nhà'
    MO_TA = 'Theo dõi thông tin các tòa nhà trong ký túc xá.'
    CO_LUU_TRU = True

    # Không khai báo TRUONG và BAT_BUOC thủ công.
    # Lớp cha sẽ đọc trực tiếp tên tham số từ ToaNha.__init__,
    # nhờ đó GUI gửi đúng tên keyword mà constructor thực sự nhận.

    @staticmethod
    def ten_truong(truong):
        if truong == 'ten':
            return 'Tên tòa nhà'
        return ManHinhDanhMucCoSo.ten_truong(truong)

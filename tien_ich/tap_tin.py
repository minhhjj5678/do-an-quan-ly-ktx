# Phần C
# Làm 2 việc
# 1. Xác định đường dẫn hiện tại của các file json để app hoạt dộng trong môi trường mã nguồn lẫn môi trường đóng gói
# 2. Tạo thư mục ẩn .sao_luu để lưu trữ các file json phòng trường hợp dữ liệu bị hỏng ngoài ý muốn


import os

DANG_TRONG_THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_DU_LIEU = os.path.join(DANG_TRONG_THU_MUC_GOC, "du_lieu")
THU_MUC_SAO_LUU = os.path.join(THU_MUC_DU_LIEU, ".sao_luu")

# Tự động tạo thư mục dữ liệu và thư mục ẩn .sao_luu nếu chưa có
os.makedirs(THU_MUC_DU_LIEU, exist_ok=True)
os.makedirs(THU_MUC_SAO_LUU, exist_ok=True)

def lay_duong_dan_du_lieu(ten_file: str) -> str:
    return os.path.join(THU_MUC_DU_LIEU, ten_file)

def lay_duong_dan_sao_luu(ten_file: str) -> str:
    return os.path.join(THU_MUC_SAO_LUU, ten_file)
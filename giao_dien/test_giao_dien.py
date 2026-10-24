import os
import sys

# Lấy thư mục cha của giao_dien
thu_muc_hien_tai = os.path.dirname(os.path.abspath(__file__))
thu_muc_goc = os.path.dirname(thu_muc_hien_tai)

# Thêm thư mục gốc vào đường dẫn import
if thu_muc_goc not in sys.path:
    sys.path.insert(0, thu_muc_goc)

from giao_dien.app import App
from giao_dien.mock_backend import MockDieuPhoi, MockPhien


def main():
    dieu_phoi = MockDieuPhoi()
    phien = MockPhien()

    app = App(dieu_phoi, phien)
    app.mainloop()


if __name__ == "__main__":
    main()
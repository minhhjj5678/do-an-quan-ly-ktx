from thuc_the.thuc_the_goc import ThucTheCoTen


class Xa(ThucTheCoTen):
    def __init__(self, ma: str, ten: str):
        super().__init__(ma, ten)


class Tinh(ThucTheCoTen):
    def __init__(self, ma: str, ten: str, danh_sach_xa: list[Xa]):
        super().__init__(ma, ten)
        self.__danh_sach_xa = danh_sach_xa

    @property
    def danh_sach_xa(self) -> list[Xa]:
        return self.__danh_sach_xa.copy()
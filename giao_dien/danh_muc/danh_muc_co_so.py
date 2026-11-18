"""Màn hình danh mục dùng chung: giao diện, tìm kiếm và CRUD qua Adapter.

Các màn hình con chỉ cần khai báo LOAI, TRUONG, BAT_BUOC.
Nếu chưa biết tên trường, chương trình đọc các tham số của __init__.
"""
import inspect
import tkinter as tk
from datetime import date, datetime
from enum import Enum
from tkinter import ttk, messagebox
from typing import get_type_hints, get_origin, get_args

from thuc_the.thuc_the_goc import ThucTheGoc
from ..dung_chung.ho_tro import hien_thi
from ..dung_chung.mau_sac import lay_mau


class ManHinhDanhMucCoSo(ttk.Frame):
    LOAI: type[ThucTheGoc] = ThucTheGoc
    TIEU_DE = ''
    MO_TA = 'Xem, tìm kiếm và cập nhật thông tin dễ dàng.'
    TRUONG = []
    BAT_BUOC = []
    TRUONG_CHI_DOC_KHI_SUA = set()
    CO_LUU_TRU = False
    CHO_PHEP_XOA = True
    CHO_PHEP_SUA = True
    TRUONG_CHI_DOC_KHI_TAO = {"trang_thai"}
    NGHIEP_VU_CHI_TIET: tuple[tuple[str, str], ...] = ()  # (Tên nút, tên nghiệp vụ Adapter)

    def __init__(self, parent, adapter):
        super().__init__(parent, padding=12)
        self.adapter = adapter
        self.hien_luu_tru = tk.BooleanVar(master=self, value=False)
        self._tham_so = inspect.signature(self.LOAI.__init__).parameters
        try:
            self._kieu_truong = get_type_hints(self.LOAI.__init__)
        except (NameError, TypeError):
            self._kieu_truong = {}
        if not self.TRUONG:
            self.TRUONG = [t for t, p in self._tham_so.items()
                           if t != 'self' and p.kind in (
                               inspect.Parameter.POSITIONAL_ONLY,
                               inspect.Parameter.POSITIONAL_OR_KEYWORD,
                               inspect.Parameter.KEYWORD_ONLY)]
        if not self.BAT_BUOC:
            self.BAT_BUOC = [t for t, p in self._tham_so.items()
                             if t not in ('self', 'ma')
                             and p.default is inspect.Parameter.empty
                             and p.kind not in (inspect.Parameter.VAR_KEYWORD,
                                                 inspect.Parameter.VAR_POSITIONAL)]
        self.tao_giao_dien()
        self.tai_du_lieu()

    def _tao_kieu_nut(self):
        mau = lay_mau(getattr(self.winfo_toplevel(), 'chu_de_hien_tai', 'LIGHT'))
        style = ttk.Style(self)
        style.configure('KTX.Primary.TButton', background=mau['chinh'],
                        foreground='white', padding=(13, 9),
                        font=('Segoe UI', 10, 'bold'))
        style.map('KTX.Primary.TButton',
                  background=[('active', mau['chinh_dam'])],
                  foreground=[('active', 'white')])
        style.configure('KTX.Light.TButton', padding=(12, 8),
                        background=mau['nut'], foreground=mau['chu'])
        la_toi = getattr(self.winfo_toplevel(), 'chu_de_hien_tai', 'LIGHT') == 'DARK'
        style.configure('KTX.Danger.TButton',
                        background='#673A41' if la_toi else '#FFF0ED',
                        foreground='#FFFFFF' if la_toi else '#A93E38',
                        padding=(12, 8))
        style.map('KTX.Danger.TButton',
                  background=[('active', '#8A454C' if la_toi else '#FAD9D3')],
                  foreground=[('active', '#FFFFFF' if la_toi else '#A93E38')])
        style.configure('KTX.Treeview', rowheight=34,
                        font=('Segoe UI', 10),
                        background=mau['the'], fieldbackground=mau['the'],
                        foreground=mau['chu'])
        style.configure('KTX.Treeview.Heading',
                        font=('Segoe UI', 10, 'bold'), padding=(9, 9),
                        background=mau['nhat'], foreground=mau['chu'])
        style.map('KTX.Treeview', background=[('selected', mau['chon'])],
                  foreground=[('selected', mau['chu'])])

    def cap_nhat_mau(self):
        """Đổi màu bảng nếu người dùng đổi chủ đề."""
        self._tao_kieu_nut()
        if hasattr(self, 'bang'):
            mau = lay_mau(getattr(self.winfo_toplevel(), 'chu_de_hien_tai', 'LIGHT'))
            self.bang.tag_configure('chan', background=mau['the'], foreground=mau['chu'])
            self.bang.tag_configure('le', background=mau['nhat'], foreground=mau['chu'])

    def tao_giao_dien(self):
        self._tao_kieu_nut()
        ten = self.TIEU_DE or f'Quản lý {self.LOAI.__name__}'
        dau = tk.Frame(self, bg='#207B68', padx=20, pady=17)
        dau.pack(fill='x', pady=(0, 12))
        tk.Label(dau, text=ten, bg='#207B68', fg='white',
                 font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        tk.Label(dau, text=self.MO_TA, bg='#207B68', fg='#DBF3EB',
                 font=('Segoe UI', 10)).pack(anchor='w', pady=(4, 0))

        tong = tk.Frame(self, bg='#E7F5EF', padx=15, pady=10)
        tong.pack(fill='x', pady=(0, 12))
        self.lbl_so_luong = tk.Label(tong, text='Đang tải dữ liệu...', bg='#E7F5EF',
                                    fg='#205A4B', font=('Segoe UI', 11, 'bold'))
        self.lbl_so_luong.pack(side='left')
        ttk.Button(tong, text='+ Thêm mới', style='KTX.Primary.TButton',
                   command=self.them_moi).pack(side='right')

        thanh = ttk.Frame(self)
        thanh.pack(fill='x', pady=(0, 12))
        ttk.Label(thanh, text='Tìm nhanh:').pack(side='left', padx=(0, 7))
        self.txt_tim = ttk.Entry(thanh, width=25)
        self.txt_tim.pack(side='left', fill='x', expand=True, padx=(0, 7))
        self.txt_tim.bind('<Return>', lambda _event: self.tim_kiem())
        ttk.Button(thanh, text='Tìm kiếm', command=self.tim_kiem).pack(side='left', padx=3)
        ttk.Button(thanh, text='Làm mới', command=self.lam_moi).pack(side='left', padx=3)
        if self.CO_LUU_TRU:
            ttk.Checkbutton(thanh, text='Bao gồm lưu trữ',
                            variable=self.hien_luu_tru,
                            command=self.tai_du_lieu).pack(side='right', padx=(8, 0))

        duoi = ttk.Frame(self)
        duoi.pack(fill='x', pady=(0, 12))
        nut = [('Xem chi tiết', self.xem_chi_tiet)]
        if self.CHO_PHEP_SUA:
            nut.append(('Chỉnh sửa', self.chinh_sua))
        if self.CO_LUU_TRU:
            nut += [('Lưu trữ', self.luu_tru), ('Khôi phục', self.tai_kich_hoat)]
        if self.CHO_PHEP_XOA:
            nut += [('Xóa', self.xoa)]
        for ten, ham in nut:
            ttk.Button(duoi, text=ten, command=ham,
                       style=('KTX.Danger.TButton' if ten == 'Xóa'
                              else 'KTX.Light.TButton')).pack(side='left', padx=(0, 7))
        ttk.Label(duoi, text='Nhấp đúp một dòng để xem chi tiết.').pack(side='right')

        khung_bang = ttk.Frame(self)
        khung_bang.pack(fill='both', expand=True)
        khung_bang.columnconfigure(0, weight=1)
        khung_bang.rowconfigure(0, weight=1)
        self.bang = ttk.Treeview(khung_bang, columns=self.TRUONG,
                                 show='headings', selectmode='browse',
                                 style='KTX.Treeview')
        for truong in self.TRUONG:
            self.bang.heading(truong, text=self.ten_truong(truong))
            self.bang.column(truong, width=155, minwidth=105)
        self.cap_nhat_mau()
        cuon_y = ttk.Scrollbar(khung_bang, orient='vertical', command=self.bang.yview)
        cuon_x = ttk.Scrollbar(khung_bang, orient='horizontal', command=self.bang.xview)
        self.bang.configure(yscrollcommand=cuon_y.set, xscrollcommand=cuon_x.set)
        self.bang.grid(row=0, column=0, sticky='nsew')
        cuon_y.grid(row=0, column=1, sticky='ns')
        cuon_x.grid(row=1, column=0, sticky='ew')
        self.bang.bind('<Double-1>', lambda _event: self.xem_chi_tiet())

    @staticmethod
    def ten_truong(truong):
        return truong.replace('_', ' ').capitalize()

    @staticmethod
    def lay_gia_tri(obj, truong):
        return obj.get(truong) if isinstance(obj, dict) else getattr(obj, truong, None)

    def doc_luu_tru(self):
        return self.CO_LUU_TRU and self.hien_luu_tru.get()

    def hien_thi_danh_sach(self, data):
        self.bang.delete(*self.bang.get_children())
        if isinstance(data, dict):
            data = list(data.values())
        for i, obj in enumerate(data):
            ma = str(self.lay_gia_tri(obj, 'ma') or '')
            if not ma:
                continue
            values = [hien_thi(self.lay_gia_tri(obj, t)) for t in self.TRUONG]
            self.bang.insert('', 'end', iid=ma, values=values,
                             tags=('chan' if i % 2 == 0 else 'le',))
        self.lbl_so_luong.configure(text=f'Hiển thị {len(self.bang.get_children())} bản ghi')

    def tai_du_lieu(self):
        try:
            self.hien_thi_danh_sach(self.adapter.lay_tat_ca(
                self.LOAI, lay_luu_tru=self.doc_luu_tru()))
        except Exception as exc:
            messagebox.showerror('Lỗi tải dữ liệu', str(exc), parent=self.winfo_toplevel())

    def tim_kiem(self):
        tu = self.txt_tim.get().strip().casefold()
        if not tu:
            self.tai_du_lieu()
            return
        try:
            ket_qua = self.adapter.loc(
                self.LOAI,
                lambda obj: any(tu in hien_thi(self.lay_gia_tri(obj, t)).casefold()
                                for t in self.TRUONG),
                lay_luu_tru=self.doc_luu_tru())
            self.hien_thi_danh_sach(ket_qua)
        except Exception as exc:
            messagebox.showerror('Lỗi tìm kiếm', str(exc), parent=self.winfo_toplevel())

    def lam_moi(self):
        self.txt_tim.delete(0, 'end')
        self.tai_du_lieu()

    def lay_ma_chon(self):
        chon = self.bang.selection()
        if not chon:
            messagebox.showwarning('Chưa chọn', 'Bạn hãy chọn một dòng trước.',
                                   parent=self.winfo_toplevel())
            return None
        return chon[0]

    def xem_chi_tiet(self):
        ma = self.lay_ma_chon()
        if ma is None:
            return
        try:
            obj = self.adapter.lay_theo_ma(self.LOAI, ma,
                                         lay_luu_tru=self.doc_luu_tru())
            noidung = '\n'.join(f'{self.ten_truong(t)}: '
                                f'{hien_thi(self.lay_gia_tri(obj, t))}'
                                for t in self.TRUONG)
            if not self.NGHIEP_VU_CHI_TIET:
                messagebox.showinfo('Chi tiết', noidung, parent=self.winfo_toplevel())
                return
            cua_so = tk.Toplevel(self)
            cua_so.title(f'Chi tiết {self.LOAI.__name__} – {ma}')
            cua_so.geometry('620x540')
            cua_so.minsize(480, 340)
            cua_so.transient(self.winfo_toplevel())
            cua_so.grab_set()
            khung = ttk.Frame(cua_so, padding=18)
            khung.pack(fill='both', expand=True)
            ttk.Label(khung, text=f'CHI TIẾT {self.LOAI.__name__.upper()}',
                      font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 12))
            khung_van_ban = ttk.Frame(khung)
            khung_van_ban.pack(fill='both', expand=True)
            van_ban = tk.Text(khung_van_ban, wrap='word', height=14, relief='flat')
            cuon = ttk.Scrollbar(khung_van_ban, orient='vertical', command=van_ban.yview)
            van_ban.configure(yscrollcommand=cuon.set)
            van_ban.pack(side='left', fill='both', expand=True)
            cuon.pack(side='right', fill='y')
            van_ban.insert('1.0', noidung)
            van_ban.configure(state='disabled')
            hang = ttk.Frame(khung)
            hang.pack(fill='x', pady=(14, 0))

            def thuc_hien(ten_ham, mo_ta):
                if not messagebox.askyesno('Xác nhận', f'{mo_ta} cho mã {ma}?', parent=cua_so):
                    return
                try:
                    self.adapter.nghiep_vu(ten_ham, ma)
                    self.tai_du_lieu()
                    cua_so.destroy()  # Mở lại chi tiết để đọc trạng thái mới
                    messagebox.showinfo('Thành công', f'Đã {mo_ta.lower()}.',
                                        parent=self.winfo_toplevel())
                except Exception as exc:
                    messagebox.showerror('Lỗi nghiệp vụ', str(exc), parent=cua_so)

            for nhan, ham in self.NGHIEP_VU_CHI_TIET:
                ttk.Button(hang, text=nhan, style='KTX.Primary.TButton',
                           command=lambda t=nhan, h=ham: thuc_hien(h, t)).pack(
                               side='left', padx=(0, 8))
            ttk.Button(hang, text='Đóng', command=cua_so.destroy).pack(side='right')
        except Exception as exc:
            messagebox.showerror('Lỗi', str(exc), parent=self.winfo_toplevel())

    def them_moi(self):
        self.mo_form()

    def chinh_sua(self):
        if not self.CHO_PHEP_SUA:
            messagebox.showwarning('Không thể sửa', 'Thực thể này không được chỉnh sửa sau khi tạo.', parent=self.winfo_toplevel())
            return
        ma = self.lay_ma_chon()
        if ma is None:
            return
        try:
            obj = self.adapter.lay_theo_ma(self.LOAI, ma,
                                         lay_luu_tru=self.doc_luu_tru())
            du_lieu = {t: self.lay_gia_tri(obj, t) for t in self.TRUONG}
            self.mo_form(du_lieu, ma)
        except Exception as exc:
            messagebox.showerror('Lỗi sửa', str(exc), parent=self.winfo_toplevel())

    def tao_o_nhap(self, parent, truong, gia_tri):
        entry = ttk.Entry(parent, width=40)
        entry.insert(0, hien_thi(gia_tri))
        return entry

    def cau_hinh_form(self, form, o_nhap, du_lieu):
        """Class con có thể thiết lập Combobox ở đây."""
        pass

    def chuan_hoa_du_lieu_form(self, data, o_nhap):
        """Class con có thể đổi nhãn Combobox thành mã tại đây."""
        return data

    def _la_truong_ma_chinh(self, truong):
        """Xác định chính xác trường mã chính tự sinh của từng thực thể."""
        return truong == 'ma'

    def _chi_doc(self, truong):
        if self._la_truong_ma_chinh(truong) or truong in self.TRUONG_CHI_DOC_KHI_SUA:
            return True
        thuoc_tinh = getattr(self.LOAI, truong, None)
        return isinstance(thuoc_tinh, property) and thuoc_tinh.fset is None

    def _chuyen_kieu(self, truong, value):
        """Chuyển kiểu dữ liệu và báo lỗi bằng tiếng Việt khi nhập sai."""
        if value == '':
            return None
        kieu = self._kieu_truong.get(truong)
        if get_origin(kieu) is not None:
            kieu = next((k for k in get_args(kieu) if k is not type(None)), kieu)
        
        ten_hien_thi = self.ten_truong(truong)
        try:
            if kieu is int:
                return int(value)
            if kieu is float:
                return float(value)
            if kieu is date:
                try:
                    return date.fromisoformat(value)
                except ValueError:
                    return datetime.strptime(value, '%d/%m/%Y').date()
            if kieu is datetime:
                return datetime.fromisoformat(value)
            if kieu is bool:
                if value.casefold() in ('true', '1', 'có'):
                    return True
                if value.casefold() in ('false', '0', 'không'):
                    return False
                raise ValueError()
            if isinstance(kieu, type) and issubclass(kieu, Enum):
                try:
                    return kieu[value]
                except KeyError:
                    return kieu(value)
            return value
        except Exception:
            raise ValueError(f"Dữ liệu ở trường '{ten_hien_thi}' không hợp lệ. Vui lòng nhập đúng định dạng kiểu dữ liệu.")

    def mo_form(self, du_lieu=None, ma_cu=None):
        sua = ma_cu is not None
        if sua and not self.CHO_PHEP_SUA:
            messagebox.showwarning('Không thể sửa', 'Thực thể này không được chỉnh sửa sau khi tạo.', parent=self.winfo_toplevel())
            return
        du_lieu = dict(du_lieu or {})
        cua_so = tk.Toplevel(self)
        cua_so.title(('Chỉnh sửa ' if sua else 'Thêm mới ') + (self.TIEU_DE or self.LOAI.__name__))
        cua_so.geometry('560x640')
        cua_so.minsize(430, 420)
        cua_so.transient(self.winfo_toplevel())
        cua_so.grab_set()

        dau = tk.Frame(cua_so, bg='#207B68', padx=18, pady=14)
        dau.pack(fill='x')
        tk.Label(dau, text='Chỉnh sửa thông tin' if sua else 'Thêm thông tin mới',
                 bg='#207B68', fg='white',
                 font=('Segoe UI', 17, 'bold')).pack(anchor='w')
        tk.Label(dau, text='Mã được sinh tự động khi thêm mới.' if not sua
                 else 'Các trường không được phép sửa sẽ bị khóa.',
                 bg='#207B68', fg='#DBF3EB').pack(anchor='w', pady=(4, 0))

        khung = ttk.Frame(cua_so, padding=15)
        khung.pack(fill='both', expand=True)
        khung.columnconfigure(0, weight=1)
        khung.rowconfigure(0, weight=1)
        canvas = tk.Canvas(khung, bd=0, highlightthickness=0)
        cuon = ttk.Scrollbar(khung, orient='vertical', command=canvas.yview)
        form = ttk.Frame(canvas, padding=5)
        id_form = canvas.create_window((0, 0), window=form, anchor='nw')
        form.bind('<Configure>', lambda _e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfigure(id_form, width=e.width))
        canvas.configure(yscrollcommand=cuon.set)
        canvas.grid(row=0, column=0, sticky='nsew')
        cuon.grid(row=0, column=1, sticky='ns')

        o_nhap = {}
        for truong in self.TRUONG:
            if not sua and (self._la_truong_ma_chinh(truong) or truong in self.TRUONG_CHI_DOC_KHI_TAO):
                continue
            ttk.Label(form, text=self.ten_truong(truong)).pack(anchor='w', pady=(10, 4))
            o = self.tao_o_nhap(form, truong, du_lieu.get(truong, ''))
            o.pack(fill='x', ipady=2)
            o_nhap[truong] = o
            if sua and self._chi_doc(truong):
                o.configure(state='readonly')
        self.cau_hinh_form(form, o_nhap, du_lieu)

        def luu():
            try:
                data = {ten: o.get().strip() for ten, o in o_nhap.items()}
                data = self.chuan_hoa_du_lieu_form(data, o_nhap)
                if sua:
                    data = {k: v for k, v in data.items() if not self._chi_doc(k)}
                
                for ten in self.BAT_BUOC:
                    if not sua and self._la_truong_ma_chinh(ten):
                        continue
                    if ten in data and not str(data[ten]).strip():
                        raise ValueError(f'Bạn chưa nhập {self.ten_truong(ten)}')
                
                data = {ten: self._chuyen_kieu(ten, val) for ten, val in data.items()}
                if sua:
                    self.adapter.cap_nhat_truong(self.LOAI, ma_cu, **data)
                else:
                    # Kiểm tra chữ ký __init__ để loại bỏ các trường mã tự sinh rỗng/không hợp lệ
                    for k in list(data.keys()):
                        if (self._la_truong_ma_chinh(k) or k == 'ma') and not str(data[k]).strip():
                            data.pop(k, None)
                    self.adapter.tao_va_them(self.LOAI, **data)
                
                cua_so.destroy()
                self.tai_du_lieu()
                messagebox.showinfo('Đã lưu', 'Thông tin đã được lưu thành công.',
                                    parent=self.winfo_toplevel())
            except Exception as exc:
                messagebox.showerror('Không thể lưu', str(exc), parent=cua_so)

        duoi = ttk.Frame(khung)
        duoi.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(12, 0))
        ttk.Button(duoi, text='Hủy', command=cua_so.destroy).pack(side='right')
        ttk.Button(duoi, text='Lưu thông tin', style='KTX.Primary.TButton',
                   command=luu).pack(side='right', padx=(0, 8))

    def thao_tac_trang_thai(self, ham, mo_ta):
        ma = self.lay_ma_chon()
        if ma is None:
            return
        if not messagebox.askyesno('Xác nhận', f'{mo_ta} mã {ma}?',
                                   parent=self.winfo_toplevel()):
            return
        try:
            getattr(self.adapter, ham)(self.LOAI, ma)
            self.tai_du_lieu()
        except Exception as exc:
            messagebox.showerror('Lỗi thao tác', str(exc), parent=self.winfo_toplevel())

    def luu_tru(self):
        self.thao_tac_trang_thai('luu_tru', 'Lưu trữ')

    def tai_kich_hoat(self):
        self.thao_tac_trang_thai('tai_kich_hoat', 'Khôi phục')

    def xoa(self):
        ma = self.lay_ma_chon()
        if ma is None:
            return
        if not messagebox.askyesno(
                'Xác nhận xóa vĩnh viễn',
                f'Xóa vĩnh viễn mã {ma}?\nThao tác không thể hoàn tác và có thể bị từ chối nếu dữ liệu đang được tham chiếu.',
                parent=self.winfo_toplevel()):
            return
        try:
            self.adapter.xoa(self.LOAI, ma, ep_xoa=True)
            self.tai_du_lieu()
        except Exception as exc:
            messagebox.showerror('Lỗi xóa', str(exc), parent=self.winfo_toplevel())
"""Bảng màu dùng chung cho bốn chủ đề. Không chứa logic nghiệp vụ."""

BANG_MAU = {
    'LIGHT': {
        'nen': '#F6F9F7', 'chu': '#263D36', 'menu': '#E5F2EB',
        'the': '#FFFFFF', 'nut': '#FFFFFF', 'chon': '#C5E7D8',
        'chinh': '#207B68', 'chinh_dam': '#176655', 'phu': '#60776F',
        'vien': '#D7E5DD', 'trang': '#FFFFFF', 'nhat': '#E9F6EF',
    },
    'GREY': {
        'nen': '#F0F2F5', 'chu': '#303B49', 'menu': '#DFE5EB',
        'the': '#FFFFFF', 'nut': '#FFFFFF', 'chon': '#CCD9E8',
        'chinh': '#576B83', 'chinh_dam': '#3D516A', 'phu': '#657588',
        'vien': '#D2D9E0', 'trang': '#FFFFFF', 'nhat': '#E4EAF1',
    },
    'DARK': {
        'nen': '#1F2630', 'chu': '#EAF0F5', 'menu': '#17202A',
        'the': '#2A3440', 'nut': '#344252', 'chon': '#415F79',
        'chinh': '#457A88', 'chinh_dam': '#32616E', 'phu': '#B3C2CE',
        'vien': '#445260', 'trang': '#FFFFFF', 'nhat': '#344654',
    },
    'BLUE': {
        'nen': '#F1F6FD', 'chu': '#24354F', 'menu': '#DFEAFB',
        'the': '#FFFFFF', 'nut': '#FFFFFF', 'chon': '#C8DDFC',
        'chinh': '#2D67B6', 'chinh_dam': '#1B518F', 'phu': '#5D7599',
        'vien': '#D1E0F2', 'trang': '#FFFFFF', 'nhat': '#E5F0FF',
    },
}


def lay_mau(chu_de):
    return BANG_MAU.get(str(chu_de).upper(), BANG_MAU['LIGHT'])

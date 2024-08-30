
import fitz  # PyMuPDF


def check_fonts(pdf_path, _supported_fonts):
    supported_fonts = [font.lower() for font in _supported_fonts]

    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for font in page.get_fonts():
            font_name = font[2]  # 可以获取更多字体信息
            if font_name.lower() not in supported_fonts:
                print(f"不支持的字体类型：{font_name}")
                doc.close()
                return False
    doc.close()
    return True


pdf_file = '/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/交通银行_收.pdf'

# 目前只支持底下三种字体类型
_FONT_LIST = ['TrueType', 'Type1', 'Type0']

illegal = check_fonts(pdf_file, _FONT_LIST)
if not illegal:
    print(f"字体类型不支持")

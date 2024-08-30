
import pdfplumber
import pypdf

import os
import fitz  # PyMuPDF


def list_pdf_fonts_pdfplumber(pdf_path):
    pdf = pdfplumber.open(pdf_path)

    print(set(char["fontname"] for char in pdf.chars))


def list_path_fonts(pdf_path):
    f_set = set()
    # 遍历pdf_path目录下的所有pdf文件
    for root, dirs, files in os.walk(pdf_path):
        for file in files:
            if not file.endswith(".pdf"):
                continue

            file_path = os.path.join(root, file)
            fonts = get_pdf_fonts(file_path)
            f_set = f_set | fonts
    return f_set

# list_path_fonts('/Users/qinqiang02/job/test/发票测试数据')


def check_fonts(pdf_path, _supported_fonts):
    doc = fitz.open(pdf_path)

    supported_fonts = [font.lower() for font in _supported_fonts]

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


def get_pdf_fonts(pdf_path):
    # 获取字体列表
    doc = fitz.open(pdf_path)

    all_fonts = set()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for font in page.get_fonts():
            # 取字体的类型
            font_name = font[2]
            all_fonts.add(font_name)

    doc.close()
    return all_fonts


file_path = '/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks'

pdf_file = '/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/交通银行_收.pdf'

_FONT_LIST = ['TrueType', 'Type1', 'Type0']

illegal = check_fonts(pdf_file, _FONT_LIST)
if not illegal:
    print(f"字体类型不支持")

# extract_text_and_images(file_path)
# list_pdf_fonts_pdfdumper(file_path)
# extract_text_and_images(file_path)

import os
import re
from pypdf import PdfReader
import pdftotext
import openpyxl
import pdftotext
from openpyxl.workbook import Workbook

from test_pdf_font import check_fonts, get_pdf_fonts

# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/上海银行_付.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/交通银行_收.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/广州_收付款.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/建行_建行收付回单.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/创兴_收付回单.pdf"
fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/农商银行_付.pdf"


def save_excel(root, filename, ret):
    # 设置文件名为 "a.xlsx"
    excel_file = os.path.join(root, "a.xlsx")

    # 检查文件是否存在
    if os.path.exists(excel_file):
        # 如果文件存在，则加载工作簿
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active
    else:
        # 如果文件不存在，则创建一个新的工作簿和工作表
        workbook = Workbook()
        sheet = workbook.active
        # 写入表头
        headers = ["文件名"] + ["layout_txt"]
        sheet.append(headers)

    # 创建一行数据，第一列为文件名，后面为格式化后的JSON字符串
    row_data = [filename] + [ret]

    # 将数据追加到工作表的末尾
    sheet.append(row_data)

    # 保存工作簿，避免中文乱码
    workbook.save(excel_file)
    print(f"[{filename}] data saved")


def save_text(root, filename, ret):
    fn = os.path.join(root, "ex2_2", f"{filename}.txt")
    with open(fn, "w", encoding="utf-8") as text_file:
        text_file.write(ret)


def extract_from_pdftotext(pdf_file):
    with open(pdf_file, "rb") as f:
        pdf = pdftotext.PDF(f)
        text = pdf[0]
        text = "\n".join([line for line in text.splitlines() if line.strip()])
        return text


def extract_layout_txt(pdf_file):
    reader = PdfReader(pdf_file)
    # 暂时只取第一页
    page = reader.pages[0]

    text = None
    try:
        text = page.extract_text(extraction_mode="layout")
    except Exception as e:
        print(f"Error extracting text in layout mode: {e}, {pdf_file}")
        try:
            print(f"[{pdf_file}] using pdftotext")
            text = extract_from_pdftotext(pdf_file)
            print(text)
        except Exception as e2:
            print(f"Error extracting text in standard mode: {e2}, {pdf_file}")

    return text


def batch_pdf(root_dir):
    # 列出 root_dir 目录下的所有文件和文件夹
    for filename in os.listdir(root_dir):
        # 获取当前文件的完整路径
        pdf_file = os.path.join(root_dir, filename)

        if not (os.path.isfile(pdf_file) and filename.lower().endswith('.pdf')):
            continue

        text = ""
        if not check_fonts(pdf_file):
            print(f"[{pdf_file}]不能解析字体：{get_pdf_fonts(pdf_file)}")
        else:
            # text = extract_layout_txt(pdf_file)
            text = extract_from_pdftotext(pdf_file)
            if not text:
                print(f"[{pdf_file}]不能解析文件：{get_pdf_fonts(pdf_file)}")

        # save_excel(root_dir, filename, text)
        save_text(root_dir, filename, text)


batch_pdf("/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks")


def test(pdf_file):
    if not check_fonts(pdf_file):
        print(f"不能解析{pdf_file}, 字体：{get_pdf_fonts(pdf_file)}")
        return

    reader = PdfReader(pdf_file)
    page = reader.pages[0]

    try:
        text = page.extract_text(extraction_mode="layout")
        print(text)
        print("\n====================================================================\n",
              page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False))
    except Exception as e:
        print(f"Error extracting text in layout mode: {e}")
        # 尝试使用标准模式
        try:
            print(page.extract_text())
        except Exception as e2:
            print(f"Error extracting text in standard mode: {e2}")

    input("按下回车键继续...")

    # extract text in a fixed width format that closely adheres to the rendered
    # layout in the source pdf
    print("---extract text in a fixed width format that closely adheres to the rendered---")
    print(page.extract_text(extraction_mode="layout"))

    # extract text preserving horizontal positioning without excess vertical
    # whitespace (removes blank and "whitespace only" lines)
    print("---extract text preserving horizontal positioning without excess vertical---")
    print(page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False))

    # adjust horizontal spacing
    print("---adjust horizontal spacingl---")
    print(page.extract_text(extraction_mode="layout", layout_mode_scale_weight=1.0))

    # exclude (default) or include (as shown below) text rotated w.r.t. the page
    print("---exclude (default) or include (as shown below) text rotated w.r.t. the page---")
    print(page.extract_text(extraction_mode="layout", layout_mode_strip_rotated=False))

# test(fp)

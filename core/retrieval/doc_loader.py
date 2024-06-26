import os
import os.path as osp
import pdfplumber
from dotenv import load_dotenv
import logging
import re

from core.common import OCRProvider, DocLanguage
from core.retrieval.ocr import ocr

logging.basicConfig(format='[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s: %(message)s', level=logging.INFO, force=True)
load_dotenv(override=True)
fonts_list = os.getenv("KNOWN_FONTS").split(',')


def cid_percentage(text):
    # 计算文本中CID字符的比例
    cid_matches = re.findall(r'\(cid:\d+\)', text)
    cid_length = sum(len(match) for match in cid_matches)
    total_length = len(text)

    # 计算比例
    percentage = cid_length / total_length * 100
    return percentage


# pdf_path: pdf文件路径
# page: pdfplumber.Page对象
def save_page_as_image(pdf_path, page):
    file_path, filename = os.path.split(pdf_path)
    file_base, file_extension = os.path.splitext(filename)
    dest_path = os.path.join(file_path, 'tmp', f"{file_base}_{page.page_number}.png")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    image = page.to_image(resolution=300)
    image.save(dest_path, format='PNG')
    logging.info(f"已保存第{page.page_number}页到：{dest_path}")
    return dest_path


# 异步读取文档，将结果放入队列queue
# 如果provider!=None
#   --queue：队列，元素是一个三元组：(页码, 识别结果, 总页数)； 页码为-1表示结束
# 如果provider==None
#   --如果pdf是图片
#       --queue：队列，元素是一个三元组：(页码, 图片地址, 总页数)； 页码为-1表示结束
#   --如果pdf是文本
#       --queue：队列，元素是一个三元组：(页码, 识别结果, 总页数)； 页码为-1表示结束

def async_load(doc_path, queue, provider=OCRProvider.RuiZhen, lang=DocLanguage.chs):
    # 非pdf文件，直接ocr
    if not doc_path.lower().endswith(".pdf"):
        logging.info(f"put to queue: {osp.split(doc_path)[1]}")
        if provider is None:
            queue.put((1, doc_path, 1))
        else:
            queue.put((1, ocr(doc_path, -1, provider, lang), 1))
        queue.put((-1, None, -1))
        return

    pdf = pdfplumber.open(doc_path)
    num_pages = len(pdf.pages)
    for page in pdf.pages:
        text = page.extract_text()

        # todo: 校验字体；单独成一个判断函数
        # 判断是否扫描件后包含无法解析字体，39是一个经验值
        if provider is None or not text or len(text) < 39 or len(page.images) > 5 or cid_percentage(text) > 19:
            logging.info(f"扫描件[{osp.split(doc_path)[1]}]: len(text)[{len(text)}], len(images)[{len(page.images)}]")
            if provider is None:
                text = save_page_as_image(doc_path, page)
            else:
                text = ocr(doc_path, page.page_number, provider, lang)

        logging.info(f"[{osp.split(doc_path)[1]}] put to queue: {page.page_number}")
        queue.put((page.page_number, text, num_pages))

    pdf.close()
    logging.info(f"[{osp.split(doc_path)[1]}] put to queue: finish")
    queue.put((-1, None, -1))


# pdfplumber的文本更全一点
def extract_text(pdf_path, page_no=0):
    pdf = pdfplumber.open(pdf_path)
    page = pdf.pages[page_no]
    return page.extract_text()


def known_fonts(font):
    return font in fonts_list

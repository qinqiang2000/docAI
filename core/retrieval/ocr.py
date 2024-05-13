import logging
import os
import fitz
from dotenv import load_dotenv
from core.retrieval.ocr_ruizhen import ruizhen_ocr
from core.common import OCRProvider, DocLanguage, get_file_hash

logging.basicConfig(format='[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s: %(message)s', level=logging.INFO,
                    force=True)


# todo: 先将page_no页写到一个单独pdf，再读(待优化）
def before_ocr(doc_path, page_no):
    # 将doc_path分成路径和文件名
    with open(doc_path, 'rb') as file:
        doc = fitz.open(file)

    file_path, filename = os.path.split(doc_path)
    file_base, file_extension = os.path.splitext(filename)
    dest_path = os.path.join(file_path, 'tmp', f"{file_base}_{page_no}{file_extension}")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # 单独提取第page_no页
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=page_no - 1, to_page=page_no - 1)
    new_doc.save(dest_path)
    logging.info(f"已保存第{page_no}页到：{dest_path}")

    new_doc.close()
    return dest_path


def mock_ocr(doc_path):
    # 从本地文件mock_ocr_result.txt中读取mock结果
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, 'mock_ocr_result.txt'), 'r') as f:
        return f.read()


def get_cache_path(doc_hash, provider):
    ocr_cache_dir = os.getenv('OCR_CACHE_DIR', 'data/ocr_cache')
    provider_cache_dir = os.path.join(ocr_cache_dir, provider.name)
    os.makedirs(provider_cache_dir, exist_ok=True)

    cache_path = os.path.join(provider_cache_dir, f'{doc_hash}.txt')

    return cache_path


def ocr(doc_path, page_no, provider=OCRProvider.MOCK, lang=DocLanguage.chs):
    _hash = get_file_hash(doc_path)
    doc_hash = f"{_hash}_{page_no}"
    logging.info(f"[hash] {doc_path}, {doc_hash}")

    # page_no >= 0表示是pdf，需预处理
    if page_no >= 0:
        doc_path = before_ocr(doc_path, page_no)

    ocr_cache = os.getenv('OCR_CACHE', 'FALSE').upper() == 'TRUE'

    # 如果缓存文件存在，则直接读取
    if ocr_cache:
        cache_path = get_cache_path(doc_hash, provider)
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as file:
                text = file.read()
                logging.info(f"ocr cache raw result from {cache_path}:\n {text}]")
                return text

    # 如果不读取缓存，或缓存文件存在，则直接OCR
    text = ""
    if provider == OCRProvider.MOCK:
        text = mock_ocr(doc_path)
        # logging.info("使用mock ocr, text=" + text)
        return text
    elif provider == OCRProvider.RuiZhen:
        text = ruizhen_ocr(doc_path, lang)

    # 将结果写入缓存文件
    if ocr_cache:
        cache_path = get_cache_path(doc_hash, provider)
        with open(cache_path, 'w', encoding='utf-8') as file:
            file.write(text)

    logging.debug(f"[{doc_path}] [{provider}] ocr raw result:\n {text}]")
    return text

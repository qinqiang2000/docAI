import hashlib
import logging
import os
import queue
import shutil
import tempfile
import os.path as osp
import threading

from core.common import OCRProvider, DocLanguage, LlmProvider
from core.retrieval.doc_loader import async_load
from core.llm import llm


def save_uploaded_file(_file):
    dir_name = 'tmp'
    os.makedirs(dir_name, exist_ok=True)

    hasher = hashlib.sha256()
    _file.seek(0)
    for chunk in iter(lambda: _file.read(4096), b''):
        hasher.update(chunk)
    file_hash = hasher.hexdigest()
    # Generate a temporary file name
    tmp_file_name = osp.join(dir_name, osp.splitext(_file.name)[0] + '_' + file_hash[:8] + osp.splitext(_file.name)[1])
    # Write the uploaded file's contents to the temporary file
    with open(tmp_file_name, 'wb') as tmp_file:
        _file.seek(0)
        shutil.copyfileobj(_file, tmp_file)
    return tmp_file_name


class Extractor:
    def __init__(self, name, description, fields):
        self.name = name
        self.description = description
        self.fields = fields

    def generate_prompt(self):
        result = self.description + "\n 字段列表：\n"
        for key, value in self.fields.items():
            result += f"- {key}: {value}\n"

        result = result + "输出要求：以JSON数组输出答案；确保用```json 和 ```标签包装答案。"
        return result

    def run(self, file, stream_callback,
            llm_provider=LlmProvider.GPT35, ocr_provider=OCRProvider.RuiZhen, lang=DocLanguage.chs):
        """
        Process the given file based on the core's configuration and stream the results
        using the provided stream_callback function.

        Args:
        file (file-like object): The file to process.
        stream_callback (function): A callback function to stream processing results.
        """
        # 保存为临时文件
        file_path = save_uploaded_file(file)

        result = []
        # 异步读取/识别文档的raw text
        q = queue.Queue()
        threading.Thread(target=async_load, args=(file_path, q, ocr_provider, lang)).start()
        while True:
            page_no, text, total = q.get()  # 从队列获取进度和结果, page_no 从1开始
            if page_no == -1:
                break

            # 提取字段
            print(text)
            ret = llm.extract_bill(text, llm_provider, self.generate_prompt(), callback=stream_callback)
            result.append(ret)
            # result =[[{'Doc Type': 'other', 'Invoice No.': 'FPL2308002', 'Invoice Date': '3-Aug-23', 'Currency': '', 'Amount': 0, 'Bill To': '海信(香港)有限公司', 'From': '福芯電子有限公司', 'Ship To': '青旅思捷物流有限公司'}], [{'Doc Type': 'Invoice', 'Invoice Date': '3-Aug-23', 'Currency': 'USD', 'Amount': 15048.0, 'Bill To': '海信(香港)有限公司', 'From': '福芯電子有限公司 FORCHIP ELECTRONICS LIMITED'}]]

        logging.info(f"{file.name}: {result}")
        return result


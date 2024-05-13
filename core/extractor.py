import json
import logging
import queue
import threading

from core.common import OCRProvider, DocLanguage, LlmProvider
from core.llm import llm
from core.retrieval.doc_loader import async_load


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

    def mock_ret(self):
        mock_data = [{key: "" for key in self.fields.keys()}]
        return mock_data

    def run(self, file_path, stream_callback,
            llm_provider=LlmProvider.AZURE_GPT35, ocr_provider=OCRProvider.RuiZhen, lang=DocLanguage.chs):
        """
        Process the given file based on the core's configuration and stream the results
        using the provided stream_callback function.

        Args:
        file (file-like object): The file to process.
        stream_callback (function): A callback function to stream processing results.
        """
        result = []
        # 异步读取/识别文档的raw text
        q = queue.Queue()
        threading.Thread(target=async_load, args=(file_path, q, ocr_provider, lang)).start()
        while True:
            page_no, text, total = q.get()  # 从队列获取进度和结果, page_no 从1开始
            if page_no == -1:
                break

            # 提取字段
            if llm_provider == LlmProvider.MOCK:  # 使用mock数据
                ret = self.mock_ret()
            else:
                # logging.info(f"第{page_no}页：{text}")
                ret = llm.extract_bill(text, llm_provider, self.generate_prompt(), callback=stream_callback)
            result.append(ret)

        logging.info(f"{file_path}: {result}")
        return result


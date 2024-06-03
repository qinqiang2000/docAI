import json
import logging
import queue
import re
import threading
from time import sleep

from core.common import OCRProvider, DocLanguage
from core.llm import llm
from core.llm.llm import LlmProvider, pure_llm
from core.retrieval.doc_loader import async_load


def clean_js_to_json(js_code):
    try:
        # Remove single line comments
        js_code = re.sub(r'//.*', '', js_code)
        # Remove multi-line comments
        js_code = re.sub(r'/\*.*?\*/', '', js_code, flags=re.DOTALL)
        # Replace values with empty strings
        js_code = re.sub(r'":\s*".*?"', '": ""', js_code)
        # Remove trailing commas
        js_code = re.sub(r',\s*([}\]])', r'\1', js_code)

        # Try to parse JSON
        parsed_json = json.loads(js_code)

        # Remove empty objects from the top-level array
        if isinstance(parsed_json, list):
            parsed_json = [item for item in parsed_json if item]
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


class Extractor:
    def __init__(self, name, description, fields):
        self.name = name
        self.description = description
        self.fields = fields

    def generate_prompt(self):
        result = self.description
        result = result + "\n 输出json格式：\n" + self.fields
        result = result + f"""\n\n输出要求:
         - 以JSON数组输出答案；确保用```json 和 ```标签包装答案。 JSON对象的值都转成字符串返回。
         """
        return result

    def mock_ret(self):
        cleaned_json = clean_js_to_json(self.fields)
        sleep(0.1)
        return cleaned_json

    def run(self, file_path, stream_callback,
            llm_provider=LlmProvider.AZURE_GPT35, ocr_provider=OCRProvider.RuiZhen, lang=DocLanguage.chs):
        """
        Process the given file based on the core's configuration and stream the results
        using the provided stream_callback function.

        Args:
        file (file-like object): The file to process.
        stream_callback (function): A callback function to stream processing results.
        ocr_provider: 如果是None，说明是用视觉模型
        """
        logging.info(f"开始处理文件：{file_path}, OCR提供商：{ocr_provider}, 语言：{lang}")
        result = []

        # 纯LLM提取，则将ocr_provider设置为None，以告知doc_loader模块不要ocr
        if pure_llm(llm_provider):
            ocr_provider = None

        # 异步读取/识别文档的raw text
        # 如果ocr_provider是None，则返回的是图片的url
        q = queue.Queue()
        threading.Thread(target=async_load, args=(file_path, q, ocr_provider, lang)).start()

        while True:
            page_no, text, total = q.get()  # 从队列获取进度和结果, page_no 从1开始
            if page_no == -1:
                break

            # 提取字段
            if llm_provider == LlmProvider.MOCK:  # 使用mock数据
                ret = self.mock_ret()
            elif len(text) < 3:
                ret = []
            else:
                ret = llm.extract_bill(text, llm_provider, self.generate_prompt(), callback=stream_callback)
            result.append(ret)

        logging.info(f"{file_path}: {result}")
        return result


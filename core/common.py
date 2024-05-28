import base64
import hashlib
import logging
import pandas as pd
import re
import difflib
from enum import Enum
from mimetypes import guess_type

DATASET_DIR = "data/dataset"
LABEL_DIR = "data/labels"
EVALUATE_DIR = "data/evaluate"


class OCRProvider(Enum):
    RuiZhen_Hack = 2
    RuiZhen = 1
    MOCK = 6


class DocLanguage(Enum):
    chs = "简体中文"
    eng = "英语"
    cht = "繁体中文"
    jpn = "日语"
    kor = "韩语"
    vie = "越南语"
    tha = "泰语"
    spa = "西班牙语"
    deu = "德语"
    fra = "法语"
    rus = "俄语"
    nld = "荷兰语"
    ita = "意大利语"
    por = "葡萄牙语"


def get_file_hash(filepath):
    """ 计算文件的MD5 hash值。 """
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# Function to encode a local image into data URL
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"


def compare_values(val1, val2):
    # 自定义比较函数
    def is_date(string):
        try:
            pd.to_datetime(string)
            return True
        except ValueError:
            return False

    def is_amount(string):
        if isinstance(string, float) or isinstance(string, int):
            return True
        return bool(re.match(r'^\d+(\.\d+)?$', string))

    def normalize_string(string):
        if not isinstance(string, str):
            string = str(string)
        return re.sub(r'[\s\W_]+', '', string).lower()

    # todo: 改为特殊标识，而非空值
    if pd.isnull(val1):
        return True  # 如果 val1 是空值，则返回 True

    val1 = str(val1)
    val2 = str(val2)

    if is_date(val1) and is_date(val2):
        # 日期比较
        date1 = pd.to_datetime(val1, errors='coerce')
        date2 = pd.to_datetime(val2, errors='coerce')
        if date1 != date2:
            date2 = pd.to_datetime(val2, errors='coerce', dayfirst=True)
            logging.warning(f"调整了dayfirst：date1[{date1}] : date2[{date2}] ")
            return date1 == date2
        return True
    elif is_amount(val1) and is_amount(val2):
        # 金额比较
        amount1 = float(val1) if pd.notnull(val1) else None
        amount2 = float(val2) if pd.notnull(val2) else None
        return amount1 == amount2
    else:
        # 字符串比较，忽略大小写、空格和标点符号
        str1 = normalize_string(val1) if pd.notnull(val1) else None
        str2 = normalize_string(val2) if pd.notnull(val2) else None

        similarity = difflib.SequenceMatcher(None, str1, str2).ratio()
        return similarity >= 0.8
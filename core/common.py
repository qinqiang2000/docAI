import base64
import hashlib
import os
from enum import Enum
from mimetypes import guess_type

DATASET_DIR = "data/dataset"
LABEL_DIR = "data/labels"


# 如果要用纯视觉模型，需要在枚举后缀加上'_V'
class LlmProvider(Enum):
    AZURE_GPT35 = 7
    GPT4o = 8
    GPT4o_V = 9
    AZURE_GPT4 = 1
    GPT35 = 3
    # GPT4 = 2
    # MOONSHOT = 4
    # GEMINI_PRO = 5
    MOCK = 6


class OCRProvider(Enum):
    RuiZhen = 1
    Tencent = 2
    MOCK = 6


class DocLanguage(Enum):
    eng = "英语"
    chs = "简体中文"
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

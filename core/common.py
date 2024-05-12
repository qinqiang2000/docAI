import hashlib
from enum import Enum

DATASET_DIR = "data/dataset"


class LlmProvider(Enum):
    AZURE_GPT35 = 7
    AZURE_GPT4 = 1
    GPT35 = 3
    GPT4 = 2
    MOONSHOT = 4
    GEMINI_PRO = 5
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



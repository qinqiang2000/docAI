import base64
import hashlib
import json
from typing import List, Any

import re
from enum import Enum
from mimetypes import guess_type

DATASET_DIR = "data/dataset"
LABEL_DIR = "data/labels"
EVALUATE_DIR = "data/evaluate"


class OCRProvider(Enum):
    REGENAI_DOC_HACK = 2
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


def flatten_if_single_nested_array(arr: List[Any]) -> List[Any]:
    """
    Flatten an array if it consists of a single nested array.

    Parameters:
        arr (List[Any]): The potentially nested array to flatten.

    Returns:
        List[Any]: A flattened version of the input array if the top level contains
                   only a single nested array, otherwise the original array.
    """
    # Check if the list contains exactly one element and that element is a list
    while len(arr) == 1 and isinstance(arr[0], list):
        arr = arr[0]
    return arr


# Custom parser
def extract_json(text) -> List[dict]:
    """Extracts JSON content from a string where JSON is embedded between ```json and ``` tags.

    Parameters:
        text (str): The text containing the JSON content.

    Returns:
        list: A list of extracted JSON strings.
    """
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```json(.*?)```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
        parse_json = [json.loads(match.strip()) for match in matches]
        return flatten_if_single_nested_array(parse_json)
    except Exception:
        raise ValueError(f"Failed to parse: {text}")


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


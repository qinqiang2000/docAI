import json
import re

text = """
```json
[
    {
        "Doc Type": "other",
        "Invoice No.": "",
        "Invoice Date": "",
        "Currency": "",
        "Total Amount": "0",
        "Subtotal": "0",
        "Bill To": "Hisense Boardband Multimedia Technologies (HK) Co., Limited",
        "From": "ORANGETEK CORPORATION"
    }
]
```
"""

# 使用正则表达式移除对象最后一个字段后的逗号
# 匹配规则：找到逗号后跟着右大括号的位置，并移除该逗号
text_fixed = re.sub(r',(\s*})', r'\1', text)

# Define the regular expression pattern to match JSON blocks
pattern = r"```json(.*?)```"

# Find all non-overlapping matches of the pattern in the string
matches = re.findall(pattern, text_fixed, re.DOTALL)

# Return the list of matched JSON strings, stripping any leading or trailing whitespace
try:
    print(matches[0])
    parse_json = json.loads(matches[0].strip())
    print(parse_json)
except Exception:
    raise ValueError(f"Failed to parse: {text}")

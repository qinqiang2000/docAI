import json
import re
from typing import List, Any

from core.retrieval.ocr_ruizhen_doc_hacker import DocumentHacker


def extract_json(text: str) -> List[dict]:
    """Extracts JSON content from a string where JSON is embedded between ```json and ``` tags.

    Parameters:
        text (str): The text containing the JSON content.

    Returns:
        list: A list of extracted JSON objects.
    """
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Attempt to parse the matches as JSON
    extracted_json = []
    for match in matches:
        print(match.strip())
        # Remove the 'json' string if present at the beginning
        cleaned_match = re.sub(r"^json\s*", "", match.strip(), flags=re.IGNORECASE)
        try:
            parsed_json = json.loads(cleaned_match)
            extracted_json.append(parsed_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {cleaned_match}. Error: {e}")

    return extracted_json


def flatten_if_single_nested_array(parsed_json: List[Any]) -> List[dict]:
    """Flattens the JSON if it is a single nested array.

    Parameters:
        parsed_json (list): The parsed JSON content.

    Returns:
        list: Flattened JSON content if applicable.
    """
    if len(parsed_json) == 1 and isinstance(parsed_json[0], list):
        return parsed_json[0]
    return parsed_json


str = """
 Here is the extracted information in JSON format:

```
json
[
  {
    "guest_name": "张君",
    "arrival": "2023-09-07",
    "departure": "",
    "total_amount": "380.00"
  }
]
```

Note: The `departure` field is left blank since there is no information about the departure date in the provided OCR text. The `hotel_name` field is also left blank since there is no information about the hotel name in the provided OCR text.

"""

# print(extract_json(str))

import os
import shutil


def rename_and_copy_pdfs(root_dir, target_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                # 获取当前文件的完整路径
                current_file_path = os.path.join(dirpath, filename)

                # 获取上级目录名称
                parent_dir_name = os.path.basename(dirpath)

                # 新文件名
                new_filename = f"{parent_dir_name}_{filename}"

                # 构建目标文件路径
                new_file_path = os.path.join(target_dir, new_filename)

                # 复制文件到目标目录
                shutil.copy2(current_file_path, new_file_path)
                print(f"Copied: {current_file_path} -> {new_file_path}")


def batch_ruizhen_doc(root_dir, access_token):
    processor = DocumentHacker(access_token)

    # 列出 root_dir 目录下的所有文件和文件夹
    for filename in os.listdir(root_dir):
        # 获取当前文件的完整路径
        fp = os.path.join(root_dir, filename)

        if not (os.path.isfile(fp) and filename.lower().endswith('.pdf')):
            continue

        # 处理文档，包括上传、检查状态、导出和文本提取
        # return: None， 表示不成功
        text = processor.process_document(fp)
        print(text)

        fn = os.path.join(root_dir, "ruizhen_doc", f"{filename}.txt")
        with open(fn, "w", encoding="utf-8") as text_file:
            text_file.write(text)


# 指定需要递归遍历的根目录
root_directory = '/Users/qinqiang02/Desktop/银行账户资料收集'

# 指定目标目录
target_directory = '/Users/qinqiang02/Desktop/banks'

# 调用函数
# rename_and_copy_pdfs(root_directory, target_directory)
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiIxMzcxNDk2MjYwNCIsInNjb3BlIjpbInNlcnZlciJdLCJpZCI6ODY0MSwiZXhwIjoxNzI0NDg1MjA1LCJhdXRob3JpdGllcyI6WyJST0xFX0RJU1RSSUJVVE9SIiwiUk9MRV9MQUJFTCJdLCJqdGkiOiI0NDlmYWYyYy1iZTdkLTQ4NmEtYjY2Ny0wMjEzN2RiMTk1ZTYiLCJjbGllbnRfaWQiOiJnbG9yaXR5LW9hdXRoIn0.602o20_BSlrSfhoEUBJKfMIfVSvg47PwYe8l2Z4N_0U"
# batch_ruizhen_doc("/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks", token)

import json
from openai import AzureOpenAI
import os
import dotenv
import openai
dotenv.load_dotenv()

# Setting up the deployment name
deployment_name = "gpt-4o"

# The API key for your Azure OpenAI resource.
api_key = "b90546f796434a0a9535213f455c3647"

# The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
azure_endpoint = "https://test-openai-service-wus3-rg4.openai.azure.com/"

# Currently OPENAI API have the following versions available: 2022-12-01
api_version = "2024-05-01-preview"

client = AzureOpenAI(
  api_key=api_key,
  azure_endpoint=azure_endpoint,
  api_version=api_version
)
# Give your prompt here
prompt = "Hello world"

# A sample API call for chat completions looks as follows:
# Messages must be an array of message objects, where each object has a role (either "system", "user", or "assistant") and content (the content of the message).
# For more info: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#chat-completions

try:
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
    )

    # print the response
    print(response.choices[0].message.content)

except openai.AuthenticationError as e:
    # Handle Authentication error here, e.g. invalid API key
    print(f"OpenAI API returned an Authentication Error: {e}")

except openai.APIConnectionError as e:
    # Handle connection error here
    print(f"Failed to connect to OpenAI API: {e}")

except openai.BadRequestError as e:
    # Handle connection error here
    print(f"Invalid Request Error: {e}")

except openai.RateLimitError as e:
    # Handle rate limit error
    print(f"OpenAI API request exceeded rate limit: {e}")

except openai.InternalServerError as e:
    # Handle Service Unavailable error
    print(f"Service Unavailable: {e}")

except openai.APITimeoutError as e:
    # Handle request timeout
    print(f"Request timed out: {e}")

except openai.APIError as e:
    # Handle API error here, e.g. retry or log
    print(f"OpenAI API returned an API Error: {e}")

except:
    # Handles all other exceptions
    print("An exception has occured.")
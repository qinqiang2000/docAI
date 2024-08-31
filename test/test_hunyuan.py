import base64
import json
import os
import random
import re
from mimetypes import guess_type
from typing import List

from dotenv import load_dotenv
from pdf2image import convert_from_path
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models

load_dotenv(override=True)


# 字符串转json，todo：增加异常情况处理
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
        # Remove the 'json' string if present at the beginning
        cleaned_match = re.sub(r"^json\s*", "", match.strip(), flags=re.IGNORECASE)
        try:
            parsed_json = json.loads(cleaned_match)
            extracted_json.append(parsed_json)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON: {cleaned_match}. Error: {e}")

    return extracted_json


def conv_pdf_png(pdf_path):
    # 将PDF文件的每一页转换为图像
    images = convert_from_path(pdf_path)

    rand_int = random.randint(1, 10000)

    # 保存每一页图像
    img_pages = []
    for i, image in enumerate(images):
        # 构造输出图像文件的路径
        img_path = f"./tmp/tmp_{rand_int}_page_{i}.png"
        # 保存图像
        image.save(img_path, "png")
        img_pages.append(img_path)

    return img_pages


def local_image_to_base64(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"


def extract_pdf_hunyuanV(pdf_path, sys_prompt):
    cred = credential.Credential(os.environ['TENCENT_SecretId'], os.environ['TENCENT_SecretKey'])

    cpf = ClientProfile()
    # 预先建立连接可以降低访问延迟
    cpf.httpProfile.pre_conn_pool_size = 3
    client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou", cpf)

    # 转换pdf为图片，模型只支持图片格式
    img_pages = conv_pdf_png(pdf_path)

    for img_path in img_pages:
        url = local_image_to_base64(img_path)

        req = models.ChatCompletionsRequest()
        params = {
            "Model": "hunyuan-vision",
            "Messages": [ {
                    "Role": "user",
                    "Contents": [
                        {
                            "Type": "text",
                            "Text": sys_prompt
                        },
                        {
                            "Type": "image_url",
                            "ImageUrl": {
                                "Url": url
                            }
                        }
                    ]
                }
            ]
        }
        req.from_json_string(json.dumps(params))

        resp = client.ChatCompletions(req)

        # 文本返回
        json_str = resp.Choices[0].Message.Content
        print(f"token耗用量：{resp.Usage} \n 返回文本：\n{json_str}")

        # 转为json对象
        json_obj = extract_json(json_str)
        print(json_obj)


sys_prompt = """
根据给出图片，提取银行回单的关键字段，并以JSON格式输出。
注意：
- 如果字段没值，取空字符串为值。
- 只输出json格式的结果，不附带解释等其他内容
- json字符串和key用双引号
- 输出结果用```json和```包裹
 输出json格式：
[
  {
  "payer_name": "付款人户名、付款人姓名或付款人全称、付款人账户名称或全称",
  "payer_account_number": "付款人账号、账号",
  "payer_bank_name": "付款人开户银行、开户行、或银行名称的打印机构",
  "payee_name": "收款人户名、收款人姓名或收款人全称、收款人账户名称或全称",
  "payee_account_number": "收款人账号、账号",
  "payee_bank_name": "收款人开户银行、开户行名称、或银行名称的打印机构",
  "date":"交易时间、交易日期、记账日期或时间戳。要求：只提取到日期，格式YYYY-MM-DD",
  "amount": "交易金额；要求：number格式",
  "summary": "摘要、用途或客户附言；没有则留空",
  "type": "交易类型、业务种类、产品种类或回单种类",
  "serial_number": "交易流水号、核心流水号、流水号",
  "receipt_number": "回单编号、电子回单号、回单流水号；要求：不和serial_number重复；没有则留空"
  }
]
"""

extract_pdf_hunyuanV("/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/交通银行_收.pdf", sys_prompt)
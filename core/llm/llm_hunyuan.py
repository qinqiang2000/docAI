import base64
import json
import logging
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


def hunyuan_text(file_path, sys_prompt, callback):
    cred = credential.Credential(os.environ['TENCENT_SecretId'], os.environ['TENCENT_SecretKey'])

    cpf = ClientProfile()
    # 预先建立连接可以降低访问延迟
    cpf.httpProfile.pre_conn_pool_size = 3
    client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou", cpf)

    img_pages = [file_path]

    # 转换pdf为图片，模型只支持图片格式
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    if file_extension == '.pdf':
        img_pages = conv_pdf_png(file_path)

    for img_path in img_pages:
        url = local_image_to_base64(img_path)

        req = models.ChatCompletionsRequest()
        params = {
            "Model": "hunyuan-vision",
            "Stream": True,
            "Messages": [
                {
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

        full_content = ""
        usage = {"PromptTokens": 0, "CompletionTokens": 0, "TotalTokens": 0}
        if req.Stream:  # stream 示例
            for event in resp:
                data = json.loads(event['data'])
                if 'Usage' in data:
                    usage["PromptTokens"] += data['Usage']["PromptTokens"]
                for choice in data['Choices']:
                    full_content += choice['Delta']['Content']
                    if callback:
                        callback(choice['Delta']['Content'])
        else:
            full_content = resp.Choices[0].Message.Content
            usage = resp.Usage

        logging.info(f"token耗用量：{usage} \n 返回文本：\n{full_content}")

        return full_content

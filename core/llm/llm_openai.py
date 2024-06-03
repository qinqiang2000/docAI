import json
import logging

from dotenv import load_dotenv
from openai import OpenAI

from core.common import local_image_to_data_url

load_dotenv(override=True)


class LLMOpenAI:
    def __init__(self, model, client=None, stream=False, callback=None):
        self.model = model
        self.callback = callback
        self.stream = stream
        self.isOpenai = False
        if client is None:
            self.client = OpenAI()
            self.isOpenai = True
        else:
            self.client = client

    def generate_text(self, text, sys_prompt, file_path=None):
        try:
            # 系统提示词
            msgs = [{"role": "system", "content": sys_prompt}]

            # 文档的文本
            if text and len(text) > 0:
                msgs.append({"role": "user", "content": text})
            # 文档的地址（图片格式）
            if file_path:
                image_url = local_image_to_data_url(file_path)
                m = {"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_url}}]}
                msgs.append(m)

            kwargs = {"model": self.model, "temperature": 0, "stream": self.stream, "messages": msgs}
            if self.isOpenai and self.stream:
                kwargs["stream_options"] = {"include_usage": True}

            response = self.client.chat.completions.create(**kwargs)
        except Exception as e:
            print(f"调用openai出错：{e}")
            return json.dumps({"error": "fail: 调用大模型接口出错"})

        result = ""
        if not self.stream:
            result = response.choices[0].message.content
            logging.info(f"***total tokens***: {response.usage}")
        else:
            for chunk in response:
                if 'usage' in chunk and chunk.usage:
                    logging.info(f"***total usage***: {chunk.usage}")
                if len(chunk.choices) == 0:
                    continue
                if chunk.choices[0].delta.content is None:
                    continue

                if self.callback:
                    self.callback(chunk.choices[0].delta.content)
                result += chunk.choices[0].delta.content

            if self.callback:
                self.callback("\n")

        logging.info(f"raw result: {result}")

        return result

import json
import logging

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)


class LLMOpenAI:
    def __init__(self, model, client=None, stream=False, callback=None):
        self.model = model
        self.callback = callback
        self.stream = stream
        if client is None:
            self.client = OpenAI()
        else:
            self.client = client

    def generate_text(self, text, sys_prompt):
        print("使用模型API：", self.model)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                # response_format={"type": "json_object"},
                temperature=0,
                stream=self.stream,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": text}
                ]
            )
        except Exception as e:
            print(f"调用openai出错：{e}")
            return json.dumps({"error": "fail: 调用大模型接口出错"})

        result = ""
        if not self.stream:
            result = response.choices[0].message.content
            logging.info(f"total tokens: {response.usage.total_tokens}")
        else:
            for chunk in response:
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

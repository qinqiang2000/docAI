import logging
import os
import time
import re
from enum import Enum
from openai.lib.azure import AzureOpenAI

from core.common import extract_json
from core.llm.llm_openai import LLMOpenAI
from groq import Groq


class LlmProvider(Enum):
    LLaMA3_70b_GROQ = 9
    AZURE_GPT4o = 1
    GPT4o = 8
    AZURE_GPT35 = 7
    GPT4o_V = 91
    GPT35 = 3
    # GPT4 = 2
    # MOONSHOT = 4
    # GEMINI_PRO = 5
    MOCK = 6


# option: LlmProvider类型
def pure_llm(option):
    return str(option.value).startswith('9') and option.value > 10


def is_number(value):
    return isinstance(value, (int, float))


def before_extract(text):
    return text


# 定义函数，处理json字符串不合法的情况
def remove_illegal(json_str):
    # 定义一个函数，该函数用于计算表达式并返回结果
    def eval_expression(match):
        expression = match.group(2).strip()  # 移除头尾的空白字符，包括换行符
        try:
            # 计算表达式的值
            result = eval(expression)
            # 将结果格式化为保留两位小数的字符串
            result = f"{result:.2f}"
            # 返回替换字符串，即字段名和计算后的结果
            return f'{match.group(1)}: {result}'
        except Exception as e:
            print(f"Error evaluating expression '{expression}': {e}")
            return match.group(0)  # 发生错误时返回原始匹配字符串

    # 使用正则表达式查找并替换表达式
    pattern = re.compile(r'("Total amount"|"Additional fees"|"Usage"): ([\d\.\s\+\-\*]+)', re.MULTILINE)
    updated_string = pattern.sub(eval_expression, json_str)

    return updated_string


def preprocess_json(json_str):
    # 正则表达式匹配 JSON 中数值带逗号的部分，并将逗号去掉
    json_str = re.sub(r'(\d{1,3}(,\d{3})*(\.\d+)?)', lambda x: x.group(0).replace(',', ''), json_str)
    return json_str


# 后处理
def after_extract(result):
    # 使用正则表达式移除对象最后一个字段后的逗号
    # 匹配规则：找到逗号后跟着右大括号的位置，并移除该逗号
    result = re.sub(r',(\s*})', r'\1', result)

    # 去除 JSON 字符串中的单行注释
    result = re.sub(r'//.*', '', result)

    # 去除usage产生的可能错误的JSON字符串
    result = re.sub(r'^.*?"Usage": .*? - .*(?=\n|$)', '', result, flags=re.MULTILINE)
    # 处理 JSON 字符串中的算术表达式
    result = remove_illegal(result)
    # todo: 处理数值类型的，且带千分位的
    # result = preprocess_json(result)

    ret = extract_json(result)
    return ret


# 入口，包括事前、事中、事后处理
def extract_bill(text, provider=LlmProvider.AZURE_GPT35, sys_prompt=None, callback=None):
    # 事前
    ret = before_extract(text)

    # 事中
    ret = extract(ret, provider, sys_prompt, callback=callback)

    # 事后
    return after_extract(ret)


def extract(text, provider=LlmProvider.AZURE_GPT35, sys_prompt=None, callback=None):
    if provider == LlmProvider.MOCK:
        # 模拟延时，睡眠1秒
        time.sleep(1)
        return """[
            {
                "Type": "电费",
                "Date": "2023/12/25",
                "Current reading": 11727,
                "Last reading": 11403.67,
                "Multiplier": 1,
                "Usage": 323.33,
                "Unit price": 0.008,
                "Total amount": 190.11,
                "Additional fees": 9.05
            }
        ]
    """

    # base_prompt = unify_prompt(get_prompt_template())
    logging.info(f"llm={provider}, [prompt + text]：\n{sys_prompt}\n{text}")

    if provider == LlmProvider.GPT35:
        return LLMOpenAI("gpt-3.5-turbo", None, True, callback).generate_text(text, sys_prompt)

    if provider == LlmProvider.GPT4o:
        return LLMOpenAI("gpt-4o", None, True, callback).generate_text(text, sys_prompt)

    if provider == LlmProvider.GPT4o_V:
        file_path = text
        logging.info(f"using GPT4o_V to extract file: {file_path}")
        return LLMOpenAI("gpt-4o", None, True, callback).generate_text("", sys_prompt, file_path)

    if provider == LlmProvider.LLaMA3_70b_GROQ:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
        return LLMOpenAI("llama3-70b-8192", client, True, callback).generate_text(text, sys_prompt)

    if provider == LlmProvider.AZURE_GPT4o:
        client = AzureOpenAI(
            api_key=os.environ['AZURE_OPENAI_API_KEY'],
            api_version=os.environ['OPENAI_API_VERSION'],
            azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
        )
        model = os.environ['OPENAI_DEPLOYMENT_NAME']
        print("使用模型API：Azure ", model)
        return LLMOpenAI(model, client, True, callback).generate_text(text, sys_prompt)

    if provider == LlmProvider.AZURE_GPT35:
        client = AzureOpenAI(
            api_key=os.environ['AZURE_OPENAI_GPT35_API_KEY'],
            api_version=os.environ['OPENAI_API_GPT35_VERSION'],
            azure_endpoint=os.environ['AZURE_OPENAI_GPT35_ENDPOINT']
        )
        model = os.environ['OPENAI_GPT35_DEPLOYMENT_NAME']
        print("使用模型API：Azure ", model)
        return LLMOpenAI(model, client, True, callback).generate_text(text, sys_prompt)

    return """ {"Doc Type": "LLM配置错误"}"""


def unify_prompt(prompt):
    # 保证prompt引导LLM按json数组输出
    for line in prompt.splitlines():
        line = line.lower()
        # 检查行是否包含"json"和"数组"
        if "json" in line and "数组" in line:
            return prompt
        if "json" in line and "array" in line:
            return prompt

    # 如果没有找到，添加指定的文本
    return prompt + "\n仅按json schema输出JSON数组，不包含其他文字。"


def contain_keywords(text, excludes):
    # 将关键词列表转换为正则表达式
    # 使用 \s* 来匹配关键词中可能存在的空格或换行符
    keywords_pattern = '|'.join([keyword.replace(" ", r"\s*") for keyword in excludes])
    pattern = re.compile(keywords_pattern, re.IGNORECASE)

    ret = pattern.search(text)
    return bool(ret)

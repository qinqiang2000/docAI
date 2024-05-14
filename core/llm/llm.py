import json
import os
import time
import re
from typing import Any, List
from openai.lib.azure import AzureOpenAI
from core.llm.llm_openai import LLMOpenAI
from core.common import LlmProvider


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


# 后处理
def after_extract(result):
    # 提取字符串中的json数组部分
    # result = result[result.find('['):result.rfind(']') + 1]
    # 去除 JSON 字符串中的单行注释
    result = re.sub(r'//.*', '', result)
    # 去除usage产生的可能错误的JSON字符串
    result = re.sub(r'^.*?"Usage": .*? - .*(?=\n|$)', '', result, flags=re.MULTILINE)
    # 处理 JSON 字符串中的算术表达式
    result = remove_illegal(result)

    return extract_json(result)


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
    print("使用prompt template：\n", sys_prompt)

    if provider == LlmProvider.GPT35:
        return LLMOpenAI("gpt-3.5-turbo", None, True, callback).generate_text(text, sys_prompt)

    if provider == LlmProvider.GPT4o:
        return LLMOpenAI("gpt-4o", None, True, callback).generate_text(text, sys_prompt)

    if provider == LlmProvider.GPT4o_V:
        return LLMOpenAI("gpt-4o", None, True, callback).generate_text("", sys_prompt, text)

    if provider == LlmProvider.AZURE_GPT4:
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

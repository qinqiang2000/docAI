import json
from typing import Any, Callable, Optional, Union
import pandas as pd
import difflib
import re
import logging


def compare_values(val1, val2):
    # 自定义比较函数
    def is_date(string):
        try:
            pd.to_datetime(string)
            return True
        except ValueError:
            return False

    def is_amount(string):
        if isinstance(string, float) or isinstance(string, int):
            return True
        return bool(re.match(r'^\d+(\.\d+)?$', string))

    def normalize_string(string):
        if not isinstance(string, str):
            string = str(string)
        return re.sub(r'[\s\W_]+', '', string).lower()

    # val1作为label，如果是空，则直接返回true。todo: 改为特殊标识，而非空值;
    if pd.isnull(val1):
        return True

    val1 = str(val1)
    val2 = str(val2)

    if val1 == val2:
        return True  # 直接比较字符串

    if is_date(val1) and is_date(val2):
        # 日期比较
        date1 = pd.to_datetime(val1, errors='coerce')
        date2 = pd.to_datetime(val2, errors='coerce')
        if date1 != date2:
            date2 = pd.to_datetime(val2, errors='coerce', dayfirst=True)
            logging.warning(f"调整了dayfirst：date1[{date1}] : date2[{date2}] ")
            return date1 == date2
        return True
    elif is_amount(val1) and is_amount(val2):
        # 金额比较
        amount1 = float(val1) if pd.notnull(val1) else None
        amount2 = float(val2) if pd.notnull(val2) else None
        return amount1 == amount2
    else:
        # 字符串比较，忽略大小写、空格和标点符号
        str1 = normalize_string(val1) if pd.notnull(val1) else None
        str2 = normalize_string(val2) if pd.notnull(val2) else None

        similarity = difflib.SequenceMatcher(None, str1, str2).ratio()
        return similarity >= 0.95


def flatten_json(json_obj, parent_key=''):
    items = {}
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, (dict, list)):
                items.update(flatten_json(value, new_key))
            else:
                items[new_key] = value
    elif isinstance(json_obj, list):
        for i, value in enumerate(json_obj):
            new_key = f"{parent_key}[{i}]"
            if isinstance(value, (dict, list)):
                items.update(flatten_json(value, new_key))
            else:
                items[new_key] = value
    else:
        raise ValueError("JSON对象必须是字典或列表")
    return items


def evaluate_json(prediction, reference=None):
    """
    对比prediction和reference两个JSON对象的每一个value，并返回对比结果。

    参数:
        prediction (dict or list): 预测的JSON对象或包含字典的列表。
        reference (dict或list, optional): 参考的JSON对象或包含字典的列表。

    返回:
        dict: 包含对比结果的字典，包含以下键：
            score (float): JSON所有value的compare_values为True的百分比。
            negative (list): 一个数组，存放所有compare_values为False的键及其prediction和reference的值。
            total_keys (int): 所有对比过的键的总数。
    """
    if reference is None:
        # 如果reference为空，返回0分数，并将prediction的所有key及其值放入negative数组
        return {
            "score": 0,
            "negative": [{"key": key, "prediction": prediction[key], "reference": None} for key in prediction],
            "total_keys": len(prediction)
        }

    # Flatten the JSON objects
    flattened_prediction = flatten_json(prediction)
    flattened_reference = flatten_json(reference)

    true_count = 0
    total_keys = len(flattened_reference)
    negative = []

    for key in flattened_reference:
        pred_value = flattened_prediction.get(key, None)
        ref_value = flattened_reference[key]
        if compare_values(ref_value, pred_value):
            true_count += 1
        else:
            negative.append({"key": key, "prediction": pred_value, "reference": ref_value})

    score = true_count / total_keys if total_keys > 0 else 0

    return {
        "score": score,
        "negative": negative,
        "total_keys": total_keys
    }

def evaluate_json_(prediction, reference=None):
    """
    对比prediction和reference两个JSON对象的每一个value，并返回对比结果。

    参数:
        prediction (dict or list): 预测的JSON对象或包含字典的列表。
        reference (dict or list, optional): 参考的JSON对象或包含字典的列表。

    返回:
        dict: 包含对比结果的字典，包含以下键：
            score (float): JSON所有value的compare_values为True的百分比。
            negative (list): 一个数组，存放所有compare_values为False的键及其prediction和reference的值。
    """
    if reference is None:
        # 如果reference为空，返回0分数，并将prediction的所有key及其值放入negative数组
        return {
            "score": 0,
            "negative": [{"key": key, "prediction": prediction[key], "reference": None} for key in prediction]
        }

    if isinstance(prediction, list) and isinstance(reference, list):
        total_true = 0
        total_keys = 0
        negative = []

        for pred_item, ref_item in zip(prediction, reference):
            result = evaluate_json(pred_item, ref_item)
            total_true += result['score'] * result['total_keys']
            total_keys += result['total_keys']
            negative.extend(result['negative'])

        score = total_true / total_keys if total_keys > 0 else 0
        return {
            "score": score,
            "negative": negative,
            "total_keys": total_keys  # 添加total_keys到返回结果中
        }

        # 计算总键数，包括嵌套对象中的键
    total_keys = 0
    true_count = 0
    negative = []

    for key in prediction:
        pred_value = prediction[key]
        ref_value = reference.get(key, None)
        if isinstance(pred_value, list) and isinstance(ref_value, list):
            # 递归比较列表
            result = evaluate_json(pred_value, ref_value)
            true_count += result['score'] * result['total_keys']
            total_keys += result['total_keys']
            negative.extend(result['negative'])
        else:
            total_keys += 1
            if compare_values(pred_value, ref_value):
                # 如果compare_values返回True，计数加1
                true_count += 1
            else:
                # 否则，将key及其预测值和参考值加入negative数组
                negative.append({"key": key, "prediction": pred_value, "reference": ref_value})

    score = true_count / total_keys if total_keys > 0 else 0

    print(f"==={true_count}/{total_keys}")
    return {
        "score": score,
        "negative": negative,
        "total_keys": total_keys  # 添加total_keys到返回结果中
    }


def evaluate_json_str(prediction_str, reference_str):
    """
    对比prediction_str和reference_str两个字符串类型的JSON对象，并返回对比结果。

    参数:
        prediction_str (str): 预测的JSON对象字符串。
        reference_str (str): 参考的JSON对象字符串。

    返回:
        dict: 包含对比结果的字典，包含以下键：
            score (float): JSON所有value的compare_values为True的百分比，或者直接比较两个字符串的结果。
            negative (list): 一个数组，存放所有compare_values为False的键及其prediction和reference的值，或者为空。
    """
    try:
        prediction = json.loads(prediction_str)
        reference = json.loads(reference_str)
        return evaluate_json(prediction, reference)
    except json.JSONDecodeError:
        # 无法解析为JSON时，直接调用compare_values进行字符串比较
        score = 1 if compare_values(prediction_str, reference_str) else 0
        return {
            "score": score,
            "negative": []
        }
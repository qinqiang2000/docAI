# Initialize the ExtractorManager
import json
import os

from openai.lib.azure import AzureOpenAI

from core.extractor_manager import ExtractorManager
from core.llm.llm import LlmProvider
import openpyxl
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import os
from datetime import datetime


manager = ExtractorManager("../data/extractors.json")

# 通过 extractor 的值和 ExtractorManager 的 get_extractor 获取 extractor 对象
extractor = manager.get_extractor('银行回单1')

def save_excel(root, filename, ret, out_name="a"):
    # 设置文件名
    o_file = out_name + '.xlsx'
    excel_file = os.path.join(root, o_file)

    # 检查文件是否存在
    if os.path.exists(excel_file):
        # 如果文件存在，则加载工作簿
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active
    else:
        # 如果文件不存在，则创建一个新的工作簿和工作表
        workbook = Workbook()
        sheet = workbook.active
        # 写入表头
        headers = ["文件名"] + [f"第{i}页" for i in range(1, 10)]
        sheet.append(headers)

    # 限制ret数组的长度最多为9个元素
    limited_ret = ret[:9]

    # 将列表中的每个元素转化为格式化后的JSON字符串
    formatted_ret = [json.dumps(element, ensure_ascii=False, indent=4) for element in limited_ret]

    # 创建一行数据，第一列为文件名，后面为格式化后的JSON字符串
    row_data = [filename] + formatted_ret

    # 将数据追加到工作表的末尾
    sheet.append(row_data)

    # 保存工作簿，避免中文乱码
    workbook.save(excel_file)
    print(f"Data saved to {excel_file}")


def batch_banks(root_dir):
    provider = LlmProvider.AZURE_GPT4oMini

    time_str = datetime.now().strftime("%Y%m%d_%H%M")

    # 列出 root_dir 目录下的所有文件和文件夹
    for filename in os.listdir(root_dir):
        # 获取当前文件的完整路径
        fp = os.path.join(root_dir, filename)

        # 检查是否为文件且扩展名为 .pdf
        if os.path.isfile(fp) and filename.lower().endswith('.pdf'):
            # 调用 extractor 的 run 接口
            ret = extractor.run(
                file_path=fp,
                stream_callback=None,
                llm_provider=provider)

            save_excel(root_dir, filename, ret, f"{provider.name}_"+time_str)
        break

# 示例调用
batch_banks("/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks")
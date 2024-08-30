# Initialize the ExtractorManager
import json

from groq import Groq

from core.common import extract_json
from core.llm.llm import LlmProvider
import openpyxl
from openpyxl import Workbook
import os

from test_hunyuan import hy_img_text

sys_prompt = """
根据给出图片，提取银行回单的关键字段，并以JSON格式输出。
注意：
- 如果字段没值，取空字符串为值。
- 只输出json格式的结果，不附带解释等其他内容
- 输出结果用```json和```包裹
 输出json格式：
[
  {
  "payer_name": "付款人户名、付款人姓名或付款人全称、付款人账户名称或全称",
  "payer_account_number": "付款人账号、账号",
  "payer_bank_name": "付款人开户银行、开户行名称、或银行名称的打印机构",
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

def save_excel(root, filename, ret):
    # 设置文件名为 "a.xlsx"
    excel_file = os.path.join(root, "hunyuan_vision.xlsx")

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
    print(f"[{filename}] saved")


def batch_banks(root_dir):
    # 列出 root_dir 目录下的所有文件和文件夹
    for filename in os.listdir(root_dir):
        # 获取当前文件的完整路径
        fp = os.path.join(root_dir, filename)

        if os.path.isfile(fp) and filename.lower().endswith('.png'):
            str = hy_img_text(fp, sys_prompt)
            print(str, "\n", 9*"=")
            ret = extract_json(str)
            print(ret, "\n", 9*"=")
            save_excel(root_dir, filename, ret)


# 示例调用
batch_banks("/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/img")
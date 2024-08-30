# Initialize the ExtractorManager
import json

from dotenv import load_dotenv
from groq import Groq
from openai.lib.azure import AzureOpenAI

from core.common import extract_json
from core.llm.llm import LlmProvider
import openpyxl
from openpyxl import Workbook
import os

from core.llm.llm_openai import LLMOpenAI

load_dotenv(override=True)

sys_prompt = """
根据给出的pdf提取文本，提取银行回单的关键字段，并以JSON格式输出。
    注意：
    - 如果字段没值，请留空。
    - 文本可能有错位，请智能调整。
    
    输出json格式：
    [
      {
        "serial_number": "银行流水号、交易流水号、核心流水号、流水号",
        "trade_date": "交易日期、交易时间、记账日期或时间戳。要求：只提取到日期，格式YYYY-MM-DD",
        "amount": "交易金额；要求：number格式",
        "trade_type": "交易类型、交易种类、业务种类、产品种类或回单种类",
        "payer_name": "付款人姓名、付款人户名或付款人全称、付款人账户名称或全称",
        "payer_bank_name": "付款人开户银行、开户行、或银行名称的打印机构",
        "payer_account_number": "付款人账号、账号",
        "payee_name": "收款人姓名、收款人户名或收款人全称、收款人账户名称或全称",
        "payee_bank_name": "收款人开户银行、开户行名称、或银行名称的打印机构",
        "payee_account_number": "收款人账号、账号",
        "summary": "摘要或客户附言；没有则返回 None",
        "receipt_number": "回单编号、电子回单号、回单流水号；要求：不和serial_number重复；没有则返回 None",
        "receipt_check_code": "回单校验码、回单验证码",
        "use": "用途；没有则返回 None"
      }
    ]
    
    输出要求:
    - 确保JSON数组输出答案；确保用```json 和 ```标签包装答案。
    - 只输出JSON数组，不要生成其他解释
"""

provider = LlmProvider.AZURE_GPT4o
if provider == LlmProvider.AZURE_GPT4o:
    azure_client = AzureOpenAI(
        api_key=os.environ['AZURE_OPENAI_API_KEY'],
        azure_endpoint="https://test-openai-service-wus3-rg4.openai.azure.com/",
        api_version="2024-05-01-preview"
    )
    azure_model = "gpt-4o"
else:
    azure_client = AzureOpenAI(
        api_key=os.environ['AZURE_OPENAI_GPT4oMINI_API_KEY'],
        api_version=os.environ['OPENAI_API_GPT4oMINI_VERSION'],
        azure_endpoint=os.environ['AZURE_OPENAI_GPT4oMINI_ENDPOINT']
        )
    azure_model = os.environ['OPENAI_GPT4OMIN_DEPLOYMENT_NAME']

def save_excel(root, filename, ret):
    # 设置文件名为 "a.xlsx"
    excel_file = os.path.join(root, "a.xlsx")

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

        # 检查是否为文件且扩展名为 .txt
        if os.path.isfile(fp) and filename.lower().endswith('.txt'):
            # 打开文件并读取内容
            with open(fp, 'r', encoding='utf-8') as file:
                text = file.read()

            # client = Groq(api_key=os.environ.get("GROQ_API_KEY"), )
            # str = LLMOpenAI("llama-3.1-70b-versatile", client, True, None).generate_text(text, sys_prompt)
            if not text or len(text) < 3:
                str = ""
            else:
                # str = LLMOpenAI("gpt-4o-mini").generate_text(text, sys_prompt)
                str = LLMOpenAI(azure_model, azure_client).generate_text(sys_prompt + '\n' + text, "")
            print(str, "\n", 9 * "=")
            ret = extract_json(str)
            print(ret, "\n", 9 * "=")
            save_excel(root_dir, filename, ret)


def bank_one(text):
    print("使用模型API：Azure ", azure_model)
    ret = LLMOpenAI(azure_model, azure_client).generate_text(text, sys_prompt)

    # ret = LLMOpenAI("gpt-4o-mini").generate_text(text, sys_prompt)
    print(ret)


# batch_banks("/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/ruizhen_doc")

t = """
 国内支付业务收款回单
客户号：606008453 日期：2024年01月05日
收款人账号：700375568869 付款人账号：120902063210008
收款人名称：索菲亚家居股份有限公司 付款人名称：索菲亚家居股份有限公司
收款人开户行：中国银行广州越秀支行营业部 付款人开户行：招商银行股份有限公司广州新塘支行
金额：CNY50,000,000.00
人民币伍仟万元整
报文种类：hvps.111.001.01-客户发起汇兑业务报文
业务类型：A100-普通汇兑 收支申报号：
业务标识号：2024010524000920 业务编号：
发起行行号：308581002216 接收行行号：104581003017
发起行名称：招商银行股份有限公司广州新塘支行 接收行名称：中国银行股份有限公司广东省分行
入账账号：700375568869 入账户名：索菲亚家居股份有限公司
用途：
附言：归还中行贷款 归还中行贷款
本机构吸收的本外币存款依照《存款保险条例》受到保护。
如您已通过银行网点取得相应纸质回单，请注意核对，勿重复记账！
交易机构：33519 交易渠道：其他 交易流水号：51044484-905 经办：
回单编号：2024010562319213 回单验证码：242S2CKLBZ8P 打印时间： 打印次数： 次
国内支付业务收款回单
客户号：606008453 日期：2024年03月29日
收款人账号：700375568869 付款人账号：3602075119100236474
收款人名称：索菲亚家居股份有限公司 付款人名称：索菲亚家居股份有限公司
收款人开户行：中国银行广州越秀支行营业部 付款人开户行：中国工商银行股份有限公司广州正佳支行
金额：CNY5,000,000.00
人民币伍佰万元整
报文种类：hvps.111.001.01-客户发起汇兑业务报文
业务类型：A100-普通汇兑 收支申报号：
业务标识号：2024032998436757 业务编号：
发起行行号：102581004316 接收行行号：104581010011
发起行名称：中国工商银行股份有限公司广州正佳支行 接收行名称：中国银行股份有限公司广州越秀支行
入账账号：700375568869 入账户名：索菲亚家居股份有限公司
用途：
附言：
本机构吸收的本外币存款依照《存款保险条例》受到保护。
如您已通过银行网点取得相应纸质回单，请注意核对，勿重复记账！
交易机构：33519 交易渠道：其他 交易流水号：84431484-894 经办：
回单编号：2024032967675894 回单验证码：242S32Y9P5VY 打印时间： 打印次数： 次
 """
bank_one(t)

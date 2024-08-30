import pdftotext
import pdfplumber
import fitz  # PyMuPDF

fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/上海银行_付.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/交通银行_付.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/交通银行_收.pdf"
fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/广州_收付款.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/建行_建行收付回单.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/创兴_收付回单.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/农商银行_付.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/农商银行_收.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/农业_付款.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/农业_收款.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/农业_中国农业银行企业金融服务平台.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/浦发_浦发收付回单.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/浙商银行_付.pdf"
# # fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/农商银行_收.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/工行_工行付款回单.pdf"
# fp = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks/工行_工行收款回单.pdf"

def pdftotext_test(pdf_path):
    print("\n------------------------ pdftotext ------------------------")
    # Load your PDF
    with open(pdf_path, "rb") as f:
        pdf = pdftotext.PDF(f)

    # How many pages?
    # print(len(pdf))

    # Iterate over all the pages
    for page in pdf:
        # 去除空行
        page = "\n".join([line for line in page.splitlines() if line.strip()])
        print(page)
        print("==============")

    # Read some individual pages
    # print(pdf[0])
    # print(pdf[1])

    # Read all the text into one string
    # print("\n\n".join(pdf))

def pdfplumber_test(pdf_path):
    print("\n------------------------ pdfplumber ------------------------")
    pdf = pdfplumber.open(pdf_path)
    num_pages = len(pdf.pages)
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
        # table = page.extract_table()
        # print(table)
        print('\n', 9*"=", '\n')


from pdfminer.high_level import extract_text
def pdfminer_test(pdf_path):
    try:
        text = extract_text(pdf_path)
        print(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None


def tabula_test(pdf_path):
    print("\n------------------------ tabula ------------------------")

    import tabula

    # Read pdf into list of DataFrame
    dfs = tabula.read_pdf(pdf_path, pages='all')
    for df in dfs:
        markdown_str = df.to_markdown(index=False)
        print(markdown_str)


print(f"[---{fp}---]")

pdfplumber_test(fp)
# tabula_test(fp)
pdftotext_test(fp)
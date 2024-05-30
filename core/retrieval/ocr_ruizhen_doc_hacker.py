import os
import requests
import time
from docx import Document
from dotenv import load_dotenv, set_key

load_dotenv(override=True)


class DocumentHacker:
    def __init__(self, access_token=None):
        if access_token:
            self.access_token = access_token
        else:
            self.access_token = os.getenv('RUIZHEN_WEB_TOKEN')
        self.headers = {
            'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://regenai.glority.cn/engine/document_reduction',
            'sec-ch-ua-platform': '"macOS"'
        }

    def get_access_token(self, username='13714962604',
                         password='9262bc9cf6a33916fd56b4602d76a4492f9a561414a331ba6a7ced4d16292957'):
        url = 'https://regenai.glority.cn/sso/login'
        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'origin': 'https://regenai.glority.cn',
            'referer': 'https://regenai.glority.cn/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        data = {
            'username': username,
            'password': password
        }

        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()

        if response_data.get('result') == 1 and 'response' in response_data:
            self.access_token = response_data['response']['data']['access_token']
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            set_key('.env', 'RUIZHEN_WEB_TOKEN', self.access_token)
        else:
            raise Exception("Failed to get access token: " + response_data.get('message', 'Unknown error'))

    def upload_image(self, file_path):
        url = 'https://regenai.glority.cn/api/v1/document/upload'

        with open(file_path, 'rb') as file:
            files = {
                'fileList': (file_path.split('/')[-1], file, 'image/png')
            }
            response = requests.post(url, headers=self.headers, files=files)

        if 'invalid_token' in response.text:
            return "A001"
        return response.json()

    def check_document_status(self, document_uid):
        url = f'https://regenai.glority.cn/api/v1/document/result?document_uid={document_uid}'
        retry = 12
        while retry > 0:
            retry -= 1
            response = requests.get(url, headers=self.headers)
            response_json = response.json()

            if response_json['result'] == 1:
                status = response_json['response']['data']['status']
                name = response_json['response']['data']['name']
                print(f"File[{name}]: current status: {status}")
                if status == "SUCCESS":
                    print(f"File[{name}]: Document processing completed successfully.")
                    return True
            else:
                print(f"Error: {response_json['message']}")
                break

            time.sleep(0.5)
        return False

    def export_document_to_word(self, document_uid, path):
        os.makedirs(path, exist_ok=True)

        url = f'https://regenai.glority.cn/api/v1/document/export?document_uid={document_uid}&export_type=word'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            file_path = f"{path}/{document_uid}.docx"
            with open(file_path, 'wb') as f:
                f.write(response.content)
                print(f"Word document has been successfully saved to {file_path}")

            return self.extract_text_data_from_docx(file_path)
        else:
            print(f"Failed to export document. Status code: {response.status_code}, Response: {response.text}")
            return None

    @staticmethod
    def extract_text_data_from_docx(docx_path):
        doc = Document(docx_path)
        full_text = []

        # Traverse the document to maintain the order of paragraphs, tables, and text boxes
        def recursive_extract(element):
            for child in element:
                if child.tag.endswith('p'):
                    para_text = ''.join([node.text for node in child.findall('.//w:t', namespaces=doc.element.nsmap)])
                    full_text.append(para_text)
                elif child.tag.endswith('tbl'):
                    for row in child.findall('.//w:tr', namespaces=doc.element.nsmap):
                        row_text = []
                        for cell in row.findall('.//w:tc', namespaces=doc.element.nsmap):
                            cell_text = ''.join(
                                [node.text for node in cell.findall('.//w:t', namespaces=doc.element.nsmap)])
                            row_text.append(cell_text)
                        full_text.append('\t'.join(row_text))
                elif child.tag.endswith('txbxContent'):
                    recursive_extract(child)

        recursive_extract(doc.element.body)

        return '\n'.join(full_text)

    @staticmethod
    def clean_empty_line(text):
        lines = text.splitlines()
        cleaned_lines = []
        previous_line_empty = False

        for line in lines:
            if line.strip():
                cleaned_lines.append(line)
                previous_line_empty = False
            else:
                if not previous_line_empty:
                    cleaned_lines.append('')
                previous_line_empty = True

        return '\n'.join(cleaned_lines)

    def process_document(self, file_path, save_path='tmp'):
        upload_response = self.upload_image(file_path)
        if upload_response == "A001":
            self.get_access_token()
            upload_response = self.upload_image(file_path)

        if 'response' in upload_response and 'data' in upload_response['response']:
            document_uid = upload_response['response']['data']['uid']
            success = self.check_document_status(document_uid)
            if not success:
                return None
            text_data = self.export_document_to_word(document_uid, save_path)
            print(f"[Text data]\n {text_data}")
            cleaned_text = self.clean_empty_line(text_data)
            return cleaned_text
        else:
            print(f"Failed to upload image. Response: {upload_response}")
            return None


# 这里增加main
if __name__ == "__main__":
    # 使用示例
    processor = DocumentHacker()

    # 处理文档，包括上传、检查状态、导出和文本提取
    # return: None， 表示不成功
    text = processor.process_document('/Users/qinqiang02/job/客户/百胜新财务影像和档案系统/poc/缴费通知单1/86002212.png')
    print(text)

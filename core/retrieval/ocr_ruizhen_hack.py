import json
import logging
import os
import requests
import time
from dotenv import load_dotenv, set_key

from core.retrieval.ocr_ruizhen import extract_text

load_dotenv(override=True)

# 请求的URL
hack_url = 'https://regenai.glority.cn/api/v1/general/fetch?language='
token = os.getenv('RUIZHEN_WEB_TOKEN')


# 设置请求头
def mk_headers():
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'Authorization': f'Bearer {token}',
        'Cookie': f'ACCESS_TOKEN={token}; REFRESH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiIxMzcxNDk2MjYwNCIsInNjb3BlIjpbInNlcnZlciJdLCJhdGkiOiJmZmIyMzU5MS0zYzhmLTQwNWQtOGViNS1lNWI3NDYwMTcxMjciLCJpZCI6ODY0MSwiZXhwIjoxNzE2MzY4NjA2LCJhdXRob3JpdGllcyI6WyJST0xFX0RJU1RSSUJVVE9SIiwiUk9MRV9MQUJFTCJdLCJqdGkiOiJhZWY4ZTMwOS1kNzQ1LTQ2NTUtOTZhMi1iMTczZWNhNWQ2YzkiLCJjbGllbnRfaWQiOiJnbG9yaXR5LW9hdXRoIn0.eqA-2rDNtQAFZbra-3Bfodi6MWE2MDiZkFZxklZ1VKY',
        'Origin': 'https://regenai.glority.cn'
    }
    return headers


def get_access_token(username=None, password=None):
    if not username:
        username = '13714962604'
        password = '9262bc9cf6a33916fd56b4602d76a4492f9a561414a331ba6a7ced4d16292957'

    url = 'https://regenai.glority.cn/sso/login'
    headers = {
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://regenai.glority.cn',
        'priority': 'u=1, i',
        'referer': 'https://regenai.glority.cn/',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    data = {
        'username': username,
        'password': password
    }

    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

    if response_data.get('result') == 1 and 'response' in response_data:
        return response_data['response']['data']['access_token']
    else:
        raise Exception("Failed to get access token: " + response_data.get('message', 'Unknown error'))


def ruizhen_hack_ocr(img_path, lang):
    global token
    url = hack_url + lang.name

    # 准备文件和数据
    files = {
        'image_file': (os.path.basename(img_path), open(img_path, 'rb'), 'application/pdf')
    }

    ret = ""
    retry = 2
    for i in range(retry):
        try:
            # 发起请求
            logging.info(f"[{i}/{retry}] Requesting OCR from {url} with {img_path}")
            response = requests.post(url, files=files, headers=mk_headers())

            # 如果response.text包含invalid_token，则需要重新获取token并更新headers
            if 'invalid_token' in response.text:
                token = get_access_token()
                set_key('.env', 'RUIZHEN_WEB_TOKEN', token)
                continue

            ret = json.loads(response.text)
            ret = extract_text(ret)
            break
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error: {e}")
            time.sleep(1)
            continue

    # 关闭文件
    files['image_file'][1].close()
    return ret

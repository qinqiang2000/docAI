from core.common import OCRProvider

print(OCRProvider.RuiZhen.value, OCRProvider.RuiZhen.name)

import re


def remove_cid(text):
    # 使用正则表达式匹配所有的 (cid:X) 模式，其中 X 为数字
    # 并将它们替换为空字符串
    cleaned_text = re.sub(r'\(cid:\d+\)', '', text)
    return cleaned_text


# 示例文本
sample_text = """(cid:4)(cid:5)(cid:20)(cid:2)(cid:11)(cid:3)(cid:24)(cid:5)(cid:4)(cid:3)(cid:5)(cid:15)(cid:2)(cid(cid:6)(cid:7)(cid:7)(cid:2)(cid:8)(cid:3)(cid:10)(cid:9)(cid:5)(cid:10)(cid:6)(cid:7)(cid:11)(cid:14)(cid:7)(cid:12)(cid:12)(cid:17)(cid:8)(cid:5)(cid:3)
JRFAX1 I(cid:2)N(cid:3)V(cid:4)O(cid:5)I(cid:2)(cid:6)C(cid:7)E(cid:8) (cid:3)N(cid:9)U(cid:10)M(cid:11)B(cid:7)E(cid:12)R(cid:8)
JRFAX1
(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:5)(cid:10)(cid:11)(cid:12)(cid:5)(cid:13)(cid:14)(cid:11)(cid:5)(cid:3)(cid:6)(cid:8)(cid:15)(cid:4)(cid:12)(cid:16)(cid:5)(cid:17)(cid:4)(cid:10)(cid:8)(cid:18)(cid:6)(cid:17)(cid:19)
(cid:20)(cid:4)(cid:21)(cid:22)(cid:8)(cid:23)(cid:24)(cid:19)(cid:25)(cid:26)(cid:27)(cid:19)(cid:28)(cid:29)(cid:27)(cid:19)(cid:29)(cid:30)(cid:26)(cid:26)(cid:8)(cid:8)(cid:31)(cid:8)(cid:8)(cid:32)(cid:33)(cid:34)(cid:22)(cid:8)(cid:23)(cid:24)(cid:19)(cid:25)(cid:26)(cid:27)(cid:19)(cid:27)(cid:26)(cid:35)(cid:19)(cid:35)(cid:24)(cid:28)(cid:24)(cid:8)(cid:31)(cid:8)(cid:36)(cid:36)(cid:36)(cid:19)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:9)(cid:5)(cid:10)(cid:11)(cid:12)(cid:5)(cid:13)(cid:14)(cid:11)(cid:5)(cid:3)(cid:6)(cid:19)(cid:17)(cid:3)(cid:37)
(cid:12)(cid:23)(cid:16)(cid:27)(cid:28)(cid:8)(cid:28)(cid:14)(cid:8)(cid:29)(cid:30)(cid:30)(cid:15)(cid:23)(cid:31)(cid:31)(cid:32)(cid:8)(cid:38)(cid:38)(cid:29)(cid:38)(cid:28)(cid:8)(cid:39)(cid:34)(cid:40)(cid:4)(cid:41)(cid:5)(cid:11)(cid:4)(cid:8)(cid:42)(cid:33)(cid:43)(cid:44)(cid:8)(cid:45)(cid:46)(cid:5)(cid:17)(cid:33)(cid:7)(cid:3)(cid:44)(cid:8)(cid:18)(cid:47)(cid:8)(cid:30)(cid:26)(cid:30)(cid:28)(cid:27)(cid:48)(cid:26)(cid:26)(cid:26)(cid:24)
PAGE 1 OF 2
(cid:33)(cid:27)(cid:15)(cid:23)(cid:8)(cid:2)(cid:34)(cid:31)(cid:28)(cid:15)(cid:35)(cid:36)(cid:28)(cid:27)(cid:14)(cid:34)(cid:31)(cid:32)(cid:8)(cid:2)(cid:3)(cid:4)(cid:5)(cid:6)(cid:7)(cid:8)(cid:9)(cid:5)(cid:10)(cid:11)(cid:12)(cid:5)(cid:13)(cid:14)(cid:11)(cid:5)(cid:3)(cid:6)(cid:8)(cid:15)(cid:4)(cid:12)(cid:16)(cid:5)(cid:17)(cid:4)(cid:10)(cid:8)(cid:18)(cid:6)(cid:17)(cid:19)(cid:8)(cid:31)(cid:8)(cid:49)(cid:50)(cid:51)(cid:3)(cid:12)(cid:7)(cid:33)(cid:6)(cid:8)(cid:45)(cid:46)(cid:33)(cid:10)(cid:4)(cid:8)(cid:2)(cid:33)(cid:6)(cid:52)(cid:8)(cid:53)(cid:4)(cid:36)(cid:8)(cid:54)(cid:3)(cid:12)(cid:52)
(cid:55)(cid:2)(cid:55)(cid:22)(cid:8)(cid:26)(cid:29)(cid:24)(cid:26)(cid:26)(cid:26)(cid:26)(cid:29)(cid:24)(cid:8)(cid:8)(cid:31)(cid:8)(cid:8)(cid:55)(cid:17)(cid:17)(cid:3)(cid:14)(cid:6)(cid:11)(cid:22)(cid:8)(cid:25)(cid:26)(cid:56)(cid:30)(cid:25)(cid:28)(cid:29)(cid:35)(cid:25)(cid:8)(cid:31)(cid:8)(cid:15)(cid:42)(cid:18)(cid:32)(cid:20)(cid:22)(cid:8)(cid:45)(cid:57)(cid:55)(cid:15)(cid:58)(cid:15)(cid:25)(cid:25)(cid:8)(cid:31)(cid:8)(cid:45)(cid:57)(cid:18)(cid:50)(cid:8)(cid:58)(cid:18)(cid:9)(cid:22)(cid:8)(cid:26)(cid:26)(cid:26)(cid:29)
(cid:18)(cid:2)(cid:20)(cid:4)(cid:6)(cid:10)(cid:2)(cid:21) (cid:18)(cid:22)(cid:11)(cid:16)(cid:6)(cid:10)(cid:2)(cid:21)
024089
TAIKOO (XIAMEN) AIRCRAFT TAIKOO (XIAMEN) AIRCRAFT
ATTN: TAIKOO (XIAMEN) AIRCRAFT
GAOQL INT’L AIRPORT GAOQL INT’L AIRPORT
XIAMEN 361006 XIAMEN 361006
PEOPLE’S REPUBLIC OF CHINA PEOPLE’S REPUBLIC OF CHINA
(cid:2)(cid:3)(cid:4)(cid:5)(cid:3)(cid:6)(cid:7)(cid:2)(cid:8) (cid:4)(cid:9)(cid:10)(cid:5) (cid:18)(cid:22)(cid:11)(cid:16)(cid:6)(cid:24)(cid:11)(cid:9) (cid:10)(cid:5)(cid:3)(cid:12)(cid:18) (cid:18)(cid:22)(cid:11)(cid:16)(cid:16)(cid:11)(cid:7)(cid:25)(cid:6)(cid:10)(cid:5)(cid:3)(cid:12)(cid:18)
C1900304/R 03/20/19 BOLLORE IN GERMANY NET 45 FCA-SELLER’S WHSE
(cid:11)(cid:10)(cid:5)(cid:12) (cid:13)(cid:14)(cid:9)(cid:7)(cid:10)(cid:11)(cid:10)(cid:15) (cid:16)(cid:9)(cid:3)(cid:10)(cid:6)(cid:7)(cid:14)(cid:12)(cid:17)(cid:5)(cid:3)(cid:6)(cid:9)(cid:7)(cid:4)(cid:6)(cid:4)(cid:5)(cid:18)(cid:19)(cid:3)(cid:11)(cid:16)(cid:10)(cid:11)(cid:2)(cid:7) (cid:16)(cid:3)(cid:11)(cid:19)(cid:5) (cid:14)(cid:7)(cid:11)(cid:10) (cid:17)(cid:9)(cid:19)(cid:23)(cid:6)(cid:2)(cid:3)(cid:4)(cid:5)(cid:3) (cid:18)(cid:22)(cid:11)(cid:16)(cid:16)(cid:5)(cid:4) (cid:9)(cid:12)(cid:2)(cid:14)(cid:7)(cid:10)
(cid:7)(cid:2)(cid:8) (cid:2)(cid:3)(cid:4)(cid:5)(cid:3)(cid:5)(cid:4)
FED. TAX# 47-163-9172
2 ROCOL AEROSPEC PROTECT SPRAY 25.000 CA 0 2 50.00
Commercial PN: ROCOL AEROSPEC PROTECT SPRAY
HEAVY DUTY WAXY FILM LEIGHT BEIGE
Container Size: 300ML
ECCN :EURNL
Country Origin: UK
TARIFF: 34039900
MFR: ROCOL LUBRICANTS
CTRL# : 2018K15644
LOT# : 25841J18
LOT QTY: 2
**REF: ROCOL AEROSPEC PROTECT SPRAY
VAT exempt export sale according to sec. 4 no. 1 a) German VAT Code
Ultimate Destination
TAIKOO (XIAMEN) AIRCRAFT
GAOQL INT’L AIRPORT
XIAMEN
361006
PEOPLE’S REPUBLIC OF CHINA
***CONTINUED***
(cid:12)(cid:9)(cid:10)(cid:5)(cid:3)(cid:11)(cid:9)(cid:20)(cid:6)(cid:10)(cid:2)(cid:6)(cid:17)(cid:5)(cid:6)(cid:3)(cid:5)(cid:10)(cid:14)(cid:3)(cid:7)(cid:5)(cid:4)(cid:6)(cid:12)(cid:14)(cid:18)(cid:10)(cid:6)(cid:22)(cid:9)(cid:24)(cid:5)(cid:6)(cid:16)(cid:3)(cid:11)(cid:2)(cid:3)(cid:6)(cid:9)(cid:14)(cid:10)(cid:22)(cid:2)(cid:3)(cid:11)(cid:30)(cid:9)(cid:10)(cid:11)(cid:2)(cid:7)(cid:6)(cid:17)(cid:15)(cid:6)(cid:17)(cid:2)(cid:5)(cid:11)(cid:7)(cid:25)(cid:6)(cid:4)(cid:11)(cid:18)(cid:10)(cid:3)(cid:11)(cid:17)(cid:14)(cid:10)(cid:11)(cid:2)(cid:7)(cid:6)(cid:18)(cid:5)(cid:3)(cid:24)(cid:11)(cid:19)(cid:5)(cid:18)(cid:6)(cid:11)(cid:7)(cid:19)(cid:8)
(cid:9)(cid:20)(cid:20)(cid:6)(cid:11)(cid:10)(cid:5)(cid:12)(cid:18)(cid:6)(cid:9)(cid:3)(cid:5)(cid:6)(cid:18)(cid:14)(cid:17)(cid:26)(cid:5)(cid:19)(cid:10)(cid:6)(cid:10)(cid:2)(cid:6)(cid:9)(cid:6)(cid:27)(cid:28)(cid:28)(cid:29)(cid:6)(cid:3)(cid:5)(cid:18)(cid:10)(cid:2)(cid:19)(cid:23)(cid:11)(cid:7)(cid:25)(cid:6)(cid:19)(cid:22)(cid:9)(cid:3)(cid:25)(cid:5)(cid:8)
SHIPPED FROM: KISDORFER WEG 36-38, 24568, KALTENKIRCHEN, GERMANY
VAT REGISTERED ADDRESS:BOEING DISTRIBUTION SERVICES INC 10000 N.W. 15TH TERRACE, MIAMI, FL 33172
ORIGINAL COPY
BY RECEIVING DELIVERY OF THE ITEMS COVERED BY THIS INVOICE, BUYER AGREES TO THE TERMS AND CONDITIONS OF SALE AT:
https://www.boeingdistribution.com/content/conditions-sale
(cid:13)(cid:14)(cid:15)(cid:16)(cid:8)(cid:17)(cid:18)(cid:18)(cid:8)(cid:19)(cid:20)(cid:21)(cid:13)(cid:22)(cid:8)(cid:12)(cid:23)(cid:24)(cid:8)(cid:25)(cid:26)(cid:18)"""


def check_cid_percentage(text):
    # 计算文本中CID字符的比例
    cid_matches = re.findall(r'\(cid:\d+\)', text)
    cid_length = sum(len(match) for match in cid_matches)
    total_length = len(text)

    # 计算比例
    percentage = cid_length / total_length * 100
    return percentage


print("CID字符的比例:", check_cid_percentage(sample_text))

cleaned_text = remove_cid(sample_text)
print("清理后的文本:", cleaned_text)

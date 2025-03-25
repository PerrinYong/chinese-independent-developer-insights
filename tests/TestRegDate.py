import re

date_pattern = re.compile(r'^###\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})(?:\s*(号|日))?\s*(?:&.*)?\s*添加\s*$')

# 测试日期字符串
test_dates = [
    "### 2018年9月13号 & 14号添加",
    "### 2018年5月22号 & 23号 & 24号添加",
    "### 2018年4月23号 & 24号添加",
    "### 2018年4月11号 & 12号添加",
    "### 2018年4月3号 & 4号添加",
    "### 2018年4月1号 & 2号添加",
    "### 2018年3月29号 & 30号添加",
    "### 2018年3月27号 & 28号添加",
    "### 2018年3月25号 & 26号添加"
]

# 迭代匹配
for date_str in test_dates:
    match = date_pattern.match(date_str)
    if match:
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
        print(f"年份: {year}, 月份: {month}, 日期: {day}")

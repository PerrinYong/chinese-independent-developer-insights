import re
import csv
from datetime import datetime

import models

text = ""
# 读取README.md文件
with open('README.md', 'r', encoding='utf-8') as f:
    text = f.read()


# 预处理，替换中文冒号为英文
text = text.replace('：', ":")

with open('README.md.processed', 'w', encoding='utf-8') as f:
    f.write(text)

with open('README.md.processed', 'r', encoding='utf-8') as f:
    text = f.read()


# 初始化数据存储
data = []
current_date = None
current_author = None
current_location = ""
current_github = ""
current_blog = ""

# 增强版正则表达式模式
date_pattern = re.compile(r'^### (\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 号添加\s*$')
date_pattern = re.compile(r'^###\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*[号|日]添加\s*$')
date_pattern = re.compile(r'^###\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})(?:\s*(号|日))?\s*(?:&.*)?\s*添加\s*$')
date_pattern = re.compile(r'^###\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*[号|日]?\s*(?:&.*)?\s*添加\s*$')

author_pattern = re.compile(
    r'^#### ([^(]+)(?:\(([^)]+)\))?\s*-?\s*(?:\[Github\]\(([^)]*)\))?\s*,?\s*(?:\[博客\]\(([^)]*)\))?\s*$'
)
author_pattern = re.compile(
    r'^#### ([^(]+)(?:\(([^)]+)\))?\s*-?\s*(?:\[Github\]\(([^)]+)\))?\s*(?:,\s*\[Twitter(?:/X)?\]\(([^)]+)\))?\s*(?:,\s*\[博客\]\(([^)]+)\))?\s*$'
)

author_pattern = re.compile(
    r'^#### ([^(]+)(?:\(([^)]+)\))?\s*-?\s*(?:\[[Gg]ithub\]\(([^)]+)\))?\s*(?:[,|，]?\s*\[博客\]\(([^)]+)\))?\s*$'
)


project_pattern = re.compile(
    r'^\* ：white_check_mark: \[([^\]]+)\]\(([^)]+)\)\s*：\s*(.*?)(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)

project_pattern1 = re.compile(
    r'^\* :white_check_mark: \[([^\]]+)\]\(([^)]+)\)\s*：\s*(.*?)(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)


# project_pattern = re.compile(
#     r'^\* :white_check_mark: \[([^\]]+)\]\(([^)]+)\)\s*：\s*(.*?)(?:\s*- \[更多介绍\]\(([^)]+)\))?(?:\s*-? \[更多介绍\]\(([^)]+)\))?',
#     re.DOTALL
# )

# project_pattern = re.compile(
#     r'\* :white_check_mark: \[([^\]]+)\]\(([^)]+)\)\s*：\s*((?:.|\n)*?)(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$'
# )

project_pattern = re.compile(
    r'^[\*-] :(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*：\s*((?:.|\n)*?)(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)
project_pattern = re.compile(
    r'^[\*\-] :(?:white_check_mark|x): \[([^\]\)]+)\]\(([^)]+)\)\s*：\s*((?:.|\n)*?)'
    r'(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)
project_pattern = re.compile(
    r'^[\*-] :(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*：\s*((?:.|\n)*?)(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)
project_pattern = re.compile(
    r'^[\*-] :(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*：\s*((?:.|\n)*?)(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)

project_pattern = re.compile(
    r'^[\*-] :(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*：\s*((?:.|\n)*?)(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)
# 允许中英文冒号
project_pattern = re.compile(
    r'^[\*-] :(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*[：:]\s*((?:.|\n)*?)(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)

# 去除对 - 的要求
project_pattern = re.compile(
    r'^[\*-] :(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*[:：]\s*((?:.|\n)*?)(?:\s*\[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)

project_pattern = re.compile(
    r'^[\*-]\s*:(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*[:：]\s*((?:.|\n)*?)(?:\s*\[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)
# 宽容策略正则表达式：匹配方括号里的内容作为项目名，匹配小括号里的内容作为链接
fallback_pattern = re.compile(
    r'\[([^\]]+)\]\(([^)]+)\)'
)
fallback_pattern = re.compile(
    r'\[([^\]]+)\]\(([^)]+)\)(?:\s*(.*))?'  # 这里匹配了小括号后的描述内容
)


# project_pattern = re.compile(
#     r'^[\*-]\s+:\s*(?:white_check_mark|x):\s+\[([^\]]+)\]\(([^)]+)\)\s*：\s*((?:.|\n)*?)(?:\s*-\s*\[更多介绍\]\(([^)]+)\))?\s*$',
#     re.DOTALL
# )


# project_pattern = re.compile(
#     r"""
#     ^\*                       # 起始星号
#     \s*:\s*                   # 可能存在的空格（兼容中英文排版）
#     (white_check_mark|x)      # 状态标识（提升为第一捕获组）
#     :\s*                      # 结束冒号和空格
#     \[([^\]]+)\]              # 项目名称（第二捕获组）
#     \(([^)]+)\)               # 主链接（第三捕获组）
#     \s*：\s*                  # 中文冒号分隔符
#     (.*?)                     # 描述内容（第四捕获组，非贪婪匹配）
#     (?:\s*-\[更多介绍\]       # 可选更多介绍开始
#     \(([^)]*)\))?             # 更多介绍链接（第五捕获组）
#     \s*$                      # 行尾空格
#     """, 
#     re.VERBOSE | re.MULTILINE | re.DOTALL
# )

# pattern = r"""
# ^\*                      # 起始星号
# \s*:\s*(white_check_mark|x):  # 状态标志（强制英文冒号）
# \s+                      # 分隔空格
# \[([^\]]+)\]             # 项目名称（捕获组1）
# \(([^)]+)\)              # 主链接URL（捕获组2）
# ：\s*                    # 中文冒号分隔符（注意全角字符）
# ([^\n-]*)                # 主要描述（捕获组3，匹配到换行或短横线前）
# (?:\s+-\s+\[更多介绍\]\(([^)]*)\))?  # 可选更多介绍链接（捕获组4）
# """
# project_pattern = re.compile(pattern)

# project_pattern = re.compile(
#     r'^[\*-]\s*(?:white_check_mark|x):\s*\[([^\]]+)\]\(([^)]+)\)(?:\s*：\s*((?:.|\n)*?))?(?:\s*- \[更多介绍\]\(([^)]+)\))?\s*$',
#     re.DOTALL
# )



# 不兼容行计数：
failed_proj_cnt = 0

with open("项目匹配失败行.txt", "w", encoding="utf-8") as f:  # 使用追加模式，避免覆盖
    # 清空文件
    f.write("")

failed_line_file = open("项目匹配失败行.txt", "a", encoding="utf-8")  # 使用追加模式，避免覆盖


# 解析文本
lines = text.split('\n')
i = 0

current_date = None
# 重置作者信息
current_author = None
current_location = None
current_github = None
current_blog = None


def process_date(line):
    if date_pattern.match(line):
        year, month, day ="","",""
        try:
            year, month, day = date_pattern.match(line).groups()
        except:
            return False

        current_date = f"{int(year)}-{int(month):02d}-{int(day):02d}"
        # 重置作者信息

    else:
        return False
    
    return True

def process_author(line):
    match = author_pattern.match(line.strip())
    
    if match:
        # 解析作者和城市
        author_city = match.group(1).strip()  # 作者名+城市信息
        current_location = match.group(2) or ""  # 城市（如果有）

        # 分离作者名和城市信息
        if '(' in author_city and ')' in author_city:
            # 如果括号内有城市信息，则分开作者名和城市
            current_author = re.sub(r'\(.*?\)', '', author_city).strip()  # 去除城市信息
            current_location = re.search(r'\((.*?)\)', author_city).group(1)  # 获取城市
        else:
            # 如果没有城市信息，作者名就是整个 `author_city`
            current_author = author_city
            current_location = ""

        # 获取 Github、Twitter 和博客链接
        current_github = match.group(3) or ""  # Github链接
        current_blog = match.group(4) or ""  # 博客链接

    else:
        # 如果正则没有匹配到作者信息，将整行文字作为作者名称
        current_author = line.strip().replace(',','')
        current_location = ""
        current_github = ""
        current_blog = ""
        return False


while i < len(lines):
    line = lines[i].strip()
    line = line.replace("\r\n", "\n")  # 处理 Windows 的换行符

    # 匹配日期行
    if line.startswith("###") and not line.startswith("####"):
        if process_date(line):
            i += 1
            continue
        else:
            print("日期识别失败")
            print(line)
            failed_line_file.write(line+"\n")
            i += 1
            continue


            
    
    # 匹配作者信息
    if line.startswith("####"):


        i += 1
        continue
    
    # 匹配项目信息
    match = project_pattern.match(line)
    if (line.startswith('*')or line.startswith('-')) and (line.__contains__("white_check_mark") or line.__contains__(":x:") ):
        project_name, project_url, description, more_info = '','','',''

        if match:
            project_name, project_url, description, more_info = match.groups()
            # 清理数据
            project_name = project_name.strip()
            project_url = project_url.strip()
            description = re.sub(r'\s+', ' ', (description or '').strip())
            more_info = (more_info or "").strip()
            # print("project_name: ", project_name)
            # print("project_url: ", project_url)
            # print("description: ", description)
            # print("more_info: ", more_info)

        else:
            # 写入匹配失败的行
            print(f"项目匹配失败行：{line}")
            fallback_match = fallback_pattern.search(line)
            if fallback_match:
                print(f"宽容匹配成功！\n标题: {fallback_match.group(1)}\n链接: {fallback_match.group(2)}\n描述: {description}\n")   
                project_name = fallback_match.group(1)
                project_url = fallback_match.group(2)
                description = fallback_match.group(3) if fallback_match.group(3) else '无描述'
            else:
                print(f"fallback匹配失败：{line}\n")
                project_name = line

            



        data.append([
            current_date,
            current_author,
            current_location,
            current_github if current_github else "N/A",  # 如果GitHub为空填充 "N/A"
            current_blog if current_blog else "N/A",  # 如果博客为空填充 "N/A"
            project_name if project_name else "N/A",  # 如果项目名为空填充 "N/A"
            project_url if project_url else "N/A",  # 如果项目链接为空填充 "N/A"
            description if description else "No description",  # 如果描述为空填充 "No description"
            more_info if more_info else "No more info"  # 如果更多介绍为空填充 "No more info"
        ])

    
    i += 1

# 写入CSV文件
headers = [
    '添加日期', '作者', '城市', 'Github链接', '博客链接',
    '项目名称', '项目链接', '项目简介', '更多介绍链接'
]

with open('indie_projects_full.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(data)

print(f"转换完成，共处理 {len(data)} 个项目")
print("项目匹配失败行数：", failed_proj_cnt)
# print("示例数据：")
# print(headers)
# print(data[0] if data else "无数据")

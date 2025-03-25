import re
import csv
from datetime import datetime
from models import Author, Project
# import logging
import sys
import logging
import os

# 创建一个logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

# 创建一个控制台输出处理器
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

# 创建一个日志格式器
formatter = logging.Formatter('%(levelname)s: %(message)s')
ch.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(ch)

logger.log(logging.DEBUG, "This is a debug message")
logger.log(logging.INFO, "This is a info message")
logger.log(logging.WARNING, "This is a warning message")
logger.log(logging.ERROR, "This is a error message")
logger.log(logging.CRITICAL, "This is a critical message")





date_pattern = re.compile(r'^###\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*[号|日]?\s*(?:&.*)?\s*添加\s*$')

author_pattern = re.compile(
    r'^#### ([^(]+)(?:\(([^)]+)\))?\s*-?\s*(?:\[[Gg]ithub\]\(([^)]+)\))?\s*(?:[,|，]?\s*\[博客\]\(([^)]+)\))?\s*$'
)
author_pattern = re.compile(
    r'^#### ([^(]+)(?:\(([^)]+)\))?\s*-?\s*(?:\[[Gg]ithub\]\(([^)]+)\))?\s*(?:[,|，]?\s*\[博客\]\(([^)]+)\))?\s*$'
)


project_pattern = re.compile(
    r'^[\*-]\s*:(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*[:：]\s*((?:.|\n)*?)(?:\s*\[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)

# 宽容策略正则表达式：匹配方括号里的内容作为项目名，匹配小括号里的内容作为链接

fallback_pattern = re.compile(
    r'\[([^\]]+)\]\(([^)]+)\)(?:\s*(.*))?'  # 这里匹配了小括号后的描述内容
)


# 初始化数据存储
data = []

# 不兼容行计数：
failed_date_cnt = 0
failed_author_cnt = 0
failed_proj_cnt = 0

current_date = None
# 重置作者信息
current_author = None
authors = []
current_project = None
projects = []




def process_date(line):
    logger.log(logging.INFO, f"process date {line} ")
    global current_date
    if date_pattern.match(line):
        year, month, day ="","",""
        try:
            year, month, day = date_pattern.match(line).groups()
        except:
            return False

        current_date = f"{int(year)}-{int(month):02d}-{int(day):02d}"
        # 重置作者信息

    else:
        current_date = line
        return False
    
    return True


def process_author(line):
    logger.log(logging.INFO, f"process author  {line} ")
    match = author_pattern.match(line.strip())
    global current_author, authors
    current_author = Author()
    authors.append(current_author)
    current_author.dataline = line

    # 1. 提取作者名字：根据是否包含 `[` 来判断
    if "[" in line:
        # 如果包含 `[`, 提取 `####` 到第一个 `[` 之间的内容
        author_info_match = re.match(r'^####\s*([^\[]+)', line.strip())
        if author_info_match:
            author_info = author_info_match.group(1).replace('-', '').strip()
            # 如果作者信息中包含城市信息，分离作者名和城市
            if '(' in author_info and ')' in author_info:
                current_author.name = re.sub(r'\(.*?\)', '', author_info).strip()
                current_author.location = re.search(r'\((.*?)\)', author_info).group(1)
            else:
                current_author.name = author_info
        else:
            logger.log(logging.ERROR, f"未能匹配到作者名：{line}")
            return False
    else:
        # 如果没有 `[`, 直接将 `####` 后的内容作为作者名
        current_author.name = line.strip().replace('####', '').strip()

 # 2. 提取 Github 链接
    github_match = re.search(r'\[([Gg]it[Hh]ub)\]\((\s*https?://[^\)]+)\)', line)
    if github_match:
        current_author.github = github_match.group(2)  # 获取 URL 部分
        # 去除右边的括号
        if current_author.github.endswith(')'):
            current_author.github = current_author.github[:-1]

        logger.log(logging.INFO, f"Github匹配成功：{current_author.github}")
    else:
        if "[github]" in line.lower():
            logger.log(logging.ERROR, f"Github匹配失败：{line}")
            return False
        

    # 3. 提取博客链接
    blog_match = re.search(r'\[博客\]\((.*)', line)
    if blog_match:
        current_author.blog = blog_match.group(1)  # 获取 URL 部分
        logger.log(logging.INFO, f"博客匹配成功：{current_author.blog}")
    else:
        if "[博客]" in line.lower():
            logger.log(logging.ERROR, f"博客匹配失败：{line}")

    # 打印提取的信息
    logger.log(logging.INFO, f"处理后的作者信息：{current_author.name}, Github: {current_author.github}, 博客: {current_author.blog}")

    return True


# def process_author(line):
#     logger.log(logging.INFO, f"process author  {line} ")
#     match = author_pattern.match(line.strip())
#     global current_author, authors
#     current_author = Author()
#     authors.append(current_author)
#     current_author.dataline = line
#     if match:
#         # 解析作者和城市
#         author_city = match.group(1).strip()  # 作者名+城市信息
#         current_location = match.group(2) or ""  # 城市（如果有）

#         # 分离作者名和城市信息
#         if '(' in author_city and ')' in author_city:
#             # 如果括号内有城市信息，则分开作者名和城市
#             current_author.name = re.sub(r'\(.*?\)', '', author_city).strip()  # 去除城市信息
#             current_author.location = re.search(r'\((.*?)\)', author_city).group(1)  # 获取城市
#         else:
#             # 如果没有城市信息，作者名就是整个 `author_city`
#             current_author.name = author_city

#         # 获取 Github、Twitter 和博客链接
#         current_author.github = match.group(3) or ""  # Github链接
#         current_author.blog = match.group(4) or ""  # 博客链接

#         if current_author.github == "" and current_author.name.__contains__("github"):
#             return False

#     else:
#         # 如果正则没有匹配到作者信息，将整行文字作为作者名称
#         current_author.name = line.strip().replace(',','')
#         return False

#     return False


def process_project(line):
    logger.log(logging.INFO, f"process project  {line} ")
    global current_project, projects
    project_name, project_url, description, more_info = '','','',''
    current_project = Project()
    projects.append(current_project)
    current_project.dataline = line
    current_project.date = current_date

    if current_author is None:
        raise Exception("作者信息为空！")
    else:
        current_project.author = current_author
    match = project_pattern.match(line)

    if match:
        project_name, project_url, description, more_info = match.groups()
        current_project.name = project_name.strip()
        current_project.url = project_url.strip()
        current_project.description = re.sub(r'\s+', ' ', (description or '').strip())
        current_project.more_info = (more_info or "").strip()

    else:
        fallback_match = fallback_pattern.search(line)
        if fallback_match:
            logger.log(logging.INFO, f"宽容匹配成功！\n标题: {fallback_match.group(1)}\n链接: {fallback_match.group(2)}\n描述: {description}\n")   
            current_project.name = fallback_match.group(1)
            current_project.url = fallback_match.group(2)
            current_project.description = fallback_match.group(3) if fallback_match.group(3) else '无描述'
        else:
            logger.log(logging.ERROR, f"fallback匹配失败：{line}\n")
            current_project.name = line
            return False

    return True


OrignalFile1 = "README-Programmer-Edition.md"
Target1 = "独立开发（程序员）.csv"
OrignalFile2 = "README.md"
Target2 = "独立开发（一般人员）.csv"
def process(Org, Tgt):

    # 初始化全局数据
    global data 
    data = []
    global failed_date_cnt 
    failed_date_cnt = 0
    global failed_author_cnt 
    failed_author_cnt = 0
    global failed_proj_cnt 
    failed_proj_cnt = 0

    global current_date, current_author, authors, current_project, projects
    current_date = None
    current_author = None
    authors = []
    current_project = None
    projects = []
    

    text = ""
    # 读取README.md文件
    # with open('README.md', 'r', encoding='utf-8') as f:
    with open(Org, 'r', encoding='utf-8') as f:
        text = f.read()


    # 预处理，替换中文冒号为英文
    text = text.replace('：', ":")




    with open("failed.txt", "w", encoding="utf-8") as f:  # 使用追加模式，避免覆盖
        # 清空文件
        f.write("")

    failed_line_file = open("failed.txt", "a", encoding="utf-8")  # 使用追加模式，避免覆盖


    # 解析文本
    lines = text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        line = line.replace("\r\n", "\n")  # 处理 Windows 的换行符

        # 匹配日期行
        if line.startswith("###") and not line.startswith("####"):
            if process_date(line):
                i += 1
                continue
            else:
                logger.log(logging.ERROR, "日期识别失败")
                logger.log(logging.ERROR, line)
                failed_line_file.write(line+"\n")
                failed_date_cnt += 1
                i += 1
                continue

        # 匹配作者信息
        if line.startswith("####"):
            if process_author(line):
                i += 1
                continue
            else:
                logger.log(logging.ERROR, "作者识别失败")
                logger.log(logging.ERROR, line)
                failed_line_file.write(line+"\n")
                failed_author_cnt += 1
                i += 1
                continue

        # 匹配项目信息
        if (line.startswith('*')or line.startswith('-')) and (line.__contains__("white_check_mark") or line.__contains__(":x:") ):
            if process_project(line):
                i += 1
                continue
            else:
                logger.log(logging.ERROR, "项目识别失败")
                logger.log(logging.ERROR, line)
                failed_line_file.write(line+"\n")
                failed_proj_cnt += 1
                i += 1
                continue

        i += 1
                
            

    logger.log(logging.INFO, f"转换完成，共处理 {len(data)} 个项目")
    logger.log(logging.INFO, f"项目匹配失败行数：{ failed_proj_cnt}")
    logger.log(logging.INFO, f"作者匹配失败行数：{ failed_author_cnt}")
    logger.log(logging.INFO, f"日期匹配失败行数：{ failed_date_cnt}")

    # 写入CSV文件
    headers = [
        'ID','添加日期', '作者', '位置', 'Github链接', '博客链接',
        '项目名称', '项目链接', '项目简介', '更多介绍链接', 'dataline'
    ]

    cnt=0
    for project in projects:
        cnt+=1

        try:
            data.append([
                cnt,
                project.date,
                project.author.name,
                project.author.location,
                project.author.github,
                project.author.blog,
                project.name,
                project.url,
                project.description,
                project.more_info,
                project.dataline
            ])

        except Exception as e:
            
            logger.log(logging.ERROR, f"output project {cnt} failed")
            # log e
            logger.log(logging.ERROR, e)
            logger.log(logging.ERROR, f"project line: {project.dataline}")
            break


    # target_file = Org.replace(".md", ".csv")

    with open(Tgt, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)


    failed_line_file.close()

process(OrignalFile1, Target1)
process(OrignalFile2, Target2)

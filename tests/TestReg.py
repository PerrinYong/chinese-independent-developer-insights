import re

# 原正则表达式，尝试精确匹配
project_pattern = re.compile(
    r'^[\*-]\s*:(?:white_check_mark|x):\s*\[([^\]]+)\]\(([^)]+)\)\s*[:：]\s*((?:.|\n)*?)(?:\s*\[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)

# 宽容策略正则表达式：匹配方括号里的内容作为项目名，匹配小括号里的内容作为链接，提取描述为小括号后的所有内容
fallback_pattern = re.compile(
    r'\[([^\]]+)\]\(([^)]+)\)\s*(?:\((.*?)\))?'
)
fallback_pattern = re.compile(
    r'\[([^\]]+)\]\(([^)]+)\)(?:\s*(.*))?'  # 这里匹配了小括号后的描述内容
)

# 测试数据
test_lines = [
    "* :white_check_mark: [网页版屏保小工具](https://www.screensaver.top/zh)",
    "* :white_check_mark: [One-Click SEO Links](https://chromewebstore.google.com/detail/jllecdngjonjinaffdjdcojfdikimdlj?authuser=0&hl=zh-TW) (Chrome 插件）帮助站长进行 SEO 外链推广。包含全自动模式、半自动模式和人工模式，在外链推广的复杂填表场景能节省大量时间。",
    "* :white_check_mark: [亲戚称呼计算器](https://passer-by.com/relationship/) “中国亲戚关系计算器”为你避免了叫错、不会叫亲戚的尴尬，收录了中国亲戚关系称呼大全，只需简单的输入即可完成称呼计算。称呼计算器同时兼容了不同地域的方言叫法，你可以称呼父亲为:“老爸”、“爹地”、“老爷子”等等。让您准确的叫出亲戚称谓，理清亲属之间的亲戚关系，轻松掌握中国式的亲戚关系换算，让你更了解中国文化 - [更多介绍](https://github.com/mumuy/relationship)",
    "* :white_check_mark: [Siphon 吸词](https://siphon.ink/)，安装 Siphon 浏览器插件后，在线英文阅读中如果遇到生词，只要双击单词即可翻译并自动加入到生词本中，记录生词的同时会记录上下文句子。然后可以在 siphon 网站通过多种方式复习生词。能够帮用户养成微习惯:双击查单词->自动收藏单词->卡片复习记忆 - [更多介绍](https://siphon.ink/docs/)"
]

# 匹配并输出结果
for line in test_lines:
    match = project_pattern.match(line)
    if match:
        print(f"匹配成功！\n标题: {match.group(1)}\n链接: {match.group(2)}\n描述: {match.group(3)}\n更多介绍: {match.group(4)}\n")
    else:
        print(f"匹配失败，尝试宽容策略...\n")
        fallback_match = fallback_pattern.search(line)
        if fallback_match:
            print(f"宽容匹配成功！\n标题: {fallback_match.group(1)}\n链接: {fallback_match.group(2)}\n描述: {fallback_match.group(3) if fallback_match.group(3) else '无描述'}\n")
        else:
            print(f"匹配失败：{line}\n")

# import re

# lines = []
# with open("项目匹配失败行.txt", "r", encoding="utf-8") as f:
#     lines = f.readlines()

# project_pattern = re.compile(
#     r'^[\*-] :(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*[:：]\s*((?:.|\n)*?)(?:\s*\[更多介绍\]\(([^)]+)\))?\s*$',
#     re.DOTALL
# )

# failed_proj_cnt = 0
# for line in lines:
#     match = project_pattern.match(line)
#     if match:
#         print("匹配成功！")
#         print(f"标题: {match.group(1)}")
#         print(f"链接: {match.group(2)}")
#         print(f"描述: {match.group(3)}")
#         print(f"更多介绍: {match.group(4)}")
#     else:
#         print("匹配失败！")
#         print(f"原始输入: {line}")
#         failed_proj_cnt += 1
# print(
#     f"共有 {failed_proj_cnt} 行匹配失败！"
# )


# # 测试字符串
# test_string = "* :white_check_mark: [BoilerplateHunt](https://boilerplatehunt.com)：SaaS模板导航站，找到最合适的模板，加速你的SaaS上线。"

# # 简化版正则表达式
# simple_pattern = re.compile(
#     r'^[\*-] :(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*：\s*((?:.|\n)*?)$',
#     re.DOTALL
# )

# # 测试匹配
# match = simple_pattern.match(test_string)

# if match:
#     print("匹配成功！")
#     print(f"标题: {match.group(1)}")
#     print(f"链接: {match.group(2)}")
#     print(f"描述: {match.group(3)}")
# else:
#     print("匹配失败！")
#     print(f"原始输入: {test_string}")

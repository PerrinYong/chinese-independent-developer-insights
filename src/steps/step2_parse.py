import logging
import os
import sys
import csv
import re
from datetime import datetime

# 添加项目根目录到路径，确保可以导入src包
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config.settings import BatchManager, LOG_LEVEL
from src.extraction.models import Author, Project

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 正则表达式模式
date_pattern = re.compile(r'^###\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*[号|日]?\s*(?:&.*)?\s*添加\s*$')
author_pattern = re.compile(
    r'^#### ([^(]+)(?:\(([^)]+)\))?\s*-?\s*(?:\[[Gg]ithub\]\(([^)]+)\))?\s*(?:[,|，]?\s*\[博客\]\(([^)]+)\))?\s*$'
)
project_pattern = re.compile(
    r'^[\*-]\s*:(?:white_check_mark|x): \[([^\]]+)\]\(([^)]+)\)\s*[:：]\s*((?:.|\n)*?)(?:\s*\[更多介绍\]\(([^)]+)\))?\s*$',
    re.DOTALL
)
fallback_pattern = re.compile(
    r'\[([^\]]+)\]\(([^)]+)\)(?:\s*(.*))?'
)

class ReadmeParser:
    """README解析器类"""
    def __init__(self):
        self.data = []
        self.authors = []
        self.projects = []
        self.current_date = None
        self.current_author = None
        self.failed_counts = {
            'date': 0,
            'author': 0,
            'project': 0
        }
        self.failed_lines = []
        self.stats = {
            "total_projects": 0,
            "total_authors": 0,
            "parsing_started": datetime.now().isoformat(),
        }

    def process_date(self, line):
        """处理日期行"""
        match = date_pattern.match(line)
        if match:
            year, month, day = match.groups()
            self.current_date = f"{int(year)}-{int(month):02d}-{int(day):02d}"
            return True
        else:
            self.current_date = line
            return False

    def process_author(self, line):
        """处理作者行"""
        match = author_pattern.match(line.strip())
        self.current_author = Author()
        self.authors.append(self.current_author)
        self.current_author.dataline = line

        # 提取作者名字
        if "[" in line:
            author_info_match = re.match(r'^####\s*([^\[]+)', line.strip())
            if author_info_match:
                author_info = author_info_match.group(1).replace('-', '').strip()
                if '(' in author_info and ')' in author_info:
                    self.current_author.name = re.sub(r'\(.*?\)', '', author_info).strip()
                    self.current_author.location = re.search(r'\((.*?)\)', author_info).group(1)
                else:
                    self.current_author.name = author_info
            else:
                logger.error(f"未能匹配到作者名：{line}")
                return False
        else:
            self.current_author.name = line.strip().replace('####', '').strip()

        # 提取 Github 链接
        github_match = re.search(r'\[([Gg]it[Hh]ub)\]\((\s*https?://[^\)]+)\)', line)
        if github_match:
            self.current_author.github = github_match.group(2).strip()
            if self.current_author.github.endswith(')'):
                self.current_author.github = self.current_author.github[:-1]
        elif "[github]" in line.lower():
            logger.error(f"Github匹配失败：{line}")
            return False

        # 提取博客链接
        blog_match = re.search(r'\[博客\]\((.*?)\)', line)
        if blog_match:
            self.current_author.blog = blog_match.group(1)
        elif "[博客]" in line:
            logger.error(f"博客匹配失败：{line}")

        return True

    def process_project(self, line):
        """处理项目行"""
        current_project = Project()
        self.projects.append(current_project)
        current_project.dataline = line
        current_project.date = self.current_date
        
        # 关联当前作者
        current_project.author = self.current_author

        if self.current_author is None:
            logger.error("作者信息为空！")
            return False
        
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
                current_project.name = fallback_match.group(1)
                current_project.url = fallback_match.group(2)
                current_project.description = fallback_match.group(3) if fallback_match.group(3) else '无描述'
            else:
                logger.error(f"项目匹配失败：{line}")
                current_project.name = line
                return False
        
        return True

    def parse_file(self, file_path):
        """解析README文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            # 预处理，替换中文冒号为英文
            text = text.replace('：', ":")
                
            # 解析文本
            lines = text.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                line = line.replace("\r\n", "\n")  # 处理 Windows 的换行符
                
                # 匹配日期行
                if line.startswith("###") and not line.startswith("####"):
                    if not self.process_date(line):
                        logger.error(f"日期识别失败: {line}")
                        self.failed_counts['date'] += 1
                        self.failed_lines.append(line)
                    i += 1
                    continue
                
                # 匹配作者信息
                elif line.startswith("####"):
                    if not self.process_author(line):
                        logger.error(f"作者识别失败: {line}")
                        self.failed_counts['author'] += 1
                        self.failed_lines.append(line)
                    i += 1
                    continue
                
                # 匹配项目信息
                elif (line.startswith('*') or line.startswith('-')) and \
                     (":white_check_mark:" in line or ":x:" in line):
                    if not self.process_project(line):
                        logger.error(f"项目识别失败: {line}")
                        self.failed_counts['project'] += 1
                        self.failed_lines.append(line)
                    i += 1
                    continue
                
                i += 1
            
            # 更新统计信息
            self.stats["total_projects"] = len(self.projects)
            self.stats["total_authors"] = len(self.authors)
            self.stats["parsing_completed"] = datetime.now().isoformat()
            self.stats["failed_counts"] = self.failed_counts
            
            logger.info(f"解析完成: {file_path}")
            logger.info(f"共解析项目数: {len(self.projects)}")
            logger.info(f"失败统计 - 日期: {self.failed_counts['date']}, " 
                        f"作者: {self.failed_counts['author']}, "
                        f"项目: {self.failed_counts['project']}")
            
            return True
            
        except Exception as e:
            logger.error(f"解析文件异常: {e}")
            return False
    
    def export_to_csv(self, output_path):
        """导出解析结果到CSV"""
        try:
            headers = [
                'ID', '添加日期', '作者', '位置', 'Github链接', '博客链接',
                '项目名称', '项目链接', '项目简介', '更多介绍链接', 'dataline'
            ]
            
            data = []
            for i, project in enumerate(self.projects, 1):
                author = project.author if hasattr(project, 'author') else None
                
                data.append([
                    i,  # ID
                    project.date or "",
                    author.name if author else "",
                    author.location if author and hasattr(author, 'location') else "",
                    author.github if author else "",
                    author.blog if author else "",
                    project.name or "",
                    project.url or "",
                    project.description or "",
                    project.more_info or "",
                    project.dataline or ""
                ])
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
                
            logger.info(f"数据已成功导出到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出CSV异常: {e}")
            return False
    
    def export_failed_lines(self, output_path):
        """导出解析失败的行到文本文件"""
        try:
            if not self.failed_lines:
                logger.info("没有解析失败的行需要导出")
                return True
                
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.failed_lines))
            logger.info(f"失败行已导出到: {output_path}")
            return True
        except Exception as e:
            logger.error(f"导出失败行异常: {e}")
            return False

def parse_readme_files(batch_id=None):
    """
    解析指定批次的README文件并生成CSV
    
    Args:
        batch_id: 批次ID，如果为None则使用最新批次
    
    Returns:
        str or False: 操作成功返回批次ID，失败返回False
    """
    try:
        # 在parse_readme_files函数中添加
        if batch_id is None:
            try:
                batch_id = BatchManager.get_latest_batch_id()
                logger.info(f"未提供批次ID，使用最新批次: {batch_id}")
            except FileNotFoundError:
                logger.error("未找到有效批次，请先运行爬取数据步骤")
                print("\n❌ 错误: 未找到有效数据批次，请先执行爬取数据步骤 (python main.py fetch)\n")
                return False
                
        # 获取批次的raw和parsed目录
        raw_dir = BatchManager.get_raw_dir(batch_id)
        parsed_dir = BatchManager.get_parsed_dir(batch_id)
        
        # 定义要处理的README文件
        readme_files = {
            "README.md": "独立开发（一般人员）.csv",
            "README-Programmer-Edition.md": "独立开发（程序员）.csv"
        }
        
        success = False
        for readme_file, output_csv in readme_files.items():
            input_path = os.path.join(raw_dir, readme_file)
            output_path = os.path.join(parsed_dir, output_csv)
            failed_lines_path = os.path.join(parsed_dir, f"{readme_file}_failed_lines.txt")
            
            if os.path.exists(input_path):
                logger.info(f"开始解析文件: {input_path}")
                
                parser = ReadmeParser()
                if parser.parse_file(input_path):
                    parser.export_to_csv(output_path)
                    parser.export_failed_lines(failed_lines_path)
                    logger.info(f"成功解析 {readme_file} 并导出到 {output_path}")
                    success = True
                else:
                    logger.error(f"解析 {readme_file} 失败")
            else:
                logger.warning(f"文件不存在: {input_path}")
        
        # 更新批次状态
        if success:
            BatchManager.update_batch_status(batch_id, "parsed", "parse")
            logger.info(f"批次 {batch_id} 的解析操作成功完成")
            return batch_id
        else:
            BatchManager.update_batch_status(batch_id, "failed_parsing", None)
            logger.error(f"批次 {batch_id} 的解析操作失败")
            return False
            
    except Exception as e:
        logger.exception(f"解析过程中发生错误: {e}")
        return False

def main():
    """主入口函数"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        batch_id = sys.argv[1]
        logger.info(f"使用指定批次ID: {batch_id}")
    else:
        batch_id = None
        logger.info("未指定批次ID，将使用最新批次")
    
    # 执行解析
    result_batch_id = parse_readme_files(batch_id)
    
    if result_batch_id:
        logger.info(f"数据解析成功! 批次ID: {result_batch_id}")
        logger.info(f"解析数据保存在: {BatchManager.get_parsed_dir(result_batch_id)}")
        return 0
    else:
        logger.error("数据解析失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
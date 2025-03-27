import os
import logging
import time
import base64
import urllib3
import requests
from github import Github
from github.GithubException import RateLimitExceededException

# 配置日志
logger = logging.getLogger(__name__)

class GitHubFetcher:
    def __init__(self, github_token, disable_proxy=False):
        """
        初始化GitHub爬取器
        
        Args:
            github_token: GitHub API访问令牌
            disable_proxy: 是否禁用代理
        """
        # 处理代理设置
        if disable_proxy:
            self._disable_proxy()
            
        self.github = Github(github_token)
        
    @staticmethod
    def _disable_proxy():
        """禁用系统代理设置"""
        os.environ['NO_PROXY'] = 'api.github.com,github.com'
        if 'HTTP_PROXY' in os.environ:
            del os.environ['HTTP_PROXY']
        if 'HTTPS_PROXY' in os.environ:
            del os.environ['HTTPS_PROXY']
            
        # 重置urllib3连接池
        urllib3.disable_warnings()
        urllib3.util.connection.HAS_IPV6 = False
        
        # 设置requests库不使用代理
        session = requests.Session()
        session.trust_env = False
    
    def _handle_rate_limit(self):
        """处理API速率限制"""
        try:
            rate_limit = self.github.get_rate_limit()
            reset_timestamp = rate_limit.core.reset.timestamp()
            sleep_time = max(1, reset_timestamp - time.time() + 10)  # 多等10秒，确保重置完成
            logger.warning(f"API速率限制已达到，等待{sleep_time}秒后重试")
            time.sleep(sleep_time)
        except Exception as e:
            logger.warning(f"获取API速率限制信息失败: {e}，将等待60秒")
            time.sleep(60)
    
    def get_repo(self, repo_name):
        """
        获取GitHub仓库
        
        Args:
            repo_name: 仓库名称，格式为 "用户名/仓库名"
            
        Returns:
            GitHub仓库对象
        """
        try:
            return self.github.get_repo(repo_name)
        except Exception as e:
            logger.error(f"获取仓库 {repo_name} 失败: {e}")
            if "404" in str(e):
                logger.error(f"仓库 {repo_name} 不存在，请检查仓库名称")
            elif "403" in str(e):
                logger.error(f"无权访问仓库 {repo_name}，请检查GitHub Token权限")
            raise
    
    def get_file_content(self, repo, file_path):
        """
        获取指定文件内容
        
        Args:
            repo: GitHub仓库对象
            file_path: 文件路径
            
        Returns:
            文件内容字符串，失败时返回None
        """
        try:
            contents = repo.get_contents(file_path)
            content = base64.b64decode(contents.content).decode('utf-8')
            logger.info(f"成功获取{file_path}文件内容")
            return content
        except RateLimitExceededException:
            self._handle_rate_limit()
            return self.get_file_content(repo, file_path)
        except Exception as e:
            logger.error(f"获取{file_path}时出错: {e}")
            return None
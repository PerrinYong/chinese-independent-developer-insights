import os
import logging
from github import Github
from github.GithubException import RateLimitExceededException
import time
import base64
from src.config.settings import GITHUB_TOKEN, GITHUB_REPO, README_PATH, PROGRAMMER_README_PATH, RAW_DATA_DIR

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubFetcher:
    def __init__(self):
        self.github = Github(GITHUB_TOKEN)
        self.repo = self.github.get_repo(GITHUB_REPO)
        
    def _handle_rate_limit(self):
        """处理API速率限制"""
        rate_limit = self.github.get_rate_limit()
        reset_timestamp = rate_limit.core.reset.timestamp()
        sleep_time = max(1, reset_timestamp - time.time() + 10)  # 多等10秒，确保重置完成
        logger.warning(f"API速率限制已达到，等待{sleep_time}秒后重试")
        time.sleep(sleep_time)
    
    def get_file_content(self, file_path):
        """获取指定文件内容"""
        try:
            contents = self.repo.get_contents(file_path)
            content = base64.b64decode(contents.content).decode('utf-8')
            logger.info(f"成功获取{file_path}文件内容")
            return content
        except RateLimitExceededException:
            self._handle_rate_limit()
            return self.get_file_content(file_path)
        except Exception as e:
            logger.error(f"获取{file_path}时出错: {e}")
            return None
    
    def fetch_and_save_files(self):
        """获取并保存README文件"""
        readme_content = self.get_file_content(README_PATH)
        programmer_readme_content = self.get_file_content(PROGRAMMER_README_PATH)
        
        if readme_content:
            readme_path = os.path.join(RAW_DATA_DIR, "README.md")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            logger.info(f"已保存README.md至{readme_path}")
        
        if programmer_readme_content:
            programmer_readme_path = os.path.join(RAW_DATA_DIR, "README-Programmer-Edition.md")
            with open(programmer_readme_path, 'w', encoding='utf-8') as f:
                f.write(programmer_readme_content)
            logger.info(f"已保存README-Programmer-Edition.md至{programmer_readme_path}")
        
        return bool(readme_content or programmer_readme_content)

if __name__ == "__main__":
    fetcher = GitHubFetcher()
    fetcher.fetch_and_save_files()
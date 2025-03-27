import logging
import os
import sys

# 添加项目根目录到路径，确保可以导入src包
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config.settings import (
    GITHUB_TOKEN, GITHUB_REPO, README_PATH, PROGRAMMER_README_PATH,
    BatchManager, LOG_LEVEL
)
from src.extraction.github_fetcher import GitHubFetcher

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_and_save_files(batch_id=None, disable_proxy=True):
    """
    获取并保存GitHub README文件
    
    Args:
        batch_id: 批次ID，如果为None则创建新批次
        disable_proxy: 是否禁用代理
        
    Returns:
        批次ID或False
    """
    try:
        # 如果未提供batch_id，则创建新批次
        if batch_id is None:
            batch_id = BatchManager.create_batch()
            logger.info(f"已创建新批次: {batch_id}")
        
        # 获取批次的raw目录
        raw_dir = BatchManager.get_raw_dir(batch_id)
        
        # 创建GitHub抓取器，并禁用代理（如有需要）
        fetcher = GitHubFetcher(GITHUB_TOKEN, disable_proxy=disable_proxy)
        
        # 获取仓库
        try:
            repo = fetcher.get_repo(GITHUB_REPO)
        except Exception as e:
            logger.error(f"无法访问GitHub仓库: {e}")
            BatchManager.update_batch_status(batch_id, "failed", None)
            return False
        
        # 获取并保存README文件
        readme_content = fetcher.get_file_content(repo, README_PATH)
        programmer_readme_content = fetcher.get_file_content(repo, PROGRAMMER_README_PATH)
        
        success = False
        if readme_content:
            readme_path = os.path.join(raw_dir, "README.md")
            os.makedirs(os.path.dirname(readme_path), exist_ok=True)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            logger.info(f"已保存README.md至{readme_path}")
            success = True
        
        if programmer_readme_content:
            programmer_readme_path = os.path.join(raw_dir, "README-Programmer-Edition.md")
            os.makedirs(os.path.dirname(programmer_readme_path), exist_ok=True)
            with open(programmer_readme_path, 'w', encoding='utf-8') as f:
                f.write(programmer_readme_content)
            logger.info(f"已保存README-Programmer-Edition.md至{programmer_readme_path}")
            success = True
        
        # 更新批次状态
        if success:
            BatchManager.update_batch_status(batch_id, "fetched", "fetch")
            logger.info(f"批次 {batch_id} 的GitHub数据获取成功")
            return batch_id
        else:
            BatchManager.update_batch_status(batch_id, "failed", None)
            logger.error(f"批次 {batch_id} 的GitHub数据获取失败")
            return False
    
    except Exception as e:
        logger.exception(f"数据获取过程中发生错误: {e}")
        if batch_id:
            BatchManager.update_batch_status(batch_id, "failed", None)
        return False

def main():
    """主入口函数"""
    # 检查命令行参数
    disable_proxy = True  # 默认禁用代理
    batch_id = None
    
    for arg in sys.argv[1:]:
        if arg.startswith('--batch-id='):
            batch_id = arg.split('=')[1]
        elif arg == '--use-proxy':
            disable_proxy = False
    
    if batch_id:
        logger.info(f"使用指定批次ID: {batch_id}")
    else:
        logger.info("未指定批次ID，将创建新批次")
    
    logger.info(f"代理设置: {'禁用' if disable_proxy else '启用'}")
    
    # 执行爬取
    result_batch_id = fetch_and_save_files(batch_id, disable_proxy)
    
    if result_batch_id:
        logger.info(f"数据爬取成功! 批次ID: {result_batch_id}")
        logger.info(f"原始数据保存在: {BatchManager.get_raw_dir(result_batch_id)}")
        return 0
    else:
        logger.error("数据爬取失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
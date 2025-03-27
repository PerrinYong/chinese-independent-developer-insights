import logging
import os
from datetime import datetime
from src.extraction.github_fetcher import GitHubFetcher
from src.extraction.parsers import process_readme_files
from src.config.settings import PROCESSED_DATA_DIR

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline():
    """运行完整数据处理管道"""
    try:
        logger.info("开始执行数据处理管道...")
        
        # 步骤1: 从GitHub获取README文件
        logger.info("步骤1: 从GitHub获取README文件")
        fetcher = GitHubFetcher()
        if not fetcher.fetch_and_save_files():
            logger.error("获取GitHub文件失败，中止处理")
            return False
        
        # 步骤2: 解析README文件并导出为CSV
        logger.info("步骤2: 解析README文件并导出为CSV")
        if not process_readme_files():
            logger.error("解析README文件失败，中止处理")
            return False
        
        # 完成
        logger.info("数据处理管道执行完成")
        
        # 输出处理结果路径
        for file in os.listdir(PROCESSED_DATA_DIR):
            if file.endswith(".csv"):
                logger.info(f"生成的CSV文件: {os.path.join(PROCESSED_DATA_DIR, file)}")
        
        return True
        
    except Exception as e:
        logger.error(f"执行处理管道时发生错误: {e}")
        return False

if __name__ == "__main__":
    run_pipeline()
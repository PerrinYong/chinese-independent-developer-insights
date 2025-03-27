import logging
import os
import sys
import time
from datetime import datetime

# 添加项目根目录到路径，确保可以导入src包
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config.settings import BatchManager, LOG_LEVEL
from src.steps.step1_fetch import GitHubFetcher
from src.steps.step2_parse import parse_readme_files

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_full_pipeline(force_new_batch=False):
    """
    运行完整数据处理流水线
    
    Args:
        force_new_batch: 是否强制创建新批次
    
    Returns:
        str or False: 成功返回批次ID，失败返回False
    """
    start_time = time.time()
    logger.info("开始执行完整数据处理流水线...")
    
    try:
        # 步骤1: 从GitHub获取数据
        logger.info("步骤1: 从GitHub获取数据...")
        fetcher = GitHubFetcher()
        
        if force_new_batch:
            batch_id = None  # 这会触发创建新批次
        else:
            # 检查是否有最新批次且未完成处理
            try:
                latest_id = BatchManager.get_latest_batch_id()
                metadata = BatchManager.get_batch_metadata(latest_id)
                
                if "fetch" in metadata.get("steps_completed", []) and "parse" not in metadata.get("steps_completed", []):
                    # 有批次已完成爬取但未完成解析，可以继续使用
                    batch_id = latest_id
                    logger.info(f"检测到有未完成处理的批次 {batch_id}，将继续使用该批次")
                else:
                    # 创建新批次
                    batch_id = None
            except Exception:
                # 出错了就创建新批次
                batch_id = None
        
        # 执行数据获取
        batch_id = fetcher.fetch_and_save_files(batch_id)
        if not batch_id:
            logger.error("步骤1失败: 无法从GitHub获取数据，中止流程")
            return False
            
        # 步骤2: 解析README文件并生成CSV
        logger.info(f"步骤2: 解析README文件并生成CSV，使用批次: {batch_id}...")
        if not parse_readme_files(batch_id):
            logger.error("步骤2失败: 解析README文件失败，中止流程")
            return False
            
        # 完成所有步骤
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"数据处理流水线执行完成! 总耗时: {duration:.2f}秒")
        logger.info(f"批次ID: {batch_id}")
        logger.info(f"原始数据: {BatchManager.get_raw_dir(batch_id)}")
        logger.info(f"解析数据: {BatchManager.get_parsed_dir(batch_id)}")
        
        # 更新批次状态为已完成
        BatchManager.update_batch_status(batch_id, "completed", None)
        
        return batch_id
        
    except Exception as e:
        logger.exception(f"执行流水线时发生错误: {e}")
        return False

def main():
    """主入口函数"""
    # 处理命令行参数
    force_new = "--force-new" in sys.argv
    
    result = run_full_pipeline(force_new_batch=force_new)
    
    if result:
        logger.info("流水线执行成功!")
        return 0
    else:
        logger.error("流水线执行失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
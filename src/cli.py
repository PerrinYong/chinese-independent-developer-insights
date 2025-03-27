import sys
import argparse
import logging
import os
from datetime import datetime

# 将项目根目录添加到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config.settings import BatchManager, LOG_LEVEL
from src.steps.step1_fetch import GitHubFetcher
from src.steps.step2_parse import parse_readme_files
from src.steps.run_pipeline import run_full_pipeline

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def list_batches(args):
    """列出所有批次"""
    try:
        batches = []
        batches_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "batches")
        
        if os.path.exists(batches_dir):
            batch_ids = sorted([d for d in os.listdir(batches_dir) 
                             if os.path.isdir(os.path.join(batches_dir, d))],
                             reverse=True)
            
            for batch_id in batch_ids:
                metadata_file = os.path.join(batches_dir, batch_id, "metadata.json")
                created_at = "Unknown"
                status = "Unknown"
                
                if os.path.exists(metadata_file):
                    try:
                        import json
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        created_at = metadata.get("created_at_human", "Unknown")
                        status = metadata.get("status", "Unknown")
                    except:
                        pass
                
                batches.append({
                    'id': batch_id,
                    'created_at': created_at,
                    'status': status
                })
        
        if not batches:
            print("没有找到任何数据批次。")
            return 0
            
        print(f"\n找到 {len(batches)} 个数据批次:")
        print("-" * 80)
        print(f"{'批次ID':20} | {'创建时间':25} | {'状态':<15}")
        print("-" * 80)
        
        for batch in batches:
            print(f"{batch['id']:20} | {batch['created_at']:25} | {batch['status']:<15}")
            
        print("-" * 80)
        print("\n使用 '--batch-id BATCH_ID' 参数指定要处理的批次\n")
        return 0
    except Exception as e:
        logger.exception(f"列出批次时出错: {e}")
        return 1

def fetch_data(args):
    """执行数据爬取步骤"""
    try:
        batch_id = args.batch_id
        disable_proxy = not getattr(args, 'use_proxy', False)
        
        from src.steps.step1_fetch import fetch_and_save_files
        result = fetch_and_save_files(batch_id, disable_proxy)
        
        if result:
            print(f"\n✅ 数据爬取成功! 批次ID: {result}")
            print(f"原始数据保存在: {BatchManager.get_raw_dir(result)}\n")
            return 0
        else:
            print("\n❌ 数据爬取失败!\n")
            return 1
    except Exception as e:
        logger.exception(f"数据爬取时出错: {e}")
        return 1

def parse_data(args):
    """执行数据解析步骤"""
    try:
        batch_id = args.batch_id
        result = parse_readme_files(batch_id)
        
        if result:
            print(f"\n✅ 数据解析成功! 批次ID: {result}")
            print(f"解析数据保存在: {BatchManager.get_parsed_dir(result)}\n")
            return 0
        else:
            print("\n❌ 数据解析失败!\n")
            return 1
    except Exception as e:
        logger.exception(f"数据解析时出错: {e}")
        return 1

def run_pipeline(args):
    """执行完整数据处理流水线"""
    try:
        result = run_full_pipeline(force_new_batch=args.force_new)
        
        if result:
            print(f"\n✅ 数据处理流水线执行成功! 批次ID: {result}")
            print(f"原始数据: {BatchManager.get_raw_dir(result)}")
            print(f"解析数据: {BatchManager.get_parsed_dir(result)}\n")
            return 0
        else:
            print("\n❌ 数据处理流水线执行失败!\n")
            return 1
    except Exception as e:
        logger.exception(f"执行流水线时出错: {e}")
        return 1

def main():
    """CLI主入口"""
    parser = argparse.ArgumentParser(description='中国独立开发者洞察 - 数据处理工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # list命令 - 列出所有批次
    list_parser = subparsers.add_parser('list', help='列出所有数据批次')
    
    # fetch命令 - 爬取数据
    fetch_parser = subparsers.add_parser('fetch', help='从GitHub爬取数据')
    
    fetch_parser.add_argument('--batch-id', help='指定批次ID（不指定则创建新批次）')
    fetch_parser.add_argument('--use-proxy', action='store_true', help='使用系统代理设置')
    # parse命令 - 解析数据
    parse_parser = subparsers.add_parser('parse', help='解析README文件并生成CSV')
    parse_parser.add_argument('--batch-id', default=None, help='指定批次ID（不指定则使用最新批次）')
    
    # pipeline命令 - 执行完整流水线
    pipeline_parser = subparsers.add_parser('pipeline', help='执行完整数据处理流水线')
    pipeline_parser.add_argument('--force-new', action='store_true', help='强制创建新批次')
    
    args = parser.parse_args()
    
    # 根据子命令调用相应的函数
    if args.command == 'list':
        return list_batches(args)
    elif args.command == 'fetch':
        return fetch_data(args)
    elif args.command == 'parse':
        return parse_data(args)
    elif args.command == 'pipeline':
        return run_pipeline(args)
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main())
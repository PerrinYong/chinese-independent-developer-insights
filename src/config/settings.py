import os
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
# 加载环境变量
load_dotenv()

# 基本路径配置
ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
DATA_DIR = ROOT_DIR / "data"
BATCHES_DIR = DATA_DIR / "batches"
LATEST_LINK = DATA_DIR / "latest"

# GitHub配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 日志配置中移除敏感信息
logger.info(f"ROOT_DIR: {ROOT_DIR}")
logger.info(f"DATA_DIR: {DATA_DIR}")
logger.info(f"BATCHES_DIR: {BATCHES_DIR}")
logger.info(f"LATEST_LINK: {LATEST_LINK}")
logger.info(f"GITHUB_TOKEN: {'已设置' if GITHUB_TOKEN else '未设置'}")  # 不输出实际token

GITHUB_REPO = "1c7/chinese-independent-developer"
README_PATH = "README.md"
PROGRAMMER_README_PATH = "README-Programmer-Edition.md"

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class BatchManager:
    """批次管理类"""
    
    @staticmethod
    def create_batch():
        """创建新批次并返回批次ID"""
        # 生成批次ID (时间戳格式)
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建批次目录结构
        batch_dir = BATCHES_DIR / batch_id
        raw_dir = batch_dir / "raw"
        parsed_dir = batch_dir / "parsed"
        
        # 创建所需目录
        os.makedirs(BATCHES_DIR, exist_ok=True)
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(parsed_dir, exist_ok=True)
        
        # 创建并保存批次元数据
        metadata = {
            "batch_id": batch_id,
            "created_at": time.time(),
            "created_at_human": datetime.now().isoformat(),
            "status": "created",
            "steps_completed": []
        }
        
        with open(batch_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, sort_keys=True, indent=2, ensure_ascii=False, fp=f)
        
        # 更新latest链接
        BatchManager.update_latest_link(batch_id)
        
        return batch_id
    
    @staticmethod
    def get_batch_dir(batch_id=None):
        """获取批次目录路径"""
        if not batch_id:
            # 如果没有提供批次ID，返回最新批次
            if os.path.exists(LATEST_LINK) and os.path.islink(LATEST_LINK):
                return Path(os.readlink(LATEST_LINK))
            else:
                # 如果没有latest链接，返回最新创建的批次目录
                all_batches = sorted([d for d in BATCHES_DIR.iterdir() if d.is_dir()], 
                                   key=lambda x: x.stat().st_mtime, reverse=True)
                if all_batches:
                    return all_batches[0]
                raise FileNotFoundError("No batch found. Please create a new batch first.")
        else:
            batch_dir = BATCHES_DIR / batch_id
            if not batch_dir.exists():
                raise FileNotFoundError(f"Batch ID {batch_id} not found")
            return batch_dir
    
    @staticmethod
    def update_latest_link(batch_id):
        """更新latest链接到指定批次"""
        batch_dir = BATCHES_DIR / batch_id
        if not batch_dir.exists():
            raise FileNotFoundError(f"Batch ID {batch_id} not found")
        
        # 创建或更新符号链接
        if os.path.exists(LATEST_LINK) or os.path.islink(LATEST_LINK):
            os.unlink(LATEST_LINK)
        
        # 创建相对路径的符号链接 (兼容性更好)
        os.symlink(os.path.join("batches", batch_id), LATEST_LINK, target_is_directory=True)
    
    @staticmethod
    def update_batch_status(batch_id, status, step_completed=None):
        """更新批次状态"""
        batch_dir = BatchManager.get_batch_dir(batch_id)
        metadata_file = batch_dir / "metadata.json"
        
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        metadata["status"] = status
        metadata["updated_at"] = time.time()
        metadata["updated_at_human"] = datetime.now().isoformat()
        
        if step_completed and step_completed not in metadata["steps_completed"]:
            metadata["steps_completed"].append(step_completed)
        
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, sort_keys=True, indent=2, ensure_ascii=False, fp=f)
    

    
    @staticmethod
    def get_raw_dir(batch_id=None):
        """获取原始数据目录"""
        raw_dir = BatchManager.get_batch_dir(batch_id) / "raw"
        os.makedirs(raw_dir, exist_ok=True)  # 确保目录存在
        return raw_dir
    
    @staticmethod
    def get_parsed_dir(batch_id=None):
        """获取解析数据目录"""
        parsed_dir = BatchManager.get_batch_dir(batch_id) / "parsed"
        os.makedirs(parsed_dir, exist_ok=True)  # 确保目录存在
        return parsed_dir
        
    @staticmethod
    def get_latest_batch_id():
        """获取最新批次ID"""
        if os.path.exists(LATEST_LINK) and os.path.islink(LATEST_LINK):
            # 获取链接指向的目录名称
            target = os.readlink(LATEST_LINK)
            return os.path.basename(target)
        
        # 如果没有latest链接或链接无效，返回最新创建的批次
        all_batches = sorted([d.name for d in BATCHES_DIR.iterdir() if d.is_dir()], 
                           reverse=True)
        if all_batches:
            return all_batches[0]
        raise FileNotFoundError("No batch found. Please create a new batch first.")
    
    @staticmethod
    def get_batch_metadata(batch_id):
        """获取批次元数据"""
        batch_dir = BatchManager.get_batch_dir(batch_id)
        metadata_file = batch_dir / "metadata.json"
        
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file for batch {batch_id} not found")
        
        with open(metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    @staticmethod
    def list_batches():
        """列出所有可用的批次"""
        batches = []
        if os.path.exists(BATCHES_DIR):
            for item in os.listdir(BATCHES_DIR):
                batch_path = os.path.join(BATCHES_DIR, item)
                if os.path.isdir(batch_path):
                    metadata_file = os.path.join(batch_path, 'metadata.json')
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            batches.append({
                                'id': item,
                                'created_at': metadata.get('created_at_human', 'Unknown'),
                                'status': metadata.get('status', 'Unknown')
                            })
                        except:
                            batches.append({
                                'id': item,
                                'created_at': 'Error reading metadata',
                                'status': 'Unknown'
                            })
        
        return sorted(batches, key=lambda x: x['id'], reverse=True)
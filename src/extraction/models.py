class Author:
    """表示独立开发者的作者信息"""
    def __init__(self):
        self.name = None        # 作者名称
        self.location = None    # 地理位置
        self.github = None      # GitHub链接
        self.blog = None        # 博客链接
        self.dataline = None    # 原始数据行
        
    def __str__(self):
        return f"Author(name={self.name}, location={self.location})"

class Project:
    """表示独立开发者的项目信息"""
    def __init__(self):
        self.name = None          # 项目名称
        self.url = None           # 项目链接
        self.description = None   # 项目描述
        self.more_info = None     # 更多信息链接
        self.date = None          # 添加日期
        self.author = None        # 关联作者
        self.dataline = None      # 原始数据行
        
    def __str__(self):
        return f"Project(name={self.name}, url={self.url})"
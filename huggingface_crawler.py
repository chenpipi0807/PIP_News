import requests
import json
import os
from datetime import datetime, timedelta
import config

class HuggingFaceCrawler:
    def __init__(self):
        self.cache_dir = config.CACHE_DIR
        self.max_cache_age_days = config.MAX_CACHE_AGE_DAYS
        self.num_projects = config.NUM_PROJECTS
        
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, category):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"huggingface_{category}.json")
    
    def _is_cache_valid(self, cache_path):
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False
        
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        max_age = timedelta(days=self.max_cache_age_days)
        
        return datetime.now() - cache_time < max_age
    
    # 定义大公司或知名组织的列表
    MAJOR_ORGANIZATIONS = [
        "google", "meta", "facebook", "microsoft", "openai", "deepmind", "anthropic", 
        "baidu", "tencent", "alibaba", "huawei", "nvidia", "apple", "amazon", "intel",
        "ibm", "adobe", "twitter", "netflix", "salesforce", "uber", "lyft", "airbnb",
        "pinterest", "snap", "dropbox", "huggingface", "stability", "cohere", "deepseek",
        "zhipu", "bytedance", "xiaomi", "01ai", "mila", "stanford", "berkeley", "mit",
        "carnegie", "nvidia", "amd", "pytorch", "tensorflow", "jax", "neurips", "google-research",
        "facebookresearch", "openai-research", "stabilityai", "mistralai", "llama"
    ]
    
    def _fetch_projects(self, sort="trending", limit=None):
        """获取Hugging Face上的项目"""
        if limit is None:
            limit = self.num_projects
        
        # 获取更多项目以便筛选
        fetch_limit = max(50, limit * 3)
            
        url = "https://huggingface.co/api/models"
        params = {
            "sort": sort,
            "limit": fetch_limit,
            "full": "true"  # 获取完整信息
        }
        
        response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        data = response.json()
        
        # 打印API返回数据结构，便于调试
        print(f"Hugging Face API返回数据类型: {type(data)}")
        
        # 检查数据是列表还是字典
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "items" in data:
            items = data.get("items", [])
        else:
            # 尝试获取其他可能的键
            if isinstance(data, dict):
                possible_keys = ["data", "models", "results"]
                for key in possible_keys:
                    if key in data and isinstance(data[key], list):
                        items = data[key]
                        break
                else:
                    # 如果没有找到合适的键，则尝试使用字典的值
                    values = list(data.values())
                    items = [v for v in values if isinstance(v, dict)]
            else:
                items = []
                print(f"无法解析Hugging Face API返回的数据: {data}")
        
        # 对项目进行初步处理
        all_projects = []
        for item in items:
            try:
                if not isinstance(item, dict):
                    continue
                    
                # 构建项目信息
                model_id = item.get("modelId", "")
                name = item.get("id", model_id) or item.get("name", "")
                
                if not name:
                    continue
                    
                # 获取描述
                description = item.get("description", "")
                if not description:  # 跳过没有描述的项目
                    continue
                    
                # 获取其他元数据
                tags = item.get("tags", [])
                likes = item.get("likes", 0)
                downloads = item.get("downloads", 0)
                author = item.get("author", "") or name.split("/")[0] if "/" in name else ""
                
                # 创建项目对象
                project = {
                    "name": name,
                    "url": f"https://huggingface.co/{name}",
                    "description": description,
                    "tags": tags,
                    "likes": likes,
                    "downloads": downloads,
                    "author": author,
                    "is_major_org": False,  # 默认为非大公司
                    "score": 0  # 初始评分
                }
                
                # 检查是否来自大公司
                for org in self.MAJOR_ORGANIZATIONS:
                    if org.lower() in author.lower() or org.lower() in name.lower():
                        project["is_major_org"] = True
                        # 大公司项目评分+100
                        project["score"] += 100
                        break
                
                # 根据点赞和下载量计算评分
                project["score"] += min(likes * 2, 200)  # 每个点赞2分，最多200分
                project["score"] += min(downloads // 1000, 300)  # 每1000下载1分，最多300分
                
                # 将项目添加到列表中
                all_projects.append(project)
            except Exception as e:
                print(f"解析Hugging Face项目时出错: {e}")
        
        # 按评分排序
        all_projects.sort(key=lambda p: p["score"], reverse=True)
        
        # 返回排序后的项目，限制数量
        return all_projects[:limit]
    
    def get_trending_projects(self):
        """获取Hugging Face上的热门项目（优先使用缓存）"""
        cache_path = self._get_cache_path("trending")
        
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        projects = self._fetch_projects(sort="trending")
        
        # 保存到缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        
        return projects
    
    def get_newest_projects(self):
        """获取Hugging Face上的最新项目（优先使用缓存）"""
        cache_path = self._get_cache_path("newest")
        
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        projects = self._fetch_projects(sort="created_at")
        
        # 保存到缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        
        return projects

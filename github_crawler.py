import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import config

class GitHubCrawler:
    def __init__(self):
        self.cache_dir = config.CACHE_DIR
        self.max_cache_age_days = config.MAX_CACHE_AGE_DAYS
        self.num_projects = config.NUM_PROJECTS
        
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, category):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"github_{category}.json")
    
    def _is_cache_valid(self, cache_path):
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False
        
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        max_age = timedelta(days=self.max_cache_age_days)
        
        return datetime.now() - cache_time < max_age
    
    def _fetch_trending_projects(self):
        """获取GitHub上的热门项目"""
        url = "https://github.com/trending"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        projects = []
        article_elements = soup.select('article.Box-row')
        
        # 对所有收集到的项目进行筛选，所以这里多获取一些
        for article in article_elements[:self.num_projects * 2]:
            try:
                # 获取项目名和链接
                repo_element = article.select_one('h2 a')
                if repo_element:
                    repo_path = repo_element.get('href', '').strip('/')
                    if repo_path:
                        name = repo_path
                        url = f"https://github.com/{repo_path}"
                        
                        # 获取项目描述
                        description_element = article.select_one('p')
                        description = description_element.text.strip() if description_element else ""
                        
                        # 如果没有描述，跳过该项目
                        if not description or description == "无描述":
                            continue
                        
                        # 获取编程语言
                        language_element = article.select_one('span[itemprop="programmingLanguage"]')
                        language = language_element.text.strip() if language_element else "未知"
                        
                        # 获取星标数
                        stars_element = article.select_one('a.Link--muted[href$="/stargazers"]')
                        stars_text = stars_element.text.strip() if stars_element else "0"
                        
                        # 处理星标数的格式，如"1.2k"转换为数字
                        try:
                            if 'k' in stars_text.lower():
                                stars_value = float(stars_text.lower().replace('k', '')) * 1000
                            else:
                                stars_value = float(stars_text.replace(',', ''))
                            
                            # 转换回字符串形式保存
                            stars = stars_text
                            
                            # 如果星标数低于500，跳过该项目
                            if stars_value < 500:
                                continue
                        except:
                            # 如果无法解析星标数，使用原始文本
                            stars = stars_text
                        
                        projects.append({
                            "name": name,
                            "url": url,
                            "description": description,
                            "language": language,
                            "stars": stars,
                            "stars_value": stars_value if 'stars_value' in locals() else 0
                        })
            except Exception as e:
                print(f"解析GitHub热门项目时出错: {e}")
                
        # 只返回指定数量的项目
        return projects[:self.num_projects]
    
    def _fetch_newest_projects(self):
        """获取GitHub上的最新项目"""
        # 使用GitHub API搜索最近更新的项目，要求星标数达到或超过500
        url = "https://api.github.com/search/repositories"
        params = {
            "q": "stars:>=500",  # 要求星标数至少500
            "sort": "updated",  # 按最近更新排序
            "order": "desc",
            "per_page": 50  # 获取更多项目，便于筛选
        }
        
        response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        data = response.json()
        
        projects = []
        # 处理所有返回的项目
        for item in data.get("items", []):
            try:
                # 跳过没有描述的项目
                description = item.get("description", "")
                if not description:
                    continue
                    
                # 获取星标数
                stars_count = item.get("stargazers_count", 0)
                
                # 确保星标数足够
                if stars_count < 500:
                    continue
                
                # 添加到项目列表
                projects.append({
                    "name": item["full_name"],
                    "url": item["html_url"],
                    "description": description,
                    "language": item.get("language", "未知") or "未知",
                    "stars": str(stars_count),
                    "stars_value": stars_count,
                    "updated_at": item.get("updated_at", ""),
                    "created_at": item.get("created_at", "")
                })
                
                # 如果收集到足够的项目，则停止
                if len(projects) >= self.num_projects:
                    break
            except Exception as e:
                print(f"解析GitHub最新项目时出错: {e}")
        
        return projects[:self.num_projects]
    
    def get_trending_projects(self):
        """获取GitHub上的热门项目（优先使用缓存）"""
        cache_path = self._get_cache_path("trending")
        
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        projects = self._fetch_trending_projects()
        
        # 保存到缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        
        return projects
    
    def get_newest_projects(self):
        """获取GitHub上的最新项目（优先使用缓存）"""
        cache_path = self._get_cache_path("newest")
        
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        projects = self._fetch_newest_projects()
        
        # 保存到缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        
        return projects

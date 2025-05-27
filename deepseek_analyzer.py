import requests
import json
import os
from datetime import datetime, timedelta
import config

class DeepSeekAnalyzer:
    def __init__(self):
        self.cache_dir = config.CACHE_DIR
        self.max_cache_age_days = config.MAX_CACHE_AGE_DAYS
        
        # 从配置文件获取API密钥
        self.api_key = self._get_api_key()
        self.api_url = config.DEEPSEEK_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_api_key(self):
        """从apikey.txt文件中获取API密钥"""
        try:
            with open("apikey.txt", "r") as f:
                return f.readline().strip()
        except Exception as e:
            print(f"读取API密钥时出错: {e}")
            # 如果无法读取文件，则使用配置中的API密钥
            return config.DEEPSEEK_API_KEY
    
    def _get_cache_path(self, project_url):
        """获取项目分析缓存文件路径"""
        # 使用项目URL的哈希值作为缓存文件名
        import hashlib
        url_hash = hashlib.md5(project_url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"analysis_{url_hash}.json")
    
    def _is_cache_valid(self, cache_path):
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False
        
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        max_age = timedelta(days=self.max_cache_age_days)
        
        return datetime.now() - cache_time < max_age
    
    def analyze_project(self, project):
        """使用DeepSeek API分析项目"""
        project_url = project.get("url", "")
        cache_path = self._get_cache_path(project_url)
        
        # 如果缓存有效，直接返回缓存结果
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取缓存时出错: {e}")
        
        # 准备发送给DeepSeek的提示文本
        prompt = self._create_prompt(project)
        
        # 调用DeepSeek API
        try:
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            analysis = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 保存结果到缓存
            analysis_data = {
                "project": project,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            return analysis_data
        
        except Exception as e:
            print(f"调用DeepSeek API时出错: {e}")
            return {
                "project": project,
                "analysis": f"无法分析项目。错误: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_prompt(self, project):
        """创建用于DeepSeek API的提示文本"""
        name = project.get("name", "未知项目")
        url = project.get("url", "")
        description = project.get("description", "无描述")
        
        # 为GitHub项目添加特定信息
        language = project.get("language", "")
        stars = project.get("stars", "")
        
        # 为Hugging Face项目添加特定信息
        tags = project.get("tags", [])
        likes = project.get("likes", "")
        downloads = project.get("downloads", "")
        
        prompt = f"""请对以下开源项目进行详细解读：

项目名称：{name}
项目链接：{url}
项目描述：{description}
"""

        if language:
            prompt += f"编程语言：{language}\n"
        if stars:
            prompt += f"星标数量：{stars}\n"
        if tags:
            prompt += f"标签：{', '.join(tags)}\n"
        if likes:
            prompt += f"点赞数量：{likes}\n"
        if downloads:
            prompt += f"下载数量：{downloads}\n"
        
        prompt += """
请提供以下信息：
1. 项目介绍（用通俗易懂的语言描述）
2. 项目的应用场景
3. 项目评价（优点和缺点）

请确保你的回答结构清晰，内容全面，语言通俗易懂。"""
        
        return prompt

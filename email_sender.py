import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import os
import config
from datetime import datetime

class EmailSender:
    def __init__(self):
        # 从配置文件或文本文件中获取邮件信息
        self.sender_email = self._get_sender_email()
        self.sender_password = self._get_sender_password()
        self.recipients = self._get_recipients()
        
    def _get_sender_email(self):
        """从发件邮箱文件中获取发件人邮箱"""
        try:
            with open("发件邮箱与授权码.txt", "r") as f:
                return f.readline().strip()
        except Exception as e:
            print(f"读取发件邮箱时出错: {e}")
            return config.SENDER_EMAIL
    
    def _get_sender_password(self):
        """从发件邮箱文件中获取发件人授权码"""
        try:
            with open("发件邮箱与授权码.txt", "r") as f:
                # 跳过第一行（邮箱地址）
                f.readline()
                # 读取第二行（授权码）
                return f.readline().strip()
        except Exception as e:
            print(f"读取发件邮箱授权码时出错: {e}")
            return config.SENDER_PASSWORD
    
    def _get_recipients(self):
        """从收件邮箱文件中获取收件人邮箱列表"""
        try:
            recipients = []
            with open("收件邮箱.txt", "r") as f:
                for line in f:
                    email = line.strip()
                    if email:
                        recipients.append(email)
            return recipients if recipients else config.RECIPIENTS
        except Exception as e:
            print(f"读取收件邮箱时出错: {e}")
            return config.RECIPIENTS
    
    def send_project_report(self, github_trending, github_newest, huggingface_trending, huggingface_newest):
        """发送项目报告邮件"""
        # 检查是否有项目数据
        if not any([github_trending, github_newest, huggingface_trending, huggingface_newest]):
            print("警告：所有项目列表均为空，不发送邮件")
            return False
            
        # 创建邮件主体
        msg = MIMEMultipart()
        
        # 设置邮件主题
        current_date = datetime.now().strftime("%Y-%m-%d")
        msg['Subject'] = Header(f'AI开源项目日报 ({current_date})', 'utf-8')
        
        # 设置发件人和收件人
        msg['From'] = self.sender_email
        msg['To'] = ','.join(self.recipients)
        
        try:
            # 创建邮件内容
            email_content = self._create_email_content(
                github_trending, 
                github_newest, 
                huggingface_trending, 
                huggingface_newest
            )
            
            msg.attach(MIMEText(email_content, 'html', 'utf-8'))
        except Exception as e:
            print(f"创建邮件内容时出错: {e}")
            # 如果创建邮件内容失败，则创建一个简单的错误邮件
            error_content = f"""
            <html>
            <body>
                <h1>AI开源项目日报生成失败</h1>
                <p>在生成项目报告时遇到问题，请查看系统日志以获取更多信息。</p>
                <p>错误信息: {str(e)}</p>
                <p>时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </body>
            </html>
            """
            msg.attach(MIMEText(error_content, 'html', 'utf-8'))
        
        try:
            # 连接到SMTP服务器并发送邮件
            if '@qq.com' in self.sender_email:
                smtp_server = 'smtp.qq.com'
                port = 587
            elif '@163.com' in self.sender_email:
                smtp_server = 'smtp.163.com'
                port = 25
            elif '@gmail.com' in self.sender_email:
                smtp_server = 'smtp.gmail.com'
                port = 587
            else:
                raise ValueError(f"不支持的邮箱类型: {self.sender_email}")
            
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"邮件已成功发送至: {', '.join(self.recipients)}")
            return True
        except Exception as e:
            print(f"发送邮件时出错: {e}")
            return False
    
    def _create_email_content(self, github_trending, github_newest, huggingface_trending, huggingface_newest):
        """创建邮件内容HTML"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
                h2 {{ color: #3498db; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                h3 {{ color: #2c3e50; margin-top: 20px; }}
                .project {{ margin-bottom: 30px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }}
                .project h3 {{ margin-top: 0; }}
                .project-link {{ color: #3498db; text-decoration: none; }}
                .project-link:hover {{ text-decoration: underline; }}
                .project-meta {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 10px; }}
                .section-description {{ color: #666; margin-bottom: 20px; }}
                .timestamp {{ color: #999; text-align: center; margin-top: 30px; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI开源项目日报</h1>
                <p class="section-description">这份报告汇总了GitHub和Hugging Face平台上最热门和最新的AI开源项目，希望能帮助您了解AI领域的最新动态。</p>
        """
        
        # GitHub热门项目
        if github_trending:
            html += f"""
                    <h2>GitHub热门项目</h2>
                    <p class="section-description">以下是GitHub平台上当前最受欢迎的{len(github_trending)}个项目：</p>
            """
            
            for item in github_trending:
                try:
                    project = item.get("project", {})
                    analysis = item.get("analysis", "无分析结果")
                    
                    name = project.get("name", "未知项目")
                    url = project.get("url", "#")
                    description = project.get("description", "无描述")
                    language = project.get("language", "未知")
                    stars = project.get("stars", "0")
                    
                    html += f"""
                    <div class="project">
                        <h3><a href="{url}" class="project-link" target="_blank">{name}</a></h3>
                        <p class="project-meta">语言: {language} | 星标: {stars}</p>
                        <p><strong>描述:</strong> {description}</p>
                        <p><strong>AI解析:</strong></p>
                        <div>{analysis.replace('\n', '<br>')}</div>
                    </div>
                    """
                except Exception as e:
                    print(f"处理GitHub热门项目时出错: {e}")
        else:
            html += f"""
                    <h2>GitHub热门项目</h2>
                    <p class="section-description">无法获取GitHub热门项目数据。</p>
            """
        
        # GitHub最新项目
        if github_newest:
            html += f"""
                    <h2>GitHub最新项目</h2>
                    <p class="section-description">以下是GitHub平台上最近更新的{len(github_newest)}个项目：</p>
            """
            
            for item in github_newest:
                try:
                    project = item.get("project", {})
                    analysis = item.get("analysis", "无分析结果")
                    
                    name = project.get("name", "未知项目")
                    url = project.get("url", "#")
                    description = project.get("description", "无描述")
                    language = project.get("language", "未知")
                    stars = project.get("stars", "0")
                    
                    html += f"""
                    <div class="project">
                        <h3><a href="{url}" class="project-link" target="_blank">{name}</a></h3>
                        <p class="project-meta">语言: {language} | 星标: {stars}</p>
                        <p><strong>描述:</strong> {description}</p>
                        <p><strong>AI解析:</strong></p>
                        <div>{analysis.replace('\n', '<br>')}</div>
                    </div>
                    """
                except Exception as e:
                    print(f"处理GitHub最新项目时出错: {e}")
        else:
            html += f"""
                    <h2>GitHub最新项目</h2>
                    <p class="section-description">无法获取GitHub最新项目数据。</p>
            """
        
        # Hugging Face热门项目
        if huggingface_trending:
            html += f"""
                    <h2>Hugging Face热门项目</h2>
                    <p class="section-description">以下是Hugging Face平台上当前最受欢迎的{len(huggingface_trending)}个项目：</p>
            """
            
            for item in huggingface_trending:
                try:
                    project = item.get("project", {})
                    analysis = item.get("analysis", "无分析结果")
                    
                    name = project.get("name", "未知项目")
                    url = project.get("url", "#")
                    description = project.get("description", "无描述")
                    tags = project.get("tags", [])
                    likes = project.get("likes", "0")
                    downloads = project.get("downloads", "0")
                    
                    html += f"""
                    <div class="project">
                        <h3><a href="{url}" class="project-link" target="_blank">{name}</a></h3>
                        <p class="project-meta">标签: {', '.join(tags) if tags else '无'} | 点赞: {likes} | 下载: {downloads}</p>
                        <p><strong>描述:</strong> {description}</p>
                        <p><strong>AI解析:</strong></p>
                        <div>{analysis.replace('\n', '<br>')}</div>
                    </div>
                    """
                except Exception as e:
                    print(f"处理Hugging Face热门项目时出错: {e}")
        else:
            html += f"""
                    <h2>Hugging Face热门项目</h2>
                    <p class="section-description">无法获取Hugging Face热门项目数据。</p>
            """
        
        # Hugging Face最新项目
        if huggingface_newest:
            html += f"""
                    <h2>Hugging Face最新项目</h2>
                    <p class="section-description">以下是Hugging Face平台上最新发布的{len(huggingface_newest)}个项目：</p>
            """
            
            for item in huggingface_newest:
                try:
                    project = item.get("project", {})
                    analysis = item.get("analysis", "无分析结果")
                    
                    name = project.get("name", "未知项目")
                    url = project.get("url", "#")
                    description = project.get("description", "无描述")
                    tags = project.get("tags", [])
                    likes = project.get("likes", "0")
                    downloads = project.get("downloads", "0")
                    
                    html += f"""
                    <div class="project">
                        <h3><a href="{url}" class="project-link" target="_blank">{name}</a></h3>
                        <p class="project-meta">标签: {', '.join(tags) if tags else '无'} | 点赞: {likes} | 下载: {downloads}</p>
                        <p><strong>描述:</strong> {description}</p>
                        <p><strong>AI解析:</strong></p>
                        <div>{analysis.replace('\n', '<br>')}</div>
                    </div>
                    """
                except Exception as e:
                    print(f"处理Hugging Face最新项目时出错: {e}")
        else:
            html += f"""
                    <h2>Hugging Face最新项目</h2>
                    <p class="section-description">无法获取Hugging Face最新项目数据。</p>
            """
        
        # 结束HTML
        html += f"""
                <p class="timestamp">报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </body>
        </html>
        """
        
        return html

import os
import time
import schedule
from datetime import datetime
import json

from github_crawler import GitHubCrawler
from huggingface_crawler import HuggingFaceCrawler
from deepseek_analyzer import DeepSeekAnalyzer
from email_sender import EmailSender
import config

def create_report():
    print(f"开始生成AI项目报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建缓存目录
    if not os.path.exists(config.CACHE_DIR):
        os.makedirs(config.CACHE_DIR)
    
    # 初始化各个组件
    github_crawler = GitHubCrawler()
    huggingface_crawler = HuggingFaceCrawler()
    deepseek_analyzer = DeepSeekAnalyzer()
    email_sender = EmailSender()
    
    print("正在获取GitHub热门项目...")
    github_trending_projects = github_crawler.get_trending_projects()
    
    print("正在获取GitHub最新项目...")
    github_newest_projects = github_crawler.get_newest_projects()
    
    print("正在获取Hugging Face热门项目...")
    huggingface_trending_projects = huggingface_crawler.get_trending_projects()
    
    print("正在获取Hugging Face最新项目...")
    huggingface_newest_projects = huggingface_crawler.get_newest_projects()
    
    # 分析项目
    print("正在使用DeepSeek API分析项目...")
    
    # 定义一个辅助函数来处理项目分析，增加错误处理
    def analyze_projects(projects, source_name):
        analyses = []
        if not projects:
            print(f"警告：{source_name}项目列表为空，跳过分析")
            return analyses
            
        for project in projects:
            try:
                name = project.get('name', '未知项目')
                print(f"分析{source_name}项目: {name}")
                analysis = deepseek_analyzer.analyze_project(project)
                analyses.append(analysis)
            except Exception as e:
                print(f"分析{source_name}项目 {project.get('name', '未知项目')} 时出错: {e}")
                # 添加一个错误分析记录，避免跳过
                analyses.append({
                    "project": project,
                    "analysis": f"分析过程中出错: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
        return analyses
    
    # 分析各平台项目
    github_trending_analyses = analyze_projects(github_trending_projects, "GitHub热门")
    github_newest_analyses = analyze_projects(github_newest_projects, "GitHub最新")
    huggingface_trending_analyses = analyze_projects(huggingface_trending_projects, "Hugging Face热门")
    huggingface_newest_analyses = analyze_projects(huggingface_newest_projects, "Hugging Face最新")
    
    # 发送邮件报告
    print("正在发送邮件报告...")
    email_sent = email_sender.send_project_report(
        github_trending_analyses,
        github_newest_analyses,
        huggingface_trending_analyses,
        huggingface_newest_analyses
    )
    
    if email_sent:
        print("邮件报告已成功发送！")
    else:
        print("发送邮件报告失败，请检查日志。")
    
    # 保存本次报告到文件
    report_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(config.CACHE_DIR, f"report_{report_time}.json")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "github_trending": github_trending_analyses,
            "github_newest": github_newest_analyses,
            "huggingface_trending": huggingface_trending_analyses,
            "huggingface_newest": huggingface_newest_analyses,
            "timestamp": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"报告已保存到: {report_file}")
    print(f"AI项目报告生成完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def schedule_report(hour=9, minute=0):
    """设置定时任务，每天指定时间生成报告"""
    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(create_report)
    print(f"已设置定时任务，将在每天 {hour:02d}:{minute:02d} 生成AI项目报告")

def run_scheduler():
    """运行定时任务调度器"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次是否有待执行的任务

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI开源项目新闻汇报工具")
    parser.add_argument("--now", action="store_true", help="立即生成一次报告")
    parser.add_argument("--schedule", action="store_true", help="设置定时任务")
    parser.add_argument("--hour", type=int, default=9, help="定时任务小时（0-23）")
    parser.add_argument("--minute", type=int, default=0, help="定时任务分钟（0-59）")
    
    args = parser.parse_args()
    
    if args.now:
        create_report()
    
    if args.schedule:
        schedule_report(args.hour, args.minute)
        run_scheduler()
    
    # 如果没有指定任何参数，则立即生成一次报告
    if not (args.now or args.schedule):
        create_report()

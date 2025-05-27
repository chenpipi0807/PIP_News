# AI新闻汇报工具

这是一个自动化的AI开源项目新闻汇报工具，可以抓取GitHub和Hugging Face上的热门和最新项目，使用DeepSeek AI进行项目解读，并将结果通过邮件发送给指定收件人。

## 功能特点

1. 自动抓取GitHub和Hugging Face平台上的热门和最新项目（各平台最热和最新各10个）
2. 使用DeepSeek R1 API对项目进行智能解读，包括：
   - 项目介绍（通俗易懂的语言）
   - 项目的应用场景
   - 项目评价（优点和缺点）
3. 将完整的项目分析结果通过邮件发送到指定邮箱
4. 支持本地缓存，避免重复API调用
5. 支持定时任务，可以设置每天自动生成报告

## 安装方法

1. 克隆或下载本项目到本地
2. 安装必要的依赖包：

```bash
pip install -r requirements.txt
```

## 配置说明

工具使用以下文件进行配置：

1. `apikey.txt`：包含DeepSeek API密钥
2. `发件邮箱与授权码.txt`：包含发件人邮箱和授权码
3. `收件邮箱.txt`：包含收件人邮箱列表
4. `config.py`：包含其他配置项，如缓存目录、API URL等

## 使用方法

### 立即生成一次报告

```bash
python main.py --now
```

### 设置定时任务

```bash
python main.py --schedule --hour 9 --minute 0
```

这将设置每天上午9:00自动生成报告。

### 同时生成报告并设置定时任务

```bash
python main.py --now --schedule --hour 9 --minute 0
```

## 输出示例

程序会在控制台输出执行过程，并将报告以邮件形式发送给指定收件人。同时，报告也会以JSON格式保存在缓存目录中。

## 注意事项

- 确保DeepSeek API密钥有效
- 确保发件邮箱的SMTP服务已开启，且授权码正确
- 首次运行可能需要较长时间，因为需要从网络获取数据并调用API



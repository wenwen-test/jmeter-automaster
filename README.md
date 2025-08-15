JMeter自动化性能测试框架文档



一、框架概述


本框架是一个基于Python的JMeter自动化性能测试解决方案，提供以下核心功能：

•批量执行JMeter测试脚本

•并行运行多个测试计划

•自动生成可视化测试报告

•邮件发送测试结果

•完善的日志记录和错误处理

核心组件
1.JMeterTestRunner​ - 测试执行引擎

2.ReportGenerator​ - 报告生成器

3.​EmailSender​ - 邮件通知服务

4.TestUtils​ - 工具函数库

5.mainrun​ - 主程序入口

技术栈
•Python 3.7+

•Apache JMeter 5.4+

•Plotly (数据可视化)

•Jinja2 (HTML模板渲染)

•Pandas (数据分析)

二、详细说明文档
1. EmailSender.py
邮件发送工具类，封装了SMTP邮件发送功能

类说明
​EmailSender​

•功能​：发送带附件的邮件

•参数​：

•sender_email: 发件人邮箱

•sender_password: SMTP授权码

•smtp_server: SMTP服务器（默认163）

•smtp_port: SMTP端口（默认465）

•方法​：

•send_email(recipient_email, subject, body, attachment_path=None)

•发送邮件

•参数：

•recipient_email: 收件人邮箱

•subject: 邮件主题

•body: 邮件正文

•attachment_path: 附件路径（可选）

2. JMeterTestRunner.py
JMeter测试运行器，负责执行JMeter测试计划

类说明
​JMeterTestRunner​

•功能​：管理JMeter测试的执行

•参数​：

•jmeter_home: JMeter安装目录

•test_dir: JMX文件目录

•result_base_dir: 结果基础目录

•max_workers: 最大并行线程数（默认4）

•方法​：

•find_jmx_files(): 查找所有JMX文件

•run_single_test(jmx_file): 运行单个测试

•run_all_tests(): 并行运行所有测试

•parse_results(jtl_file, test_name): 解析测试结果

自定义异常
•JMeterNotFoundException: JMeter未找到

•JMXFileNotFoundException: JMX文件未找到

•TestExecutionException: 测试执行失败

•JMeterTestException: JMeter测试异常

•ResultParseException: 结果解析失败

3. ReportGenerator.py
测试报告生成器，创建可视化HTML报告

类说明
​ReportGenerator​

•功能​：生成HTML测试报告并发送邮件

•参数​：

•results: 测试结果数据

•output_dir: 输出目录

•方法​：

•generate_charts(): 生成图表

•generate_html_report(): 生成HTML报告

•_send_email_notification(report_file): 发送邮件通知

•_get_html_template(): 获取HTML模板

4. TestUtils.py
工具函数库，提供通用功能

类说明
​TestUtils​

•
​静态方法​：

•setup_logging(log_dir, logger_name): 配置日志系统

•ensure_directory(directory, writable): 确保目录存在且可写

•create_daily_directory(base_dir): 创建按天组织的目录

•check_jmeter_installation(jmeter_home): 检查JMeter安装

•clean_old_directories(base_dir, days_to_keep): 清理旧目录

•delete_directory(directory): 递归删除目录

•validate_file_path(file_path, expected_extension): 验证文件路径

•get_file_size(file_path): 获取文件大小

5. mainrun.py
主程序入口，协调整个测试流程

功能
1.加载配置

2.验证环境

3.初始化日志

4.执行测试

5.生成报告

6.发送通知



三、环境部署文档
1. 系统要求
•操作系统：Windows/Linux/macOS

•Python 3.7+

•Java 8+

•Apache JMeter 5.4+

2. 安装步骤
2.1 安装Python
1.访问 Python官网

2.下载并安装Python 3.7+

3.验证安装：

bash
复制
python --version
pip --version
2.2 安装JMeter
1.访问 JMeter官网

2.下载二进制包（建议5.4+版本）

3.解压到目标目录，如 D:\apache-jmeter-5.4.1

4.设置环境变量：

bash
复制
# Windows
set JMETER_HOME=D:\apache-jmeter-5.4.1
set PATH=%PATH%;%JMETER_HOME%\bin

# Linux/macOS
export JMETER_HOME=/opt/apache-jmeter-5.4.1
export PATH=$PATH:$JMETER_HOME/bin
5.验证安装：

bash
复制
jmeter -v
2.3 安装Python依赖
bash
复制
pip install pandas plotly jinja2
2.4 配置邮箱服务
1.申请SMTP服务（推荐163邮箱）

2.获取SMTP授权码

3.设置环境变量：

bash
复制
# Windows
set REPORT_SENDER_EMAIL=your_email@163.com
set REPORT_SENDER_PASSWORD=your_smtp_password
set REPORT_RECIPIENT_EMAIL=recipient@example.com

# Linux/macOS
export REPORT_SENDER_EMAIL=your_email@163.com
export REPORT_SENDER_PASSWORD=your_smtp_password
export REPORT_RECIPIENT_EMAIL=recipient@example.com
3. 目录结构
复制
├── scripts/                   # 脚本目录
│   ├── EmailSender.py          # 邮件发送模块
│   ├── JMeterTestRunner.py     # 测试运行器
│   ├── ReportGenerator.py      # 报告生成器
│   ├── TestUtils.py            # 工具函数
│   └── mainrun.py              # 主程序
├── tests/                      # JMX测试目录
│   ├── system1_test.jmx
│   └── system2_test.jmx
└── results/                    # 测试结果目录（自动生成）
4. 配置文件
框架支持通过环境变量配置：

bash
复制
# JMeter安装目录
export JMETER_HOME=/opt/apache-jmeter-5.4.1

# 测试目录
export TEST_DIR=/path/to/tests

# 结果目录
export RESULT_DIR=/path/to/results

# 最大并行数
export MAX_WORKERS=4

# 邮件配置
export REPORT_SENDER_EMAIL=your_email@163.com
export REPORT_SENDER_PASSWORD=your_smtp_password
export REPORT_RECIPIENT_EMAIL=recipient@example.com
5. 运行测试
bash
复制
# 进入脚本目录
cd scripts

# 运行主程序
python mainrun.py

# 使用命令行参数
python mainrun.py \
  --jmeter-home /opt/apache-jmeter-5.4.1 \
  --test-dir /path/to/tests \
  --result-dir /path/to/results \
  --max-workers 8 \
  --no-email
6. 定时任务配置（可选）
Windows任务计划程序
1.
创建基本任务

2.
设置每日执行

3.
操作：启动程序 python D:\scripts\mainrun.py

Linux cron任务
bash
复制
# 编辑crontab
crontab -e

# 添加每日凌晨2点执行
0 2 * * * cd /path/to/scripts && python mainrun.py
7. 结果查看
1.
HTML报告：results/YYYYMMDD/test_report_YYYYMMDD_HHMMSS.html

2.
日志文件：results/logs/test_YYYYMMDD.log

3.
JMeter原始结果：results/YYYYMMDD/test_name_YYYYMMDD_HHMMSS/

四、常见问题解答
Q1: JMeter无法找到
​解决方案​：

1.确认JMETER_HOME环境变量设置正确

2.检查jmeter.bat/jmeter文件是否存在

3.在mainrun.py中指定--jmeter-home参数

Q2: 邮件发送失败
​解决方案​：

1.检查SMTP授权码是否正确

2.确认邮箱服务开启SMTP功能

3.检查防火墙是否阻止SMTP连接

4.使用--no-email跳过邮件发送

Q3: 测试结果为空
​解决方案​：

1.检查JMX文件是否正确

2.验证测试目标服务是否可用

3.查看日志文件中的错误信息

4.增加JMeter日志级别：在JMeterTestRunner.py中添加 -L DEBUG参数

Q4: 并行执行问题
​解决方案​：

1.降低max-workers数量

2.增加系统资源（CPU/内存）

3.检查是否有资源冲突（端口、文件等）

五、扩展与定制
自定义报告模板
1.修改ReportGenerator.py中的_get_html_template方法

2.使用Jinja2模板语法定制HTML结构

3.添加自定义CSS样式

添加新图表
1.在ReportGenerator.generate_charts中添加新图表

2.使用Plotly创建图表

3.在HTML模板中添加图表占位符

集成CI/CD
1.
Jenkins集成：

groovy
复制
pipeline {
  agent any
  stages {
    stage('Performance Test') {
      steps {
        bat 'python scripts/mainrun.py'
      }
    }
  }
}
2.
GitLab CI：

yaml
复制
performance_test:
  script:
    - python scripts/mainrun.py
  artifacts:
    paths:
      - results/
支持分布式测试
1.修改JMeterTestRunner.run_single_test

2.添加JMeter远程执行参数：

python
下载
复制
运行
command.extend([
    '-R', 'remote_host1,remote_host2',
    '-G', 'global_property=value'
])

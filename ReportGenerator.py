import datetime
from typing import Dict, Any
from pathlib import Path
import plotly.graph_objects as go  # 生成图表所需
from jinja2 import Template  # HTML模板渲染
from EmailSender import EmailSender


class ReportGenerator:
    def __init__(self, results: Dict[str, Any], output_dir: Path):
        """
        初始化报告生成器
        Args:
            results: 所有测试结果
            output_dir: 输出目录
        """
        self.results = results  # 存储测试结果数据
        self.output_dir = output_dir  # 设置报告输出目录
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')  # 生成时间戳

    def generate_charts(self) -> Dict[str, str]:
        """
        生成所有需要的图表
        Returns:
            Dict: 包含所有图表HTML的字典
        """
        charts = {}  # 初始化图表字典

        # 生成总体成功率饼图
        total_success = sum(r['successful_requests'] for r in self.results.values())  # 计算总成功请求数
        total_failed = sum(r['failed_requests'] for r in self.results.values())  # 计算总失败请求数

        fig_success_rate = go.Figure(data=[
            go.Pie(
                labels=['成功', '失败'],
                values=[total_success, total_failed],
                hole=.3,  # 设置饼图中心空洞大小
                marker_colors=['#00C851', '#ff4444']  # 设置颜色
            )
        ])
        fig_success_rate.update_layout(
            title='总体请求成功率',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)  # 设置图例位置
        )
        charts['overall_success_rate'] = fig_success_rate.to_html(full_html=False)  # 将图表转为HTML

        # 生成各系统响应时间对比图
        systems = list(self.results.keys())  # 获取所有系统名称
        avg_response_times = [r['average_response_time'] for r in self.results.values()]  # 获取平均响应时间

        fig_response_time = go.Figure(data=[
            go.Bar(
                x=systems,
                y=avg_response_times,
                marker_color='#3366cc',  # 设置柱状图颜色
                text=[f"{rt:.2f}ms" for rt in avg_response_times],  # 添加数值标签
                textposition='auto',  # 自动标签位置
            )
        ])
        fig_response_time.update_layout(
            title='平均响应时间',
            xaxis_title="系统名称",
            yaxis_title="响应时间(ms)",
            showlegend=False
        )
        charts['response_time_comparison'] = fig_response_time.to_html(full_html=False)  # 将图表转为HTML

        # 生成TPS对比图
        tps_values = [r['tps'] for r in self.results.values()]  # 获取各系统TPS值

        fig_tps = go.Figure(data=[
            go.Bar(
                x=systems,
                y=tps_values,
                marker_color='#00C851',  # 设置柱状图颜色
                text=[f"{tps:.2f}/s" for tps in tps_values],  # 添加数值标签
                textposition='auto',  # 自动标签位置
            )
        ])
        fig_tps.update_layout(
            title='TPS',
            xaxis_title="系统名称",
            yaxis_title="每秒事务数",
            showlegend=False
        )
        charts['tps_comparison'] = fig_tps.to_html(full_html=False)  # 将图表转为HTML

        return charts  # 返回所有图表

    def generate_html_report(self):
        """生成HTML报告"""
        # 生成图表
        charts = self.generate_charts()  # 调用方法生成所有图表

        # 读取HTML模板
        template = self._get_html_template()  # 获取HTML模板

        # 生成报告文件路径
        report_file = self.output_dir / f'test_report_{self.timestamp}.html'  # 设置报告文件路径

        # 渲染HTML
        html_content = template.render(
            timestamp=self.timestamp,  # 时间戳
            results=self.results,  # 测试结果
            charts=charts,  # 图表数据
            total_systems=len(self.results),  # 系统总数
            total_requests=sum(r['total_requests'] for r in self.results.values()),  # 总请求数
            total_success=sum(r['successful_requests'] for r in self.results.values()),  # 总成功数
            total_failed=sum(r['failed_requests'] for r in self.results.values()),  # 总失败数
            overall_avg_response_time=sum(r['average_response_time'] for r in self.results.values()) / len(
                self.results) if self.results else 0  # 平均响应时间
        )

        # 写入文件
        with open(report_file, 'w', encoding='utf-8') as f:  # 打开文件准备写入
            f.write(html_content)  # 写入HTML内容

        # 初始化邮件发送器
        sender = EmailSender(
            sender_email="2343434344@163.com",  # 发件人邮箱
            sender_password="EBiNKCD4TBn19JDJx"  # 你的SMTP授权码
        )

        # 发送邮件（带附件）
        success = sender.send_email(
            recipient_email="1229334343@qq.com",
            subject="自动化性能测试报告",
            body="自动化性能测试报告每日自动执行，详细报告数据请查看附件",
            attachment_path=report_file
        )

        if success:
            print("邮件发送任务已执行成功")
        else:
            print("邮件发送失败")

        print(f"HTML汇总报告已生成: {report_file}")

    def _get_html_template(self) -> Template:
        """
        获取HTML报告模板
        Returns:
            Template: Jinja2模板对象
        """
        # 这里是完整的HTML模板，包含了所有样式和结构
        template_str = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>性能测试报告</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.0.0/css/all.min.css" rel="stylesheet">
     <!-- 必须添加响应式meta声明 -->
    <meta name="viewport" content="width=device-width, initial-scale=1"> 

    <!-- 引入Bootstrap 5 CSS -->
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
</head>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        :root {
            --primary-color: #4285f4;
            --success-color: #00C851;
            --warning-color: #ffbb33;
            --danger-color: #ff4444;
        }
        body { 
            background-color: #f8f9fa; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .card { 
            margin-bottom: 20px; 
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            border: none;
            border-radius: 10px;
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card-header { 
            background-color: var(--primary-color); 
            color: white;
            border-radius: 10px 10px 0 0 !important;
            padding: 1rem;
        }
        .summary-item { 
            padding: 15px; 
            text-align: center;
            background: white;
            border-radius: 10px;
        }
        .summary-item i { 
            font-size: 2.5rem; 
            margin-bottom: 15px;
        }
        .success-rate { color: var(--success-color); }
        .error-rate { color: var(--danger-color); }
        .response-time { color: var(--primary-color); }
        .tps-rate { color: var(--warning-color); }
        .chart-container { 
            margin-top: 20px;
            background: white;
            padding: 15px;
            border-radius: 10px;
        }
        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .status-success { 
            background-color: var(--success-color); 
            color: white;
        }
        .status-error { 
            background-color: var(--danger-color); 
            color: white;
        }
        .table thead th {
            background-color: #f8f9fa;
            border-bottom: 2px solid var(--primary-color);
        }
        .system-card {
            border-left: 5px solid var(--primary-color);
        }
        .animate-on-scroll {
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.5s ease;
        }
        .animate-on-scroll.visible {
            opacity: 1;
            transform: translateY(0);
        }
        .progress {
            height: 10px;
            border-radius: 5px;
        }
        .progress-bar {
            background-color: var(--success-color);
        }
        .error-details {
            max-height: 300px;
            overflow-y: auto;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.5s ease forwards;
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // 添加滚动动画
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            });
            document.querySelectorAll('.animate-on-scroll').forEach((element) => {
                observer.observe(element);
            });
        });
    </script>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- 报告标题 -->
        <div class="row mb-4">
            <div class="col">
                <div class="card fade-in">
                    <div class="card-header">
                        <h3 class="mb-0">
                            <i class="fas fa-chart-line me-2"></i>性能测试报告
                        </h3>
                        <small class="text-white">生成时间: {{ timestamp }}</small>
                    </div>
                </div>
            </div>
        </div>
        <!-- 总体统计 -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card summary-item animate-on-scroll">
                    <div class="card-body">
                        <i class="fas fa-server"></i>
                        <h5>测试系统数</h5>
                        <h3>{{ total_systems }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card summary-item animate-on-scroll">
                    <div class="card-body">
                        <i class="fas fa-check-circle success-rate"></i>
                        <h5>总成功率</h5>
                        <h3>{{ "%.2f"|format(total_success / total_requests * 100 if total_requests > 0 else 0) }}%</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card summary-item animate-on-scroll">
                    <div class="card-body">
                        <i class="fas fa-clock response-time"></i>
                        <h5>平均响应时间</h5>
                        <h3>{{ "%.2f"|format(overall_avg_response_time) }}ms</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card summary-item animate-on-scroll">
                    <div class="card-body">
                        <i class="fas fa-exclamation-triangle error-rate"></i>
                        <h5>总错误数</h5>
                        <h3>{{ total_failed }}</h3>
                    </div>
                </div>
            </div>
        </div>
        <!-- 图表展示 -->
        <div class="row">
            <div class="col-md-4">
                <div class="card animate-on-scroll">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-pie me-2"></i>请求成功率</h5>
                    </div>
                    <div class="card-body">
                        {{ charts.overall_success_rate | safe }}
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card animate-on-scroll">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-bar me-2"></i>响应时间对比</h5>
                    </div>
                    <div class="card-body">
                        {{ charts.response_time_comparison | safe }}
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card animate-on-scroll">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-tachometer-alt me-2"></i>TPS对比</h5>
                    </div>
                    <div class="card-body">
                        {{ charts.tps_comparison | safe }}
                    </div>
                </div>
            </div>
        </div>
        <!-- 系统运行详情 -->
        {% for system_name, result in results.items() %}
        <div class="row mt-4">
            <div class="col">
                <div class="card system-card animate-on-scroll">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-server me-2"></i>{{ system_name }}
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="summary-item">
                                    <h6>总请求数</h6>
                                    <h4>{{ result.total_requests }}</h4>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="summary-item">
                                    <h6>成功率</h6>
                                    <h4>{{ "%.2f"|format(result.successful_requests / result.total_requests * 100 if result.total_requests > 0 else 0) }}%</h4>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="summary-item">
                                    <h6>平均响应时间</h6>
                                    <h4>{{ "%.2f"|format(result.average_response_time) }}ms</h4>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="summary-item">
                                    <h6>TPS</h6>
                                    <h4>{{ "%.2f"|format(result.tps) }}</h4>
                                </div>
                            </div>
                        </div>
                        <!-- 事务详情 -->
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>事务名称</th>
                                        <th>总次数</th>
                                        <th>成功率</th>
                                        <th>平均响应时间</th>
                                        <th>最小响应时间</th>
                                        <th>最大响应时间</th>
                                        <th>状态</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for label, stats in result.transactions.items() %}
                                    <tr>
                                        <td>{{ label }}</td>
                                        <td>{{ stats.count }}</td>
                                        <td>
                                            <div class="progress">
                                                <div class="progress-bar" role="progressbar" 
                                                     style="width: {{ "%.2f"|format(stats.success / stats.count * 100) }}%">
                                                    {{ "%.2f"|format(stats.success / stats.count * 100) }}%
                                                </div>
                                            </div>
                                        </td>
                                        <td>{{ "%.2f"|format(stats.avg_response_time) }}ms</td>
                                        <td>{{ "%.2f"|format(stats.min_response_time) }}ms</td>
                                        <td>{{ "%.2f"|format(stats.max_response_time) }}ms</td>
                                        <td>
                                            {% if stats.fail == 0 %}
                                            <span class="status-badge status-success">通过</span>
                                            {% else %}
                                            <span class="status-badge status-error">失败</span>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        <!-- 错误详情 -->
                        {% if result.error_details %}
                        <div class="mt-4">
                            <h6><i class="fas fa-exclamation-circle me-2"></i>错误详情</h6>
                            <div class="error-details">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>时间</th>
                                            <th>事务名称</th>
                                            <th>响应码</th>
                                            <th>错误信息</th>
                                            <th>线程组</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for error in result.error_details %}
                                        <tr>
                                            <td>{{ error.timestamp }}</td>
                                            <td>{{ error.label }}</td>
                                            <td>{{ error.response_code }}</td>
                                            <td>{{ error.response_message }}</td>
                                            <td>{{ error.thread_name }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
        '''
        return Template(template_str)

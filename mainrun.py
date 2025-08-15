import JMeterTestRunner
import ReportGenerator
import sys


def mainrun():
    """
    主程序入口
    """
    # 配置信息
    config = {
        'jmeter_home': r"D:/apache-jmeter-5.4.1",  # Jmeter安装目录
        'test_dir': r"D:/test/performance/program",  # JMX文件目录
        'result_dir': r"D:/test/performance/program/test_results"  # 结果保存目录
    }

    try:
        # 创建测试运行器
        runner = JMeterTestRunner.JMeterTestRunner(
            config['jmeter_home'],
            config['test_dir'],
            config['result_dir'])

        # 运行所有测试
        runner.run_all_tests()

        # 生成报告
        if runner.all_results:
            report_generator = ReportGenerator.ReportGenerator(
                runner.all_results,
                runner.result_dir
            )
            report_generator.generate_html_report()
            runner.logger.info("测试报告生成完成")
        else:
            runner.logger.warning("没有成功完成的测试，跳过报告生成")
    except Exception as e:
        print(f"发生未预期的错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    mainrun()
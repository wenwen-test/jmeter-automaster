import os
import subprocess
import pandas as pd
from typing import Dict, List, Any
import concurrent.futures
import datetime
from pathlib import Path
from typing import Optional
import TestUtils
# 自定义异常
class JMeterNotFoundException(Exception): pass
class JMXFileNotFoundException(Exception): pass
class TestExecutionException(Exception): pass
class JMeterTestException(Exception): pass

class JMeterTestRunner:
    def __init__(self, jmeter_home: str, test_dir: str, result_base_dir: str):
        """
        初始化JMeter测试运行器
        Args:
            jmeter_home: JMeter安装目录
            test_dir: 包含JMX文件的测试目录
            result_base_dir: 结果基础目录
        """
        # 设置Java和JMeter的编码环境
        os.environ['JAVA_TOOL_OPTIONS'] = '-Dfile.encoding=UTF-8'
        os.environ['JMETER_OPTS'] = '-Dfile.encoding=UTF-8'
        # 将路径转换为Path对象以便更好地处理
        self.jmeter_home = Path(jmeter_home)
        self.test_dir = Path(test_dir)
        self.result_base_dir = Path(result_base_dir)

        # 创建当天的结果目录
        self.result_dir = TestUtils.TestUtils.create_daily_directory(self.result_base_dir)

        # 设置日志
        log_dir = self.result_base_dir / 'logs'
        self.logger = TestUtils.TestUtils.setup_logging(log_dir)

        # 检查JMeter安装
        if not TestUtils.TestUtils.check_jmeter_installation(self.jmeter_home):
            raise JMeterNotFoundException(f"JMeter未在指定目录找到: {self.jmeter_home}")

        # 设置JMeter可执行文件路径
        self.jmeter_bin = self.jmeter_home / 'bin' / 'jmeter.bat'
        # 生成时间戳用于结果目录命名
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        # 存储所有测试结果的字典
        self.all_results = {}

    def find_jmx_files(self) -> List[Path]:
        """
        在测试目录中查找所有JMX文件
        Returns:
            List[Path]: JMX文件路径列表
        Raises:
            JMXFileNotFoundException: 未找到JMX文件时抛出
        """
        # 递归查找所有.jmx文件
        jmx_files = list(self.test_dir.glob('**/*.jmx'))
        if not jmx_files:
            raise JMXFileNotFoundException(f"在目录 {self.test_dir} 中未找到JMX文件")
        return jmx_files

    def run_single_test(self, jmx_file: Path) -> Optional[Dict[str, Any]]:
        """
        运行单个JMX文件的测试
        Args:
            jmx_file: JMX文件路径
        Returns:
            Optional[Dict]: 测试结果统计，失败时返回None
        Raises:
            TestExecutionException: 测试执行失败时抛出
        """
        try:
            # 获取测试名称并创建结果目录
            test_name = jmx_file.stem
            test_result_dir = self.result_dir / f"{test_name}_{self.timestamp}"
            jtl_file = test_result_dir / f"{test_name}.jtl"
            report_dir = test_result_dir / "html_report"

            # 创建结果目录
            test_result_dir.mkdir(parents=True, exist_ok=True)

            # 构建JMeter命令
            command = [
                str(self.jmeter_bin),
                '-Jjmeter.save.saveservice.output_format=csv',  # 设置输出格式为CSV
                '-Jfile.encoding=UTF-8',  # 设置文件编码
                '-n',  # 非GUI模式
                '-t', str(jmx_file),  # 测试文件
                '-l', str(jtl_file),  # 结果文件
                '-e',  # 生成测试报告
                '-o', str(report_dir)  # 报告输出目录
            ]

            self.logger.info(f"开始执行测试计划: {test_name}")

            # 执行命令并捕获输出
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            # 记录JMeter输出
            self.logger.debug(f"JMeter输出:\n{process.stdout}")
            if process.stderr:
                self.logger.warning(f"JMeter警告:\n{process.stderr}")

            self.logger.info(f"测试完成: {test_name}")

            # 检查结果文件
            if not jtl_file.exists():
                raise TestExecutionException(f"结果文件未生成: {jtl_file}")

            # 解析结果并返回
            results = self.parse_results(jtl_file, test_name)
            results['report_dir'] = str(report_dir)
            return results

        except subprocess.CalledProcessError as e:
            self.logger.error(f"执行测试失败 {test_name}: {e}")
            self.logger.error(f"错误输出: {e.stderr}")
            raise TestExecutionException(f"执行测试 {test_name} 失败: {e}")
        except Exception as e:
            self.logger.error(f"测试过程发生异常 {test_name}: {e}")
            raise TestExecutionException(f"测试 {test_name} 发生异常: {e}")

    def run_all_tests(self):
        """
        并行运行所有JMX文件的测试
        Raises:
            JMeterTestException: 测试过程中的任何异常
        """
        try:
            # 查找所有JMX文件
            jmx_files = self.find_jmx_files()
            self.logger.info(f"找到 {len(jmx_files)} 个JMX文件")

            failed_tests = []
            # 使用线程池并行执行测试
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_jmx = {
                    executor.submit(self.run_single_test, jmx): jmx
                    for jmx in jmx_files
                }

                # 处理完成的测试
                for future in concurrent.futures.as_completed(future_to_jmx):
                    jmx = future_to_jmx[future]
                    try:
                        result = future.result()
                        if result:
                            self.all_results[jmx.stem] = result
                        else:
                            failed_tests.append(jmx.stem)
                    except Exception as e:
                        self.logger.error(f"测试 {jmx.stem} 执行失败: {e}")
                        failed_tests.append(jmx.stem)

            # 记录失败的测试
            if failed_tests:
                self.logger.warning(f"以下测试执行失败: {', '.join(failed_tests)}")

        except Exception as e:
            self.logger.error(f"执行测试套件时发生错误: {e}")
            raise

    def parse_results(self, jtl_file: Path, test_name: str) -> Dict[str, Any]:
        """
        解析JMeter测试结果
        Args:
            jtl_file: JTL结果文件路径
            test_name: 测试名称
        Returns:
            Dict: 包含测试结果统计的字典
        """
        # 初始化结果统计字典
        summary = {
            'test_name': test_name,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'min_response_time': float('inf'),
            'max_response_time': 0,
            'error_details': [],
            'transactions': {},
            'tps': 0,
            'error_rate': 0
        }

        # 读取CSV文件进行结果分析
        df = pd.read_csv(jtl_file)

        # 基本统计
        summary['total_requests'] = len(df)
        summary['successful_requests'] = len(df[df['success'] == True])
        summary['failed_requests'] = len(df[df['success'] == False])
        summary['average_response_time'] = df['elapsed'].mean()
        summary['min_response_time'] = df['elapsed'].min()
        summary['max_response_time'] = df['elapsed'].max()

        # 计算TPS
        test_duration = (df['timeStamp'].max() - df['timeStamp'].min()) / 1000  # 转换为秒
        summary['tps'] = summary['total_requests'] / test_duration if test_duration > 0 else 0

        # 计算错误率
        summary['error_rate'] = (summary['failed_requests'] / summary['total_requests'] * 100
                                 if summary['total_requests'] > 0 else 0)

        # 按事务名称分组统计
        for label, group in df.groupby('label'):
            summary['transactions'][label] = {
                'count': len(group),
                'success': len(group[group['success'] == True]),
                'fail': len(group[group['success'] == False]),
                'avg_response_time': group['elapsed'].mean(),
                'min_response_time': group['elapsed'].min(),
                'max_response_time': group['elapsed'].max(),
                'error_rate': (len(group[group['success'] == False]) / len(group) * 100
                               if len(group) > 0 else 0)
            }

        # 收集错误详情
        error_df = df[df['success'] == False]
        for _, row in error_df.iterrows():
            summary['error_details'].append({
                'label': row['label'],
                'response_code': row['responseCode'],
                'response_message': row['failureMessage'],
                'thread_name': row['threadName'],
                'timestamp': datetime.datetime.fromtimestamp(row['timeStamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            })

        return summary
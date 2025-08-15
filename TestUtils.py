import logging
import  datetime
from pathlib import Path

class TestUtils:
    """测试工具类，处理目录创建和日志配置"""

    @staticmethod
    def setup_logging(log_dir: Path) -> logging.Logger:
        """
        配置日志
        Args:
            log_dir: 日志目录
        Returns:
            logging.Logger: 日志记录器
        """
        # 确保日志目录存在
        log_dir.mkdir(parents=True, exist_ok=True)  # 创建日志目录，包括所有必要的父目录

        # 创建日志记录器
        logger = logging.getLogger('JMeterTest')  # 创建名为'JMeterTest'的日志记录器
        logger.setLevel(logging.INFO)  # 设置日志级别为INFO

        # 创建按天滚动的文件处理器
        log_file = log_dir / f'test_{datetime.datetime.now().strftime("%Y%m%d")}.log'  # 生成按日期命名的日志文件
        file_handler = logging.FileHandler(log_file, encoding='utf-8')  # 创建文件处理器，使用UTF-8编码
        file_handler.setLevel(logging.INFO)  # 设置文件处理器日志级别为INFO

        # 创建控制台处理器
        console_handler = logging.StreamHandler()  # 创建控制台处理器
        console_handler.setLevel(logging.INFO)  # 设置控制台处理器日志级别为INFO

        # 设置日志格式
        formatter = logging.Formatter(  # 创建日志格式器
            '%(asctime)s - %(levelname)s - %(message)s',  # 日志格式：时间-级别-消息
            datefmt='%Y-%m-%d %H:%M:%S'  # 日期格式
        )
        file_handler.setFormatter(formatter)  # 设置文件处理器格式
        console_handler.setFormatter(formatter)  # 设置控制台处理器格式

        # 添加处理器
        logger.addHandler(file_handler)  # 添加文件处理器到日志记录器
        logger.addHandler(console_handler)  # 添加控制台处理器到日志记录器

        return logger  # 返回配置好的日志记录器

    @staticmethod
    def create_daily_directory(base_dir: Path) -> Path:
        """
        创建按天组织的目录结构
        Args:
            base_dir: 基础目录
        Returns:
            Path: 当天的结果目录
        """
        today = datetime.datetime.now().strftime('%Y%m%d')  # 获取当前日期，格式为YYYYMMDD
        daily_dir = base_dir / today  # 组合基础目录和日期目录
        daily_dir.mkdir(parents=True, exist_ok=True)  # 创建目录，包括所有必要的父目录
        return daily_dir  # 返回创建的目录路径

    @staticmethod
    def check_jmeter_installation(jmeter_home: Path) -> bool:
        """
        检查JMeter安装是否有效
        Args:
            jmeter_home: JMeter安装目录
        Returns:
            bool: 安装是否有效
        """
        jmeter_bin = jmeter_home / 'bin' / 'jmeter.bat'  # 组合JMeter可执行文件路径
        return jmeter_bin.exists()  # 检查文件是否存在，返回布尔值

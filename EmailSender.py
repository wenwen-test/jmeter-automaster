import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


class EmailSender:
    """
    邮件发送工具类（163邮箱专用）
    示例用法：
        sender = EmailSender("45893882@163.com", "your_smtp_password")
        sender.send_email(
            "recipient@example.com",
            "邮件主题",
            "邮件正文",
            "/path/to/attachment.txt"
        )
    """

    def __init__(self, sender_email, sender_password, smtp_server="smtp.163.com", smtp_port=465):
        """
        初始化邮件发送器

        :param sender_email: 发件人163邮箱地址
        :param sender_password: SMTP授权码
        :param smtp_server: SMTP服务器地址，默认163
        :param smtp_port: SMTP端口，默认465(SSL)
        """
        self.sender_email = sender_email  # 发件人邮箱地址
        self.sender_password = sender_password  # SMTP授权码
        self.smtp_server = smtp_server  # SMTP服务器地址
        self.smtp_port = smtp_port  # SMTP端口号

    def send_email(self, recipient_email, subject, body, attachment_path=None):
        """
        发送带附件的邮件

        :param recipient_email: 收件人邮箱地址
        :param subject: 邮件主题
        :param body: 邮件正文
        :param attachment_path: 附件路径(可选)
        :return: 是否发送成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()  # 创建一个MIMEMultipart对象，用于构建邮件
            msg['From'] = self.sender_email  # 设置发件人
            msg['To'] = recipient_email  # 设置收件人
            msg['Subject'] = subject  # 设置邮件主题
            msg.attach(MIMEText(body, 'plain', 'utf-8'))  # 添加邮件正文

            # 添加附件（如果存在）
            if attachment_path:  # 如果提供了附件路径
                attachment_name = os.path.basename(attachment_path)  # 获取附件文件名
                with open(attachment_path, "rb") as attachment:  # 以二进制模式读取附件
                    part = MIMEBase('application', 'octet-stream')  # 创建MIMEBase对象
                    part.set_payload(attachment.read())  # 设置附件内容
                encoders.encode_base64(part)  # 对附件进行Base64编码
                part.add_header('Content-Disposition',  # 添加附件头信息
                                f'attachment; filename={attachment_name}')
                msg.attach(part)  # 将附件添加到邮件中

            # 连接SMTP服务器并发送
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:  # 建立SSL连接
                server.login(self.sender_email, self.sender_password)  # 登录SMTP服务器
                server.sendmail(self.sender_email, recipient_email, msg.as_string())  # 发送邮件

            print("邮件发送成功！")  # 发送成功提示
            return True  # 返回发送成功标志

        except smtplib.SMTPAuthenticationError:  # 处理SMTP认证错误
            print("认证失败：请检查邮箱地址和SMTP授权码是否正确")
        except Exception as e:  # 处理其他异常
            print(f"邮件发送失败: {e}")
        return False  # 返回发送失败标志
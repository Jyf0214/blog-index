import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from email import encoders

# 配置
login_url = "https://passport.arknights.app/api/v1/login"
game_log_url_template = "https://api.arknights.app/game/log/{}/{}"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_ID_SERVER_TOKEN"  # 替换为实际的Token
}
login_data = {
    "email": os.getenv("EMAIL"),
    "password": os.getenv("PASSWORD")
}

smtp_server = "smtp-relay.brevo.com"
smtp_port = 587
smtp_user = os.getenv("SMTP_USER")  # 发送方邮箱账号
smtp_password = os.getenv("SMTP_PASSWORD")  # 发送方邮箱密码
to_email = os.getenv("TOEMAIL")
subject = os.getenv("MAIL_SUBJECT")

# 下载图片并保存
def download_image(image_url, image_path):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        with open(image_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"图片已保存: {image_path}")
    except requests.exceptions.RequestException as e:
        print(f"下载图片失败: {e}")

# 登录并获取Token
def login():
    try:
        response = requests.post(login_url, json=login_data, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        response_json = response.json()

        if response_json["code"] == 1:
            token = response_json["data"]["token"]
            print("登录成功，Token:", token)
            return token
        else:
            print("登录失败:", response_json["message"])
            return None
    except requests.exceptions.RequestException as e:
        print(f"登录请求错误: {e}")
    except ValueError as e:
        print(f"JSON解析错误: {e}")

# 获取游戏日志
def get_game_logs(token, account, offset):
    try:
        headers["Authorization"] = f"Bearer {token}"  # 使用登录获取的Token
        url = game_log_url_template.format(account, offset)
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        response_json = response.json()

        if response_json["code"] == 1:
            logs_data = response_json.get("data", {})
            print("获取游戏日志成功")
            return logs_data
        else:
            print("获取游戏日志失败:", response_json["message"])
            return None
    except requests.exceptions.RequestException as e:
        print(f"获取游戏日志请求错误: {e}")
    except ValueError as e:
        print(f"JSON解析错误: {e}")

# 将时间戳转换为可读的时间格式
def timestamp_to_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# 打印符合条件的游戏日志并生成邮件内容
def get_filtered_game_logs(logs_data):
    keywords = [
        "[卡池] 单抽获得干员：[5",
        "[卡池] 单抽获得干员：[6",
        "[公招] 高星提醒",
    ]

    filtered_logs = []
    for log_entry in logs_data.get("logs", []):
        log_id = log_entry.get("id", "无")
        log_ts = log_entry.get("ts", "无")
        log_name = log_entry.get("name", "无")
        log_level = log_entry.get("logLevel", "无")
        log_content = log_entry.get("content", "无")

        # 转换时间戳为时间格式
        log_time = timestamp_to_datetime(log_ts)

        if any(keyword in log_content for keyword in keywords):
            filtered_logs.append(
                f"<br>时间: {log_time}<br>日志: {log_content}<br>"
            )

    return "<br>".join(filtered_logs) if filtered_logs else "<br>没有符合条件的日志<br>"

# 使用Lark SMTP发送邮件

def send_email(subject, body, attachments):
    try:
        msg = MIMEMultipart()
        # 优先从环境变量获取发件人邮箱地址
        frommail = os.getenv("FROMMAIL", smtp_user)
        msg["From"] = frommail
        msg["To"] = to_email
        msg["Subject"] = subject

        # 邮件内容
        msg.attach(MIMEText(body, "html", "utf-8"))

        # 添加附件
        for image_path, cid in attachments:
            with open(image_path, 'rb') as img:
                mime_image = MIMEImage(img.read())
                mime_image.add_header('Content-ID', f'<{cid}>')
                # 使用 inline 并指定 filename，提示这是嵌入图像，同时可下载
                mime_image.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
                msg.attach(mime_image)

        # 判断端口并选择相应的加密方式
        if smtp_port == 465:
            # 使用 SSL
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(frommail, to_email, msg.as_string())
        else:
            # 使用 TLS 或普通连接（通常是 25 或 587）
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if smtp_port == 587:
                    server.starttls()  # 使用 TLS
                server.login(smtp_user, smtp_password)
                server.sendmail(frommail, to_email, msg.as_string())

        print("邮件发送成功")
    except Exception as e:
        print(f"发送邮件失败: {e}")

# 执行流程
if __name__ == "__main__":
    token = login()
    if token:
        # 从环境变量中获取账号列表
        accounts = os.getenv("ACCOUNTS").split(",")  # 使用逗号分隔的账号列表
        offsets = [0]  # 根据需要调整offset

        all_filtered_logs = ""

        for account in accounts:
            print(f"\n查询账号中(公开库不提示私密信息)")
            for offset in offsets:
                logs_data = get_game_logs(token, account.strip(), offset)  # 去除账号中的空格
                if logs_data:
                    filtered_logs = get_filtered_game_logs(logs_data)
                    all_filtered_logs += f"\n\n账号: {account}\nOffset: {offset}\n{filtered_logs}"
                else:
                    print("没有更多日志")

        # 如果有符合条件的日志，才发送邮件
        if all_filtered_logs.strip():  # 检查是否有非空的日志内容
            # 下载背景图
            background_image_url = "https://t.mwm.moe/mp"
            image_path = "background.jpg"
            download_image(background_image_url, image_path)

            # 创建邮件正文
            email_body = f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Jyf0214</title>
            </head>
            <body>
                <div class="cover" style="position: relative; width: 100%; max-width: 600px; margin: 0 auto; overflow: hidden; border-radius: 15px;">
                    <img src="cid:background_cid" alt="background" style="width: 100%; height: 100%; object-fit: cover; display: block; filter: brightness(50%);">
                    <section style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; text-align: center; color: #000; padding: 20px; box-sizing: border-box; background-color: rgba(255, 255, 255, 0.5); border-radius: 15px;">
                        <h2 style="margin: 0; font-size: 24px;">日志</h2>
                        <p style="margin: 10px 0; font-size: 16px;">{all_filtered_logs}</p>
                    </section>
                </div>
            </body>
            </html>
            """

            # 创建附件列表
            attachments = [(image_path, "background_cid")]

            # 发送邮件
            send_email(subject, email_body, attachments)
        else:
            print("没有符合条件的日志，邮件未发送")
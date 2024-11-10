import requests
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 配置
login_url = "https://passport.arknights.app/api/v1/login"
game_log_url_template = "https://api.arknights.app/game/log/{}/{}"
background_image_url = "https://t.mwm.moe/mp"  # 背景图片 URL
hitokoto_api_url = "https://v1.hitokoto.cn/?c=i"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_ID_SERVER_TOKEN"  # 替换为实际的Token
}
login_data = {
    "email": os.getenv("EMAIL"),
    "password": os.getenv("PASSWORD")
}

smtp_server = "smtp.larksuite.com"
smtp_port = 465
smtp_user = os.getenv("SMTP_USER")  # 发送方邮箱账号
smtp_password = os.getenv("SMTP_PASSWORD")  # 发送方邮箱密码
to_email = os.getenv("TOEMAIL")
subject = os.getenv("MAIL_SUBJECT")

# 登录并获取Token
def login():
    try:
        response = requests.post(login_url, json=login_data, headers=headers)
        response.raise_for_status()
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
        headers["Authorization"] = f"Bearer {token}"
        url = game_log_url_template.format(account, offset)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
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

# 获取一言
def get_hitokoto():
    try:
        response = requests.get(hitokoto_api_url)
        response.raise_for_status()
        data = response.json()
        return f"{data['hitokoto']} ——{data['from_who']}《{data['from']}》"
    except Exception as e:
        print(f"获取一言失败: {e}")
        return ""

# 下载背景图片
def download_background_image():
    try:
        response = requests.get(background_image_url, stream=True)
        response.raise_for_status()
        with open("background_image.jpg", "wb") as img_file:
            for chunk in response.iter_content(1024):
                img_file.write(chunk)
        return "background_image.jpg"
    except Exception as e:
        print(f"下载背景图片失败: {e}")
        return None

# 将时间戳转换为可读的时间格式
def timestamp_to_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# 打印符合条件的游戏日志并生成邮件内容
def get_filtered_game_logs(logs_data):
    keywords = [
        "[基建] 当前训练室角色",
        "[公招] 高星提醒",
    ]

    filtered_logs = []
    for log_entry in logs_data.get("logs", []):
        log_ts = log_entry.get("ts", "无")
        log_content = log_entry.get("content", "无")
        log_time = timestamp_to_datetime(log_ts)

        if any(keyword in log_content for keyword in keywords):
            filtered_logs.append(
                f"时间: {log_time}<br>日志: {log_content}<br><br>"
            )

    return "<br>".join(filtered_logs) if filtered_logs else "没有符合条件的日志"

# 使用Lark SMTP发送邮件
def send_email(subject, body, background_image_path):
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject

        with open(background_image_path, "rb") as img_file:
            image_data = img_file.read()

        # 添加背景图片为附件
        image_part = MIMEText(image_data, "base64", "utf-8")
        image_part["Content-Disposition"] = f'attachment; filename="background_image.jpg"'
        image_part["Content-Type"] = "image/jpeg"
        msg.attach(image_part)

        # 邮件内容 HTML
        msg.attach(MIMEText(body, "html", "utf-8"))

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(f"发送邮件失败: {e}")

# 执行流程
if __name__ == "__main__":
    token = login()
    if token:
        accounts = os.getenv("ACCOUNTS").split(",")
        offsets = [0]

        all_filtered_logs = ""
        for account in accounts:
            for offset in offsets:
                logs_data = get_game_logs(token, account.strip(), offset)
                if logs_data:
                    filtered_logs = get_filtered_game_logs(logs_data)
                    all_filtered_logs += f"账号: {account}<br>Offset: {offset}<br>{filtered_logs}<br><br>"

        if all_filtered_logs.strip():
            hitokoto_text = get_hitokoto()
            background_image_path = download_background_image()

            # 邮件 HTML 模板
            email_body = f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>日志邮件</title>
            </head>
            <body>
                <div class="cover" style="text-align: center;">
                    <h2 style="font-size: 24px;">日志</h2>
                    <p style="font-size: 16px;">{all_filtered_logs}</p>
                    <p style="font-size: 16px;">一言: {hitokoto_text}</p>
                    <p style="font-size: 14px;">背景图片</p>
                </div>
            </body>
            </html>
            """
            if background_image_path:
                send_email(subject, email_body, background_image_path)
        else:
            print("没有符合条件的日志，邮件未发送")
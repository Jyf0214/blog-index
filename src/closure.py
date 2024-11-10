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

# 获取随机一言
def get_random_quote():
    try:
        response = requests.get("https://v1.hitokoto.cn/?c=i")
        response.raise_for_status()  # 检查请求是否成功
        quote_data = response.json()
        return quote_data["hitokoto"], quote_data["from"], quote_data["from_who"]
    except requests.exceptions.RequestException as e:
        print(f"获取一言失败: {e}")
        return "这是一句随机一言。", "未知", "未知"

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
        log_id = log_entry.get("id", "无")
        log_ts = log_entry.get("ts", "无")
        log_name = log_entry.get("name", "无")
        log_level = log_entry.get("logLevel", "无")
        log_content = log_entry.get("content", "无")

        # 转换时间戳为时间格式
        log_time = timestamp_to_datetime(log_ts)

        if any(keyword in log_content for keyword in keywords):
            filtered_logs.append(
                f"\n时间: {log_time}<br>名称: {log_name}<br><br>日志: {log_content}"
            )

    return "<br>".join(filtered_logs) if filtered_logs else "没有符合条件的日志"

# 使用Lark SMTP发送邮件
def send_email(subject, body):
    try:
        # 获取随机一言
        quote, from_info, from_who = get_random_quote()
        background_image_url = "https://t.mwm.moe/mp"  # API背景图片链接

        # 构建HTML邮件内容
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
                <img src="{background_image_url}" alt="background" style="width: 100%; height: 100%; object-fit: cover; display: block; filter: brightness(50%);">
                <section style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; text-align: center; color: #000; padding: 20px; box-sizing: border-box; background-color: rgba(255, 255, 255, 0.5); border-radius: 15px;">
                    <h2 style="margin: 0; font-size: 24px;">日志</h2>
                    <p style="margin: 10px 0; font-size: 16px;">{body}</p>
                    <p style="margin: 10px 0; font-size: 16px;">一言: {quote}</p>
                    <p style="margin: 10px 0; font-size: 16px;">出自: {from_info} — {from_who}</p>
                    <p style="margin: 10px 0; font-size: 16px;">背景图片链接</p>
                    <a href="{background_image_url}" style="color: #000; font-size: 14px; text-decoration: none;">{background_image_url}</a>
                </section>
            </div>

            <div class="container" style="display: flex; align-items: center; max-width: 400px; margin: 20px auto; position: relative; overflow: hidden; border-radius: 15px; background-color: #eaeaea; padding: 10px; height: 80px;">
                <div class="background" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: url('https://k.sinaimg.cn/n/sinacn10107/742/w1024h518/20190623/0bf4-hyvnhqp8087508.jpg/w700d1q75cms.jpg'); background-size: cover; background-position: center; opacity: 0.2; z-index: 1;"></div>
                <div class="mask" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(255, 255, 255, 0.8); z-index: 2;"></div>
                <img src="https://avatars.githubusercontent.com/u/169313142?v=4" alt="头像" style="width: 60px; height: 60px; border-radius: 50%; margin-right: 15px; z-index: 3;">
                <div class="info" style="display: flex; flex-direction: column; flex-grow: 1; z-index: 3;">
                    <h2 style="font-size: 1.2em; margin: 0; color: #333;">Amiya(Jyf0214)</h2>
                    <p style="font-size: 1em; margin: 0; color: #555;"><strong>Email:</strong> admin@amiya.ip-dynamic.org</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 发送邮件
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject

        # 邮件内容
        msg.attach(MIMEText(email_body, "html", "utf-8"))

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(f"发送邮件失败: {e}")

# 执行流程
# 执行流程
if __name__ == "__main__":
    # 登录并获取Token
    token = login()
    
    if token:
        # 获取游戏日志
        account = os.getenv("ACCOUNT")  # 替换为实际的账号
        logs_data = get_game_logs(token, account, offset=0)
        
        if logs_data:
            # 过滤并生成邮件内容
            body = get_filtered_game_logs(logs_data)
            
            # 发送邮件
            send_email(subject, body)
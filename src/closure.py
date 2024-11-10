import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
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

# 时间戳转换
def timestamp_to_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# 筛选游戏日志
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
        log_content = log_entry.get("content", "无")
        log_time = timestamp_to_datetime(log_ts)

        if any(keyword in log_content for keyword in keywords):
            filtered_logs.append(
                f"时间: {log_time}<br>名称: {log_name}<br>日志: {log_content}<br><br>"
            )
    return "<br>".join(filtered_logs) if filtered_logs else "没有符合条件的日志"

# 获取“一言”内容
def get_hitokoto():
    try:
        response = requests.get("https://v1.hitokoto.cn/?c=i")
        response.raise_for_status()
        data = response.json()
        hitokoto = data.get("hitokoto", "无")
        from_who = data.get("from_who", "未知")
        return f"{hitokoto} ——{from_who}"
    except requests.exceptions.RequestException as e:
        print(f"获取一言内容失败: {e}")
        return "获取一言内容失败"

# 下载并获取背景图片
def download_background_image():
    try:
        response = requests.get("https://t.mwm.moe/mp")
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"下载背景图片失败: {e}")
        return None

# 发送邮件
def send_email(subject, body, image_data):
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject

        # 邮件内容
        msg.attach(MIMEText(body, "html", "utf-8"))

        # 添加背景图片作为附件
        if image_data:
            image = MIMEImage(image_data)
            image.add_header('Content-ID', '<background_image>')  # 确保Content-ID一致
            msg.attach(image)

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(f"发送邮件失败: {e}")

# 主流程
if __name__ == "__main__":
    token = login()
    if token:
        accounts = os.getenv("ACCOUNTS").split(",")
        offsets = [0]

        all_filtered_logs = ""
        for account in accounts:
            print(f"\n查询账号中(公开库不提示私密信息)")
            for offset in offsets:
                logs_data = get_game_logs(token, account.strip(), offset)
                if logs_data:
                    filtered_logs = get_filtered_game_logs(logs_data)
                    all_filtered_logs += f"<br><br>账号: {account}<br>Offset: {offset}<br>{filtered_logs}"
                else:
                    print("没有更多日志")

        # 处理“一言”内容
        random_quote = get_hitokoto()
        background_image_data = download_background_image()

        # 邮件HTML内容
        email_body = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>日志</title>
        </head>
        <body>
            <div style="position: relative; width: 100%; max-width: 600px; margin: 0 auto; overflow: hidden; border-radius: 15px;">
                <img src="cid:background_image" alt="background" style="width: 100%; height: 100%; object-fit: cover; display: block; filter: brightness(50%);">
                <section style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; text-align: center; color: #000; padding: 20px; background-color: rgba(255, 255, 255, 0.5); border-radius: 15px;">
                    <h2 style="margin: 0; font-size: 24px;">日志</h2>
                    <p style="margin: 10px 0; font-size: 16px;">{all_filtered_logs}</p>
                    <p style="margin: 10px 0; font-size: 16px;">一言: {random_quote}</p>
                </section>
            </div>
        </body>
        </html>
        """
        if all_filtered_logs.strip():
            send_email(subject, email_body, background_image_data)
        else:
            print("没有符合条件的日志，邮件未发送")
import requests
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 配置和登录函数保持不变

# 获取随机的一言内容
def get_random_quote():
    try:
        response = requests.get("https://v1.hitokoto.cn/?c=i")
        response.raise_for_status()
        data = response.json()
        return data.get("hitokoto", "没有获取到一言")
    except requests.exceptions.RequestException as e:
        print(f"获取一言请求错误: {e}")
        return "没有获取到一言"

# 邮件内容生成函数，添加背景图片和一言
def generate_email_body(log_content):
    background_image_url = "https://t.mwm.moe/mp"  # 背景图片链接
    random_quote = get_random_quote()  # 获取一言内容

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
        <div class="cover" style="position: relative; width: 100%; max-width: 600px; margin: 0 auto; overflow: hidden; border-radius: 15px;">
            <img src="{background_image_url}" alt="background" style="width: 100%; height: 100%; object-fit: cover; display: block; filter: brightness(50%);">
            <section style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; text-align: center; color: #000; padding: 20px; box-sizing: border-box; background-color: rgba(255, 255, 255, 0.5); border-radius: 15px;">
                <h2 style="margin: 0; font-size: 24px;">日志</h2>
                <p style="margin: 10px 0; font-size: 16px;">{log_content}</p>
                <p style="margin: 10px 0; font-size: 16px;">一言: {random_quote}</p>
                <p style="margin: 10px 0; font-size: 16px;">背景图片链接</p>
                <a href="{background_image_url}" style="color: #000; font-size: 14px; text-decoration: none;">{background_image_url}</a>
            </section>
        </div>
    </body>
    </html>
    """
    return email_body

# 发送邮件函数，添加图片附件
def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject

        # 邮件内容
        msg.attach(MIMEText(body, "html", "utf-8"))

        # 添加背景图片为附件
        response = requests.get("https://t.mwm.moe/mp")
        if response.status_code == 200:
            attachment = MIMEText(response.content, "base64", "utf-8")
            attachment["Content-Disposition"] = 'attachment; filename="background.jpg"'
            msg.attach(attachment)
        else:
            print("获取背景图片失败")

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(f"发送邮件失败: {e}")

# 主流程保持不变，修改调用generate_email_body
if __name__ == "__main__":
    token = login()
    if token:
        accounts = os.getenv("ACCOUNTS").split(",")
        offsets = [0]
        all_filtered_logs = ""

        for account in accounts:
            print(f"\n查询账号中...")
            for offset in offsets:
                logs_data = get_game_logs(token, account.strip(), offset)
                if logs_data:
                    filtered_logs = get_filtered_game_logs(logs_data)
                    all_filtered_logs += f"\n\n账号: {account}\nOffset: {offset}\n{filtered_logs}"
                else:
                    print("没有更多日志")

        if all_filtered_logs.strip():
            email_body = generate_email_body(all_filtered_logs)
            send_email(subject, email_body)
        else:
            print("没有符合条件的日志，邮件未发送")
import os
import subprocess

# 配置
repo_url = "git@github.com:Jyf0214/blog-index.git"
assets_dir = "."  # 需要推送的目录
git_username = "Jyf0214"
git_email = os.getenv("EMAIL")  # 使用你的 GitHub 邮箱

# 确保当前工作目录是正确的
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 初始化 Git 仓库（如果还没有的话）
if not os.path.exists(".git"):
    subprocess.run(["git", "init", "-b", "main"])  # 指定初始分支为 main

# 设置 Git 用户名和邮箱
subprocess.run(["git", "config", "user.name", git_username])
subprocess.run(["git", "config", "user.email", git_email])

# 添加远程仓库 origin（如果还没有的话）
try:
    subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
except subprocess.CalledProcessError:
    print("Remote origin already exists. Continuing with existing remote.")

# 添加、提交并推送到 GitHub
try:
    # 拉取远程仓库最新内容，以便合并历史记录
    subprocess.run(["git", "fetch", "origin", "main"], check=True)
    subprocess.run(["git", "merge", "origin/main", "--allow-unrelated-histories"], check=True)

    # 添加文件夹内容
    subprocess.run(["git", "add", assets_dir], check=True)

    # 提交更改
    subprocess.run(["git", "commit", "-m", "Update assets folder"], check=True)

    # 推送到远程仓库
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Successfully pushed assets folder to GitHub.")
except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
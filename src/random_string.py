import random
import string

# 生成 16 位随机字符串
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# 保存为 TXT 文件
with open('data.txt', 'w') as f:
    f.write(random_string)

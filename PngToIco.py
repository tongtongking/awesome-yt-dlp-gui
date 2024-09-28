from PIL import Image

# 打开 PNG 文件
img = Image.open("bilibili.png")

# 保存为 ICO 文件
img.save("bilibili.ico")
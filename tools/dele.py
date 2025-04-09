import os

# 指定图片文件夹路径，与之前代码中的 image_folder 保持一致
image_folder = r"D:\Microsoft Downloads\CCPD2019\train"

# 检查文件夹是否存在
if os.path.exists(image_folder):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(image_folder):
        # 检查文件是否为 .txt 文件
        if filename.lower().endswith('.txt'):
            # 构建文件的完整路径
            txt_path = os.path.join(image_folder, filename)
            try:
                # 删除文件
                os.remove(txt_path)
                print(f"已删除文件: {txt_path}")
            except Exception as e:
                print(f"删除文件 {txt_path} 时出错: {e}")
else:
    print(f"指定的文件夹路径 {image_folder} 不存在，请检查。")
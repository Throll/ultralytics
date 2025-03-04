import os
import random
import shutil

# 设置随机数种子，保证结果可复现
random.seed(42)

def split_images(source_folder, train_folder, val_folder, split_ratio=0.8):
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder):
        print(f"源文件夹 {source_folder} 不存在。")
        return

    # 创建训练集和验证集文件夹
    if not os.path.exists(train_folder):
        os.makedirs(train_folder)
    if not os.path.exists(val_folder):
        os.makedirs(val_folder)

    # 获取源文件夹中的所有图片文件
    image_files = [f for f in os.listdir(source_folder) if f.lower().endswith(('txt', '.jpeg', '.png', '.bmp'))]

    # 随机打乱图片文件列表
    random.shuffle(image_files)

    # 计算训练集和验证集的分割点
    split_index = int(len(image_files) * split_ratio)

    # 划分训练集和验证集
    train_files = image_files[:split_index]
    val_files = image_files[split_index:]

    # 将图片复制到训练集和验证集文件夹
    for file in train_files:
        source_path = os.path.join(source_folder, file)
        destination_path = os.path.join(train_folder, file)
        shutil.copyfile(source_path, destination_path)

    for file in val_files:
        source_path = os.path.join(source_folder, file)
        destination_path = os.path.join(val_folder, file)
        shutil.copyfile(source_path, destination_path)

    print(f"训练集图片数量: {len(train_files)}")
    print(f"验证集图片数量: {len(val_files)}")
    print("图片划分完成。")

if __name__ == "__main__":
    # 源图片文件夹路径
    source_folder = "D:\data\labels"
    # 训练集文件夹路径
    train_folder = r"D:\data\train1"
    # 验证集文件夹路径
    val_folder = r"D:\data\val1"

    split_images(source_folder, train_folder, val_folder)
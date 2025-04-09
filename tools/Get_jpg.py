import os
import shutil

def extract_jpg_files(source_folder, destination_folder):
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder):
        print(f"源文件夹 {source_folder} 不存在。")
        return

    # 如果目标文件夹不存在，则创建它
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历源文件夹中的所有文件和文件夹
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            # 检查文件是否为JPG文件
            if file.lower().endswith('.jpg'):
                # 构建源文件的完整路径
                source_file_path = os.path.join(root, file)
                # 构建目标文件的完整路径
                destination_file_path = os.path.join(destination_folder, file)
                # 复制文件到目标文件夹
                shutil.move(source_file_path, destination_file_path)
                print(f"已复制 {source_file_path} 到 {destination_file_path}")

# 示例用法
source_folder = 'D:\data\JPEGImages1'  # 替换为实际的源文件夹路径
destination_folder = 'D:\data\images'  # 替换为实际的目标文件夹路径

extract_jpg_files(source_folder, destination_folder)
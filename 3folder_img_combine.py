import os
import shutil

def merge_images(source_folders, destination_folder):
    # 检查目标文件夹是否存在，如果不存在则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历每个源文件夹
    for source_folder in source_folders:
        # 检查源文件夹是否存在
        if not os.path.exists(source_folder):
            print(f"源文件夹 {source_folder} 不存在，跳过该文件夹。")
            continue

        # 获取源文件夹中的所有文件，并按文件名排序
        files = sorted(os.listdir(source_folder))
        for filename in files:
            # 检查文件是否为图片文件
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                source_path = os.path.join(source_folder, filename)
                destination_path = os.path.join(destination_folder, filename)
                # 复制图片文件到目标文件夹
                shutil.copy2(source_path, destination_path)
                print(f"已复制文件: {source_path} 到 {destination_path}")

    print("图片合并完成。")

if __name__ == "__main__":
    # 定义三个源文件夹的路径
    source_folders = [
        r"D:\Microsoft Downloads\CCPD2019\train",
        r"D:\Microsoft Downloads\CCPD2020\ccpd_green\train",
        r"D:\Microsoft Downloads\CCPD2021\CCPD2021\train"
    ]
    # 定义目标文件夹的路径
    destination_folder = r"D:\Microsoft Downloads\train1"

    merge_images(source_folders, destination_folder)
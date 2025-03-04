import os
import shutil

def move_txt_files(folder_paths, destination_folder):
    # 检查目标文件夹是否存在，若不存在则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历每个源文件夹
    for folder_path in folder_paths:
        # 检查源文件夹是否存在
        if not os.path.exists(folder_path):
            print(f"文件夹 {folder_path} 不存在，跳过该文件夹。")
            continue

        # 获取该文件夹下所有的文件
        files = sorted(os.listdir(folder_path))
        # 遍历该文件夹下的每个文件
        for file in files:
            # 检查文件是否为txt文件
            if file.endswith('.txt'):
                # 构建该txt文件的完整路径
                source_file_path = os.path.join(folder_path, file)
                destination_file_path = os.path.join(destination_folder, file)
                try:
                    # 复制txt文件到目标文件夹
                    shutil.copy2(source_file_path, destination_file_path)
                    print(f"已复制文件: {source_file_path} 到 {destination_file_path}")
                except Exception as e:
                    print(f"复制文件 {source_file_path} 时出错: {e}")

    print("所有txt文件复制完成。")

if __name__ == "__main__":
    # 定义三个文件夹的路径
    folder_paths = [
        r"D:\Microsoft Downloads\CCPD2019\0val",
        r"D:\Microsoft Downloads\CCPD2020\ccpd_green\1val",
        r"D:\Microsoft Downloads\CCPD2021\CCPD2021\2val"
    ]
    # 定义目标文件夹的路径
    destination_folder = (r"D:\Microsoft Downloads\labels\val")
    # 调用复制函数
    move_txt_files(folder_paths, destination_folder)
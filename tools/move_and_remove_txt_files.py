import os
import shutil

def extract_and_delete_txt_files(source_folder, destination_folder):
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder):
        print(f"源文件夹 {source_folder} 不存在。")
        return

    # 创建目标文件夹，如果不存在的话
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 获取源文件夹中的所有文件，并按名称排序
    files = sorted(os.listdir(source_folder))

    # 遍历源文件夹中的所有文件
    for filename in files:
        if filename.endswith('.txt'):
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(destination_folder, filename)
            # 移动txt文件到目标文件夹
            shutil.move(source_path, destination_path)
            print(f"已移动文件: {source_path} 到 {destination_path}")

    # 再次检查源文件夹中的txt文件并删除（确保无遗漏）
    remaining_txt_files = [f for f in os.listdir(source_folder) if f.endswith('.txt')]
    for txt_file in remaining_txt_files:
        txt_path = os.path.join(source_folder, txt_file)
        os.remove(txt_path)
        print(f"已删除文件: {txt_path}")

    print("操作完成。")

if __name__ == "__main__":
    # 替换为实际的源文件夹路径
    source_folder = r"D:\Microsoft Downloads\CCPD2021\CCPD2021\val"
    # 替换为实际的目标文件夹路径
    destination_folder = r"D:\Microsoft Downloads\CCPD2021\CCPD2021\2val"

    extract_and_delete_txt_files(source_folder, destination_folder)
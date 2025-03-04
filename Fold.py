import os

# 定义要修改的文件夹路径
folder_path = r'D:\data\labels'  # 请将此路径替换为实际的文件夹路径

# 定义需要修改的类别映射
category_mapping = {
    5:4
}

# 遍历文件夹中的所有文件
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.txt'):
            file_path = os.path.join(root, file)
            new_lines = []
            # 读取文件内容并修改类别
            with open(file_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split()
                    category = int(parts[0])
                    if category in category_mapping:
                        parts[0] = str(category_mapping[category])
                    new_lines.append(' '.join(parts) + '\n')
            # 将修改后的内容写回文件
            with open(file_path, 'w') as f:
                f.writelines(new_lines)

print("所有 txt 文件已修改完成。")
import os
import xml.etree.ElementTree as ET

# 定义输入文件夹路径，这里需要替换为你实际的 XML 文件夹路径
input_folder = r'D:\BaiduNetdiskDownload\train\trainlabel'

# 用于存储所有出现的类别及其第一次出现的文件名称
categories = {}

# 遍历输入文件夹中的所有 XML 文件
for filename in os.listdir(input_folder):
    if filename.endswith('.xml'):
        xml_path = os.path.join(input_folder, filename)
        try:
            # 解析 XML 文件
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # 遍历 XML 中的 object 标签
            for obj in root.findall('object'):
                name = obj.find('name').text
                # 如果类别还未记录，则添加到类别字典中，并记录所在文件名
                if name not in categories:
                    categories[name] = filename
        except Exception as e:
            print(f"处理文件 {xml_path} 时出错: {e}")

# 输出提取到的类别、顺序及第一次出现的文件名称
print("提取到的标签类别、顺序及第一次出现的文件名称:")
for index, (category, file_name) in enumerate(categories.items()):
    print(f"{index}: {category}，首次出现在文件: {file_name}")
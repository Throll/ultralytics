import os
import xml.etree.ElementTree as ET

# 定义类别顺序
categories = ['car', 'truck', 'feright car', 'bus', 'van', 'feright_car', 'feright', '*', 'truvk']
category_to_index = {category: index for index, category in enumerate(categories)}

# 定义输入文件夹和输出文件夹
input_folder = r'D:\BaiduNetdiskDownload\val\vallabel'  # 替换为实际的 XML 文件夹路径
output_folder = r'D:\BaiduNetdiskDownload\labels\val'  # 替换为实际的输出 TXT 文件夹路径

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

missing_info = []

# 遍历输入文件夹中的所有 XML 文件
for filename in os.listdir(input_folder):
    if filename.endswith('.xml'):
        xml_path = os.path.join(input_folder, filename)
        try:
            # 解析 XML 文件
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # 检查是否存在 <object> 标签
            objects_list = root.findall('object')
            if len(objects_list) == 0:
                print(f"文件 {xml_path} 中没有 <object> 标签，跳过处理。")
                continue

            # 提取图像的尺寸
            size = root.find('size')
            if size is None:
                print(f"文件 {xml_path} 缺少 <size> 标签，跳过处理。")
                continue
            width = int(size.find('width').text)
            height = int(size.find('height').text)

            # 存储 name 和对应的归一化坐标
            objects = []

            # 遍历 XML 中的 object 标签
            for obj in objects_list:
                name = obj.find('name').text
                if name in category_to_index:
                    category_index = category_to_index[name]
                else:
                    print(f"文件 {xml_path} 中的类别 {name} 不在预定义类别中，跳过该目标。")
                    continue

                polygon = obj.find('polygon')
                bndbox = obj.find('bndbox')

                if polygon is not None:
                    try:
                        # 提取多边形的坐标
                        x_coords = [int(polygon.find(f'x{i}').text) for i in range(1, 5)]
                        y_coords = [int(polygon.find(f'y{i}').text) for i in range(1, 5)]
                    except ValueError:
                        print(f"文件 {xml_path} 中的一个 <polygon> 标签的坐标值异常，跳过该目标。")
                        continue

                    # 计算多边形的边界框
                    xmin = min(x_coords)
                    xmax = max(x_coords)
                    ymin = min(y_coords)
                    ymax = max(y_coords)
                elif bndbox is not None:
                    try:
                        xmin = int(bndbox.find('xmin').text)
                        ymin = int(bndbox.find('ymin').text)
                        xmax = int(bndbox.find('xmax').text)
                        ymax = int(bndbox.find('ymax').text)
                    except (AttributeError, ValueError):
                        print(f"文件 {xml_path} 中的一个 <bndbox> 标签的坐标值异常，跳过该目标。")
                        continue
                else:
                    missing_info.append(f"文件 {xml_path} 中的 <object> 类别为 {name} 既缺少 <polygon> 标签也缺少 <bndbox> 标签。")
                    continue

                # 转换为中心点坐标和宽高
                x_center = (xmin + xmax) / 2.0
                y_center = (ymin + ymax) / 2.0
                w = xmax - xmin
                h = ymax - ymin

                # 归一化
                x = x_center / width
                y = y_center / height
                w = w / width
                h = h / height

                objects.append(f"{category_index} {x} {y} {w} {h}")

            # 输出结果到对应的 TXT 文件
            txt_filename = os.path.splitext(filename)[0] + '.txt'
            txt_path = os.path.join(output_folder, txt_filename)
            with open(txt_path, 'w') as f:
                for obj in objects:
                    f.write(obj + '\n')
        except ET.ParseError as e:
            print(f"文件 {xml_path} 格式错误，无法解析: {e}")
        except PermissionError as e:
            print(f"文件 {xml_path} 权限不足，无法读取或写入: {e}")
        except Exception as e:
            print(f"处理文件 {xml_path} 时出现未知错误: {e}")

# 输出缺失信息
if missing_info:
    print("以下目标存在标签缺失情况：")
    for info in missing_info:
        print(info)
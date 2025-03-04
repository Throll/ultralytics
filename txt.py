import os
from PIL import Image

def parse_filename(filename):
    try:
        parts = filename.split("-")
        print(f"分割后的部分: {parts}")  # 添加调试信息
        # 找到包含边界框坐标的部分，可能不是固定的第三个字段
        for part in parts:
            if "&" in part and "_" in part:
                # 假设坐标格式为 x1&y1_x2&y2
                coordinates = part.split("_")[0].replace("&", " ").split()
                x1 = int(coordinates[0])
                y1 = int(coordinates[1])
                x2 = int(part.split("_")[1].split("&")[0])
                y2 = int(part.split("_")[1].split("&")[1])
                return x1, y1, x2, y2
        raise ValueError("未找到有效的边界框坐标")
    except (IndexError, ValueError, AttributeError) as e:
        print(f"解析文件名 {filename} 时出错: {e}")
        return None

def convert_to_yolo_format(img_w, img_h, x1, y1, x2, y2):
    """
    将边界框坐标转换为YOLO格式（归一化的中心坐标和宽高）
    """
    # 计算边界框中心点
    x_center = ((x1 + x2) / 2) / img_w
    y_center = ((y1 + y2) / 2) / img_h
    # 计算边界框宽高
    width = (x2 - x1) / img_w
    height = (y2 - y1) / img_h
    return x_center, y_center, width, height

def process_images(image_folder):
    for filename in os.listdir(image_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            # 解析文件名
            bbox_coords = parse_filename(filename)
            if bbox_coords is None:
                print(f"跳过文件 {filename}（格式错误）")
                continue
            x1, y1, x2, y2 = bbox_coords

            # 获取图像尺寸
            img_path = os.path.join(image_folder, filename)
            try:
                with Image.open(img_path) as img:
                    img_w, img_h = img.size
            except Exception as e:
                print(f"无法读取图像尺寸：{filename}，错误信息：{e}")
                continue

            # 转换坐标格式
            x_center, y_center, width, height = convert_to_yolo_format(img_w, img_h, x1, y1, x2, y2)

            # 创建标注文件
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(image_folder, txt_filename)
            print(f"生成的 .txt 文件路径: {txt_path}")

            # YOLO格式：class x_center y_center width height（假设车牌类别为0）
            with open(txt_path, "w") as f:
                f.write(f"2 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

if __name__ == "__main__":
    image_folder = r"D:\Microsoft Downloads\CCPD2021\CCPD2021\val"
    print(f"图片文件夹路径: {image_folder}")
    if not os.path.exists(image_folder):
        print(f"指定的文件夹路径 {image_folder} 不存在，请检查。")
    else:
        process_images(image_folder)
        print("标注文件生成完成！")
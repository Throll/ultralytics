import os
from PIL import Image

def resize_and_rename_images(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹 {folder_path} 不存在。")
        return

    # 获取文件夹中所有图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = [f for f in os.listdir(folder_path) if any(f.lower().endswith(ext) for ext in image_extensions)]
    image_files.sort()

    # 初始编号
    start_number = 2562

    for i, image_file in enumerate(image_files):
        # 构建图片文件的完整路径
        image_path = os.path.join(folder_path, image_file)
        try:
            # 打开图片
            with Image.open(image_path) as img:
                # 调整图片尺寸
                resized_img = img.resize((1920, 1080), Image.LANCZOS)
                # 生成新的文件名
                new_filename = f"frame_{start_number + i}.{img.format.lower()}"
                new_filepath = os.path.join(folder_path, new_filename)
                # 保存调整尺寸后的图片
                resized_img.save(new_filepath)
                print(f"已处理并保存图片: {new_filepath}")
        except Exception as e:
            print(f"处理图片 {image_path} 时出错: {e}")

folder_path = 'D:/data/JPEGImages2'
resize_and_rename_images(folder_path)
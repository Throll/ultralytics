import cv2
import os


def extract_frames(video_path, output_folder, interval=5, start_index=85):
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 检查视频是否成功打开
    if not cap.isOpened():
        print("Error opening video file")
        return

    # 获取视频的帧率
    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_interval = int(fps * interval)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            # 生成图片文件名，修改序号起始值
            image_index = start_index + frame_count // frame_interval
            image_name = f"frame_{image_index}.jpg"
            image_path = os.path.join(output_folder, image_name)

            # 保存图片
            cv2.imwrite(image_path, frame)
            print(f"Saved {image_path}")

        frame_count += 1

    # 释放视频捕获对象
    cap.release()


# 调用函数进行截图
video_path = r"D:\BaiduNetdiskDownload\video1\DJI_20250224111848_0003_V.MP4"# 替换为你的视频文件路径
output_folder = "D:\data\JPEGImages1"  # 替换为你想要保存图片的文件夹路径
extract_frames(video_path, output_folder, start_index=2477)
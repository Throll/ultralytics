import cv2
from ultralytics.solutions.traffic_counter import TrafficCounter
import os
import sys

# 创建一个空文件对象，用于重定向标准输出
class NullWriter:
    def write(self, text):
        pass

# 视频文件路径列表，你可以在这里添加多个视频路径
video_paths = [
   r"/hdd/sa/ultralytics/data/D早高峰+B9-10/DCIM/D_weekday_0800-0900/DJI_202503170753_002/DJI_20250317075727_0001_V.MP4"
   # 可以继续添加其他视频路径
]

total_duration = 0
all_video_counts = {}

for video_path in video_paths:
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), f"Error reading video file: {video_path}"

    # 获取视频属性
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps  # 视频时长（秒）
    total_duration += duration

    # 定义显示窗口参数
    display_width = 1280  # 显示窗口宽度
    display_height = 720  # 显示窗口高度

    # 初始化目标计数器
    counter = TrafficCounter(
        show=False,  # 关闭内置显示功能
        region=[(0, h), (w, h//5)],
        model="/hdd/sa/ultralytics/yolo11x.pt",
        line_width=2,
        tracker="bytetrack.yaml"
    )

    # 用于存储当前视频每个类别的in和out数量之和
    class_counts = {}
    counted_track_ids = set()  # 用于记录已经计数过的track_id
    prev_positions_dict = {}  # 自行维护每个目标的上一帧位置信息

    # 视频写入器保持原始分辨率
    output_path = os.path.join(os.path.dirname(video_path), "object_counting_output_" + os.path.basename(video_path))
    video_writer = cv2.VideoWriter(output_path,
                                   cv2.VideoWriter_fourcc(*"mp4v"),
                                   fps,
                                   (w, h))

    # 重定向标准输出
    original_stdout = sys.stdout
    sys.stdout = NullWriter()

    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            break

        results = counter.process(im0)

        # 从counter的实例属性中获取boxes, track_ids和clss
        boxes = counter.boxes
        track_ids = counter.track_ids
        clss = counter.clss

        for box, track_id, cls in zip(boxes, track_ids, clss):
            if track_id in counted_track_ids:
                continue  # 如果已经计数过，跳过

            centroid = ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)  # 计算目标框的中心坐标
            prev_position = prev_positions_dict.get(track_id)
            class_name = counter.model.names[int(cls)]

            # 调用计数方法
            counter.count_objects(centroid, track_id, prev_position, cls)

            # 更新上一帧位置信息
            prev_positions_dict[track_id] = centroid

            # 记录已计数的目标
            counted_track_ids.add(track_id)

        video_writer.write(results.plot_im)
        display = True
        if display:
            display_frame = cv2.resize(results.plot_im, (display_width, display_height))
            cv2.imshow("Object Counter", display_frame)

        # ESC退出
        if cv2.waitKey(1) == 27:
            break

    # 恢复标准输出
    sys.stdout = original_stdout

    # 释放资源
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

    # 从counter中获取最终的计数结果
    class_counts = counter.classwise_counts

    all_video_counts[video_path] = class_counts

# 汇总所有视频的计数结果
total_class_counts = {}
for video_path, class_counts in all_video_counts.items():
    for class_name, counts in class_counts.items():
        if class_name not in total_class_counts:
            total_class_counts[class_name] = {"IN": 0, "OUT": 0}
        total_class_counts[class_name]["IN"] += counts["IN"]
        total_class_counts[class_name]["OUT"] += counts["OUT"]

# 输出所有视频的总计数结果和基于总时长的每小时数量
print(f"Total Video Duration: {total_duration} seconds, or {total_duration / 3600:.2f} hours")
for class_name, counts in total_class_counts.items():
    total_count = counts["IN"] + counts["OUT"]
    count_per_hour = total_count / (total_duration / 3600) if total_duration > 0 else 0
    print(f"  Class: {class_name}, Total In Count: {counts['IN']}, Total Out Count: {counts['OUT']}, "
          f"Total Count: {total_count}, Count per Hour: {count_per_hour:.2f} 个/h")
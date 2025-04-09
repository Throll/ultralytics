import cv2
import numpy as np
from collections import deque
from ultralytics import YOLO
import colorsys

# 配置参数
TRACK_FRAMES = 5  # 目标保持的帧数
IOU_THRESHOLD = 0.3  # 匹配阈值
MIN_CONFIDENCE = 0.5  # 修改为与第一段代码一致的置信度阈值
DUPLICATE_IOU_THRESHOLD = 0.7  # 重复检测框 IOU 阈值
MAX_MOVE_DISTANCE = 50  # 最大移动距离阈值
INITIAL_FRAMES = 3  # 用于确定初始位置的帧数


def iou(box1, box2):
    """计算两个检测框的交并比"""
    x11, y11, x12, y12 = box1
    x21, y21, x22, y22 = box2
    x_left = max(x11, x21)
    y_top = max(y11, y21)
    x_right = min(x12, x22)
    y_bottom = min(y12, y22)
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = (x12 - x11) * (y12 - y11)
    box2_area = (x22 - x21) * (y22 - y21)
    union_area = box1_area + box2_area - intersection_area
    return intersection_area / union_area


def filter_duplicate_detections(detections):
    """过滤重复的检测框"""
    filtered_detections = []
    for i, det1 in enumerate(detections):
        is_duplicate = False
        for j, det2 in enumerate(detections):
            if i == j:
                continue
            box1 = det1[1]
            box2 = det2[1]
            if iou(box1, box2) > DUPLICATE_IOU_THRESHOLD:
                if det1[2] < det2[2]:  # 保留置信度高的检测框
                    is_duplicate = True
                    break
        if not is_duplicate:
            filtered_detections.append(det1)
    return filtered_detections


class VehicleTracker:
    def __init__(self, class_names):
        self.track_id = 0
        self.tracks = {}  # {id: {'bbox': [], 'centroid': [], 'positions': deque, 'counted': bool, 'initial_frames': deque}}
        self.count_history = {'in': {c: 0 for c in class_names}, 'out': {c: 0 for c in class_names}}  # 修改为 in/out
        self.class_names = class_names

    def update(self, detections, width, height, offset):
        current_ids = []

        # 过滤重复的检测框
        detections = filter_duplicate_detections(detections)

        # 对每个检测目标进行匹配
        for det in detections:
            class_name, bbox, confidence = det
            centroid = self._get_centroid(bbox)

            # 寻找最佳匹配的已有跟踪目标
            best_match = None
            min_distance = float('inf')

            for track_id, track in self.tracks.items():
                if track['counted']:
                    continue
                last_centroid = track['positions'][-1]
                distance = np.linalg.norm(np.array(centroid) - np.array(last_centroid))

                if distance < min_distance and distance < MAX_MOVE_DISTANCE:  # 最大移动距离阈值
                    min_distance = distance
                    best_match = track_id

            # 更新或新建跟踪目标
            if best_match is not None:
                self._update_track(best_match, bbox, centroid)
                current_ids.append(best_match)
            else:
                self._create_new_track(class_name, bbox, centroid, width, height, offset, confidence)
                current_ids.append(self.track_id)

        # 更新计数并清理丢失的目标
        self._update_counts(width, height, offset)
        self._cleanup_tracks(current_ids)

    def _get_centroid(self, bbox):
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def _create_new_track(self, class_name, bbox, centroid, width, height, offset, confidence):
        self.track_id += 1
        self.tracks[self.track_id] = {
            'class': class_name,
            'bbox': bbox,
            'centroid': centroid,
            'positions': deque(maxlen=TRACK_FRAMES),
            'initial_frames': deque(maxlen=INITIAL_FRAMES),
            'counted': False,
            'confidence': confidence  # 新增置信度信息
        }
        self.tracks[self.track_id]['positions'].append(centroid)
        self.tracks[self.track_id]['initial_frames'].append(centroid)

    def _update_track(self, track_id, bbox, centroid):
        self.tracks[track_id]['bbox'] = bbox
        self.tracks[track_id]['centroid'] = centroid
        self.tracks[track_id]['positions'].append(centroid)
        if 'initial_frames' in self.tracks[track_id] and len(self.tracks[track_id]['initial_frames']) < INITIAL_FRAMES:
            self.tracks[track_id]['initial_frames'].append(centroid)

    def _update_counts(self, width, height, offset):
        for track_id, track in self.tracks.items():
            if track['counted']:
                continue

            # 确定初始位置
            if 'initial_frames' in track and len(track['initial_frames']) == INITIAL_FRAMES:
                right_bottom_count = sum(1 for c in track['initial_frames'] if c[1] > height - c[0] + offset)
                track['initial_side'] = 'right_bottom' if right_bottom_count > INITIAL_FRAMES // 2 else 'left_top'
                del track['initial_frames']

            # 检查轨迹方向
            if len(track['positions']) < 2 or 'initial_side' not in track:
                continue

            for i in range(len(track['positions']) - 1):
                first_x, first_y = track['positions'][i]
                last_x, last_y = track['positions'][i + 1]

                first_side = 'right_bottom' if first_y > height - first_x * (height / width) + offset else 'left_top'
                last_side = 'right_bottom' if last_y > height - last_x * (height / width) + offset else 'left_top'

                if first_side != last_side:
                    if first_side == 'right_bottom' and last_side == 'left_top':  # 从右下方穿到左上方 → out
                        self.count_history['out'][track['class']] += 1
                        track['counted'] = True
                        break
                    elif first_side == 'left_top' and last_side == 'right_bottom':  # 从左上方穿到右下方 → in
                        self.count_history['in'][track['class']] += 1
                        track['counted'] = True
                        break

    def _cleanup_tracks(self, current_ids):
        lost_tracks = set(self.tracks.keys()) - set(current_ids)
        for track_id in lost_tracks:
            del self.tracks[track_id]


def parse_detections(frame, model):
    detections = []
    results = model(frame)
    boxes = []
    scores = []
    class_ids = []
    for result in results:
        result_boxes = result.boxes
        for box in result_boxes:
            class_id = int(box.cls.item())
            confidence = box.conf.item()
            if confidence < MIN_CONFIDENCE:
                continue
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            boxes.append([x1, y1, x2 - x1, y2 - y1])  # 需要传入宽度和高度格式
            scores.append(confidence)
            class_ids.append(class_id)
    boxes = np.array(boxes)
    scores = np.array(scores)
    class_ids = np.array(class_ids)
    nms_indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=MIN_CONFIDENCE, nms_threshold=DUPLICATE_IOU_THRESHOLD)
    for i in nms_indices:
        class_name = model.names[class_ids[i]]
        bbox = boxes[i].tolist()
        bbox[2] += bbox[0]  # 转换回x2, y2格式
        bbox[3] += bbox[1]
        confidence = scores[i]
        detections.append((class_name, bbox, confidence))
    return detections


def adjust_color_contrast(rgb, saturation_factor=1.5, lightness_factor=1.2):
    """调整颜色的对比度"""
    r, g, b = [x / 255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    # 调整饱和度和亮度
    s = min(1.0, s * saturation_factor)
    l = min(0.5, l * lightness_factor)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return tuple(int(x * 255) for x in (r, g, b))


def process_video(video_path, model, class_names, class_colors):
    tracker = VehicleTracker(class_names)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return tracker.count_history, 0

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 检查宽度和高度是否为有效正值
    if width <= 0 or height <= 0:
        print("视频的宽度或高度无效，请检查视频文件。")
        return tracker.count_history, 0

    # 新的缩放方法
    scale_percent = 20
    new_width = int(width * scale_percent / 100)
    new_height = int(height * scale_percent / 100)

    # 获取视频的总帧数和帧率
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 计算视频时长（秒）
    video_duration = frame_count / fps if fps != 0 else 0

    # 定义偏移量
    offset = 40  # 可根据需求调整这个值

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:  # 处理视频读取失败的情况
                break

            # 使用新的宽度和高度进行缩放
            frame = cv2.resize(frame, (new_width, new_height))

            detections = parse_detections(frame, model)
            tracker.update(detections, new_width, new_height, offset)

    except:
        print("视频处理过程中出现错误")
    finally:
        cap.release()

    return tracker.count_history, video_duration


def main():
    # 加载 YOLO 模型
    model = YOLO("runs/detect/yolo11x_best.pt")
    class_names = list(model.names.values())

    # 自定义每个类别的颜色
    
    class_colors = {
        "car": (247, 225, 237),
        "bus": (128, 0, 128),
        "truck": (236, 93, 59),
        "motorcycle": (114, 170, 207),
        "person": (150, 195, 125),
        # 可以根据实际类别名称添加更多颜色配置
    }

    # 定义要处理的视频文件列表
    video_files = [r"F:\D早高峰+B9-10\DCIM\D_weekday_0800-0900\DJI_202503170753_002\DJI_20250317080428_0002_V.MP4"]

    # 初始化总的计数历史字典
    total_count_history = {'in': {c: 0 for c in class_names}, 'out': {c: 0 for c in class_names}}
    total_duration = 0

    # 循环处理每个视频
    for video_file in video_files:
        print(f"正在处理视频: {video_file}")
        video_count_history, video_duration = process_video(video_file, model, class_names, class_colors)
        total_duration += video_duration

        # 累加每个视频的计数结果
        for class_name in class_names:
            total_count_history['in'][class_name] += video_count_history['in'][class_name]
            total_count_history['out'][class_name] += video_count_history['out'][class_name]

    # 将总时长转换为小时
    total_duration_hours = total_duration / 3600

    # 输出总的计数结果和速率
    print("所有视频各个类别 in 和 out 的总数量统计及速率（个/h）：")
    for class_name in class_names:
        in_rate = total_count_history['in'][class_name] / total_duration_hours if total_duration_hours != 0 else 0
        out_rate = total_count_history['out'][class_name] / total_duration_hours if total_duration_hours != 0 else 0
        print(
            f"{class_name}: IN {total_count_history['in'][class_name]} ({in_rate:.2f} 个/h) | OUT {total_count_history['out'][class_name]} ({out_rate:.2f} 个/h)")

    # 输出所有预测视频的总时长（小时）
    print(f"所有预测视频的总时长: {total_duration_hours:.2f} 小时")


if __name__ == "__main__":
    main()
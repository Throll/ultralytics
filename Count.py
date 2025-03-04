import cv2
import numpy as np
import torch

# 假设这是加载 YOLOv11 模型的函数，你需要根据实际情况修改
def load_yolov11_model(model_path):
    model = torch.load(model_path)
    model.eval()
    return model

# 自定义函数，根据类别 ID 获取类别名称
def get_class_name(class_id):
    # 这里需要根据你的模型类别映射修改
    class_names = ["car", "truck", "bus", "motorcycle"]
    return class_names[class_id]

# 使用 YOLOv11 模型进行目标检测
def detect_objects(frame, model):
    # 预处理图像，这部分需要根据模型要求修改
    input_tensor = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float() / 255.0
    with torch.no_grad():
        results = model(input_tensor)

    detections = []
    # 解析模型输出，这里需要根据模型输出格式修改
    # 假设输出是一个包含边界框、类别和置信度的列表
    for result in results:
        boxes = result['boxes'].cpu().numpy()
        classes = result['classes'].cpu().numpy()
        for box, class_id in zip(boxes, classes):
            class_name = get_class_name(class_id)
            if class_name in ["car", "truck", "bus", "motorcycle"]:
                x1, y1, x2, y2 = box.astype(int)
                detections.append([class_name, [x1, y1, x2, y2]])
    return detections

# 计算两个边界框的交并比（IoU）
def calculate_iou(box1, box2):
    x11, y11, x12, y12 = box1
    x21, y21, x22, y22 = box2
    # 计算交集的坐标
    xA = max(x11, x21)
    yA = max(y11, y21)
    xB = min(x12, x22)
    yB = min(y12, y22)
    # 计算交集的面积
    inter_area = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # 计算两个边界框的面积
    box1_area = (x12 - x11 + 1) * (y12 - y11 + 1)
    box2_area = (x22 - x21 + 1) * (y22 - y21 + 1)
    # 计算并集的面积
    union_area = box1_area + box2_area - inter_area
    # 计算 IoU
    iou = inter_area / float(union_area)
    return iou

# 定义视频文件路径
input_video_path = 'runs/detect/predict31/test10.mp4'
output_video_path = 'runs/detect/predict31/count_test10.mp4'

# 打开视频文件
cap = cv2.VideoCapture(input_video_path)

# 获取视频的帧率、宽度和高度
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 定义输出视频的编码器和创建 VideoWriter 对象
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

# 计算视频中间位置的 y 坐标，用于绘制水平线
line_y = height // 2

# 初始化进入和出去的计数器
in_count = {
    "car": 0,
    "truck": 0,
    "bus": 0,
    "motorcycle": 0
}
out_count = {
    "car": 0,
    "truck": 0,
    "bus": 0,
    "motorcycle": 0
}

# 加载训练好的 YOLOv11 模型
model = load_yolov11_model('path/to/your/yolov11_model.pt')  # 替换为你的 .pt 文件路径

# 上一帧的检测结果，使用字典存储每个目标的唯一标识、信息和初始位置
prev_detections = {}
object_id = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 绘制中间的水平线
    cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 0), 2)

    # 获取当前帧的检测结果
    current_detections = detect_objects(frame, model)
    current_object_ids = {}

    # 处理每个检测结果
    for class_name, bbox in current_detections:
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        # 为当前目标分配一个唯一的 ID
        object_id += 1
        # 检查目标是否首次出现
        if object_id not in prev_detections:
            # 修改初始位置的判断逻辑
            if y2 < line_y - 5:  # 增加一定的容错范围
                initial_position = "above"
            elif y1 > line_y + 5:
                initial_position = "below"
            else:
                # 如果目标刚好在线附近，先不记录初始位置，等待后续帧确定
                initial_position = None
            prev_detections[object_id] = (class_name, bbox, center_y, initial_position)
        else:
            prev_class, prev_bbox, prev_center_y, initial_position = prev_detections[object_id]

            # 寻找上一帧中匹配的目标
            best_match_id = None
            best_iou = 0
            for prev_id, (prev_class, prev_bbox, prev_center_y, _) in prev_detections.items():
                if prev_class == class_name:
                    iou = calculate_iou(bbox, prev_bbox)
                    if iou > best_iou:
                        best_iou = iou
                        best_match_id = prev_id
                    print(f"Class: {class_name}, Current ID: {object_id}, Prev ID: {prev_id}, IoU: {iou}")

            if best_match_id is not None:
                prev_class, prev_bbox, prev_center_y, initial_position = prev_detections[best_match_id]
                if initial_position is not None:
                    height = y2 - y1
                    print(f"Class: {class_name}, ID: {object_id}, Initial Position: {initial_position}, Current Y1: {y1}, Current Y2: {y2}, Height: {height}")
                    # 调整穿越判断条件为中心点穿越线
                    center_y = (y1 + y2) // 2
                    if initial_position == "above" and center_y > line_y:
                        in_count[class_name] += 1
                        prev_detections[object_id] = (class_name, bbox, center_y, "below")
                        print(f"{class_name} (ID: {object_id}) entered. In count: {in_count[class_name]}")
                    elif initial_position == "below" and center_y < line_y:
                        out_count[class_name] += 1
                        prev_detections[object_id] = (class_name, bbox, center_y, "above")
                        print(f"{class_name} (ID: {object_id}) exited. Out count: {out_count[class_name]}")

        current_object_ids[object_id] = (class_name, bbox, center_y, initial_position)

    # 更新上一帧的检测结果
    prev_detections = current_object_ids

    # 在视频上方中间显示进入和出去的数量
    y_offset = 30
    for class_name in in_count.keys():
        text = f"{class_name}: In={in_count[class_name]}, Out={out_count[class_name]}"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        text_x = (width - text_size[0]) // 2
        cv2.putText(frame, text, (text_x, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y_offset += 30

    # 写入处理后的帧
    out.write(frame)

    # 显示处理后的帧
    cv2.imshow('Processed Video', frame)

    # 按 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
out.release()
cv2.destroyAllWindows()
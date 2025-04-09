import cv2
import numpy as np

# 打开 AVI 文件
cap = cv2.VideoCapture('runs/detect/predict32/tmpr1g6ki9d.avi')

# 预设窗口的宽度和高度
window_width = 800
window_height = 600

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # 缩放视频帧以适应窗口大小
        frame = cv2.resize(frame, (window_width, window_height))

        # 创建一个空白图像，大小为窗口的大小
        blank_image = np.zeros((window_height, window_width, 3), dtype=np.uint8)

        # 计算视频帧在空白图像中的起始位置，使其居中
        start_x = int((window_width - window_width) / 2)
        start_y = int((window_height - window_height) / 2)

        # 将视频帧放置在空白图像的中心位置
        blank_image[start_y:start_y + window_height, start_x:start_x + window_width] = frame

        # 显示包含视频帧的空白图像
        cv2.imshow('AVI Player', blank_image)

        # 按 'q' 键退出循环
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
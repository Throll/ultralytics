from moviepy.editor import VideoFileClip

# 读取 AVI 文件
clip = VideoFileClip("runs/detect/predict31/tmp3hrnuc9f.avi")

# 指定保存路径
save_path = "runs/detect/predict31/test10.mp4"
clip.write_videofile(save_path)
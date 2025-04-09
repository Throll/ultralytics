from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.VideoClip import ColorClip

def add_border_to_video(input_path, output_path, border_size=800):
    try:
        clip = VideoFileClip(input_path)
        # 检查并手动设置时长（作为临时解决方案）
        if clip.duration is None:
            # 这里需要根据实际情况设置合适的时长，例如使用视频播放器查看时长
            clip = clip.set_duration(59)

        width, height = clip.size
        new_width = width + 2 * border_size
        new_height = height + 2 * border_size

        # 确保新的宽度和高度是偶数
        if new_width % 2 != 0:
            new_width += 1
        if new_height % 2 != 0:
            new_height += 1

        white_background = ColorClip(size=(new_width, new_height), color=(255, 255, 255))
        video_with_border = CompositeVideoClip([white_background, clip.set_position('center')]).set_duration(59)
        # 添加 preset 和 fps 参数，确保编码和帧率设置正确
        video_with_border.write_videofile(output_path, codec='libx264', audio_codec='aac', preset='medium', fps=clip.fps)
        print(f"视频处理完成，已保存到 {output_path}")
    except Exception as e:
        print(f"处理视频时出现错误: {e}")

if __name__ == "__main__":
    input_file = 'D:/BaiduNetdiskDownload/DJI_20250218131428_0005_V.MP4'
    output_file = 'D:/BaiduNetdiskDownload/test3.MP4'
    add_border_to_video(input_file, output_file)
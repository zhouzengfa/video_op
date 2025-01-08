import os
import uuid
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips
from .models import VideoMergeTask


def download_video(video_url, download_dir):
    """下载视频到指定目录"""
    response = requests.get(video_url, stream=True)
    video_name = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join(download_dir, video_name)
    with open(video_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return video_path


def merge_videos(video_files, output_file, task_id):
    """合成视频并更新任务状态"""
    task = VideoMergeTask.objects.get(task_id=task_id)
    print(f"video files:{video_files}")

    task.status = 'processing'
    task.progress = 0
    task.save()

    # 创建一个视频剪辑列表
    clips = [VideoFileClip(video) for video in video_files]

    # 合并视频剪辑
    final_clip = concatenate_videoclips(clips, method="compose")
    task.progress = 30
    task.save()

    # 写入输出文件
    final_clip.write_videofile(output_file, preset="ultrafast", codec="libx264", fps = 24)

    task.progress = 100
    task.status = 'completed'
    # task.output_file = output_file
    task.save()



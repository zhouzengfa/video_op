import os

from django.http import JsonResponse
from django.test import TestCase
from pydub import AudioSegment

from moviepy.editor import VideoFileClip, concatenate_videoclips


def merge_audio():
     input_files = ['1.mp4', '2.mp4']
     output_file = '3.mp4'
     cur=os.getcwd()
     combined_audio = AudioSegment.empty()
     for file_name in input_files:
         file_path = os.path.join('temp', file_name)
         file_path = os.path.join(cur, file_path)

         if os.path.exists(file_path):
             # audio_segment = AudioSegment.from_file(file_path)
             audio_segment = AudioSegment.from_file("D:/plan_b/python/djangoProject/audio_app/temp/1.mp4")
             combined_audio += audio_segment

         else:
             return JsonResponse({'error': f'File {file_name} not found.'}, status=404)

     output_path = os.path.join(os.getcwd(), output_file)
     combined_audio.export(output_path, format='mp4')


def merge_videos(video_files, output_file):
    """
    合并多个视频文件为一个视频文件.

    :param video_files: 视频文件列表
    :param output_file: 输出文件名
    """
    # 创建一个视频剪辑列表
    clips = [VideoFileClip(video) for video in video_files]

    # 合并视频剪辑
    final_clip = concatenate_videoclips(clips, method="compose")

    # 写入输出文件
    final_clip.write_videofile(output_file, codec="libx264")

# 示例用法
video_files = ["1.mp4", "2.mp4", "1.mp4"]
output_file = "merged_video.mp4"

merge_videos(video_files, output_file)
# merge_audio()
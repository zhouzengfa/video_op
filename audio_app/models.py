from django.db import models

# encoding=utf8
# -*-coding:utf-8 -*-

'''
python合成视频
'''

import os  # python标准库，不需要安装，用于系统文件操作相关
import cv2  # python非标准库，pip install opencv-python 多媒体处理
from PIL import Image  # python非标准库，pip install pillow，图像处理
import moviepy.editor as mov  # python非标准库，pip install moviepy，多媒体编辑
from moviepy.editor import VideoFileClip, concatenate_videoclips

from django.db import models


class VideoMergeTask(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default='downloading')
    progress = models.FloatField(default=0.0)
    output_file = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


def image_to_video(image_path, media_path):
    '''
    图片合成视频函数
    :param image_path: 图片路径 ，路径中不能有中文，必须是全英文无空格之类的
    :param media_path: 合成视频保存路径
    :return:
    '''
    # 获取图片路径下面的所有图片名称
    image_names = os.listdir(image_path)
    print(image_names)
    # 对提取到的图片名称进行排序
    # image_names.sort(key=lambda n: int(n[:-5]))
    # 设置写入格式
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # 用小写 mp4v
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')  # avi
    # 设置每秒帧数
    fps = 24  # 由于图片数目较少，这里设置的帧数比较低
    # 读取第一个图片获取大小尺寸，因为需要转换成视频的图片大小尺寸是一样的
    image = Image.open(os.path.join(image_path, image_names[0]))
    print(image.size)
    # 初始化媒体写入对象
    media_writer = cv2.VideoWriter(media_path, fourcc, fps, image.size)
    # 遍历图片，将每张图片加入视频当中
    for image_name in image_names:
        im = cv2.imread(os.path.join(image_path, image_name))
        print(im)

        media_writer.write(im)  # 在 VideoWriter 中指定的尺寸要和 write() 中写进去的一样，不然视频会存储失败的
        print(image_name, '合并完成！')
    # 释放媒体写入对象
    media_writer.release()
    print('无声视频写入完成！')


def set_music(media_path, music_path):
    '''
    合成视频设置背景音乐函数
    :return:
    '''
    print('开始添加背景音乐！')
    # 初始化视频文件对象
    clip = mov.VideoFileClip(media_path)
    audio = mov.AudioFileClip(music_path)  # 打开音频
    # 向合成好的无声视频中添加背景音乐
    clip = clip.set_audio(audio)
    # 保存视频
    clip.write_videofile(media_path)
    print('背景音乐添加完成！')

    # # 从某个视频中提取一段背景音乐
    # audio = mov.AudioFileClip('./source.mp4').subclip(0, 83)
    # # 将背景音乐写入.mp3文件
    # audio.write_audiofile('./background.mp3')
    # # 向合成好的无声视频中添加背景音乐
    # clip = clip.set_audio(audio)
    # # 保存视频
    # clip.write_videofile('./media.mp4')
    # print('背景音乐添加完成！')


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


if __name__ == '__main__':
    image_path = r".\tupian"
    media_path = "2.mp4"
    music_path = "audio.mp3"
    image_to_video(image_path, media_path)
    set_music(media_path, music_path)

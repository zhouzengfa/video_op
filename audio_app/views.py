
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment

import os
import requests
import uuid
import threading
from django.http import JsonResponse
from django.conf import settings

from audio_app.models import image_to_video, set_music, VideoMergeTask
from audio_app.tasks import download_video, merge_videos


# 图片，音频合成视频
@csrf_exempt
def create_video(request):
    if request.method == 'POST':
        image_url = request.POST.get('image_url')
        audio_url = request.POST.get('audio_url')
        print(request)

        if not image_url or not audio_url:
            return JsonResponse({'error': 'Both image and audio URLs are required.'}, status=400)

        # 创建临时文件夹
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', f'{uuid.uuid4()}')
        os.makedirs(temp_dir, exist_ok=True)

        image_dir = os.path.join(temp_dir, "images")
        os.makedirs(image_dir, exist_ok=True)

        # 下载图片和音频
        image_path = os.path.join(image_dir, 'image.jpg')
        audio_path = os.path.join(temp_dir, 'audio.mp3')

        # 生成视频名
        video_filename = f'video_{uuid.uuid4()}.mp4'
        output_path = os.path.join(temp_dir, video_filename)

        try:
            print("downing image...")
            response_image = requests.get(image_url)
            print("downing audio...")
            response_audio = requests.get(audio_url)
            print("finish downing")

            if response_image.status_code != 200 or response_audio.status_code != 200:
                return JsonResponse({'error': 'Failed to download image or audio.'}, status=400)

            with open(image_path, 'wb') as f:
                f.write(response_image.content)

            with open(audio_path, 'wb') as f:
                f.write(response_audio.content)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        print("start image to video")
        # 合成视频
        image_to_video(image_dir, output_path)
        print("start setting music")
        set_music(output_path, audio_path)

        print("finish")
        # 返回视频的 HTTP 地址
        # video_url = f'http://127.0.0.1:8000/{output_path}'
        # 返回视频的 HTTP 地址
        relative_output_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
        video_url = request.build_absolute_uri(settings.MEDIA_URL + relative_output_path)
        # video_url = request.build_absolute_uri(output_path)
        return JsonResponse({'video_url': video_url})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


@csrf_exempt
def start_merge_videos(request):
    if request.method == 'POST':
        video_urls = request.POST.getlist('video_urls')
        print(f"start merge videos. post:{request.POST}")
        print(f"urls:{video_urls}")
        task_id = str(uuid.uuid4())
        VideoMergeTask.objects.create(task_id=task_id)

        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
        unique_dir = os.path.join(temp_dir, task_id)
        os.makedirs(unique_dir, exist_ok=True)

        task = VideoMergeTask.objects.get(task_id=task_id)
        task.status = "downing"

        video_files = []
        for url in video_urls:
            video_path = download_video(url, unique_dir)
            video_files.append(video_path)
            task.progress += 1/len(video_urls)*100
            task.save()

        output_file = os.path.join(unique_dir, "merged_video.mp4")
        relative_output_path = os.path.relpath(output_file, settings.MEDIA_ROOT)
        video_url = request.build_absolute_uri(settings.MEDIA_URL + relative_output_path)

        task.output_file = video_url
        task.save()

        threading.Thread(target=merge_videos, args=(video_files, output_file, task_id)).start()

        return JsonResponse({"task_id": task_id})


def check_merge_video_progress(request):
    task_id = request.GET.get('task_id')
    try:
        task = VideoMergeTask.objects.get(task_id=task_id)
        return JsonResponse({
            "status": task.status,
            "progress": task.progress,
            "output_file": task.output_file
        })
    except VideoMergeTask.DoesNotExist:
        return JsonResponse({"status": "not found"}, status=404)


@csrf_exempt
def merge_audio(request):
    if request.method == 'POST':
        audio1 = request.FILES.get('audio1')
        audio2 = request.FILES.get('audio2')

        if not audio1 or not audio2:
            return JsonResponse({'error': 'Both audio files are required.'}, status=400)

        audio1_path = os.path.join('temp', audio1.name)
        audio2_path = os.path.join('temp', audio2.name)

        with open(audio1_path, 'wb+') as destination:
            for chunk in audio1.chunks():
                destination.write(chunk)

        with open(audio2_path, 'wb+') as destination:
            for chunk in audio2.chunks():
                destination.write(chunk)

        output_path = os.path.join('temp', 'output.mp3')
        audio1_segment = AudioSegment.from_file(audio1_path)
        audio2_segment = AudioSegment.from_file(audio2_path)

        combined = audio1_segment + audio2_segment
        combined.export(output_path, format='mp3')

        return JsonResponse({'merged_audio_url': f'/temp/output.mp3'})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
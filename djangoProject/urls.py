"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from audio_app.views import merge_audio, create_video, start_merge_videos, check_merge_video_progress
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_video', create_video),
    path('merge_audio', merge_audio),
    path('start_merge_videos', start_merge_videos),
    path('check_merge_video_progress', check_merge_video_progress)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

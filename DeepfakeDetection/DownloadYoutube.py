from yt_dlp import YoutubeDL

ydl_opts = {
    'outtmpl': 'input_video.%(ext)s',
    'format': 'best'
}

with YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=wrpmqMz-m4w'])

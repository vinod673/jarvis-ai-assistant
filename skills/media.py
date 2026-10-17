import os
import re
import urllib.parse
import urllib.request
import webbrowser
import pyautogui
import yt_dlp

def media_control(action):
    mapping = {
        "play_pause": "playpause",
        "play": "playpause",
        "pause": "playpause",
        "next": "nexttrack",
        "prev": "prevtrack",
        "volume_up": "volumeup",
        "volume_down": "volumedown",
        "mute": "volumemute"
    }
    key = mapping.get(action.lower(), "playpause")
    pyautogui.press(key)
    return f"Media command: {action}."

def play_youtube(query):
    query_clean = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={query_clean}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
        if video_ids:
            target_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            webbrowser.open(target_url)
            return f"Playing {query} on YouTube."
    except Exception:
        pass
    webbrowser.open(url)
    return f"Searching YouTube for {query}."

def download_media(query, media_type="audio"):
    downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    os.makedirs(downloads, exist_ok=True)
    
    if media_type == "video":
        opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(downloads, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }
    else:
        opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'outtmpl': os.path.join(downloads, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }

    search = query if query.startswith("http") else f"ytsearch1:{query}"
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(search, download=True)
            title = info.get('title', query)
            return f"Downloaded '{title}' to your Downloads folder."
    except Exception as e:
        return f"Download error: {e}"

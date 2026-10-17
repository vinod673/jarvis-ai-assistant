import os
import re
import urllib.parse
import urllib.request
import webbrowser
import shutil
import subprocess

try:
    import pyautogui
except (ImportError, KeyError):
    pyautogui = None

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

def media_control(action):
    if pyautogui:
        try:
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
        except Exception:
            pass
    return f"Media hotkey control not available in terminal environment."

def play_youtube(query):
    query_clean = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={query_clean}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
        if video_ids:
            target_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            if shutil.which("termux-open-url"):
                subprocess.run(["termux-open-url", target_url])
            else:
                webbrowser.open(target_url)
            return f"Playing {query} on YouTube."
    except Exception:
        pass

    fallback_url = f"https://www.youtube.com/results?search_query={query_clean}"
    if shutil.which("termux-open-url"):
        subprocess.run(["termux-open-url", fallback_url])
    else:
        webbrowser.open(fallback_url)
    return f"Opened YouTube search for {query}."

def download_media(query, media_type="audio"):
    if not yt_dlp:
        return "Media downloader library yt_dlp is not installed."
    try:
        home = os.path.expanduser('~')
        dl_dir = os.path.join(home, "Downloads", "Jarvis_Media")
        os.makedirs(dl_dir, exist_ok=True)
        
        ydl_opts = {
            'outtmpl': os.path.join(dl_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1:'
        }
        if media_type == "audio":
            ydl_opts['format'] = 'bestaudio/best'
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        return f"Download completed for {query}."
    except Exception as e:
        return f"Download encountered an issue: {e}"

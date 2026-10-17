import os
import time
import tempfile
import ctypes
import threading
import asyncio
import queue
import win32com.client
import pythoncom
import edge_tts
from colorama import Fore, Style, init

init(autoreset=True)

speech_queue = queue.Queue()
_is_speaking_flag = False
_worker_started = False
_lock = threading.Lock()

def is_speaking():
    global _is_speaking_flag
    return _is_speaking_flag

def _play_audio_winmm(audio_path):
    try:
        alias = f"jarvis_voice_{int(time.time() * 1000)}"
        winmm = ctypes.windll.winmm
        winmm.mciSendStringW(f'close {alias}', None, 0, 0)
        winmm.mciSendStringW(f'open "{audio_path}" alias {alias}', None, 0, 0)
        winmm.mciSendStringW(f'play {alias}', None, 0, 0)

        status = ctypes.create_unicode_buffer(256)
        while True:
            winmm.mciSendStringW(f'status {alias} mode', status, 256, 0)
            if status.value == "stopped":
                break
            time.sleep(0.04)

        winmm.mciSendStringW(f'close {alias}', None, 0, 0)
    except Exception as e:
        print(f"[Audio Error] WinMM playback error: {e}")

def _speech_worker_loop():
    global _is_speaking_flag
    pythoncom.CoInitialize()
    
    # Initialize SAPI as instant fallback
    sapi_voice = None
    try:
        sp = win32com.client.Dispatch("SAPI.SpVoice")
        for i in range(sp.GetVoices().Count):
            desc = sp.GetVoices().Item(i).GetDescription()
            if "David" in desc or "George" in desc or "male" in desc.lower():
                sp.Voice = sp.GetVoices().Item(i)
                break
        sp.Rate = 1
        sapi_voice = sp
    except Exception as e:
        print(f"[TTS Fallback Warning] SAPI initialization: {e}")

    while True:
        item = speech_queue.get()
        if item is None:
            break
        text, done_event = item
        _is_speaking_flag = True

        played_neural = False
        try:
            import config
            voice = getattr(config, "TTS_VOICE", "en-GB-RyanNeural")
            temp_mp3 = os.path.join(tempfile.gettempdir(), f"jarvis_speech_{int(time.time()*1000)}.mp3")
            comm = edge_tts.Communicate(text, voice)
            asyncio.run(comm.save(temp_mp3))
            
            if os.path.exists(temp_mp3) and os.path.getsize(temp_mp3) > 1000:
                _play_audio_winmm(temp_mp3)
                played_neural = True
                try:
                    os.remove(temp_mp3)
                except:
                    pass
        except Exception:
            played_neural = False

        if not played_neural and sapi_voice:
            try:
                sapi_voice.Speak(text, 0)
            except Exception as se:
                print(f"[SAPI Fallback Error] {se}")

        _is_speaking_flag = False
        if done_event:
            done_event.set()
        speech_queue.task_done()

    pythoncom.CoUninitialize()

def _ensure_worker():
    global _worker_started
    with _lock:
        if not _worker_started:
            t = threading.Thread(target=_speech_worker_loop, daemon=True)
            t.start()
            _worker_started = True

def speak(text, async_mode=True):
    """Speaks with ultra-realistic Edge Neural voice with zero freezing and seamless fallback."""
    if not text or not str(text).strip():
        return
        
    import config
    name = getattr(config, "ASSISTANT_NAME", "Jarvis")
    clean_text = str(text).strip()
    print(Fore.CYAN + Style.BRIGHT + f"{name} > " + Fore.WHITE + clean_text)
    
    _ensure_worker()
    
    if async_mode:
        speech_queue.put((clean_text, None))
    else:
        done = threading.Event()
        speech_queue.put((clean_text, done))
        done.wait(timeout=15.0)

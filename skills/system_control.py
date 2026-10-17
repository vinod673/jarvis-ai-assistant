import os
import sys
import subprocess
import time
import ctypes
import webbrowser
import shutil
import json

IS_WINDOWS = sys.platform == "win32"

# Windows COM / GUI Libraries (guarded for Linux / Android Termux)
try:
    import psutil
except ImportError:
    psutil = None

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except (ImportError, KeyError):
    pyautogui = None

try:
    import screen_brightness_control as sbc
except (ImportError, Exception):
    sbc = None

PYCAW_AVAILABLE = False
if IS_WINDOWS:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        import comtypes
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        PYCAW_AVAILABLE = True
    except (ImportError, Exception):
        PYCAW_AVAILABLE = False

CF_UNICODETEXT = 13
user32 = getattr(ctypes, 'windll', None).user32 if IS_WINDOWS else None
kernel32 = getattr(ctypes, 'windll', None).kernel32 if IS_WINDOWS else None

def _get_volume_interface():
    if not PYCAW_AVAILABLE:
        return None
    try:
        import comtypes
        comtypes.CoInitialize()
    except Exception:
        pass
    try:
        devices = AudioUtilities.GetSpeakers()
        if hasattr(devices, 'EndpointVolume'):
            return devices.EndpointVolume
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except Exception:
        return None

def get_volume():
    if IS_WINDOWS and PYCAW_AVAILABLE:
        try:
            vol = _get_volume_interface()
            if vol:
                return int(round(vol.GetMasterVolumeLevelScalar() * 100)), bool(vol.GetMute())
        except Exception:
            pass
    elif shutil.which("termux-volume"):
        try:
            res = subprocess.run(["termux-volume"], capture_output=True, text=True)
            data = json.loads(res.stdout)
            for stream in data:
                if stream.get("stream") == "music":
                    vol = int(round((stream.get("volume", 7) / stream.get("max_volume", 15)) * 100))
                    return vol, False
        except Exception:
            pass
    return 50, False

def set_volume(level):
    level = max(0, min(100, int(level)))
    if IS_WINDOWS and PYCAW_AVAILABLE:
        try:
            vol = _get_volume_interface()
            if vol:
                vol.SetMasterVolumeLevelScalar(level / 100.0, None)
                if vol.GetMute():
                    vol.SetMute(0, None)
                return True
        except Exception as e:
            print(f"[Volume Error] {e}")
    elif shutil.which("termux-volume"):
        try:
            # Termux music stream is typically 0 to 15
            val = int(round(level * 15 / 100.0))
            subprocess.run(["termux-volume", "music", str(val)], check=True)
            return True
        except Exception:
            pass
    elif pyautogui:
        return True
    return False

def toggle_mute():
    if IS_WINDOWS and PYCAW_AVAILABLE:
        try:
            vol = _get_volume_interface()
            if vol:
                cur = vol.GetMute()
                vol.SetMute(1 - cur, None)
                return not cur
        except Exception:
            pass
    if pyautogui:
        try:
            pyautogui.press('volumemute')
            return True
        except Exception:
            pass
    return False

def get_brightness():
    if sbc:
        try:
            b = sbc.get_brightness()
            return int(b[0]) if b else 50
        except Exception:
            pass
    return 50

def set_brightness(level):
    level = max(0, min(100, int(level)))
    if sbc:
        try:
            sbc.set_brightness(level)
            return True
        except Exception:
            pass
    if IS_WINDOWS:
        try:
            ps = f"(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"
            subprocess.run(["powershell", "-Command", ps], shell=True, check=True)
            return True
        except Exception:
            pass
    elif shutil.which("termux-brightness"):
        try:
            val = int(round(level * 255 / 100.0))
            subprocess.run(["termux-brightness", str(val)], check=True)
            return True
        except Exception:
            pass
    return False

_START_MENU_CACHE = {}
_SCANNED = False

def _scan_shortcuts():
    global _SCANNED
    if not IS_WINDOWS:
        _SCANNED = True
        return
    dirs = [
        os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs'),
        r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs'
    ]
    for d in dirs:
        if os.path.exists(d):
            for root, _, files in os.walk(d):
                for f in files:
                    if f.lower().endswith('.lnk'):
                        name = f[:-4].lower()
                        _START_MENU_CACHE[name] = os.path.join(root, f)
    _SCANNED = True

def open_app(app_name):
    global _SCANNED
    app = app_name.lower().strip()

    if app.startswith("http://") or app.startswith("https://") or ("." in app and " " not in app):
        url = app if app.startswith("http") else f"https://{app}"
        if shutil.which("termux-open-url"):
            subprocess.run(["termux-open-url", url])
        else:
            webbrowser.open(url)
        return f"Opening {url}."

    if IS_WINDOWS:
        app_mappings = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "terminal": "wt.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "taskmgr": "taskmgr.exe",
            "explorer": "explorer.exe",
            "settings": "start ms-settings:",
            "camera": "start microsoft.windows.camera:",
            "clock": "start ms-clock:",
            "spotify": "start spotify:",
            "chrome": "start chrome",
            "edge": "start msedge"
        }

        if app in app_mappings:
            subprocess.Popen(app_mappings[app], shell=True)
            return f"Opening {app}."

        if not _SCANNED:
            _scan_shortcuts()

        for name, path in _START_MENU_CACHE.items():
            if app in name or name in app:
                try:
                    os.startfile(path)
                    return f"Opening {name}."
                except Exception:
                    pass

    search_url = f"https://www.google.com/search?q={app}"
    if shutil.which("termux-open-url"):
        subprocess.run(["termux-open-url", search_url])
    else:
        webbrowser.open(search_url)
    return f"Searching for {app}."

def close_active_window():
    if pyautogui:
        try:
            pyautogui.hotkey('alt', 'f4')
            return "Closing active window."
        except Exception:
            pass
    return "Action not supported on this platform."

def show_desktop():
    if pyautogui:
        try:
            pyautogui.hotkey('win', 'd')
            return "Showing desktop."
        except Exception:
            pass
    return "Action not supported on this platform."

def lock_pc():
    if IS_WINDOWS and user32:
        user32.LockWorkStation()
        return "Locking workstation."
    return "Workstation lock is only applicable to desktop."

def power_control(action):
    if IS_WINDOWS:
        if action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif action == "shutdown":
            os.system("shutdown /s /t 1")
        elif action == "restart":
            os.system("shutdown /r /t 1")
        return f"Executing {action}."
    return f"Power control not permitted in terminal sandbox."

def take_screenshot():
    if pyautogui:
        try:
            home = os.path.expanduser('~')
            save_dir = os.path.join(home, "Pictures", "Jarvis_Screenshots")
            os.makedirs(save_dir, exist_ok=True)
            filename = f"screenshot_{int(time.time())}.png"
            filepath = os.path.join(save_dir, filename)
            shot = pyautogui.screenshot()
            shot.save(filepath)
            return filepath
        except Exception:
            pass
    return "Screenshot not available on this platform."

def get_system_stats_summary():
    cpu_str = ""
    ram_str = ""
    if psutil:
        try:
            cpu = int(psutil.cpu_percent(interval=None))
            vm = psutil.virtual_memory()
            ram_pct = int(vm.percent)
            ram_used = round(vm.used / (1024**3), 1)
            cpu_str = f"CPU utilization is {cpu} percent."
            ram_str = f"Memory usage is {ram_pct} percent, with {ram_used} GB in use."
        except Exception:
            pass

    bat_str = ""
    # Check Termux battery
    if shutil.which("termux-battery-status"):
        try:
            res = subprocess.run(["termux-battery-status"], capture_output=True, text=True)
            b = json.loads(res.stdout)
            pct = b.get("percentage")
            status = b.get("status", "discharging").lower()
            bat_str = f"Battery is at {pct}% and {status}."
        except Exception:
            pass

    if not bat_str and psutil:
        try:
            bat = psutil.sensors_battery()
            if bat:
                status = "plugged in" if bat.power_plugged else "discharging"
                bat_str = f"Battery is at {int(bat.percent)}% and {status}."
        except Exception:
            pass

    parts = [p for p in [cpu_str, ram_str, bat_str] if p]
    return " ".join(parts) if parts else "System metrics operational."

def get_clipboard_text():
    if shutil.which("termux-clipboard-get"):
        try:
            res = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True)
            return res.stdout.strip()
        except Exception:
            pass

    if IS_WINDOWS and user32 and kernel32:
        for _ in range(5):
            if user32.OpenClipboard(None):
                break
            time.sleep(0.05)
        else:
            return ""
        try:
            h = user32.GetClipboardData(CF_UNICODETEXT)
            if not h: return ""
            user32.GlobalLock.restype = ctypes.c_void_p
            p = kernel32.GlobalLock(h)
            if not p: return ""
            try:
                return ctypes.c_wchar_p(p).value or ""
            finally:
                kernel32.GlobalUnlock(h)
        finally:
            user32.CloseClipboard()
    return ""

def set_clipboard_text(text):
    if shutil.which("termux-clipboard-set"):
        try:
            subprocess.run(["termux-clipboard-set", text], check=True)
            return True
        except Exception:
            pass

    if IS_WINDOWS and user32 and kernel32:
        for _ in range(5):
            if user32.OpenClipboard(None):
                break
            time.sleep(0.05)
        else:
            return False
        try:
            user32.EmptyClipboard()
            data = (text + "\0").encode('utf-16le')
            h = kernel32.GlobalAlloc(0x0042, len(data))
            p = kernel32.GlobalLock(h)
            ctypes.memmove(p, data, len(data))
            kernel32.GlobalUnlock(h)
            user32.SetClipboardData(CF_UNICODETEXT, h)
            return True
        finally:
            user32.CloseClipboard()
    return False

def type_text(text):
    if pyautogui:
        try:
            pyautogui.write(text, interval=0.01)
            return True
        except Exception:
            pass
    return False

def write_text(text):
    return type_text(text)

def press_key(key):
    if pyautogui:
        try:
            pyautogui.press(key)
            return f"Pressed {key}."
        except Exception:
            pass
    return f"Key simulation not supported."

def window_management(action):
    if IS_WINDOWS and user32:
        hwnd = user32.GetForegroundWindow()
        if action == "maximize":
            user32.ShowWindow(hwnd, 3)
        elif action == "minimize":
            user32.ShowWindow(hwnd, 6)
        elif action == "restore":
            user32.ShowWindow(hwnd, 9)
        return f"Window {action}d."
    return "Window management is desktop only."

def start_timer(minutes, callback):
    import threading
    def _timer():
        time.sleep(float(minutes) * 60)
        callback()
    t = threading.Thread(target=_timer, daemon=True)
    t.start()

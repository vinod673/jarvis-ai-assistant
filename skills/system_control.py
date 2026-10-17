import os
import subprocess
import time
import ctypes
import webbrowser
import psutil
import pyautogui
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import comtypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

pyautogui.FAILSAFE = False

CF_UNICODETEXT = 13
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def _get_volume_interface():
    try:
        comtypes.CoInitialize()
    except Exception:
        pass
    devices = AudioUtilities.GetSpeakers()
    if hasattr(devices, 'EndpointVolume'):
        return devices.EndpointVolume
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def get_volume():
    try:
        vol = _get_volume_interface()
        return int(round(vol.GetMasterVolumeLevelScalar() * 100)), bool(vol.GetMute())
    except Exception:
        return 50, False

def set_volume(level):
    try:
        level = max(0, min(100, int(level)))
        vol = _get_volume_interface()
        vol.SetMasterVolumeLevelScalar(level / 100.0, None)
        if vol.GetMute():
            vol.SetMute(0, None)
        return True
    except Exception as e:
        print(f"[Volume Error] {e}")
        return False

def toggle_mute():
    try:
        vol = _get_volume_interface()
        cur = vol.GetMute()
        vol.SetMute(1 - cur, None)
        return not cur
    except Exception:
        pyautogui.press('volumemute')
        return True

def get_brightness():
    try:
        b = sbc.get_brightness()
        return int(b[0]) if b else 50
    except Exception:
        return 50

def set_brightness(level):
    try:
        level = max(0, min(100, int(level)))
        sbc.set_brightness(level)
        return True
    except Exception:
        try:
            ps = f"(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"
            subprocess.run(["powershell", "-Command", ps], shell=True, check=True)
            return True
        except Exception:
            return False

_START_MENU_CACHE = {}
_SCANNED = False

def _scan_shortcuts():
    global _SCANNED
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

    if app.startswith("http://") or app.startswith("https://") or ("." in app and " " not in app):
        url = app if app.startswith("http") else f"https://{app}"
        webbrowser.open(url)
        return f"Opening {url}."

    if not _SCANNED:
        _scan_shortcuts()

    for name, path in _START_MENU_CACHE.items():
        if app in name or name in app:
            try:
                os.startfile(path)
                return f"Opening {name}."
            except Exception:
                pass

    webbrowser.open(f"https://www.google.com/search?q={app}")
    return f"Searching the web for {app}."

def close_active_window():
    pyautogui.hotkey('alt', 'f4')
    return "Closing active window."

def show_desktop():
    pyautogui.hotkey('win', 'd')
    return "Showing desktop."

def lock_pc():
    ctypes.windll.user32.LockWorkStation()
    return "Locking workstation."

def power_control(action):
    if action == "sleep":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif action == "shutdown":
        os.system("shutdown /s /t 1")
    elif action == "restart":
        os.system("shutdown /r /t 1")
    return f"Executing {action}."

def take_screenshot():
    home = os.path.expanduser('~')
    save_dir = os.path.join(home, "Pictures", "Jarvis_Screenshots")
    os.makedirs(save_dir, exist_ok=True)
    filename = f"screenshot_{int(time.time())}.png"
    filepath = os.path.join(save_dir, filename)
    shot = pyautogui.screenshot()
    shot.save(filepath)
    return filepath

def get_system_stats_summary():
    cpu = int(psutil.cpu_percent(interval=None))
    vm = psutil.virtual_memory()
    ram_pct = int(vm.percent)
    ram_used = round(vm.used / (1024**3), 1)
    
    bat = psutil.sensors_battery()
    bat_str = ""
    if bat:
        status = "plugged in" if bat.power_plugged else "discharging"
        bat_str = f"Battery is at {int(bat.percent)}% and {status}."
        
    return f"CPU utilization is {cpu} percent. Memory usage is {ram_pct} percent, with {ram_used} gigabytes in use. {bat_str}".strip()

def get_clipboard_text():
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

def set_clipboard_text(text):
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

def type_text(text):
    pyautogui.write(text, interval=0.01)
    return True

def write_text(text):
    return type_text(text)

def press_key(key):
    pyautogui.press(key)
    return f"Pressed {key}."

def window_management(action):
    hwnd = user32.GetForegroundWindow()
    if action == "maximize":
        user32.ShowWindow(hwnd, 3)
    elif action == "minimize":
        user32.ShowWindow(hwnd, 6)
    elif action == "restore":
        user32.ShowWindow(hwnd, 9)
    return f"Window {action}d."

def start_timer(minutes, callback):
    import threading
    def _timer():
        time.sleep(float(minutes) * 60)
        callback()
    t = threading.Thread(target=_timer, daemon=True)
    t.start()

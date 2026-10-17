import os
import sys
import tempfile
import subprocess

BASE_DIR = r"c:\Users\vinod\OneDrive\Desktop\aitomation tool\ai asiistant"

HELPER_HEADER = f"""
import os
import sys
import time
import requests
import pyautogui

sys.path.insert(0, r'{BASE_DIR}')
from skills.system_control import *
from skills.media import *
from skills.research import *
"""

def execute_python_script(code):
    """Executes a block of Python code safely with pre-imported Jarvis skills."""
    try:
        full_script = HELPER_HEADER + "\n" + code
        fd, path = tempfile.mkstemp(suffix=".py", prefix="jarvis_auto_")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(full_script)
            
        venv_python = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")
        py_exec = venv_python if os.path.exists(venv_python) else sys.executable
        
        res = subprocess.run([py_exec, path], capture_output=True, text=True, timeout=15)
        os.remove(path)
        if res.returncode == 0:
            out = res.stdout.strip()
            return out if out else "Actions completed successfully."
        else:
            return f"Execution error: {res.stderr.strip()[:200]}"
    except Exception as e:
        return f"Execution failed: {e}"

import sys
import os
import subprocess

os.environ["PYTHONUNBUFFERED"] = "1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")

if os.path.exists(VENV_PYTHON):
    current_python = os.path.abspath(sys.executable).lower()
    target_python = os.path.abspath(VENV_PYTHON).lower()
    if current_python != target_python:
        sys.exit(subprocess.call([VENV_PYTHON] + sys.argv))

import main

if __name__ == "__main__":
    main.main_loop()

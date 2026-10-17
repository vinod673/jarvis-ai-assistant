import time
import sys
import random
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except (ImportError, Exception):
    class DummyColor:
        def __getattr__(self, name): return ""
    Fore = DummyColor()
    Style = DummyColor()

try:
    import winsound
except ImportError:
    winsound = None

def play_beep(freq=1200, duration=150):
    if winsound:
        try:
            winsound.Beep(freq, duration)
            return
        except Exception:
            pass
    # Cross-platform terminal bell fallback
    sys.stdout.write('\a')
    sys.stdout.flush()

import config
from audio.speaker import speak
from audio.listener import calibrate_mic, listen_wake_word, listen_for_command
from brain.ai_core import process_input
from brain import memory_manager

from skills import system_control
from skills import media
from skills import research
from skills import android_integration
from skills import automation

WAKE_GREETINGS = [
    "Yes sir?",
    "At your service, sir.",
    "Listening, sir.",
    "How may I be of service, sir?",
    "Always ready, sir. What is on your mind?",
    "Go right ahead, sir."
]

def dispatch_task(intent, params, spoken):
    # Speak Jarvis's human response
    if spoken:
        speak(spoken)

    try:
        if intent == "volume_set":
            system_control.set_volume(params.get("value", 50))
        elif intent == "volume_change":
            cur, _ = system_control.get_volume()
            system_control.set_volume(cur + params.get("value", 10))
        elif intent == "volume_mute":
            _, muted = system_control.get_volume()
            if not muted: system_control.toggle_mute()
        elif intent == "volume_unmute":
            _, muted = system_control.get_volume()
            if muted: system_control.toggle_mute()
        elif intent == "brightness_set":
            system_control.set_brightness(params.get("value", 50))
        elif intent == "brightness_change":
            cur = system_control.get_brightness()
            system_control.set_brightness(cur + params.get("value", 10))
        elif intent == "open_app":
            system_control.open_app(params.get("app_name", ""))
        elif intent == "close_app":
            system_control.close_active_window()
        elif intent == "window_management":
            system_control.window_management(params.get("action", "maximize"))
        elif intent == "show_desktop":
            system_control.show_desktop()
        elif intent == "system_info":
            pass # The AI already incorporates system stats naturally into spoken response
        elif intent == "screenshot":
            p = system_control.take_screenshot()
        elif intent == "lock_pc":
            system_control.lock_pc()
        elif intent == "power_control":
            system_control.power_control(params.get("action", "sleep"))
        elif intent == "media_control":
            media.media_control(params.get("action", "play_pause"))
        elif intent == "play_youtube":
            media.play_youtube(params.get("query", ""))
        elif intent == "download_media":
            res = media.download_media(params.get("query", ""), params.get("media_type", "audio"))
            speak(res)
        elif intent == "search_web":
            import webbrowser
            webbrowser.open(f"https://www.google.com/search?q={params.get('query', '')}")
        elif intent == "weather":
            pass # AI integrates weather naturally into conversation
        elif intent == "set_timer":
            mins = float(params.get("minutes", 1))
            system_control.start_timer(mins, lambda: (play_beep(1200, 500), speak(f"Pardon the interruption, sir, but your {mins} minute timer has just expired.")))
        elif intent == "clipboard_read":
            txt = system_control.get_clipboard_text()
            speak(f"Your clipboard contains: {txt}" if txt else "Your clipboard is currently empty, sir.")
        elif intent == "clipboard_write":
            system_control.set_clipboard_text(params.get("text", ""))
        elif intent == "keyboard_type":
            system_control.type_text(params.get("text", ""))
        elif intent == "keyboard_press":
            system_control.press_key(params.get("key", "enter"))
        elif intent == "research_query":
            res = research.synthesize_research(params.get("query", ""))
            speak(res)
        elif intent == "android_command":
            res = android_integration.send_android_command(params.get("action", "BATTERY"), params)
            if res.get("status") != "success":
                speak(f"Phone notice: {res.get('message')}")
        elif intent == "python_execution":
            out = automation.execute_python_script(params.get("code", ""))
            if out:
                speak(f"Result: {out[:120]}")
    except Exception as e:
        print(f"[Dispatch Error] {e}")

def main_loop():
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════════════════╗
    ║        J.A.R.V.I.S. PRO SYSTEM ONLINE            ║
    ║   Conversational Neural AI | Edge British Voice  ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    # 1. Start Android Bridge in background
    android_integration.run_server_in_background()
    print(Fore.GREEN + "[Bridge] Android WebSocket Server listening on port 8765.")

    # 2. Calibrate Microphone / Input Method
    print(Fore.YELLOW + "[Audio] Initializing input system...", end="\r")
    baseline, thresh = calibrate_mic(0.8)

    # 3. Boot Greeting
    boot_greetings = [
        "System boot complete. Jarvis core online and entirely at your service, sir.",
        "Systems initialized. All protocols online and ready, sir. What are we creating today?",
        "Good to see you again, sir. All neural networks are fully operational."
    ]
    speak(random.choice(boot_greetings))

    while True:
        try:
            cmd, is_wake = listen_wake_word()
            
            if not is_wake and not cmd:
                continue

            # If user said just "Jarvis" without immediate trailing command
            if is_wake and not cmd:
                play_beep(1200, 80)
                greeting = random.choice(WAKE_GREETINGS)
                speak(greeting, async_mode=False) # Wait for speech to complete
                time.sleep(0.08) # Echo decay
                cmd = listen_for_command()
                if not cmd:
                    speak("Standing by whenever you're ready, sir.")
                    continue

            if not cmd:
                continue

            if cmd.lower() in ["exit", "quit", "shutdown", "deactivate", "goodbye jarvis", "bye jarvis"]:
                parting_words = [
                    "Deactivating system protocols. Do take care of yourself, sir.",
                    "Standing down now. It was a pleasure assisting you today, sir. Goodnight.",
                    "Powering down auxiliary systems. Call upon me whenever you need me, sir."
                ]
                speak(random.choice(parting_words))
                break

            print(Fore.MAGENTA + f"[Processing: '{cmd}']" + Style.RESET_ALL)
            memory_manager.add_history("user", cmd)

            result = process_input(cmd)
            intent = result.get("intent", "chat")
            params = result.get("parameters", {})
            spoken = result.get("spoken_response", "")

            print(Fore.BLUE + f"[Action: {intent} | Params: {params}]" + Style.RESET_ALL)

            if spoken:
                memory_manager.add_history("model", spoken)

            import threading
            t = threading.Thread(target=dispatch_task, args=(intent, params, spoken), daemon=True)
            t.start()

        except KeyboardInterrupt:
            speak("System interrupted. Standing down, sir.")
            break
        except Exception as e:
            print(Fore.RED + f"[System Loop Exception] {e}")
            time.sleep(1)

if __name__ == "__main__":
    main_loop()

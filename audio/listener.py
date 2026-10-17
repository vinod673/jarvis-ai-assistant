import time
import sys
import queue
import collections
import re
try:
    from colorama import Fore, Style
except (ImportError, Exception):
    class DummyColor:
        def __getattr__(self, name): return ""
    Fore = DummyColor()
    Style = DummyColor()
import config
from audio import speaker

try:
    import winsound
except ImportError:
    winsound = None

def _beep(freq=1200, duration=80):
    if winsound:
        try:
            winsound.Beep(freq, duration)
            return
        except Exception:
            pass
    sys.stdout.write('\a')
    sys.stdout.flush()

try:
    import numpy as np
    import sounddevice as sd
    import speech_recognition as sr
    AUDIO_LIBS_AVAILABLE = True
except Exception:
    AUDIO_LIBS_AVAILABLE = False

ambient_rms_baseline = 200.0
speech_threshold = 400.0
mic_available = AUDIO_LIBS_AVAILABLE
_audio_q = queue.Queue()

def calibrate_mic(duration=0.8):
    """Calibrates microphone ambient noise floor or activates keyboard console mode."""
    global ambient_rms_baseline, speech_threshold, mic_available
    if not AUDIO_LIBS_AVAILABLE:
        mic_available = False
        print(Fore.YELLOW + "[Input] Audio hardware libraries not detected. Operating in Interactive Terminal Mode.")
        return 100.0, 400.0

    try:
        sample_rate = 16000
        frames = int(sample_rate * duration)
        recording = sd.rec(frames, samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        rms = float(np.sqrt(np.mean(recording.astype(np.float32)**2)))
        ambient_rms_baseline = max(50.0, rms)
        speech_threshold = max(300.0, min(1200.0, ambient_rms_baseline * 1.6 + 150.0))
        mic_available = True
        print(Fore.GREEN + f"[Audio] Calibrated: Noise Floor = {ambient_rms_baseline:.1f} RMS | Speech Threshold = {speech_threshold:.1f} RMS")
        return ambient_rms_baseline, speech_threshold
    except Exception as e:
        mic_available = False
        print(Fore.YELLOW + f"[Mic Warning] Microphone initialization failed ({e}). Switching to Interactive Terminal Mode.")
        return 100.0, 400.0

def _recognize_audio(audio_data, sample_rate):
    """Transcribes audio using Google Speech Recognition."""
    if not AUDIO_LIBS_AVAILABLE:
        return ""
    r = sr.Recognizer()

    peak = int(np.max(np.abs(audio_data)))
    if peak > 0 and peak < 16000:
        gain = min(8.0, 22000.0 / peak)
        audio_data = np.clip(audio_data * gain, -32768, 32767).astype(np.int16)

    aud = sr.AudioData(audio_data.tobytes(), sample_rate, 2)
    primary_lang = getattr(config, "SPEECH_LANGUAGE", "en-IN")

    try:
        text = r.recognize_google(aud, language=primary_lang)
        return text.strip().lower()
    except sr.UnknownValueError:
        if primary_lang != "en-US":
            try:
                text = r.recognize_google(aud, language="en-US")
                return text.strip().lower()
            except Exception:
                pass
        return ""
    except Exception as e:
        if "WinError 50" not in str(e):
            print(Fore.RED + f"[Speech Recognition Error] {e}")
        return ""

def listen_vad(timeout=None, phrase_time_limit=10.0):
    """Listens with rolling pre-roll buffer so starting consonants are never cut off."""
    global mic_available, speech_threshold
    if not mic_available or not AUDIO_LIBS_AVAILABLE:
        return ""

    sample_rate = 16000
    frames_per_buffer = int(sample_rate * 0.1) # 100ms
    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        q.put(indata.copy())

    preroll = collections.deque(maxlen=3) # 300ms pre-roll buffer
    silence_limit = 0.7  # 700ms silence ends utterance
    is_speaking = False
    silence_timer = 0.0
    buffer = []

    start_time = time.time()
    speech_start_time = None

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16', blocksize=frames_per_buffer, callback=callback):
            while True:
                chunk = q.get()

                if speaker.is_speaking():
                    is_speaking = False
                    buffer = []
                    silence_timer = 0.0
                    preroll.clear()
                    continue

                chunk_rms = float(np.sqrt(np.mean(chunk.astype(np.float32)**2)))

                if not is_speaking:
                    preroll.append(chunk)
                    if chunk_rms > speech_threshold:
                        is_speaking = True
                        speech_start_time = time.time()
                        silence_timer = 0.0
                        buffer = list(preroll)
                    elif timeout and (time.time() - start_time) > timeout:
                        return ""
                else:
                    buffer.append(chunk)
                    if chunk_rms < speech_threshold:
                        silence_timer += 0.1
                    else:
                        silence_timer = 0.0

                    if silence_timer >= silence_limit or (time.time() - speech_start_time) > phrase_time_limit:
                        if not buffer or len(buffer) < 4:
                            return ""
                        audio_data = np.concatenate(buffer, axis=0)
                        return _recognize_audio(audio_data, sample_rate)
    except Exception as e:
        if "WinError 50" not in str(e):
            print(Fore.RED + f"[VAD Error] {e}")
        return ""

def extract_wake_and_command(query):
    """Extracts wake word variants and any immediately following single-shot command."""
    if not query:
        return None, False

    variants = getattr(config, "WAKE_VARIANTS", ["jarvis", "hey jarvis", "travis", "service", "javis"])
    query_lower = query.lower().strip()

    matched = False
    for v in variants:
        if v in query_lower:
            matched = True
            break

    if not matched:
        return None, False

    cleaned = re.sub(r'^(hey\s+|hi\s+|ok\s+)?(jarvis|travis|service|javis|jarves|harvest)[,\s]*', '', query_lower, flags=re.IGNORECASE).strip()
    return cleaned, True

def listen_for_command():
    """Captures command after wake word prompt with visual indicator and chime."""
    if not mic_available:
        try:
            return input(Fore.YELLOW + "\nYOU (Type) > " + Style.RESET_ALL).strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    _beep(1400, 80)
    print(Fore.GREEN + Style.BRIGHT + "[MIC ACTIVE - SPEAK YOUR COMMAND NOW]" + Style.RESET_ALL)
    query = listen_vad(timeout=8.0, phrase_time_limit=12.0)
    if query:
        print(Fore.GREEN + f"YOU > " + Fore.WHITE + query + " " * 20)
        return query
    return ""

def listen_wake_word():
    """Passive listening loop detecting wake words, or interactive keyboard prompt."""
    if not mic_available:
        try:
            cmd = input(Fore.YELLOW + "\nYOU (Type command, or 'exit' to quit) > " + Style.RESET_ALL).strip()
            if not cmd:
                return "", False
            cleaned, is_wake = extract_wake_and_command(cmd)
            if is_wake:
                return cleaned, True
            return cmd, True
        except (EOFError, KeyboardInterrupt):
            return "", False

    wake_words = getattr(config, "WAKE_WORDS", ["jarvis", "hey jarvis"])
    print(Fore.LIGHTBLACK_EX + f"Passive listening for {wake_words}... (Press Ctrl+C to stop)" + Style.RESET_ALL, end="\r")

    query = listen_vad(timeout=None, phrase_time_limit=8.0)
    if not query:
        return "", False

    cmd, is_wake = extract_wake_and_command(query)
    if is_wake:
        if cmd:
            _beep(1500, 80)
            print(Fore.GREEN + f"YOU (Single-shot) > " + Fore.WHITE + cmd + " " * 20)
            return cmd, True
        else:
            return "", True

    return "", False

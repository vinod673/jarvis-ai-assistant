import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(BASE_DIR, ".env")

try:
    from dotenv import load_dotenv
    load_dotenv(env_file)
except ImportError:
    # Built-in lightweight fallback parser for .env if python-dotenv is not installed
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except Exception:
            pass

# Assistant Identity
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Jarvis")
WAKE_WORDS = [w.strip().lower() for w in os.getenv("WAKE_WORD", "jarvis,hey jarvis").split(",")]
WAKE_VARIANTS = ["jarvis", "hey jarvis", "hi jarvis", "ok jarvis", "travis", "service", "javis", "jarves", "harvest"]
SECRET_PASSWORD = os.getenv("SECRET_PASSWORD", "omega").lower()

# AI Configuration
raw_keys = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
GEMINI_API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Audio Configuration
TTS_VOICE = os.getenv("TTS_VOICE", "en-GB-RyanNeural")
TTS_RATE = os.getenv("TTS_RATE", "+0%")
SPEECH_LANGUAGE = os.getenv("SPEECH_LANGUAGE", "en-IN")

SYSTEM_PROMPT = f"""You are {ASSISTANT_NAME}, a highly intelligent, polite, and sophisticated AI voice assistant that controls the user's computer and connected Android device.
You speak with the crisp, witty, efficient elegance of Tony Stark's J.A.R.V.I.S.
Keep spoken responses EXTREMELY CONCISE (under 2 sentences whenever possible) as they will be spoken out loud.
Categorize the user request into an intent with parameters and return strictly valid JSON."""

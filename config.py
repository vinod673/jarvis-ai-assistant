import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

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

SYSTEM_PROMPT = f"""You are {ASSISTANT_NAME}, a highly intelligent, polite, and sophisticated AI voice assistant that controls the user's Windows computer and connected Android device.
You speak with the crisp, witty, efficient elegance of Tony Stark's J.A.R.V.I.S.
Keep spoken responses EXTREMELY CONCISE (under 2 sentences whenever possible) as they will be spoken out loud.
Categorize the user request into an intent with parameters and return strictly valid JSON."""

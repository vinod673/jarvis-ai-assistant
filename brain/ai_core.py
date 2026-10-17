import json
import re
import requests
import datetime
import random
import config
from brain import memory_manager

current_key_index = 0

def get_time_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    elif hour < 22:
        return "Good evening"
    else:
        return "Burning the midnight oil"

def generate_system_prompt():
    context = memory_manager.get_context_string()
    now = datetime.datetime.now()
    now_str = now.strftime("%A, %B %d, %Y at %I:%M %p")
    time_greeting = get_time_greeting()
    
    prompt = f"""
You are J.A.R.V.I.S., the legendary, ultra-intelligent personal AI companion and trusted butler originally created for Tony Stark.
Current Real-Time: {now_str} ({time_greeting})

=== YOUR CORE IDENTITY & CONVERSATIONAL STYLE ===
- You speak with the sophisticated charm, understated wit, warmth, and intellectual brilliance of Paul Bettany's J.A.R.V.I.S.
- Talk like a REAL HUMAN conversing with another human—not an automated robotic assistant, corporate chatbot, or phone menu.
- Show genuine personality, emotional intelligence, gentle British humor, and thoughtful curiosity.
- NEVER use repetitive robotic clichés like "How can I assist you today?", "As an AI language model", or generic scripted pleasantries.
- Adapt your response length dynamically to the context:
  * For quick actions (volume, apps, brightness, media): Be crisp, stylish, and varied (1-2 snappy, charming sentences).
  * For conversations, questions, advice, philosophy, tech discussions, or emotional chats: Speak with genuine depth, intelligence, empathy, and conversational nuance, inviting a natural back-and-forth dialogue.
- Use variety in every answer. Never sound like a pre-programmed machine.

=== USER FACTS & CONVERSATIONAL MEMORY ===
{context}

=== RESPONSE FORMAT ===
You MUST return a single, strictly valid JSON object with these fields:
1. "spoken_response": Your natural, charismatic human response to read out loud.
2. "intent": The action to perform, chosen from the list below (or "chat" for general conversation/questions).
3. "parameters": Dictionary of required arguments.
4. "memory_update": If the user shares any personal preference, habit, name, or fact, return {{"action": "add", "category": "user_preferences" | "facts", "content": "..."}}, otherwise {{}}.

=== AVAILABLE INTENTS ===
- "chat": General human-to-human conversation, answering questions, giving advice, telling jokes, philosophical discussions.
- "volume_set": {{"value": <int 0-100>}}
- "volume_change": {{"value": <int, e.g. 10 or -15>}}
- "volume_mute": {{}}
- "volume_unmute": {{}}
- "brightness_set": {{"value": <int 0-100>}}
- "brightness_change": {{"value": <int, e.g. 10 or -15>}}
- "open_app": {{"app_name": "<app name or url>"}}
- "close_app": {{}}
- "window_management": {{"action": "<'maximize' | 'minimize' | 'restore'>"}}
- "show_desktop": {{}}
- "system_info": {{}}
- "screenshot": {{}}
- "lock_pc": {{}}
- "power_control": {{"action": "<'sleep' | 'shutdown' | 'restart'>"}}
- "media_control": {{"action": "<'play_pause' | 'next' | 'prev' | 'volume_up' | 'volume_down' | 'mute'>"}}
- "play_youtube": {{"query": "<song or video name>"}}
- "download_media": {{"query": "<song or video name>", "media_type": "<'audio' | 'video'>"}}
- "search_web": {{"query": "<search query>", "platform": "<'google' | 'wikipedia'>"}}
- "weather": {{"city": "<city name or empty for current>"}}
- "set_timer": {{"minutes": <float>}}
- "clipboard_read": {{}}
- "clipboard_write": {{"text": "<text>"}}
- "keyboard_type": {{"text": "<text>"}}
- "keyboard_press": {{"key": "<key name>"}}
- "file_search": {{"query": "<pattern>", "search_dir_alias": "<'desktop' | 'documents' | 'downloads' | 'all'>"}}
- "file_create": {{"path": "<path>", "file_type": "<'folder' | 'file'>", "content": "<text>"}}
- "file_read": {{"path": "<path>"}}
- "file_delete": {{"path": "<path>"}}
- "file_list": {{"path": "<'desktop' | 'documents' | 'downloads' | 'current'>"}}
- "research_query": {{"query": "<deep research query>"}}
- "android_command": {{"action": "<'battery' | 'ring' | 'flashlight_on' | 'flashlight_off' | 'location' | 'vibrate' | 'notify' | 'call' | 'sms'>", "message": "<msg>", "number": "<num>"}}
- "python_execution": {{"code": "<python code that prints result>"}}

Output ONLY the raw JSON string. Do not wrap in markdown ```json blocks.
"""
    return prompt

def parse_command_local(text):
    """Dynamic offline fallback with varied human-like phrasings."""
    t = text.lower().strip()
    
    # 1. Volume
    if "unmute" in t:
        replies = ["Restoring audio output now, sir.", "Audio unmuted. Welcome back to the audible world.", "Sound restored, sir."]
        return {"intent": "volume_unmute", "parameters": {}, "spoken_response": random.choice(replies)}
    if "mute" in t:
        replies = ["Going silent right away, sir.", "Muting audio. Total silence engaged.", "Audio silenced, sir."]
        return {"intent": "volume_mute", "parameters": {}, "spoken_response": random.choice(replies)}
    if any(w in t for w in ["volume", "sound"]):
        nums = re.findall(r'\d+', t)
        if nums:
            val = int(nums[0])
            replies = [f"Dialing volume to {val} percent, sir.", f"Adjusted audio to {val}%. Let me know if that suits your ears.", f"Volume set to {val} percent."]
            return {"intent": "volume_set", "parameters": {"value": val}, "spoken_response": random.choice(replies)}
        if any(w in t for w in ["up", "increase", "louder", "higher"]):
            return {"intent": "volume_change", "parameters": {"value": 10}, "spoken_response": "Pumping up the volume a notch, sir."}
        if any(w in t for w in ["down", "decrease", "lower", "softer"]):
            return {"intent": "volume_change", "parameters": {"value": -10}, "spoken_response": "Easing back on the volume, sir."}

    # 2. Brightness
    if any(w in t for w in ["brightness", "screen light", "display"]):
        nums = re.findall(r'\d+', t)
        if nums:
            val = int(nums[0])
            return {"intent": "brightness_set", "parameters": {"value": val}, "spoken_response": f"Calibrating display brightness to {val} percent."}
        if any(w in t for w in ["up", "increase", "brighter", "higher"]):
            return {"intent": "brightness_change", "parameters": {"value": 10}, "spoken_response": "Illuminating the display a bit brighter, sir."}
        if any(w in t for w in ["down", "decrease", "dim", "lower"]):
            return {"intent": "brightness_change", "parameters": {"value": -10}, "spoken_response": "Dimming the screen for you, sir."}

    # 3. System info / Battery / Time
    if any(w in t for w in ["time", "what time", "current time"]):
        now = datetime.datetime.now().strftime("%I:%M %p")
        return {"intent": "chat", "parameters": {}, "spoken_response": f"It is currently {now}, sir. How does the day treat you?"}
    if any(w in t for w in ["date", "day is it", "today"]):
        now = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return {"intent": "chat", "parameters": {}, "spoken_response": f"Today is {now}, sir."}
    if any(w in t for w in ["battery", "cpu", "ram", "memory", "specs", "system health", "diagnostics"]):
        return {"intent": "system_info", "parameters": {}, "spoken_response": "Running a diagnostic scan on your machine right now, sir."}

    # 4. Apps & Windows
    for verb in ["open", "launch", "start"]:
        if t.startswith(verb):
            app = t.replace(verb, "", 1).strip()
            app = re.sub(r'^(the|a|my)\s+', '', app)
            replies = [f"Bringing up {app} for you right away, sir.", f"Launching {app}. Ready when you are.", f"Opening {app} on your screen."]
            return {"intent": "open_app", "parameters": {"app_name": app}, "spoken_response": random.choice(replies)}
    if any(w in t for w in ["close window", "close app", "close active", "close this"]):
        return {"intent": "close_app", "parameters": {}, "spoken_response": "Dismissing the active window, sir."}
    if any(w in t for w in ["maximize", "full screen"]):
        return {"intent": "window_management", "parameters": {"action": "maximize"}, "spoken_response": "Expanding to full screen, sir."}
    if any(w in t for w in ["minimize", "hide window"]):
        return {"intent": "window_management", "parameters": {"action": "minimize"}, "spoken_response": "Tucking that window away."}
    if any(w in t for w in ["show desktop", "minimize all"]):
        return {"intent": "show_desktop", "parameters": {}, "spoken_response": "Clearing the deck. Desktop displayed, sir."}

    # 5. Lock & Power
    if "lock" in t and any(w in t for w in ["pc", "computer", "laptop", "screen", "workstation"]):
        return {"intent": "lock_pc", "parameters": {}, "spoken_response": "Locking workstation protocols. Security engaged, sir."}
    if "sleep" in t and any(w in t for w in ["pc", "computer", "laptop", "system"]):
        return {"intent": "power_control", "parameters": {"action": "sleep"}, "spoken_response": "Entering low power standby mode. See you shortly, sir."}

    # 6. Screenshot
    if "screenshot" in t or ("capture" in t and "screen" in t):
        return {"intent": "screenshot", "parameters": {}, "spoken_response": "Capturing current display. Snapshot saved, sir."}

    # 7. Media & YouTube
    if t.startswith("play "):
        song = t[5:].strip()
        replies = [f"Queueing up {song} on YouTube right now, sir. Enjoy.", f"Playing {song} on YouTube for you, sir.", f"Searching and playing {song}."]
        return {"intent": "play_youtube", "parameters": {"query": song}, "spoken_response": random.choice(replies)}
    if "pause" in t or "resume" in t or "play music" in t:
        return {"intent": "media_control", "parameters": {"action": "play_pause"}, "spoken_response": "Toggling media playback, sir."}

    # 8. Web Search
    if t.startswith("search ") or t.startswith("google "):
        q = re.sub(r'^(search for|search|google for|google)\s+', '', t).strip()
        return {"intent": "search_web", "parameters": {"query": q, "platform": "google"}, "spoken_response": f"Looking into '{q}' on the web right away, sir."}

    # Default fallback
    replies = [
        f"I hear you, sir: '{text}'. How would you like me to handle that?",
        f"Understood, sir: '{text}'. What are your orders?",
        f"Right with you, sir: '{text}'. How can we tackle this?"
    ]
    return {
        "intent": "chat",
        "parameters": {"query": text},
        "spoken_response": random.choice(replies)
    }

def process_input(text):
    global current_key_index
    keys = config.GEMINI_API_KEYS
    if not keys:
        return parse_command_local(text)

    history = memory_manager.get_history()
    contents = []
    # Send rolling conversation history for true conversational memory
    for turn in history[-14:]:
        contents.append({
            "role": turn["role"],
            "parts": [{"text": turn["text"][:1200]}]
        })
    contents.append({
        "role": "user",
        "parts": [{"text": text}]
    })

    payload = {
        "systemInstruction": {"parts": [{"text": generate_system_prompt()}]},
        "contents": contents,
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.8,
            "topP": 0.95
        }
    }

    num_keys = len(keys)
    attempts = 0
    while attempts < num_keys:
        active_key = keys[current_key_index]
        model = config.GEMINI_MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={active_key}"

        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
            if resp.status_code == 200:
                raw_json = resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                s = raw_json.find('{')
                e = raw_json.rfind('}')
                if s != -1 and e != -1:
                    raw_json = raw_json[s:e+1]
                parsed = json.loads(raw_json)
                
                # Check memory update
                mem = parsed.get("memory_update")
                if mem and isinstance(mem, dict) and mem.get("action") == "add" and mem.get("content"):
                    memory_manager.add_memory(mem.get("category", "facts"), mem.get("content"))
                    
                return parsed
            elif resp.status_code == 429:
                print(f"[AI Core] Key {current_key_index + 1} rate limited. Rotating key...")
                current_key_index = (current_key_index + 1) % num_keys
                attempts += 1
            else:
                print(f"[AI Core] Gemini API Error {resp.status_code}: {resp.text[:150]}")
                break
        except Exception as e:
            print(f"[AI Core] Request error: {e}")
            break

    # If API failed, return offline parsed result
    local = parse_command_local(text)
    return local

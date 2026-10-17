import requests
from bs4 import BeautifulSoup
import urllib.parse
import config

def get_weather(city=""):
    try:
        loc = urllib.parse.quote(city) if city else ""
        url = f"https://wttr.in/{loc}?format=%C+%t"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception:
        pass
    return "Weather data unavailable."

def search_duckduckgo(query):
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        for body in soup.select('.result__body')[:3]:
            a = body.select_one('.result__a')
            snip = body.select_one('.result__snippet')
            if a and snip:
                results.append(f"{a.text.strip()}: {snip.text.strip()}")
        return "\n".join(results)
    except Exception:
        return ""

def synthesize_research(query):
    snippets = search_duckduckgo(query)
    if not snippets:
        return f"I couldn't retrieve web research results for '{query}'."

    keys = config.GEMINI_API_KEYS
    if not keys:
        return f"Found research data: {snippets[:200]}..."

    prompt = f"""Synthesize a crisp, 2-sentence spoken answer to: "{query}"\n\nWeb Data:\n{snippets}"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent?key={keys[0]}"
    try:
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception:
        pass
    return f"According to web research: {snippets[:200]}..."

import webbrowser
import urllib.parse

def search_web(query):
    """Searches Google for the given query"""
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    webbrowser.open(url)

def open_website(url):
    """Opens a specific URL"""
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)

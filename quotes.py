import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTES_FILE = os.path.join(BASE_DIR, "quotes.json")

def load_quotes():
    if os.path.exists(QUOTES_FILE):
        try:
            with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading quotes from {QUOTES_FILE}: {e}")
            return {}
    return {}

# Load quotes on module import
QUOTES = load_quotes()

# Fallback defaults if file is missing or empty (Optional, but good for safety)
if not QUOTES:
    QUOTES = {
        "Duke Nukem Offensive": ["Hail to the king, baby!"],
        "Duke Nukem Defensive": ["Damn, those alien bastards are gonna pay for shooting up my ride."],
        "Evil Dead": ["Groovy."],
        "Terminator": ["I'll be back."],
        "Gattuso": ["Sometimes maybe good, sometimes maybe shit."],
        "ASCII_Toxic": [":-)"],
        "Direct Insult": ["Hey {name}, your aim is so bad even auto-aim gave up on you."]
    }








import keyboard
import time
import random
import threading
from quotes import QUOTES

class QuoteProvider:
    def __init__(self, quotes_list):
        # Remove duplicate quotes while preserving order
        self.all_quotes = list(dict.fromkeys(quotes_list)) if quotes_list else []
        self.remaining_quotes = []
        self.is_random = False
        self.last_quote = None
        self._refill()

    def set_random(self, is_random):
        self.is_random = is_random
        self._refill()

    def _refill(self):
        self.remaining_quotes = list(self.all_quotes)
        if self.is_random:
            random.shuffle(self.remaining_quotes)
            # Avoid consecutive repetition across refills
            if len(self.remaining_quotes) > 1 and self.remaining_quotes[0] == self.last_quote:
                # Find a different quote to swap with the first one
                for i in range(1, len(self.remaining_quotes)):
                    if self.remaining_quotes[i] != self.last_quote:
                        self.remaining_quotes[0], self.remaining_quotes[i] = self.remaining_quotes[i], self.remaining_quotes[0]
                        break
        
    def get_next(self):
        if not self.remaining_quotes:
            self._refill()
        if not self.remaining_quotes:
            return ""
        quote = self.remaining_quotes.pop(0)
        self.last_quote = quote
        return quote

class AutoTyper:
    def __init__(self):
        # Bindings: { 'key_name': callback_function }
        self.bindings = {}
        self.delay = 0.01
        self.is_running = False
        self.listening_thread = None
        self.stop_event = threading.Event()
        
        # Store mode settings: { category: is_random }
        self.mode_settings = {}
        
        # Quote providers for each category
        self.quote_providers = {
            category: QuoteProvider(q_list) 
            for category, q_list in QUOTES.items()
        }
        
        self.custom_message = ""
        self.target_nickname = ""
        self.click_after_typing = True

    def set_target_nickname(self, nickname):
        self.target_nickname = nickname or ""

    def set_mode(self, category, is_random):
        self.mode_settings[category] = is_random
        if category in self.quote_providers:
            self.quote_providers[category].set_random(is_random)

    def set_custom_message(self, message):
        self.custom_message = message

    def set_delay(self, delay):
        try:
            self.delay = float(delay)
        except ValueError:
            self.delay = 0.01

    def add_binding(self, key, action_type, category=None):
        """
        key: The key to bind (e.g., 'f9')
        action_type: 'custom' or 'quote'
        category: 'Duke Nukem' or 'Evil Dead' (if action_type is 'quote')
        """
        if not key:
            return

        # Remove existing binding for this key if any
        if key in self.bindings:
            del self.bindings[key]

        if action_type == 'custom':
            self.bindings[key] = self._type_custom
        elif action_type == 'quote' and category in self.quote_providers:
            # Create a closure to capture the category
            self.bindings[key] = lambda: self._type_quote(category)

    def clear_bindings(self):
        self.bindings.clear()

    def start(self):
        if not self.bindings:
            return False
        
        if self.is_running:
            return True

        # Re-initialize providers to ensure we have the latest quotes and fresh state
        # But preserve mode settings!
        self.quote_providers = {
            category: QuoteProvider(q_list) 
            for category, q_list in QUOTES.items()
        }
        
        # Apply saved modes
        for category, is_random in self.mode_settings.items():
            if category in self.quote_providers:
                self.quote_providers[category].set_random(is_random)

        self.is_running = True
        self.stop_event.clear()
        self.listening_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listening_thread.start()
        return True

    def stop(self):
        self.is_running = False
        self.stop_event.set()
        self._unhook_all()

    def _unhook_all(self):
        for key in self.bindings:
            try:
                keyboard.remove_hotkey(key)
            except:
                pass

    def _listen_loop(self):
        try:
            # Register all hotkeys
            for key, callback in self.bindings.items():
                # We wrap the callback to ensure it runs on the main logic
                keyboard.add_hotkey(key, callback)
            
            self.stop_event.wait() # Block until stopped
        except Exception as e:
            print(f"Error in listener: {e}")
        finally:
            self._unhook_all()

    def _type_custom(self):
        self._type_text(self.custom_message)

    def _type_quote(self, category):
        provider = self.quote_providers.get(category)
        if provider:
            text = provider.get_next()
            self._type_text(text)

    def _type_text(self, text):
        if not self.is_running or not text:
            return

        # Replace target nickname placeholders
        name = self.target_nickname.strip() if (self.target_nickname and self.target_nickname.strip()) else "bro"
        for ph in ["{name}", "{nickname}", "{nick}", "{target}", "{player}", "<nick>", "<name>", "<target>", "<player>", "{NAME}", "{NICKNAME}", "{NICK}", "{TARGET}", "{PLAYER}", "<NICK>", "<NAME>"]:
            if ph in text:
                text = text.replace(ph, name)

        chunks = [text[i:i+70] for i in range(0, len(text), 70)]

        for chunk in chunks:
            if not self.is_running:
                break
            
            # Open chat
            keyboard.send('enter')
            time.sleep(self.delay)
            
            # Type message
            keyboard.write(chunk, delay=self.delay)
            time.sleep(self.delay)
            
            # Send message
            keyboard.send('enter')
            time.sleep(self.delay)

        if self.click_after_typing:
            self._perform_right_click()

    def detect_key(self):
        key = keyboard.read_event(suppress=True)
        if key.event_type == keyboard.KEY_DOWN:
            return key.name
        return None

    def set_click_after_typing(self, enabled):
        self.click_after_typing = enabled

    def _perform_right_click(self):
        try:
            import ctypes
            MOUSEEVENTF_RIGHTDOWN = 0x0008
            MOUSEEVENTF_RIGHTUP = 0x0010
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        except Exception as e:
            print(f"Error performing right click: {e}")

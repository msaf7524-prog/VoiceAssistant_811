import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "assistant_name": "811",
    "provider": "groq",
    "api_key": "",
    "language": "ar",
    "voice_enabled": True,
    "auto_start": False,
    "wake_word": "811",
    "bluetooth_enabled": True
}


class SettingsManager:

    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.settings.update(json.load(f))
            except:
                self.save()
        else:
            self.save()

    def save(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                self.settings,
                f,
                indent=4,
                ensure_ascii=False
            )

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value
        self.save()

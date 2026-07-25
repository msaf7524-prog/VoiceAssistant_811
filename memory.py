import json
import os

MEMORY_FILE = "memory.json"


class MemoryManager:

    def __init__(self):
        self.memory = {}
        self.load()

    def load(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
            except:
                self.memory = {}

    def save(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(
                self.memory,
                f,
                indent=4,
                ensure_ascii=False
            )

    def remember(self, key, value):
        self.memory[key] = value
        self.save()

    def recall(self, key, default=None):
        return self.memory.get(key, default)

    def forget(self, key):
        if key in self.memory:
            del self.memory[key]
            self.save()

    def clear(self):
        self.memory = {}
        self.save()

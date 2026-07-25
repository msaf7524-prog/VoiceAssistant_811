class WakeWordEngine:

    def __init__(self, wake_word="811"):
        self.wake_word = wake_word.lower()

    def detected(self, text):

        if not text:
            return False

        text = text.lower().strip()

        return self.wake_word in text

    def set_wake_word(self, word):
        self.wake_word = word.lower()

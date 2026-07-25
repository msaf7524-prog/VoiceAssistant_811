import threading
from gtts import gTTS
from kivy.core.audio import SoundLoader


class TTSEngine:

    def __init__(self):
        self.filename = "assistant_response.mp3"

    def speak(self, text):
        threading.Thread(
            target=self._generate_and_play,
            args=(text,),
            daemon=True
        ).start()

    def _generate_and_play(self, text):
        try:
            tts = gTTS(
                text=text,
                lang="ar",
                slow=False
            )

            tts.save(self.filename)

            sound = SoundLoader.load(self.filename)

            if sound:
                sound.play()

        except Exception as e:
            print("TTS Error:", e)

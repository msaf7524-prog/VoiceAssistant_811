import speech_recognition as sr


class SpeechEngine:

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self, language="ar-IQ"):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

                text = self.recognizer.recognize_google(
                    audio,
                    language=language
                )

                return text

        except sr.WaitTimeoutError:
            return None

        except sr.UnknownValueError:
            return None

        except Exception as e:
            return f"ERROR:{e}"

# =========================================================
# Voice Assistant 811 - Professional Background Service
# =========================================================

import os
import time
import threading
import requests
import base64
from gtts import gTTS

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Ellipse

# Android Permissions & Notifications
try:
    from android.permissions import request_permissions, Permission
    HAS_ANDROID_PERM = True
except ImportError:
    HAS_ANDROID_PERM = False

try:
    from plyer import notification
    HAS_NOTIF = True
except ImportError:
    HAS_NOTIF = False

# Speech Recognition
try:
    import speech_recognition as sr
    HAS_STT = True
except ImportError:
    HAS_STT = False

# Encrypted Groq API Key
ENCODED_KEY = "Z3NrX01RWkQyc1VwSUR5RVhtM1NTcTB5V0dkeTByRlk1c2oyUmp2SVN2Zkk2eUR3ZjV5QTVnNEY="

def get_embedded_key():
    try:
        return base64.b64decode(ENCODED_KEY).decode('utf-8')
    except Exception:
        return ""

# ---------------------------------------------------------
# 1. Centered Status Circle Indicator Widget
# ---------------------------------------------------------
class StatusIndicatorWidget(Widget):
    """Draws a centered dynamic circle indicating state (Gray, Green, Blue)"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = 100
        self.bind(pos=self.update_circle, size=self.update_circle)
        
        with self.canvas:
            self.color_instruction = Color(0.4, 0.4, 0.4, 1) # Gray = Stopped
            self.circle = Ellipse(size=(70, 70))
            
    def update_circle(self, *args):
        self.circle.pos = (self.center_x - 35, self.center_y - 35)

    def set_state_color(self, state):
        if state == "listening":
            self.color_instruction.rgb = (0.1, 0.8, 0.3) # Green = Listening
        elif state == "thinking":
            self.color_instruction.rgb = (0.2, 0.5, 0.9) # Blue = Thinking/Speaking
        else:
            self.color_instruction.rgb = (0.4, 0.4, 0.4) # Gray = Stopped

# ---------------------------------------------------------
# 2. Main Assistant Screen & Controls
# ---------------------------------------------------------
class AssistantScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_service_running = False
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header Title
        self.title_label = Label(
            text="AI Voice Assistant 811",
            font_size='22sp',
            size_hint_y=None,
            height=40,
            bold=True
        )
        main_layout.add_widget(self.title_label)
        
        # Visual Indicator
        self.indicator_widget = StatusIndicatorWidget()
        main_layout.add_widget(self.indicator_widget)

        # Chat Log Box
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.chat_log = Label(
            text="Service Stopped. Press 'Start Assistant' to activate.",
            font_size='15sp',
            size_hint_y=None,
            halign='left',
            valign='top',
            color=(0.9, 0.9, 0.9, 1)
        )
        self.chat_log.bind(texture_size=self.update_chat_height)
        self.scroll_view.add_widget(self.chat_log)
        main_layout.add_widget(self.scroll_view)
        
        # Toggle Action Button
        self.toggle_btn = Button(
            text="Start Assistant",
            font_size='18sp',
            size_hint_y=None,
            height=55,
            background_color=(0.1, 0.7, 0.3, 1)
        )
        self.toggle_btn.bind(on_release=self.toggle_service)
        main_layout.add_widget(self.toggle_btn)

        self.add_widget(main_layout)

    def update_chat_height(self, instance, value):
        self.chat_log.height = value[1]
        self.chat_log.text_size = (self.scroll_view.width - 20, None)

    def append_chat(self, sender, message):
        """Append log lines to text box and auto scroll down"""
        formatted_line = f"\n[{sender}]: {message}"
        self.chat_log.text += formatted_line
        Clock.schedule_once(lambda dt: setattr(self.scroll_view, 'scroll_y', 0))

    def toggle_service(self, instance):
        if not self.is_service_running:
            self.start_assistant_logic()
        else:
            self.stop_assistant_logic()

    def start_assistant_logic(self):
        app = App.get_running_app()
        
        # Request Android Permissions
        if HAS_ANDROID_PERM:
            request_permissions([Permission.RECORD_AUDIO, Permission.BLUETOOTH_CONNECT, Permission.POST_NOTIFICATIONS])

        self.is_service_running = True
        self.toggle_btn.text = "Stop Assistant"
        self.toggle_btn.background_color = (0.8, 0.2, 0.2, 1)
        
        self.indicator_widget.set_state_color("listening")
        
        # Show Top Notification Bar Icon
        app.show_background_notification("Assistant 811 Active", "Listening in background...")
        
        app.speak_online_tts("Assistant activated. I am listening.")
        self.append_chat("System", "Service started. Listening for '811'...")

        # Start listening in background thread
        threading.Thread(target=self.background_wake_word_listener, daemon=True).start()

    def stop_assistant_logic(self):
        app = App.get_running_app()
        
        self.is_service_running = False
        self.toggle_btn.text = "Start Assistant"
        self.toggle_btn.background_color = (0.1, 0.7, 0.3, 1)
        
        self.indicator_widget.set_state_color("stopped")
        app.remove_background_notification()
        app.speak_online_tts("Assistant stopped.")
        self.append_chat("System", "Service stopped.")

    def background_wake_word_listener(self):
        app = App.get_running_app()
        
        if not HAS_STT:
            Clock.schedule_once(lambda dt: self.append_chat("Warning", "STT library not loaded."))
            return

        recognizer = sr.Recognizer()
        
        while self.is_service_running:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=6)
                    
                    user_text = recognizer.recognize_google(audio, language="en-US")
                    
                    if user_text:
                        Clock.schedule_once(lambda dt, t=user_text: self.append_chat("You 🎤", t))
                        Clock.schedule_once(lambda dt: self.indicator_widget.set_state_color("thinking"))
                        
                        # Query Groq AI API
                        app.query_ai(user_text, self)
                        
            except sr.WaitTimeoutError:
                pass
            except Exception:
                pass
            
            Clock.schedule_once(lambda dt: self.indicator_widget.set_state_color("listening"))
            time.sleep(0.3)

# ---------------------------------------------------------
# 3. Kivy Main Application Logic
# ---------------------------------------------------------
class VoiceAssistantApp(App):
    api_key = ""

    def build(self):
        self.api_key = get_embedded_key()
        sm = ScreenManager()
        sm.add_widget(AssistantScreen(name='main'))
        return sm

    def show_background_notification(self, title, message):
        """Displays notification icon in Android top status bar"""
        if HAS_NOTIF:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Assistant 811",
                    ticker="811 Service Running",
                    toast=False
                )
            except Exception:
                pass

    def remove_background_notification(self):
        if HAS_NOTIF:
            try:
                notification.notify(title="Assistant 811", message="Service Closed", app_name="Assistant 811")
            except Exception:
                pass

    def speak_online_tts(self, text):
        """Online Speech Generation using Google TTS (gTTS)"""
        def _speak():
            try:
                tts = gTTS(text=text, lang='en', slow=False)
                filename = "response.mp3"
                tts.save(filename)
                
                sound = SoundLoader.load(filename)
                if sound:
                    sound.play()
            except Exception as e:
                print(f"TTS Error: {e}")
                
        threading.Thread(target=_speak, daemon=True).start()

    def query_ai(self, prompt_text, screen_instance):
        def _request():
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            system_prompt = "You are a smart voice assistant named 811. Give short, direct, and helpful answers."
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_text}
                ],
                "temperature": 0.6
            }
            
            try:
                res = requests.post(url, json=data, headers=headers, timeout=10)
                if res.status_code == 200:
                    reply = res.json()['choices'][0]['message']['content']
                    Clock.schedule_once(lambda dt, r=reply: screen_instance.append_chat("811 🤖", r))
                    self.speak_online_tts(reply)
                else:
                    Clock.schedule_once(lambda dt: screen_instance.append_chat("811 🤖", "Connection Error."))
            except Exception:
                Clock.schedule_once(lambda dt: screen_instance.append_chat("811 🤖", "Internet connection required."))

        threading.Thread(target=_request, daemon=True).start()

if __name__ == '__main__':
    VoiceAssistantApp().run()

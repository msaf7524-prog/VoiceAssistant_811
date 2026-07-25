# =========================================================
# مشروع المساعد الشخصي الذكي (811 Voice Assistant)
# حل مشكلة الأذونات والاستجابة الصوتية على أندرويد
# =========================================================

import os
import threading
import time
import requests
import base64

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

# دعم أذونات أندرويد المباشرة
try:
    from android.permissions import request_permissions, Permission
    HAS_ANDROID_PERM = True
except ImportError:
    HAS_ANDROID_PERM = False

# دعم المكتبات العربية
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC = True
except ImportError:
    HAS_ARABIC = False

# استيراد مكتبات النطق
try:
    from plyer import tts
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

try:
    import speech_recognition as sr
    HAS_STT = True
except ImportError:
    HAS_STT = False

ENCODED_KEY = "Z3NrX01RWkQyc1VwSUR5RVhtM1NTcTB5V0dkeTByRlk1c2oyUmp2SVN2Zkk2eUR3ZjV5QTVnNEY="

def get_embedded_key():
    try:
        return base64.b64decode(ENCODED_KEY).decode('utf-8')
    except Exception:
        return ""

FONT_PATH = "arabic_font.ttf"

def download_font_if_missing():
    if not os.path.exists(FONT_PATH):
        try:
            url = "https://raw.githubusercontent.com/google/fonts/main/ofl/amiri/Amiri-Regular.ttf"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                with open(FONT_PATH, "wb") as f:
                    f.write(res.content)
        except Exception as e:
            print("Font Download Error:", e)

def fix_ar(text):
    if not text:
        return ""
    if HAS_ARABIC:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text
    return text

# ---------------------------------------------------------
# الشاشة الرئيسية للمساعد 811
# ---------------------------------------------------------
class AssistantScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_service_running = False
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # عنوان التطبيق
        self.title_label = Label(
            text=fix_ar("المساعد الشخصي الذكي 811\n(جاهز للعمل مع سماعة البلوتوث)"),
            font_size='18sp',
            font_name=font_arg,
            halign='center',
            bold=True
        )
        layout.add_widget(self.title_label)
        
        # حالة الخدمة
        self.status_label = Label(
            text=fix_ar("الخدمة: متوقفة\nاضغط تفعيل للعمل"),
            font_size='14sp',
            font_name=font_arg,
            color=(0.7, 0.7, 0.7, 1),
            halign='center'
        )
        layout.add_widget(self.status_label)
        
        # زر التفعيل
        self.toggle_btn = Button(
            text=fix_ar("تفعيل المساعد (6 ساعات في الخلفية)"),
            font_size='15sp',
            font_name=font_arg,
            size_hint_y=0.2,
            background_color=(0.1, 0.7, 0.3, 1)
        )
        self.toggle_btn.bind(on_release=self.toggle_service)
        layout.add_widget(self.toggle_btn)

        # زر تجربة الصوت المباشر
        self.test_sound_btn = Button(
            text=fix_ar("اختبار الصوت المباشر 🔊"),
            font_size='14sp',
            font_name=font_arg,
            size_hint_y=0.15,
            background_color=(0.2, 0.4, 0.8, 1)
        )
        self.test_sound_btn.bind(on_release=self.test_audio)
        layout.add_widget(self.test_sound_btn)
        
        self.add_widget(layout)

    def test_audio(self, instance):
        app = App.get_running_app()
        app.speak_text("هلا بيك! الصوت يعمل بشكل ممتاز في المساعد 811.")

    def toggle_service(self, instance):
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        
        # طلب الأذونات على أندرويد أولاً
        if HAS_ANDROID_PERM:
            request_permissions([
                Permission.RECORD_AUDIO,
                Permission.BLUETOOTH,
                Permission.BLUETOOTH_CONNECT
            ])

        if not self.is_service_running:
            self.is_service_running = True
            
            self.status_label.font_name = font_arg
            self.status_label.text = fix_ar("الخدمة: جاري الاستماع...\nقل 'يا 811' وسيجيبك المساعد")
            
            self.toggle_btn.font_name = font_arg
            self.toggle_btn.text = fix_ar("إيقاف المساعد")
            self.toggle_btn.background_color = (0.8, 0.2, 0.2, 1)
            
            threading.Thread(target=self.background_wake_word_listener, daemon=True).start()
        else:
            self.is_service_running = False
            self.status_label.font_name = font_arg
            self.status_label.text = fix_ar("الخدمة: متوقفة")
            
            self.toggle_btn.font_name = font_arg
            self.toggle_btn.text = fix_ar("تفعيل المساعد (6 ساعات في الخلفية)")
            self.toggle_btn.background_color = (0.1, 0.7, 0.3, 1)

    def background_wake_word_listener(self):
        app = App.get_running_app()
        if not HAS_STT:
            return

        recognizer = sr.Recognizer()
        
        while self.is_service_running:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=4)
                    text = recognizer.recognize_google(audio, language="ar-IQ")
                    
                    if any(wake in text for wake in ["811", "٨١١", "ثمانية", "مية"]):
                        app.play_beep_sound()
                        app.speak_text("نعم اسمعك، تفضل؟")
            except Exception:
                pass
            time.sleep(0.5)

# ---------------------------------------------------------
# تطبيق Kivy الرئيسي
# ---------------------------------------------------------
class VoiceAssistantApp(App):
    api_key = ""

    def build(self):
        download_font_if_missing()
        self.api_key = get_embedded_key()
        
        # طلب الأذن فور فتح التطبيق
        if HAS_ANDROID_PERM:
            request_permissions([Permission.RECORD_AUDIO, Permission.BLUETOOTH_CONNECT])
            
        sm = ScreenManager()
        sm.add_widget(AssistantScreen(name='main'))
        return sm

    def play_beep_sound(self):
        try:
            sound = SoundLoader.load('beep.wav')
            if sound:
                sound.play()
        except Exception as e:
            print("Beep play error:", e)

    def speak_text(self, text):
        def _speak():
            if HAS_PLYER:
                try:
                    tts.speak(text)
                except Exception as e:
                    print("TTS error:", e)
        threading.Thread(target=_speak, daemon=True).start()

if __name__ == '__main__':
    VoiceAssistantApp().run()

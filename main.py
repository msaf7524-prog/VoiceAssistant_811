# =========================================================
# مشروع المساعد الشخصي الذكي 811 (Voice & Text Chat)
# الإصدار الاحترافي: محادثة صوتية ونصية متكاملة
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
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Ellipse
from kivy.storage.jsonstore import JsonStore

# أذونات أندرويد
try:
    from android.permissions import request_permissions, Permission
    HAS_ANDROID_PERM = True
except ImportError:
    HAS_ANDROID_PERM = False

# دعم النص العربي
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC = True
except ImportError:
    HAS_ARABIC = False

# مكتبة النطق الصوتي
try:
    from plyer import tts
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

# مكتبة التعرف الصوتي
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
# ودجت الدائرة الضوئية التفاعلية المتمركزة
# ---------------------------------------------------------
class StatusIndicatorWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = 100
        self.bind(pos=self.update_circle, size=self.update_circle)
        
        with self.canvas:
            self.color_instruction = Color(0.4, 0.4, 0.4, 1) # رمادي متوقف
            self.circle = Ellipse(size=(70, 70))
            
    def update_circle(self, *args):
        # توسيط الدائرة دائماً في منتصف الشاشة عرضياً
        self.circle.pos = (self.center_x - 35, self.center_y - 35)

    def set_state_color(self, state):
        if state == "listening":
            self.color_instruction.rgb = (0.1, 0.8, 0.3) # أخضر - يستمع
        elif state == "thinking":
            self.color_instruction.rgb = (0.2, 0.5, 0.9) # أزرق - يفكر/يرد
        else:
            self.color_instruction.rgb = (0.4, 0.4, 0.4) # رمادي - متوقف

# ---------------------------------------------------------
# الشاشة الرئيسية واختبار الدردشة الكتابية والصوتية
# ---------------------------------------------------------
class AssistantScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_service_running = False
        self.store = JsonStore('assistant_state.json')
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # 1. العنوان
        self.title_label = Label(
            text=fix_ar("المساعد الذكي 811"),
            font_size='20sp',
            font_name=font_arg,
            size_hint_y=None,
            height=35,
            bold=True
        )
        main_layout.add_widget(self.title_label)
        
        # 2. المؤشر البصري الدائري
        self.indicator_widget = StatusIndicatorWidget()
        main_layout.add_widget(self.indicator_widget)

        # 3. منطقة صندوق الدردشة المكتوبة (Chat Log)
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.chat_log = Label(
            text=fix_ar("مرحباً بك! اضغط تفعيل وابدأ الكلام وسأكتب وأجيبك صوتياً وخطياً..."),
            font_size='15sp',
            font_name=font_arg,
            size_hint_y=None,
            halign='right',
            valign='top',
            color=(0.9, 0.9, 0.9, 1)
        )
        self.chat_log.bind(texture_size=self.update_chat_height)
        self.scroll_view.add_widget(self.chat_log)
        main_layout.add_widget(self.scroll_view)
        
        # 4. أزرار التحكم
        self.toggle_btn = Button(
            text=fix_ar("تفعيل المساعد"),
            font_size='16sp',
            font_name=font_arg,
            size_hint_y=None,
            height=50,
            background_color=(0.1, 0.7, 0.3, 1)
        )
        self.toggle_btn.bind(on_release=self.toggle_service)
        main_layout.add_widget(self.toggle_btn)

        self.add_widget(main_layout)

    def update_chat_height(self, instance, value):
        self.chat_log.height = value[1]
        self.chat_log.text_size = (self.scroll_view.width - 20, None)

    def append_chat(self, sender, message):
        """إضافة نص جديد لصندوق المحادثة المكتوبة"""
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        formatted_line = f"\n[{sender}]: {message}"
        new_text = self.chat_log.text + fix_ar(formatted_line)
        self.chat_log.text = new_text
        # التمرير التلقائي لأسفل المحادثة
        Clock.schedule_once(lambda dt: setattr(self.scroll_view, 'scroll_y', 0))

    def toggle_service(self, instance):
        if not self.is_service_running:
            self.start_assistant_logic()
        else:
            self.stop_assistant_logic()

    def start_assistant_logic(self):
        app = App.get_running_app()
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        
        if HAS_ANDROID_PERM:
            request_permissions([Permission.RECORD_AUDIO, Permission.BLUETOOTH_CONNECT])

        self.is_service_running = True
        self.toggle_btn.font_name = font_arg
        self.toggle_btn.text = fix_ar("إيقاف المساعد")
        self.toggle_btn.background_color = (0.8, 0.2, 0.2, 1)
        
        self.indicator_widget.set_state_color("listening")
        app.play_beep_sound()
        app.speak_text("تم التفعيل، أنا أستمع إليك.")
        self.append_chat("النظام", "تم تفعيل الاستماع المباشر...")

        threading.Thread(target=self.background_wake_word_listener, daemon=True).start()

    def stop_assistant_logic(self):
        app = App.get_running_app()
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        
        self.is_service_running = False
        self.toggle_btn.font_name = font_arg
        self.toggle_btn.text = fix_ar("تفعيل المساعد")
        self.toggle_btn.background_color = (0.1, 0.7, 0.3, 1)
        
        self.indicator_widget.set_state_color("stopped")
        app.speak_text("تم الإيقاف.")
        self.append_chat("النظام", "تم إيقاف الخدمة.")

    def background_wake_word_listener(self):
        app = App.get_running_app()
        
        if not HAS_STT:
            Clock.schedule_once(lambda dt: self.append_chat("تنبيه", "مكتبة التعرف الصوتي جاري إعدادها..."))
            return

        recognizer = sr.Recognizer()
        
        while self.is_service_running:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
                    
                    # تحويل صوتك إلى نص
                    user_text = recognizer.recognize_google(audio, language="ar-IQ")
                    
                    if user_text:
                        # عرض ما قمت بنطقه على الشاشة فوراً
                        Clock.schedule_once(lambda dt, t=user_text: self.append_chat("أنت 🎤", t))
                        Clock.schedule_once(lambda dt: self.indicator_widget.set_state_color("thinking"))
                        
                        # إرسال النص للذكاء الاصطناعي
                        app.query_ai_iraqi(user_text, self)
                        
            except sr.WaitTimeoutError:
                pass
            except Exception:
                pass
            
            Clock.schedule_once(lambda dt: self.indicator_widget.set_state_color("listening"))
            time.sleep(0.4)

# ---------------------------------------------------------
# تطبيق Kivy
# ---------------------------------------------------------
class VoiceAssistantApp(App):
    api_key = ""

    def build(self):
        self.api_key = get_embedded_key()
        sm = ScreenManager()
        sm.add_widget(AssistantScreen(name='main'))
        return sm

    def play_beep_sound(self):
        try:
            sound = SoundLoader.load('beep.wav')
            if sound: sound.play()
        except Exception: pass

    def speak_text(self, text):
        def _speak():
            if HAS_PLYER:
                try: tts.speak(text)
                except Exception: pass
        threading.Thread(target=_speak, daemon=True).start()

    def query_ai_iraqi(self, prompt_text, screen_instance):
        def _request():
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            system_prompt = "أنت مساعد شخصي ذكي اسمك 811. اجب بلهجة عراقية عامية وبسيطة ومباشرة."
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
                    # عرض إجابة الذكاء الاصطناعي كتابة ونطقها صوتياً
                    Clock.schedule_once(lambda dt, r=reply: screen_instance.append_chat("811 🤖", r))
                    self.speak_text(reply)
                else:
                    Clock.schedule_once(lambda dt: screen_instance.append_chat("811 🤖", "حصل خطأ في الاتصال."))
            except Exception:
                Clock.schedule_once(lambda dt: screen_instance.append_chat("811 🤖", "يرجى التأكد من الاتصال بالإنترنت."))

        threading.Thread(target=_request, daemon=True).start()

if __name__ == '__main__':
    VoiceAssistantApp().run()

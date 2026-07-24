# =========================================================
# مشروع المساعد الشخصي الذكي (VoiceAssistant_811)
# ملف main.py المتوافق كاملاً مع ملفات buildozer.spec و build.yml
# =========================================================

import os
import threading
import traceback
import requests

from kivy.app import App
from kivy.utils import platform
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse

# ---------------------------------------------------------
# الجزء الأول: معالجة خطوط النصوص العربية وتشكيلها
# ---------------------------------------------------------
FONT_PATH = "arabic_font.ttf"

def download_arabic_font():
    """تحميل خط عربي يدعم التشكيل والعرض الصحيح في Kivy"""
    if not os.path.exists(FONT_PATH):
        try:
            url = "https://raw.githubusercontent.com/google/fonts/main/ofl/amiri/Amiri-Regular.ttf"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                with open(FONT_PATH, "wb") as f:
                    f.write(res.content)
        except Exception as e:
            print(f"Font Download Error: {e}")

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC = True
except ImportError:
    HAS_ARABIC = False

def fix_ar(text):
    """دالة تحسين وتنسيق اتجاه النص العربي"""
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
# الجزء الثاني: إعدادات مكتبات أندرويد الصوتية (Android Native)
# ---------------------------------------------------------
if platform == "android":
    try:
        from jnius import autoclass
        from android.permissions import request_permissions, Permission
        
        # طلب الأذونات المطلوبة المحددة في buildozer.spec
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.BLUETOOTH,
            Permission.BLUETOOTH_CONNECT,
            Permission.MODIFY_AUDIO_SETTINGS
        ])
        
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
        Locale = autoclass("java.util.Locale")
    except Exception as e:
        print(f"Android Native Error: {e}")

# ---------------------------------------------------------
# الجزء الثالث: الشاشة الرئيسية (MainScreen)
# ---------------------------------------------------------
class MainScreen(Screen):
    """الشاشة الرئيسية المجهزة بدائرة التفاعل وسجل الرسائل"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # الشريط العلوي
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        self.status_label = Label(
            text="BT: Connected | Mic: Ready",
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        settings_btn = Button(
            text="Settings",
            size_hint_x=0.35,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        settings_btn.bind(on_release=self.go_to_settings)
        
        top_bar.add_widget(self.status_label)
        top_bar.add_widget(settings_btn)
        main_layout.add_widget(top_bar)
        
        # دائرة التفاعل الملونة
        indicator_layout = BoxLayout(orientation='vertical', size_hint_y=0.45)
        self.state_label = Label(
            text="811 Assistant Active\nWaiting for '811'...",
            font_size='18sp',
            halign='center',
            bold=True
        )
        self.circle_widget = Widget(size_hint=(1, 1))
        self.circle_widget.bind(pos=self.update_circle, size=self.update_circle)
        
        indicator_layout.add_widget(self.state_label)
        indicator_layout.add_widget(self.circle_widget)
        main_layout.add_widget(indicator_layout)
        
        # سجل التفاعل والنصوص
        log_layout = BoxLayout(orientation='vertical', size_hint_y=0.3)
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        self.log_label = Label(
            text=fix_ar("...أنت: «811» بانتظار الأوامر الصوتية"),
            font_size='15sp',
            font_name=font_arg,
            halign='center',
            color=(0.9, 0.9, 0.9, 1)
        )
        log_layout.add_widget(self.log_label)
        main_layout.add_widget(log_layout)
        
        # زر اختبار التفاعل
        self.speak_btn = Button(
            text="Tap to Speak (Test 811)",
            size_hint_y=0.15,
            background_color=(0.1, 0.7, 0.4, 1)
        )
        self.speak_btn.bind(on_release=self.simulate_listening)
        main_layout.add_widget(self.speak_btn)
        
        self.add_widget(main_layout)

    def update_circle(self, *args):
        """رسم دائرة التفاعل المتغيرة"""
        self.circle_widget.canvas.clear()
        with self.circle_widget.canvas:
            Color(0.1, 0.7, 0.9, 0.8)
            center_x = self.circle_widget.center_x
            center_y = self.circle_widget.center_y
            radius = min(self.circle_widget.width, self.circle_widget.height) / 4
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))

    def go_to_settings(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'settings'

    def simulate_listening(self, instance):
        """إرسال سؤال اختباري لـ Gemini"""
        app = App.get_running_app()
        user_query = "هلا 811، شنو الأخبار اليوم؟"
        
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        self.log_label.font_name = font_arg
        self.log_label.text = fix_ar(f"أنت: {user_query}\n\n811: جاري التفكير...")
        
        threading.Thread(target=app.query_gemini, args=(user_query, self.update_ai_response), daemon=True).start()

    def update_ai_response(self, response_text):
        """تحديث نص الاستجابة في الواجهة"""
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        self.log_label.font_name = font_arg
        self.log_label.text = fix_ar(f"811: {response_text}")

# ---------------------------------------------------------
# الجزء الرابع: شاشة الإعدادات (SettingsScreen)
# ---------------------------------------------------------
class SettingsScreen(Screen):
    """شاشة التحكم بـ Gemini API ومستوى الصوت والتحكم بالبلوتوث"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        header = Label(text="Settings", font_size='22sp', bold=True, size_hint_y=0.1)
        layout.add_widget(header)
        
        # أدخال API Key
        layout.add_widget(Label(text="Gemini API Key:", font_size='14sp', size_hint_y=0.08))
        self.api_input = TextInput(
            hint_text="Paste your API key here",
            multiline=False,
            size_hint_y=0.12
        )
        layout.add_widget(self.api_input)
        
        # التحكم بحساسية الميكروفون
        mic_box = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=5)
        self.mic_value_label = Label(text="Mic Sensitivity: 70%", font_size='14sp')
        self.mic_slider = Slider(min=10, max=100, value=70)
        self.mic_slider.bind(value=self.on_mic_change)
        mic_box.add_widget(self.mic_value_label)
        mic_box.add_widget(self.mic_slider)
        layout.add_widget(mic_box)
        
        # تحويل الصوت عبر البلوتوث SCO
        bt_box = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        bt_label = Label(text="Bluetooth SCO Audio:", font_size='14sp')
        self.bt_switch = Switch(active=True)
        bt_box.add_widget(bt_label)
        bt_box.add_widget(self.bt_switch)
        layout.add_widget(bt_box)
        
        # زر العودة والحفظ
        back_btn = Button(
            text="Save and Return",
            size_hint_y=0.15,
            background_color=(0.1, 0.8, 0.4, 1)
        )
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

    def on_mic_change(self, instance, value):
        self.mic_value_label.text = f"Mic Sensitivity: {int(value)}%"

    def go_back(self, instance):
        app = App.get_running_app()
        app.api_key = self.api_input.text.strip()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

# ---------------------------------------------------------
# الجزء الخامس: الكلاس الرئيسي الموحد للتطبيق (VoiceAssistantApp)
# ---------------------------------------------------------
class VoiceAssistantApp(App):
    """الكلاس الموحد الجامع لجميع دوال التطبيق والـ API دون تكرار"""
    api_key = ""
    tts_engine = None

    def build(self):
        # تحميل الخط العربي في الخلفية
        threading.Thread(target=download_arabic_font, daemon=True).start()
        self.init_tts()
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def init_tts(self):
        """تهيئة محرك النطق في نظام أندرويد"""
        if platform == 'android':
            try:
                activity = PythonActivity.mActivity
                self.tts_engine = TextToSpeech(activity, None)
                self.tts_engine.setLanguage(Locale("ar"))
            except Exception as e:
                print(f"TTS Init Error: {e}")

    def speak(self, text):
        """نطق النص الصوتي"""
        if self.tts_engine and platform == 'android':
            try:
                self.tts_engine.speak(text, TextToSpeech.QUEUE_FLUSH, None)
            except Exception as e:
                print(f"TTS Speak Error: {e}")

    def query_gemini(self, prompt, callback):
        """إرسال الاستفسارات لنظام Gemini API ومعالجة الاستجابة"""
        clean_key = self.api_key.strip()
        if not clean_key:
            reply = "احجي أقدر أجاوبك يا عيني، ادخل الإعدادات والزق الـ API Key"
            callback(reply)
            self.speak(reply)
            return

        # رابط نموذج Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={clean_key}"
        headers = {'Content-Type': 'application/json'}
        
        system_instruction = "باسم 811، أجب بأسلوب قصير جداً ومختصر جداً وباللهجة العراقية."
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\nالمستخدم يقول: {prompt}"}
                    ]
                }
            ]
        }
        
        try:
            res = requests.post(url, json=data, headers=headers, timeout=15)
            if res.status_code == 200:
                result = res.json()
                reply = result['candidates'][0]['content']['parts'][0]['text']
            else:
                reply = f"A خطأ في الاتصال ({res.status_code}) تأكد من مفتاح الـ API"
        except Exception as e:
            reply = "مشكلة بالإنترنت، تأكد من الاتصال"
        
        callback(reply)
        self.speak(reply)

# ---------------------------------------------------------
# الجزء السادس: نقطة التشغيل الرئيسية الخالية من الأخطاء
# ---------------------------------------------------------
if __name__ == '__main__':
    try:
        VoiceAssistantApp().run()
    except Exception as e:
        print("Application Crash:")
        print("Error details:", e)
        traceback.print_exc()
        

# =========================================================
# مشروع المساعد الشخصي الذكي (VoiceAssistant_811)
# ملف main.py - النسخة الآمنة المعتمدة للرفع على GitHub
# =========================================================

import os
import threading
import traceback
import requests

from kivy.app import App
from kivy.utils import platform
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
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
# المتغير الإفتراضي آمن (فارغ) لمنع حظر الحفظ على GitHub
# ---------------------------------------------------------
DEFAULT_API_KEY = ""
FONT_PATH = "arabic_font.ttf"

def download_arabic_font():
    """تحميل خط عربي مجاني لتنسيق واجهة التطبيق"""
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
    """معالجة اتجاه النصوص العربية وترتيب الأحرف"""
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
# الواجهة الرئيسية (MainScreen)
# ---------------------------------------------------------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # الشريط العلوي
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        self.status_label = Label(text="BT: Connected | Mic: Ready", font_size='14sp', color=(0.8, 0.8, 0.8, 1))
        settings_btn = Button(text="Settings", size_hint_x=0.35, background_color=(0.2, 0.6, 0.9, 1))
        settings_btn.bind(on_release=self.go_to_settings)
        top_bar.add_widget(self.status_label)
        top_bar.add_widget(settings_btn)
        main_layout.add_widget(top_bar)
        
        # مؤشر الحالة
        indicator_layout = BoxLayout(orientation='vertical', size_hint_y=0.45)
        self.state_label = Label(text="811 Assistant Active\nWaiting for '811'...", font_size='18sp', halign='center', bold=True)
        self.circle_widget = Widget(size_hint=(1, 1))
        self.circle_widget.bind(pos=self.update_circle, size=self.update_circle)
        indicator_layout.add_widget(self.state_label)
        indicator_layout.add_widget(self.circle_widget)
        main_layout.add_widget(indicator_layout)
        
        # عرض ردود المساعد
        log_layout = BoxLayout(orientation='vertical', size_hint_y=0.3)
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        self.log_label = Label(text=fix_ar("...أنت: «811» بانتظار الأوامر الصوتية"), font_size='15sp', font_name=font_arg, halign='center', color=(0.9, 0.9, 0.9, 1))
        log_layout.add_widget(self.log_label)
        main_layout.add_widget(log_layout)
        
        # زر اختبار المساعد الصوتية
        self.speak_btn = Button(text="Tap to Speak (Test 811)", size_hint_y=0.15, background_color=(0.1, 0.7, 0.4, 1))
        self.speak_btn.bind(on_release=self.simulate_listening)
        main_layout.add_widget(self.speak_btn)
        
        self.add_widget(main_layout)

    def update_circle(self, *args):
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
        app = App.get_running_app()
        user_query = "هلا 811، ما هي أحدث الأخبار اليوم؟"
        
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        self.log_label.font_name = font_arg
        self.log_label.text = fix_ar(f"أنت: {user_query}\n\n811: جاري التفكير...")
        
        threading.Thread(target=app.query_gemini, args=(user_query, self.update_ai_response), daemon=True).start()

    def update_ai_response(self, response_text):
        Clock.schedule_once(lambda dt: self._set_log_text(response_text))

    def _set_log_text(self, text):
        font_arg = FONT_PATH if os.path.exists(FONT_PATH) else "Roboto"
        self.log_label.font_name = font_arg
        self.log_label.text = fix_ar(f"811: {text}")

# ---------------------------------------------------------
# شاشة الإعدادات (SettingsScreen)
# ---------------------------------------------------------
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="Settings", font_size='20sp', bold=True, size_hint_y=0.1))
        
        # حقل إدخال المفتاح
        layout.add_widget(Label(text="Gemini API Key:", font_size='13sp', size_hint_y=0.06))
        self.api_input = TextInput(hint_text="Paste your API key here", multiline=False, size_hint_y=0.1)
        layout.add_widget(self.api_input)
        
        # خيار البحث الحي عبر جوجل
        search_box = BoxLayout(orientation='horizontal', size_hint_y=0.12)
        search_box.add_widget(Label(text="Google Search (Live Info):", font_size='13sp'))
        self.search_switch = Switch(active=True)
        search_box.add_widget(self.search_switch)
        layout.add_widget(search_box)
        
        # شريط التحكم بدرجة الحرارة
        temp_box = BoxLayout(orientation='vertical', size_hint_y=0.18, spacing=2)
        self.temp_label = Label(text="Temperature (Creativity): 1.0", font_size='13sp')
        self.temp_slider = Slider(min=0.0, max=2.0, value=1.0, step=0.1)
        self.temp_slider.bind(value=self.on_temp_change)
        temp_box.add_widget(self.temp_label)
        temp_box.add_widget(self.temp_slider)
        layout.add_widget(temp_box)
        
        # زر الحفظ والعودة
        back_btn = Button(text="Save and Return", size_hint_y=0.12, background_color=(0.1, 0.8, 0.4, 1))
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.api_input.text = app.api_key
        self.search_switch.active = app.use_google_search
        self.temp_slider.value = app.temperature
        self.temp_label.text = f"Temperature (Creativity): {round(app.temperature, 1)}"

    def on_temp_change(self, instance, value):
        self.temp_label.text = f"Temperature (Creativity): {round(value, 1)}"

    def go_back(self, instance):
        app = App.get_running_app()
        app.save_settings(
            key_text=self.api_input.text.strip(),
            use_search=self.search_switch.active,
            temp=self.temp_slider.value
        )
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

# ---------------------------------------------------------
# التطبيق الرئيسي وإدارة البيانات
# ---------------------------------------------------------
class VoiceAssistantApp(App):
    api_key = DEFAULT_API_KEY
    use_google_search = True
    temperature = 1.0
    store = None

    def build(self):
        self.store = JsonStore('app_settings.json')
        
        if self.store.exists('config'):
            config = self.store.get('config')
            saved_key = config.get('api_key', '').strip()
            self.api_key = saved_key if saved_key else DEFAULT_API_KEY
            self.use_google_search = config.get('use_search', True)
            self.temperature = config.get('temperature', 1.0)
        else:
            self.api_key = DEFAULT_API_KEY

        threading.Thread(target=download_arabic_font, daemon=True).start()
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def save_settings(self, key_text, use_search, temp):
        self.api_key = key_text if key_text else DEFAULT_API_KEY
        self.use_google_search = use_search
        self.temperature = temp
        
        self.store.put('config', 
                       api_key=self.api_key, 
                       use_search=self.use_google_search, 
                       temperature=self.temperature)

    def query_gemini(self, prompt, callback):
        clean_key = self.api_key.strip()
        
        if not clean_key:
            reply = "الرجاء الانتقال للإعدادات وإدخال مفتاح الـ API الخاص بك."
            callback(reply)
            return

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={clean_key}"
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "system_instruction": {
                "parts": [
                    {"text": "أنت مساعد ذكي اسمك 811. أجب باختصار ووضوح وبلهجة عربية لطيفة."}
                ]
            },
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature
            }
        }
        
        if self.use_google_search:
            data["tools"] = [{"google_search": {}}]
        
        try:
            res = requests.post(url, json=data, headers=headers, timeout=20)
            if res.status_code == 200:
                result = res.json()
                reply = result['candidates'][0]['content']['parts'][0]['text']
            else:
                reply = f"خطأ في الاتصال بالخدمة ({res.status_code})"
        except Exception:
            reply = "حدث خطأ في الاتصال بالشبكة."

        callback(reply)

if __name__ == '__main__':
    try:
        VoiceAssistantApp().run()
    except Exception as e:
        print("Error details:", e)
        traceback.print_exc()
    

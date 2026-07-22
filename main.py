import os
import threading
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.utils import platform

# استدعاء مكتبات أندرويد الصوتية في حال التشغيل على الهاتف
if platform == 'android':
    try:
        from jnius import autoclass
        from android.permissions import request_permissions, Permission
        
        # أذونات النظام
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.BLUETOOTH,
            Permission.BLUETOOTH_CONNECT,
            Permission.MODIFY_AUDIO_SETTINGS
        ])
        
        # محرك النطق أندرويد
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
        Locale = autoclass('java.util.Locale')
    except Exception as e:
        print(f"Android Native Error: {e}")

# ----------------------------------------------------
# 1. الشاشة الرئيسية (Main Screen)
# ----------------------------------------------------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # --- شريط الحالة العلوي (بدون رموز) ---
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
        
        # --- المؤشر التفاعلي في المنتصف ---
        indicator_layout = BoxLayout(orientation='vertical', size_hint_y=0.5, spacing=10)
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
        
        # --- سجل المحادثة النصي ---
        log_layout = BoxLayout(orientation='vertical', size_hint_y=0.25)
        self.log_label = Label(
            text="You: --\n811: Waiting for command...",
            font_size='15sp',
            halign='center',
            color=(0.9, 0.9, 0.9, 1)
        )
        log_layout.add_widget(self.log_label)
        main_layout.add_widget(log_layout)
        
        # --- زر للتجربة الصوتية والمحاكاة ---
        self.speak_btn = Button(
            text="Tap to Speak (Test 811)",
            size_hint_y=0.15,
            background_color=(0.1, 0.7, 0.4, 1)
        )
        self.speak_btn.bind(on_release=self.simulate_listening)
        main_layout.add_widget(self.speak_btn)
        
        self.add_widget(main_layout)

    def update_circle(self, *args):
        self.circle_widget.canvas.clear()
        with self.circle_widget.canvas:
            Color(0.1, 0.7, 0.9, 0.8)
            center_x = self.circle_widget.center_x
            center_y = self.circle_widget.center_y
            radius = min(self.circle_widget.width, self.circle_widget.height) * 0.25
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))

    def go_to_settings(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'settings'

    def simulate_listening(self, instance):
        # تجربة إرسال سؤال واختبار رد المساعد باللهجة العراقية
        app = App.get_running_app()
        user_query = "هلا 811 شنو السالفة اليوم؟"
        self.log_label.text = f"You: {user_query}\n811: Thinking..."
        
        # تشغيل طلب الذكاء الاصطناعي في مسار خفي (Thread) حتى لا تتجمد الشاشة
        threading.Thread(target=app.query_gemini, args=(user_query, self.update_ai_response)).start()

    def update_ai_response(self, response_text):
        self.log_label.text = f"811: {response_text}"

# ----------------------------------------------------
# 2. شاشة الإعدادات (Settings Screen)
# ----------------------------------------------------
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        header = Label(
            text="Settings",
            font_size='22sp',
            bold=True,
            size_hint_y=0.1
        )
        layout.add_widget(header)
        
        # مفتاح Gemini API Key
        layout.add_widget(Label(text="Gemini API Key:", font_size='14sp', size_hint_y=0.05))
        self.api_input = TextInput(
            hint_text="Paste your Gemini API Key here",
            multiline=False,
            size_hint_y=0.12
        )
        layout.add_widget(self.api_input)
        
        # حساسية الميكروفون
        mic_box = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=5)
        self.mic_value_label = Label(text="Mic Sensitivity: 70%", font_size='14sp')
        self.mic_slider = Slider(min=10, max=100, value=70)
        self.mic_slider.bind(value=self.on_mic_change)
        mic_box.add_widget(self.mic_value_label)
        mic_box.add_widget(self.mic_slider)
        layout.add_widget(mic_box)
        
        # Bluetooth SCO
        bt_box = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        bt_label = Label(text="Bluetooth SCO Audio:", font_size='14sp')
        self.bt_switch = Switch(active=True)
        bt_box.add_widget(bt_label)
        bt_box.add_widget(self.bt_switch)
        layout.add_widget(bt_box)
        
        # زر الحفظ والعودة
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

# ----------------------------------------------------
# محرك التطبيق الرئيسي
# ----------------------------------------------------
class VoiceAssistantApp(App):
    api_key = ""
    tts_engine = None

    def build(self):
        self.init_tts()
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def init_tts(self):
        if platform == 'android':
            try:
                activity = PythonActivity.mActivity
                self.tts_engine = TextToSpeech(activity, None)
                self.tts_engine.setLanguage(Locale("ar"))
            except Exception as e:
                print(f"TTS Init Error: {e}")

    def speak(self, text):
        if self.tts_engine and platform == 'android':
            try:
                self.tts_engine.speak(text, TextToSpeech.QUEUE_FLUSH, None, None)
            except Exception as e:
                print(f"TTS Speak Error: {e}")

    def query_gemini(self, prompt, callback):
        if not self.api_key:
            reply = "يا عيني ضيف الـ API Key بالإعدادات أول شي حتى أقدر أجاوبك!"
            callback(reply)
            self.speak(reply)
            return

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        
        # توجيه المساعد للتحدث باللهجة العراقية
        system_instruction = "أنت المساعد الصوتي 811. أجب باختصار ووضوح وبطريقة ودودة جداً باللهجة العراقية."
        full_prompt = f"{system_instruction}\n\nالمستخدم يقول: {prompt}"
        
        data = {
            "contents": [{"parts": [{"text": full_prompt}]}]
        }

        try:
            res = requests.post(url, json=data, headers=headers, timeout=10)
            if res.status_code == 200:
                result = res.json()
                reply = result['candidates'][0]['content']['parts'][0]['text']
            else:
                reply = "صار عندي خطأ بالاتصال بالشبكة، جرب مرة ثانية."
        except Exception as e:
            reply = "اكو مشكلة بالإنترنت يا طيب."

        callback(reply)
        self.speak(reply)

if __name__ == '__main__':
    VoiceAssistantApp().run()

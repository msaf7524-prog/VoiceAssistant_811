import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.utils import platform

# طلب أذونات الأندرويد عند تشغيل التطبيق
def request_android_permissions():
    if platform == 'android':
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.RECORD_AUDIO,
                Permission.BLUETOOTH,
                Permission.BLUETOOTH_CONNECT,
                Permission.MODIFY_AUDIO_SETTINGS
            ])
        except Exception as e:
            print(f"Permission error: {e}")

# ----------------------------------------------------
# 1. الشاشة الرئيسية (Main Screen)
# ----------------------------------------------------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # --- شريط الحالة العلوي ---
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        self.status_label = Label(
            text="🎧 BT: Connected | 🎤 Mic: Ready",
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        settings_btn = Button(
            text="⚙️ Settings",
            size_hint_x=0.35,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        settings_btn.bind(on_release=self.go_to_settings)
        
        top_bar.add_widget(self.status_label)
        top_bar.add_widget(settings_btn)
        main_layout.add_widget(top_bar)
        
        # --- المؤشر التفاعلي في المنتصف ---
        indicator_layout = BoxLayout(orientation='vertical', size_hint_y=0.6, spacing=10)
        self.state_label = Label(
            text="811 Assistant is Active\nWaiting for '811'...",
            font_size='18sp',
            halign='center',
            bold=True
        )
        
        # مؤشر دائري ملون يعبر عن الحالة
        self.circle_widget = Widget(size_hint=(1, 1))
        self.circle_widget.bind(pos=self.update_circle, size=self.update_circle)
        
        indicator_layout.add_widget(self.state_label)
        indicator_layout.add_widget(self.circle_widget)
        main_layout.add_widget(indicator_layout)
        
        # --- سجل المحادثة النصي ---
        log_layout = BoxLayout(orientation='vertical', size_hint_y=0.3)
        self.log_label = Label(
            text="You: --\n811: Listening for your voice command...",
            font_size='15sp',
            halign='center',
            color=(0.9, 0.9, 0.9, 1)
        )
        log_layout.add_widget(self.log_label)
        main_layout.add_widget(log_layout)
        
        self.add_widget(main_layout)

    def update_circle(self, *args):
        self.circle_widget.canvas.clear()
        with self.circle_widget.canvas:
            Color(0.1, 0.7, 0.9, 0.8) # لون أزرق تفاعلي
            center_x = self.circle_widget.center_x
            center_y = self.circle_widget.center_y
            radius = min(self.circle_widget.width, self.circle_widget.height) * 0.25
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))

    def go_to_settings(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'settings'

# ----------------------------------------------------
# 2. شاشة الإعدادات الجانبية (Settings Screen)
# ----------------------------------------------------
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        
        # العنوان
        header = Label(
            text="⚙️ Voice Assistant Settings",
            font_size='20sp',
            bold=True,
            size_hint_y=0.15
        )
        layout.add_widget(header)
        
        # التحكم بحساسية الميكروفون
        mic_box = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=5)
        self.mic_value_label = Label(text="Mic Sensitivity (Threshold): 70%", font_size='15sp')
        self.mic_slider = Slider(min=10, max=100, value=70)
        self.mic_slider.bind(value=self.on_mic_sensitivity_change)
        
        mic_box.add_widget(self.mic_value_label)
        mic_box.add_widget(self.mic_slider)
        layout.add_widget(mic_box)
        
        # التحكم بتوجيه الصوت لبلوتوث SCO
        bt_box = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
        bt_label = Label(text="Route Audio to Headset (Bluetooth SCO):", font_size='13sp')
        self.bt_switch = Switch(active=True)
        
        bt_box.add_widget(bt_label)
        bt_box.add_widget(self.bt_switch)
        layout.add_widget(bt_box)
        
        # زر العودة
        back_btn = Button(
            text="Save & Return ↩️",
            size_hint_y=0.15,
            background_color=(0.1, 0.8, 0.4, 1)
        )
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

    def on_mic_sensitivity_change(self, instance, value):
        self.mic_value_label.text = f"Mic Sensitivity (Threshold): {int(value)}%"

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

# ----------------------------------------------------
# محرك التطبيق
# ----------------------------------------------------
class VoiceAssistantApp(App):
    def build(self):
        request_android_permissions()
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

if __name__ == '__main__':
    VoiceAssistantApp().run()

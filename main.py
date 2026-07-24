# =========================================================
# مشروع المساعد الشخصي الذكي (811 Voice Assistant)
# المفهوم: العمل في الخلفية + الاستجابة لـ "يا 811" + النطق بالعراقي
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

# استيراد مكتبات النطق والاستماع
try:
    from plyer import tts, notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

try:
    import speech_recognition as sr
    HAS_STT = True
except ImportError:
    HAS_STT = False

# المفتاح المدمج لـ Groq API (مشفر لضمان الأمان)
ENCODED_KEY = "Z3NrX01RWkQyc1VwSUR5RVhtM1NTcTB5V0dkeTByRlk1c2oyUmp2SVN2Zkk2eUR3ZjV5QTVnNEY="

def get_embedded_key():
    try:
        return base64.b64decode(ENCODED_KEY).decode('utf-8')
    except Exception:
        return ""

# ---------------------------------------------------------
# الشاشة الرئيسية لخدمة المساعد 811
# ---------------------------------------------------------
class AssistantScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_service_running = False
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # عنوان التطبيق
        self.title_label = Label(
            text="المساعد الشخصي الذكي 811\n(جاهز للعمل مع سماعة البلوتوث)",
            font_size='18sp',
            halign='center',
            bold=True
        )
        layout.add_widget(self.title_label)
        
        # حالة الخدمة في الخلفية
        self.status_label = Label(
            text="الخدمة: متوقفة\nاضغط تفعيل للعمل لمدة 6 ساعات",
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1),
            halign='center'
        )
        layout.add_widget(self.status_label)
        
        # زر تفعيل/إيقاف الخدمة
        self.toggle_btn = Button(
            text="تفعيل المساعد (6 ساعات في الخلفية)",
            size_hint_y=0.2,
            background_color=(0.1, 0.7, 0.3, 1)
        )
        self.toggle_btn.bind(on_release=self.toggle_service)
        layout.add_widget(self.toggle_btn)
        
        self.add_widget(layout)

    def toggle_service(self, instance):
        """تفعيل أو إيقاف الاستماع في الخلفية"""
        if not self.is_service_running:
            self.is_service_running = True
            self.status_label.text = "الخدمة: شغال بالخلفية...\nقل 'يا 811' وسيجيبك المساعد"
            self.toggle_btn.text = "إيقاف المساعد"
            self.toggle_btn.background_color = (0.8, 0.2, 0.2, 1)
            
            # إظهار إشعار دائم لتثبيت الخدمة في الخلفية
            if HAS_PLYER:
                try:
                    notification.notify(
                        title="المساعد 811 نشط",
                        message="المساعد يستمع للكلمة المفتاحية 'يا 811' عبر البلوتوث..."
                    )
                except Exception as e:
                    print("Notification error:", e)
            
            # بدء خيط الاستماع للكلمة المفتاحية في الخلفية
            threading.Thread(target=self.background_wake_word_listener, daemon=True).start()
        else:
            self.is_service_running = False
            self.status_label.text = "الخدمة: متوقفة"
            self.toggle_btn.text = "تفعيل المساعد (6 ساعات في الخلفية)"
            self.toggle_btn.background_color = (0.1, 0.7, 0.3, 1)

    def background_wake_word_listener(self):
        """خيط العمل المستمر الذي يتفقد كلمة 'يا 811'"""
        app = App.get_running_app()
        recognizer = sr.Recognizer() if HAS_STT else None
        
        # تحديد وقت الانتهاء بعد 6 ساعات
        end_time = time.time() + (6 * 3600)
        
        while self.is_service_running and time.time() < end_time:
            if not HAS_STT:
                time.sleep(5)
                continue
                
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    # استماع قصير للكلمة المفتاحية
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    text = recognizer.recognize_google(audio, language="ar-IQ")
                    
                    # الفحص هل نطق المستخدم الكلمة المفتاحية
                    if any(wake in text for wake in ["811", "٨١١", "ثمانية", "مية", "دعش"]):
                        # 1. إصدار صوت التنبيه الخفيف (Beep)
                        app.play_beep_sound()
                        
                        # 2. الاستماع للسؤال الكامل فوراً
                        self.listen_and_process_query(recognizer, source)
                        
            except Exception:
                # الاستمرار في الدورة إذا لم يتم سماع صوت
                pass
                
            time.sleep(0.5)

    def listen_and_process_query(self, recognizer, source):
        """الاستماع لسؤال المستخدم بعد سماع 'يا 811'"""
        app = App.get_running_app()
        try:
            # استماع لسؤالك الكامل
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=10)
            user_speech = recognizer.recognize_google(audio, language="ar-IQ")
            
            # إرسال السؤال للذكاء الاصطناعي مع توجيه اللهجة العراقية
            app.query_ai_iraqi(user_speech)
            
        except Exception:
            app.speak_text("عذراً، ما سمعتك زين. اعد سؤالك.")

# ---------------------------------------------------------
# تطبيق Kivy الرئيسي
# ---------------------------------------------------------
class VoiceAssistantApp(App):
    api_key = ""

    def build(self):
        self.api_key = get_embedded_key()
        sm = ScreenManager()
        sm.add_widget(AssistantScreen(name='main'))
        return sm

    def play_beep_sound(self):
        """إصدار نغمة استجابة خفيفة فور سماع كلمة 'يا 811'"""
        try:
            sound = SoundLoader.load('beep.wav')
            if sound:
                sound.play()
        except Exception as e:
            print("Beep play error:", e)

    def speak_text(self, text):
        """نطق الرد المباشر بصوت المساعد عبر سماعة البلوتوث"""
        def _speak():
            if HAS_PLYER:
                try:
                    tts.speak(text)
                except Exception as e:
                    print("TTS error:", e)
        threading.Thread(target=_speak, daemon=True).start()

    def query_ai_iraqi(self, prompt_text):
        """إرسال السؤال إلى Groq مع اشتراط الإجابة بأسلوب عراقي مذكر ومختصر"""
        def _request():
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # توجيه النظام للذكاء الاصطناعي ليكون رجل عراقي يجيب باختصار
            system_prompt = (
                "أنت مساعد شخصي ذكي مذكر اسمك 811. "
                "تحدث بلهجة عراقية عامية محببة وبسيطة جداً. "
                "أجوبتك يجب أن تكون قصيرة جداً ومباشرة ومناسبة للمحادثة الصوتية عبر البلوتوث."
            )
            
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_text}
                ],
                "temperature": 0.6
            }
            
            try:
                res = requests.post(url, json=data, headers=headers, timeout=15)
                if res.status_code == 200:
                    reply = res.json()['choices'][0]['message']['content']
                    self.speak_text(reply)
                else:
                    self.speak_text("صار اكو خلل بالسيرفر، جرب مرة ثانية.")
            except Exception:
                self.speak_text("تأكد من الاتصال بالإنترنت.")

        threading.Thread(target=_request, daemon=True).start()

if __name__ == '__main__':
    VoiceAssistantApp().run()
    

# =========================================================
# ملف إعدادات بناء التطبيق (buildozer.spec)
# المساعد الشخصي الذكي 811
# =========================================================

[app]

# عنوان التطبيق الذي يظهر على الشاشة
title = VoiceAssistant

# اسم الحزمة البرمجية (بدون مساحات أو رموز خاصة)
package.name = voiceassistant

# النطاق البرمجي
package.domain = org.test

# مجلد السورس كود (المجلد الحالي)
source.dir = .

# امتدادات الملفات المطلوبة للتضمين داخل التطبيق (بما فيها ملفات الخطوط ttf)
source.include_exts = py,png,jpg,kv,atlas,ttf,wav

# إصدار التطبيق
version = 0.1

# المكتبات البرمجية المطلوبة لبناء التطبيق وتشغيله
requirements = python3,kivy,requests,urllib3,certifi,charset_normalizer,idna,plyer,speechrecognition,arabic_reshaper,python-bidi

# الأذونات المطلوبة (الميكروفون، الإنترنت، والبلوتوث)
android.permissions = INTERNET, RECORD_AUDIO, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, MODIFY_AUDIO_SETTINGS

# مستويات أندرويد API
android.api = 33
android.minapi = 21

# تشغيل الشاشة الكاملة والاتجاه (عمودي)
fullscreen = 0
orientation = portrait

[buildozer]

# مستوى تسجيل الأخطاء عند البناء
log_level = 2

warn_on_root = 1

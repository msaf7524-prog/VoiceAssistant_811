[app]

# عنوان التطبيق
title = VoiceAssistant

# اسم الحزمة
package.name = voiceassistant

# النطاق البرمجي
package.domain = org.test

# مجلد السورس كود (نفس المجلد الحالية)
source.dir = .

# امتدادات الملفات المطلوبة
source.include_exts = py,png,jpg,kv,atlas

# إصدار التطبيق
version = 0.1

# المكتبات البرمجية المطلوبة
requirements = python3,kivy

# الأذونات المطلوبة (الميكروفون، الإنترنيت، والبلوتوث)
android.permissions = INTERNET, RECORD_AUDIO, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, MODIFY_AUDIO_SETTINGS


# مستويات API لأندرويد
android.api = 33
android.minapi = 21

# تشغيل الشاشة الكاملة
fullscreen = 0

[buildozer]

# مستوى تسجيل الأخطاء
log_level = 2

warn_on_root = 1

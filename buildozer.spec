[app]

# (str) Title of your application
title = VoiceAssistant

# (str) Package name
package.name = voiceassistant

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,wav

# (str) Application versioning
version = 0.1

# (list) Application requirements
# تمت إضافة pyjnius و python-bidi و speechrecognition لحل مشكلة التعرف الصوتي
requirements = python3,kivy,requests,urllib3,certifi,charset_normalizer,idna,plyer,speechrecognition,arabic_reshaper,python-bidi,pyjnius

# (list) Permissions
# جميع أذونات الصوت والميكروفون والبلوتوث والإنترنت المطلوبة
android.permissions = INTERNET, RECORD_AUDIO, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, MODIFY_AUDIO_SETTINGS

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
# android.sdk = 20

# (str) Android NDK version to use
# android.ndk = 23b

# (bool) Use --private data storage (True) or --dir public storage (False)
# android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
# android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
# android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
# android.ant_path =

# (bool) If True, then skip trying to update the Android sdk terms
# android.skip_update = False

# (bool) If True, then accept all the Android SDK licenses
# android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (list) Pattern to whitelist or blacklist for python-for-android compilation
# android.whitelist =

# (str) Screen orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) List of service to declare
# services = MyServiceName:service.py


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1


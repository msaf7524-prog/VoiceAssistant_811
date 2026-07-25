[app]

# (str) Title of your application
title = VoiceAssistant

# (str) Package name
package.name = voiceassistant

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (including mp3 for gTTS audio files)
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,mp3

# (str) Application versioning
version = 0.1

# (list) Application requirements
# Added: gTTS for online voice, pyjnius for android internals, plyer for notifications
requirements = python3,kivy,requests,urllib3,certifi,charset_normalizer,idna,plyer,speechrecognition,gTTS,pyjnius

# (list) Permissions
# Required for Microphone, Bluetooth headsets, Internet, and Background Notifications
android.permissions = INTERNET, RECORD_AUDIO, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, MODIFY_AUDIO_SETTINGS, POST_NOTIFICATIONS

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (bool) If True, then skip trying to update the Android sdk terms
android.skip_update = False

# (bool) If True, then accept all the Android SDK licenses
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Screen orientation (one of landscape, sensorlandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1

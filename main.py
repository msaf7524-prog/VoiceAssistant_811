from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class VoiceAssistantApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        btn = Button(text='811 Assistant is Active\nWaiting for setup...', font_size=24)
        layout.add_widget(btn)
        return layout

if __name__ == '__main__':
    VoiceAssistantApp().run()

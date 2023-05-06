import pyttsx3
class TextToSpeech():
    def __init__(self) -> None:
        self.engine = pyttsx3.init('sapi5')  # 使用SAPI5语音引擎
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[0].id)  # 设置语音为第一个语音
        self.engine.setProperty('rate', 150)  # 设置语音速度为150
        self.engine.setProperty('volume', 0.8)  # 设置音量为0.8
    def text_to_speech(self,text,player):
        self.engine.say(text)
        self.engine.runAndWait()
        player.play()

# engine = pyttsx3.init('sapi5')  # 使用SAPI5语音引擎
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[0].id)  # 设置语音为第一个语音
# engine.setProperty('rate', 150)  # 设置语音速度为150
# engine.setProperty('volume', 0.8)  # 设置音量为0.8
# engine.say("你好世界!")
# engine.runAndWait()
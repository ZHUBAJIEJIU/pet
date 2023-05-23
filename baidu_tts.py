import requests
from pydub import AudioSegment
from pydub.playback import play
from urllib.parse import urlencode

from PyQt6.QtCore import QObject, pyqtSignal


API_KEY = "Zt7ZWfHGP202EWhbSjHUYzo9"
SECRET_KEY = "BUlwxnwO3HoW5nrbDL4zQ4oeMfUIUUXY"
url = "https://tsn.baidu.com/text2audio"


class Communicate(QObject):
    switch2say = pyqtSignal()
    switch2wait = pyqtSignal()


class BaiduTTS():
    def __init__(self) -> None:
        self.c = Communicate()
        
    def text_to_speech(self, text, player):
        text = {'tex': text}
        payload=''+urlencode(text) +'&tok='+ self.get_access_token() +'&cuid=123&ctp=1&lan=zh&per=103'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response)
        audio = AudioSegment(data=response.content, sample_width=2, frame_rate=16000, channels=1)
        out_path = 'test_tts.mp3'
        audio.export(out_path, format='mp3')
        speech = AudioSegment.from_mp3(out_path)
        self.c.switch2say.emit()
        play(speech)
        self.c.switch2wait.emit()
        player.play()
    

    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
        return str(requests.post(url, params=params).json().get("access_token"))
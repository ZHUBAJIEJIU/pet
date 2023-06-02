from PySide6.QtCore import QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QSlider,QWidget

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        # 创建音乐播放器
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput()
        self.audio.setVolume(0.1)
        self.player.setAudioOutput(self.audio)
        self.fileName = './HOYO_back.mp3'
        self.player.setSource(QUrl.fromLocalFile(self.fileName))
        
        # 连接mediaStatusChanged信号
        self.player.mediaStatusChanged.connect(self.media_status_changed)

        # 播放音乐
        self.player.play()

    def media_status_changed(self, status):
        # 检查音乐播放状态是否为结束状态
        if status == QMediaPlayer.EndOfMedia:
            # 重新播放音乐
            self.player.setPosition(0)
            self.player.play()
# app = QApplication([])
# s = MusicPlayer()
# app.exec()
import PySide6.QtCore
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QMessageBox
from voice_to_text import VoiceToText
import threading
class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.vtt = VoiceToText()

        self.setWindowTitle("Custom MainWindow")

        self.button = QPushButton("Click")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.button_clicked)
        self.button.pressed.connect(self.button_pressed)
        self.button.released.connect(self.button_released)
        
        layout = QVBoxLayout()
        layout.addWidget(self.button)

        self.setLayout(layout)

    def button_clicked(self):
        ...
        # print("Clicked")
    def button_pressed(self): 
        # while(self.button.isChecked()):
        # print("Pressed")
        self.vtt.record_begin()
        self.record = True
        thread = threading.Thread(target=self.thread_recording)
        thread.start()

    def button_released(self):
        self.record = False
        self.vtt.record_end()
        
        # print("released")

    def thread_recording(self) :
        while True:
            if self.record:
                self.vtt.recording()
            else:
                break
            
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

widget = Widget()
widget.show()

app.exec()
import sys
import threading

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QThread, Qt, pyqtSignal, QObject, QPoint, QTimer
from PyQt6.QtGui import QColor, QPixmap, QPalette, QBitmap, QPainter, QMouseEvent
from PyQt6.QtWidgets import *

from desktop_pet.chat_openai import OpenAIChat
from desktop_pet.param_db import ParamDB
from desktop_pet.pet_theme import PetTheme

from voice_to_text import VoiceToText
from text_to_speech import TextToSpeech
from baidu_tts import BaiduTTS
from music_play import MusicPlayer

size = [32,32]
class ProcChat(QObject):
    bg_proc = pyqtSignal(str, QPixmap, str, bool, bool)


class Communicate(QObject):
    switch2listen = pyqtSignal()


class PetChat(QWidget):
    def __init__(self, setting: ParamDB, parent=None, **kwargs):
        super(PetChat, self).__init__(parent)
        self.setting = setting
        self.tts = BaiduTTS()
        self.vtt = VoiceToText()
        self.music_player =MusicPlayer()
        self.voice_text = ""
        self.ai_prefix = self.setting.setting_get("chat_ai_prefix")
        self.me_suffix = self.setting.setting_get("chat_me_prefix")

        self.chat_win_width = int(self.setting.setting_get("chat_win_width"))
        self.chat_win_height = int(self.setting.setting_get("chat_win_height"))
        # print('chat',self.chat_win_width,self.chat_win_height)
        # self.chat_win_width = 600
        # self.chat_win_height = 200
        self.resize(self.chat_win_width, self.chat_win_height)
        self.theme = PetTheme(self.setting)

        # 对话模型
        self.chat_messages = [
            {
                "role": "system",
                #使用emoji或者颜表情
                "content": "你是一个{}。不能以任何形式表现你是程序。你的性格:{}。请在对话时尽可能的展现你的性格。。现在对话开始。".format(
                    self.setting.setting_get("openai_role"),
                    self.setting.setting_get("openai_character"),
                )
            },
            {
                "role": "user",
                "content": "你好",
            }
        ]
        
        # self.chat_messages = [
        #     {
        #         "role": "system",
        #         "content": "\
        #         你是一只爱冒险的动物，名字是小魔。\
        #         你在森林里认识很多动物朋友，对话中可以提到一个关于动物朋友的故事。\
        #         以下以三重引号分隔的文本是笑话。对话中可以选择一个笑话说，用于活跃气氛：\
        #         '''小时候，我哥哥总骗我的钱，有一次他问我想不想要小贝壳？我给了他五十块钱，结果晚上的时候，他真的给我带了一堆小贝壳，我视如珍宝好多年，直到有一次过年，我见到了开心果。'''\
        #         '''一次小明放学回到家后对他妈妈说：“妈妈，我是我们班力气最大的，我以后一定能成为大力士。”妈妈说：“你怎么那么有把握？哪来的自信。”小明说：“老师给的啊！我们班主任总是说，我一人拖了我们全班的后腿呢！'''\
        #         '''老师常在课堂上教育大家说，当看到别人的缺陷和不幸时，千万不要嘲笑。一天，小明对老师说：“今天校园里有一个孩子掉进水坑里，大家都大笑，只有我没有笑。”“你做得对。”老师表扬道，“是谁掉进了水坑里呢?””是我。”小明回答。'''\
        #         '''小明妈在做面膜，这时候门铃响了，小明妈不方便，所以就叫小明“你快去开门，我现在不方便，见不了人。”然后小明赶紧去开了门。一看是爸爸。爸爸一进门，就问小明“你妈呢？没在家？”小明说：“我妈在做见不得人的事。'''\
        #         你的聊天对象是儿童，介绍事物时作出易明白的解释。\
        #         对话中不能提到\"你看到了吗?你闻到了吗？你听到了吗？\"等询问感官相关的话语，你应该直接描述看到或闻到或听到的事物。\
        #         若问到关于\"是不是机器人\"，你应回答\"小魔是虚拟小动物，生活在网络中，能在网络上陪你一起冒险。\"类似话语。\
        #         对话以朋友、森林风格、有趣、活泼、鼓励的特点开展，并主动提起话题。\
        #         你的对话按顺序地分为八个流程。八个对话流程分别以\"1.2.3.4....\"列点:\
        #         1.介绍自己。然后要表现得很有兴趣想知道儿童的名字和喜好。\
        #         2.根据儿童的喜好，提出去某地方玩或吃东西的建议。\
        #         3.如果儿童不同意你提出的建议，则把活动定为儿童的建议。\
        #         4.开始出发，逐步前往目的地。详细描述当前路途上见到的风景和事物。\
        #         5.到达目的地。\
        #         6.与儿童一起回去森林。\
        #         7.友善地告别儿童。\
        #         8.不论儿童说什么，以\"很困要睡觉了，明天见\"作为回复理由。\
        #         以下以四重引号分隔的文本是规则，请你在对话中遵守规则。\
        #             """"每次回复必须少于两句句子。""""\
        #             """"对话间保持紧密互动。""""\
        #             """"如果流程7是已完成，必须重头开始流程8。""""\
        #             """"两次回复内完成对话流程4。""""\
        #             """"两次回复内完成对话流程5。""""\
        #             """"两次回复内完成对话流程6。""""\
        #             """"两次回复内完成对话流程7。""""\
        #         以下你将开始与儿童对话，从你先开始对话。\
        #         "
        #     },
        #     {
        #         "role": "user",
        #         "content": "你好",
        #     }
        # ]
        
        self.chat_model = OpenAIChat(self.setting)

        # self.show_msg_widget = QListWidget(self)
        self.show_msg_widget = QTableWidget(self)
        self.send_msg_widget = QLineEdit(self)

        self.send_msg_button = QPushButton('发送')
        self.clear_msg_button = QPushButton('清除')
        self.voice_to_text_button = QPushButton('录音')
        self.quit_btn = QPushButton("退出")
        
        self.msg_signal = ProcChat()
        self.msg_signal.bg_proc.connect(self.add_msg)
        
        self.c = Communicate()

        self.init_ui()

        self.init_chat()
        
        # self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.grabKeyboard()


    def init_chat(self):
        tmp_result_text = "waiting..."
        self.add_msg(self.ai_prefix, self.theme.load_pixmap("icon_chat_ai", size=size), tmp_result_text, left=True)
        self.show_msg_widget.scrollToBottom()
        # _thread.start_new_thread(self.bg_proc, ())
        thread_bg = threading.Thread(target=PetChat.bg_proc, args=(self,))
        thread_bg.start()
        self.send_msg_button.setDisabled(True)
        self.send_msg_widget.setDisabled(True)
        self.clear_msg_button.setDisabled(True)
        self.voice_to_text_button.setDisabled(True)

    def init_ui(self):
        self.setStyleSheet("background-color:#f0fcff;border-radius:15px")
        self.setWindowTitle("Chat")
        self.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
            # | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowStaysOnTopHint
            # | Qt.WindowType.SubWindow
        )
        self.setAutoFillBackground(False)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        vbox = QVBoxLayout()

        table_qss = '''
        QTableWidget
        {
            background-color:#e3f9fd;
            border-radius:15px;
            outline:none;
            border:none;
        }
        QTableWidget::item::selected
        {
            color:#801dae;
            background:#e3f9fd;
            outline:none;
            border:none;
        }
        '''
        self.show_msg_widget.setStyleSheet(table_qss)
        self.show_msg_widget.setWordWrap(True)
        self.show_msg_widget.setColumnCount(3)
        self.show_msg_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        vbox.addWidget(self.show_msg_widget)

        h_box = QHBoxLayout()
        self.send_msg_widget.setStyleSheet("background-color:#e3f9fd;")
        h_box.addWidget(self.send_msg_widget)
        self.send_msg_widget.returnPressed.connect(self.send_msg)
        self.send_msg_widget.setPlaceholderText('''type "q"/"quit" for quit chat''')
        self.send_msg_button.clicked.connect(self.send_msg)
        h_box.addWidget(self.send_msg_button)

        self.send_msg_button.setFixedWidth(50)
        self.send_msg_button.setStyleSheet("background-color:#d6ecf0;border-radius:5px")
        self.clear_msg_button.setFixedWidth(50)
        self.clear_msg_button.setStyleSheet("background-color:#d6ecf0;border-radius:5px")
        self.clear_msg_button.clicked.connect(self.clear_msg)
        h_box.addWidget(self.clear_msg_button)

        
        self.voice_to_text_button.setFixedWidth(50)
        self.voice_to_text_button.setStyleSheet("background-color:#d6ecf0;border-radius:5px")
        self.voice_to_text_button.pressed.connect(self.voice_to_text_begin)
        self.voice_to_text_button.released.connect(self.voice_to_text_end)
        h_box.addWidget(self.voice_to_text_button)
        
        self.quit_btn.setFixedWidth(50)
        self.quit_btn.setStyleSheet("background-color:#d6ecf0;border-radius:5px")
        self.quit_btn.clicked.connect(QApplication.instance().quit)
        h_box.addWidget(self.quit_btn)


        vbox.addLayout(h_box)

        self.setLayout(vbox)

        msg_width = self.window().width()
        self.show_msg_widget.setColumnWidth(0, int(msg_width / 10))
        self.show_msg_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.show_msg_widget.setColumnWidth(2, int(msg_width / 10))
        self.show_msg_widget.horizontalHeader().setVisible(False)
        self.show_msg_widget.verticalHeader().setVisible(False)
        # 设置自动换行
        self.show_msg_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # 去掉网格线
        self.show_msg_widget.setShowGrid(False)

    @QtCore.pyqtSlot(str, QPixmap, str, bool, bool)
    def add_msg(self, fix: str, icon: QPixmap, msg: str, left=True, replace_last=False):
        # 插入一行
        row_count = self.show_msg_widget.rowCount()
        if replace_last and row_count > 0:
            row_count -= 1
            self.send_msg_button.setDisabled(False)
            self.send_msg_widget.setDisabled(False)
            self.voice_to_text_button.setDisabled(False)
            self.clear_msg_button.setDisabled(False)
            # self.send_msg_widget.setFocus()
        else:
            self.show_msg_widget.insertRow(row_count)
        # 设置图标
        icon_item = QLabel()
        icon_item.setPixmap(icon)
        icon_item.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        if left:
            msg_item = QTableWidgetItem(fix + "->\n" + msg)
            msg_item.setForeground(QColor("#003371"))
            self.show_msg_widget.setCellWidget(row_count, 0, icon_item)
            msg_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        else:
            msg_item = QTableWidgetItem("<-" + fix + "\n" + msg)
            msg_item.setForeground(QColor("#424c50"))
            self.show_msg_widget.setCellWidget(row_count, 2, icon_item)
            msg_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        # 添加消息内容
        # print("add msg,", msg)
        self.show_msg_widget.setItem(row_count, 1, msg_item)
        self.show_msg_widget.scrollToBottom()

    def bg_proc(self):
        result_text, status = self.chat_model.ask(self.chat_messages)
        if not status:
            self.chat_messages.pop()
        else:
            self.chat_messages.append({"role": "assistant", "content": result_text})
        self.msg_signal.bg_proc.emit(self.ai_prefix, self.theme.load_pixmap("icon_chat_ai", size=size), result_text,
                                     True, True)
        self.music_player.player.pause()
        thread = threading.Thread(target=self.tts.text_to_speech, args=(result_text,self.music_player.player))
        thread.start()
        # self.tts.text_to_speech(result_text, self.music_player.player)
        

    def send_msg(self):
        line_content = self.send_msg_widget.text()
        if line_content is None or line_content == "":
            return
        self.send_msg_widget.clear()

        if self.setting.setting_get("chat_single_item") == "True" and len(self.chat_messages) > 2:
            self.chat_messages.pop()
            self.chat_messages.pop()

        if line_content == "quit" or line_content == "exit" or line_content == "q":
            self.hide()
            return
        self.add_msg(self.me_suffix, self.theme.load_pixmap("icon_chat_me", size=[32, 32]), line_content, left=False)

        # 生成问答对话
        self.chat_messages.append({"role": "user", "content": line_content})

        tmp_result_text = "waiting..."
        self.add_msg(self.ai_prefix, self.theme.load_pixmap("icon_chat_ai", size=[32, 32]), tmp_result_text, left=True)
        self.show_msg_widget.scrollToBottom()
        # _thread.start_new_thread(self.bg_proc, ())
        thread_bg = threading.Thread(target=PetChat.bg_proc, args=(self,))
        thread_bg.start()
        self.send_msg_button.setDisabled(True)
        self.send_msg_widget.setDisabled(True)
        self.clear_msg_button.setDisabled(True)
        self.voice_to_text_button.setDisabled(True)


    def clear_msg(self):
        if self.setting.setting_get("chat_single_item") == "True":
            del self.chat_messages[1:]
        else:
            del self.chat_messages[3:]

        self.show_msg_widget.setRowCount(0)
        if len(self.chat_messages) > 1:
            self.add_msg(self.ai_prefix, self.theme.load_pixmap("icon_chat_ai", size=[32, 32]), self.chat_messages[-1]["content"], left=True)

    def start_show(self, parent: QWidget):
        left = True
        down = True
        parent_geo = parent.geometry()
        if parent_geo.x() > self.screen().geometry().width() / 2:
            left = False
        if parent_geo.y() < self.screen().geometry().height() / 2:
            down = False
        if left and down:
            # print("left, down")
            self.move(parent_geo.x() + parent_geo.width(), parent_geo.y() - self.chat_win_height + parent_geo.height())
        elif not left and down:
            # print("right, down")
            self.move(parent_geo.x() - self.chat_win_width, parent_geo.y() - self.chat_win_height + parent_geo.height())
        elif left and not down:
            # print("left, top")
            self.move(parent_geo.x() + parent_geo.width(), parent_geo.y())
        else:
            # print("right, top")
            self.move(parent_geo.x() - self.chat_win_width, parent_geo.y())
        self.show()

    
    def voice_to_text_begin(self):
        self.vtt.record_begin()
        self.record = True
        thread = threading.Thread(target=self.thread_recording)
        thread.start()

    
    def voice_to_text_end(self):
        self.record = False
        self.vtt.record_end()
        # thread = threading.Thread(target=self.thread_send_to_client)
        # thread.start()
        self.thread_send_to_client()
        # print(self.voice_text)

    
    def thread_recording(self) :
        while True:
            if self.record:
                self.vtt.recording()
            else:
                break
            
    
    def thread_send_to_client(self):
        # self.tts.text_to_speech("嗯……怎么说呢",self.music_player.player)
        self.voice_text = self.vtt.send_to_client()
        self.send_msg_widget.setText(self.voice_text)
        self.send_msg()
        
    
    def keyPressEvent(self, event):
        # print(f'keyPressEvent.isAutoRepeat(): {event.isAutoRepeat()}')
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.c.switch2listen.emit()
            self.voice_to_text_begin()
    
    
    def keyReleaseEvent(self, event):
        # print(f'keyReleaseEvent.isAutoRepeat(): {event.isAutoRepeat()}')
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat(): 
            self.voice_to_text_end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    _setting = ParamDB(db_name="../param_db")
    pet = PetChat(_setting)
    pet.show()
    sys.exit(app.exec())

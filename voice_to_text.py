# -*- encoding:utf-8 -*-
import hashlib
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging
import pyaudio
import wave
import time
from PySide6.QtWidgets import QPushButton
import subprocess
class VoiceToText:
    def __init__(self):
        #audio
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 4096
        #tts api
        self.app_id = "878af839"
        self.api_key = "76dd226877195c5258abc4744bd59858"
        #ffmpegpath
        self.ffmpeg = './ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe'
        #temp file_path
        self.wav_path ="./output.wav"
        self.pcm_path = "./output.pcm"
        #

    def record_begin(self):
        self.audio = pyaudio.PyAudio()
        self.start_time = time.time()
        # 打开麦克风设备
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                            rate=self.RATE, input=True,
                            frames_per_buffer=self.CHUNK)
        self.frames = []
        print("开始录音...")
    def recording(self):
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)

    def record_end(self):
        self.end_time = time.time()
        self.run_time = self.end_time - self.start_time
        # 将录制的音频数据保存为WAV文件
        wf = wave.open(self.wav_path, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print("录音结束。")
        # 停止录制音频数据
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        print("录音时间为：", self.run_time, "秒")
        # 音频文件转换(win)
        # 执行命令，将输出打印到控制台
        # result = subprocess.run('ls', capture_output=True, text=True)
        process = subprocess.Popen(["cmd", "/c", self.ffmpeg, "-i", self.wav_path, "-f", "s16le", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",self.pcm_path ,"-y"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

    def send_to_client(self):
        # logging.basicConfig()
        self.client = Client(self.app_id,self.api_key)
        self.client.send(self.pcm_path)
        # client.send(file_path)
        # client.close()
        try:
            words = ''
            # print(json.loads(client.data))
            for i in json.loads(self.client.data['data'])['cn']['st']['rt'][0]['ws']:
                # print(i['cw'][0]['w'])
                words += i['cw'][0]['w']
            self.client.close()
            return words
        except:
            self.client.close()
            print('Nothing Repeat!')


# reload(sys)
# sys.setdefaultencoding("utf8")
class Client():
    def __init__(self,app_id,api_key):
        self.data = ''
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def send(self, file_path):
        file_object = open(file_path, 'rb')
        try:
            index = 1
            while True:
                chunk = file_object.read(1280)
                if not chunk:
                    break
                self.ws.send(chunk)

                index += 1
                time.sleep(0.04)
        finally:
            file_object.close()

        self.ws.send(bytes(self.end_tag.encode('utf-8')))
        # print("send end tag success")

    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    # print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    ...
                    # print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    result_1 = result_dict
                    # result_2 = json.loads(result_1["cn"])
                    # result_3 = json.loads(result_2["st"])
                    # result_4 = json.loads(result_3["rt"])
                    # print("rtasr result: " + result_1["data"])
                    self.data = result_1
                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            # print("receive result end")
            ...

    def close(self):
        self.ws.close()
        print("connection closed")















def voice_to_text(seconds):
    RECORD_SECONDS = seconds
    # 创建PyAudio对象   
    audio = pyaudio.PyAudio()

    # 打开麦克风设备
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("开始录音...")

    # 录制音频数据
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束。")

    # 停止录制音频数据
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 将录制的音频数据保存为WAV文件
    wf = wave.open("output.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # 音频文件转换(win)
    import subprocess

    # 执行命令，将输出打印到控制台
    # result = subprocess.run('ls', capture_output=True, text=True)
    process = subprocess.Popen(["cmd", "/c", ffmpeg, "-i", wav_path, "-f", "s16le", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",pcm_path ,"-y"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # print(stdout.decode('gbk'))
    # print(stderr.decode('gbk'))

    # 音频文件转换
    # from pydub import AudioSegment
    # print(AudioSegment.converter)
    # AudioSegment.converter = './ffmpeg-master-latest-win64-gpl/bin'

    # 将wav文件转换为mp3格式
    # sound = AudioSegment.from_file("./output.wav",format='wav')
    # sound = sound.set_frame_rate(16000).set_channels(1)
    # sound.export("./outputsf.pcm", format="s16le")

    #语音转文字
    logging.basicConfig()

    client = Client()
    file_path = pcm_path

    client.send(file_path)
    # client.send(file_path)
    # client.close()
    try:
        words = ''
        # print(json.loads(client.data))
        for i in json.loads(client.data['data'])['cn']['st']['rt'][0]['ws']:
            # print(i['cw'][0]['w'])
            words += i['cw'][0]['w']
        return words
    except:
        print('Nothing Repeat!')


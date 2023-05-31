import requests
import json 
import json
import base64
import time
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
timer = time.perf_counter


class DemoError(Exception):
    pass

class BaiduASR:
    def __init__(self):
        self.api_key = 'Zt7ZWfHGP202EWhbSjHUYzo9'
        self.secret_key = 'BUlwxnwO3HoW5nrbDL4zQ4oeMfUIUUXY'

        # 需要识别的文件
        self.audio_file = 'output.pcm'
        # 文件格式
        self.format = self.audio_file[-3:]
        self.cuid = '54-05-DB-E8-15-29'
        # 采样率
        self.rate = 16000  # 固定值

        self.dev_pid = 80001  #根据文档填写PID，选择语言及识别模型
        self.asr_url = 'https://vop.baidu.com/pro_api'
        self.token_url = 'http://aip.baidubce.com/oauth/2.0/token'
        self.scope = 'audio_voice_assistant_get'
        self.token = self.fetch_token()
        
        
    def fetch_token(self):
        params = {'grant_type': 'client_credentials',
              'client_id': self.api_key,
              'client_secret': self.secret_key}
        post_data = urlencode(params)
        post_data = post_data.encode( 'utf-8')
        req = Request(self.token_url, post_data)
        try:
            f = urlopen(req)
            result_str = f.read()
        except URLError as err:
            print('token http response http code : ' + str(err.code))
            result_str = err.read()
        result_str =  result_str.decode()

        # print(result_str)
        result = json.loads(result_str)
        # print(result)
        if ('access_token' in result.keys() and 'scope' in result.keys()):
            # print(SCOPE)
            if self.scope and (not self.scope in result['scope'].split(' ')):
                raise DemoError('scope is not correct')
    
            return result['access_token']
        else:
            raise DemoError('MAYBE API_KEY or SECRET_KEY not correct:\
                access_token or scope not found in token response')
            
            
    def recv(self):
        speech_data = []
        with open(self.audio_file, 'rb') as speech_file:
            speech_data = speech_file.read()

        length = len(speech_data)
        if length == 0:
            raise DemoError('file %s length read 0 bytes' % self.audio_file)
        speech = base64.b64encode(speech_data)
        speech = str(speech, 'utf-8')
        params = {'dev_pid': self.dev_pid,
                #"lm_id" : LM_ID,    #测试自训练平台开启此项
                'format': self.format,
                'rate': self.rate,
                'token': self.token,
                'cuid': self.cuid,
                'channel': 1,
                'speech': speech,
                'len': length
                }
        post_data = json.dumps(params, sort_keys=False)
        req = Request(self.asr_url, post_data.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        try:
            begin = timer()
            f = urlopen(req)
            result_str = f.read()
            print ("asr request time cost %f" % (timer() - begin))
        except URLError as err:
            print('asr http response http code : ' + str(err.code))
            result_str = err.read()

        result_str = str(result_str, 'utf-8')
        return json.loads(result_str)['result'][0]
    
    
if __name__ == '__main__':
    asr = BaiduASR()
    print(asr.recv())
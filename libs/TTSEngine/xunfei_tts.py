#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
#   author: iflytek
#   https://www.xfyun.cn/doc/tts/online_tts/API.html#%E6%8E%A5%E5%8F%A3%E8%B0%83%E7%94%A8%E6%B5%81%E7%A8%8B
#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#   合成小语种需要传输小语种文本、使用小语种发音人vcn、tte=unicode以及修改文本编码方式
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import ssl
import os
from os.path import dirname, abspath
import websocket
import sys
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

from pydub import AudioSegment
from pydub.playback import play

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from logging_config import get_logger
logger = get_logger(__name__)

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

speaker = {
    "1": {
        "aisjiuxu": "aisjiuxu",
    },
    "2":{
        "xiaoyan": "xiaoyan",
        "aisxping": "aisxping",
        "aisjinger":"aisjinger",
        "aisbabyxu": "aisbabyxu"
    }
}

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text, output, vcn="子阳"):
        """
        初始化讯飞语音接口

        Params:
            APPID:
            APIKey:
            APISecret:
            Text: 要合成语言的文本
            output: 生成的mp3全路径
            vcn: 语音人物/发音人（控制台https://console.xfyun.cn/app/myapp - 我的应用 - 语音合成 - 添加试用或购买发音人）
                如： xiaoyan
        """
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        output_folder = os.path.dirname(output)
        os.makedirs(output_folder, exist_ok=True)
        self.output = output

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "lame", "auf": "audio/L16;rate=16000", "vcn": vcn, "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url

    # 收到websocket连接建立的处理
    def on_open(self, ws):
        def run(*args):
            d = {"common": self.CommonArgs,
                "business": self.BusinessArgs,
                "data": self.Data,
                }
            d = json.dumps(d)
            logger.debug("开始发送文本数据到讯飞TTS服务")
            ws.send(d)
            if os.path.exists(self.output):
                os.remove(self.output)

        thread.start_new_thread(run, ())

    def on_message(self, ws, message):
        try:
            message =json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            # print(message)
            if status == 2:
                logger.debug("WebSocket连接已关闭")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                logger.error(f"讯飞TTS调用失败 - sid: {sid}, 错误信息: {errMsg}, 错误码: {code}")
            else:
                with open(self.output, 'ab') as f:
                    f.write(audio)

        except Exception as e:
            logger.error(f"接收消息时解析异常: {e}")

    # 收到websocket错误的处理
    def on_error(self, ws, error):
        logger.error(f"WebSocket错误: {error}")

    # 收到websocket关闭的处理
    def on_close(self, ws, status, msg):
        logger.debug("WebSocket连接已关闭")
        logger.debug(f"关闭状态码: {status}, 消息: {msg}")


def covert_text_to_sound(text, output, speaker):
    # https://console.xfyun.cn/services/cbm 在这里获取密码
    wsParam = Ws_Param(APPID='',
                    APISecret='',
                    APIKey='',
                    Text=text,
                    output=output,
                    vcn=speaker)
    if "enableTrace" in dir(websocket):
        websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, 
                                on_message=wsParam.on_message, 
                                on_error=wsParam.on_error, 
                                on_close=wsParam.on_close)
    ws.on_open = wsParam.on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    logger.info(f"音频文件转换完成，保存路径: {wsParam.output}")
    return wsParam.output

if __name__ == "__main__":
    covert_text_to_sound("在此吃了饭再走不迟", "output/在此吃了饭再走不迟.mp3", speaker="aisjiuxu")
    sound = AudioSegment.from_file("output/在此吃了饭再走不迟.mp3", format="mp3")
    play(sound)
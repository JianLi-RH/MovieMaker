***REMOVED***.10
***REMOVED***
***REMOVED***
***REMOVED***   author: iflytek
***REMOVED***   https://www.xfyun.cn/doc/tts/online_tts/API.html***REMOVED***%E6%8E%A5%E5%8F%A3%E8%B0%83%E7%94%A8%E6%B5%81%E7%A8%8B
***REMOVED***  本demo测试时运行的环境为：Windows + Python3.7
***REMOVED***  本demo测试成功运行时所安装的第三方库及其版本如下：
***REMOVED***   cffi==1.12.3
***REMOVED***   gevent==1.4.0
***REMOVED***   greenlet==0.4.15
***REMOVED***   pycparser==2.19
***REMOVED***   six==1.12.0
***REMOVED***   websocket==0.2.1
***REMOVED***   websocket-client==0.56.0
***REMOVED***   合成小语种需要传输小语种文本、使用小语种发音人vcn、tte=unicode以及修改文本编码方式
***REMOVED***  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED*** ***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
from datetime ***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***

import config_reader

STATUS_FIRST_FRAME = 0  ***REMOVED*** 第一帧的标识
STATUS_CONTINUE_FRAME = 1  ***REMOVED*** 中间帧标识
STATUS_LAST_FRAME = 2  ***REMOVED*** 最后一帧的标识


***REMOVED***
    ***REMOVED*** 初始化
    def __init__(self, APPID, APIKey, APISecret, Text, output, output_folder, vcn="xiaoyan"):
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
            output: 生成的mp3文件名
            output_folder: mp3存放路径
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

        if not os.path.exists(os.path.join(config_reader.output_dir, output_folder)):
            os.mkdir(os.path.join(config_reader.output_dir, output_folder))
        self.output = os.path.join(config_reader.output_dir, output_folder, output)

        ***REMOVED*** 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID***REMOVED***
        ***REMOVED*** 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "lame", "auf": "audio/L16;rate=16000", "vcn": vcn, "tte": "utf8"***REMOVED***
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")***REMOVED***
        ***REMOVED***使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        ***REMOVED***self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")***REMOVED***

    ***REMOVED*** 生成url
***REMOVED***
***REMOVED***
        ***REMOVED*** 生成RFC1123格式的时间戳
***REMOVED***
***REMOVED***

        ***REMOVED*** 拼接字符串
***REMOVED***
***REMOVED***
***REMOVED***
        ***REMOVED*** 进行hmac-sha256进行加密
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
        ***REMOVED*** 将请求的鉴权参数组合为字典
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
    ***REMOVED***
        ***REMOVED*** 拼接鉴权参数，生成url
***REMOVED***
        ***REMOVED*** print("date: ",date)
        ***REMOVED*** print("v: ",v)
        ***REMOVED*** 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        ***REMOVED*** print('websocket url :', url)
***REMOVED***

    ***REMOVED*** 收到websocket连接建立的处理
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
            ***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
            print(message)
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***

    ***REMOVED*** 收到websocket错误的处理
***REMOVED***
        print("***REMOVED******REMOVED******REMOVED*** error:", error)

    ***REMOVED*** 收到websocket关闭的处理
***REMOVED***
        print("***REMOVED******REMOVED******REMOVED*** closed ***REMOVED******REMOVED******REMOVED***")
        print(f"{status***REMOVED***:{msg***REMOVED***")


***REMOVED***
    pass

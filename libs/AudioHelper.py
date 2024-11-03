***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
import xunfei_tts

def covert_text_to_sound(text, output, output_folder):
    """
    将文字转换成语音

    Params:
        text: 文字
        output: 输出的语音文件
        output_folder: mp3存放路径
    Return:
        语音文件路径
    """
    
    ***REMOVED*** https://console.xfyun.cn/services/cbm 在这里获取密码
    wsParam = xunfei_tts.Ws_Param(APPID='bdb4df29',
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
                    output_folder=output_folder,
                    vcn=xunfei_tts.speaker["2"]["xiaoyan"])
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE***REMOVED***)
***REMOVED***

def split_audio(audio_file: str, length=None, start=0):
    """截取音频文件
        新文件会保存在相同目录, 新文件名： 原文件名_bak.原文件后缀
    
    Params:
        audio_file: 原始音频文件
        length: 截取的片段长度, 单位毫秒
        start: 截取音频的开始位置
    """
    mp3 = AudioSegment.from_file(audio_file)
    if not length:
        new_audio = mp3[start:]
    elif not start:
        new_audio = mp3[0:length]
    else:
        new_audio = mp3[start: start + length]
    file_name, file_extension =  os.path.splitext(audio_file)
    format = file_extension.replace(".", "")
    new_audio.export(file_name + "_bak" + file_extension, format=format)

***REMOVED***
    ***REMOVED*** split_audio("水浒传/第六回/确认事实/等洒家再去确认.mp3", start=2200, length=2200)
    text = "等洒家再去确认"
    result = covert_text_to_sound(text, output=f"{text***REMOVED***.mp3", output_folder="/home/jianl/1_code/personal/MovieMaker/output")
    print(result)
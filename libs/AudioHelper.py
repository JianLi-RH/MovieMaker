***REMOVED***

***REMOVED***
import TTSEngine
import TTSEngine.chat
import TTSEngine.xunfei_tts

def covert_text_to_sound(text, output, speaker, ttsengine="xunfei"):
    """
    将文字转换成语音

    Params:
        text: 文字
        output: 输出的语音文件
        speaker: 发音人
    Return:
        语音文件路径
    """

    if ttsengine=="xunfei":
        return TTSEngine.xunfei_tts.covert_text_to_sound(text=text, output=output, speaker=speaker)
    elif ttsengine=="chat":
        return TTSEngine.chat.covert_text_to_sound(text=text, output=output, speaker=speaker)

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

def get_sub_title_list(file):
    """根据文本文件生成字幕列表

    Params:
        file: 字幕文件
    Return:
        能被MovieMaker识别的字幕列表
    """

    if os.path.exists(file):
        ***REMOVED*** 处理字幕文件
        with open(file, 'r') as f:
            text = f.read()
            lines = re.split(r"\,|\.|\?|\;|\!|\，|\。|\？|\！|\t|\n|\r|\s", text)
    else:
        ***REMOVED*** 以分号分隔的字幕字符串
        lines = file.split(r'\;\s\,')

    basename = os.path.basename(file)
    new_lines = []
    subtitles = []
    for i in range(0, len(lines)):
        if lines[i].strip():
            sound = covert_text_to_sound(lines[i].strip(), f"{i***REMOVED***.mp3", basename)
            new_lines.append(f"- ['', '', '{lines[i].strip()***REMOVED***', '{sound***REMOVED***']\n")
            subtitles.append(['', '', lines[i].strip(), sound])

    new_path = os.path.join(os.path.dirname(file), os.path.basename(file).split('.')[0]+"_sound.txt")
    with open(new_path, 'w') as fn:
        fn.writelines(new_lines)
    print(f"字幕信息已写入文件: {new_path***REMOVED***")
    return subtitles

***REMOVED***
    ***REMOVED*** split_audio("水浒传/第六回/确认事实/等洒家再去确认.mp3", start=2200, length=2200)
    text = "等洒家再去确认"
    result = covert_text_to_sound(text, output_folder=f"/home/jianl/1_code/personal/MovieMaker/output/{text***REMOVED***.mp3", speaker="xiaoyan")
    print(result)
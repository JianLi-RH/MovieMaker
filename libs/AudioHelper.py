***REMOVED***

***REMOVED***


def split_audio(audio_file: str, length: int, start: 0):
    """截取音频文件
        新文件会保存在相同目录, 新文件名： 原文件名_bak.原文件后缀
    
    Params:
        audio_file: 原始音频文件
        length: 截取的片段长度, 单位毫秒
        start: 截取音频的开始位置
    """
    mp3 = AudioSegment.from_file(audio_file)
    new_audio = mp3[start: start + length] 
    file_name, file_extension =  os.path.splitext(audio_file)
    format = file_extension.replace(".", "")
    new_audio.export(file_name + "_bak" + file_extension, format=format)
    
***REMOVED***
    split_audio("resources/ShengYin/打他.mp3", 1500, 1500)
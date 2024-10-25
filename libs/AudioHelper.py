***REMOVED***
***REMOVED***

***REMOVED***
from pydub.utils import make_chunks


def split_audio(audio_file: str, length: int):
    """截取音频文件
        新文件会保存在相同目录, 新文件名： 原文件名_bak.原文件后缀
    
    Params:
        audio_file: 原始音频文件
        length: 截取的片段长度, 单位毫秒
    """
    mp3 = AudioSegment.from_file(audio_file)
    chunks = make_chunks(mp3, length)
    chunks_list = list(chunks)
    
    file_name, file_extension =  os.path.splitext(audio_file)
    format = file_extension.replace(".", "")
    chunks_list[0].export(file_name + "_bak" + file_extension, format=format)
    
***REMOVED***
    split_audio("resources/ShengYin/狗惨叫.mp3", 3500)
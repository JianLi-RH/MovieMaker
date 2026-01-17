"""
使用付费文自传语音服务： https://ttspro.cn/35.html

使用本引擎之前需要注册ttspro账号并充值
然后更新body中的user_email和user_pass
"""
import os
import requests

from logging_config import get_logger
logger = get_logger(__name__)

HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

body = {
    "user_email": "",
    "user_pass": "",
    "type": "getSpeek",
    "kbitrate": "audio-16khz-32kbitrate-mono-mp3"
}

speaker = [
    {"晓墨": "zh-CN-XiaomoNeural"}, # Female
    {"晓伊": "zh-CN-XiaoyiNeural"}, # Female
    {"晓辰": "zh-CN-XiaochenNeural"},   # Female
    {"晓涵": "zh-CN-XiaohanNeural"},    # Female
    {"晓梦": "zh-CN-XiaomengNeural"},   # Female
    {"晓柔": "zh-CN-XiaorouNeural"},    # Female
    {"晓睿": "zh-CN-XiaoruiNeural"},    # Female
    {"晓颜": "zh-CN-XiaoyanNeural"},    # Female
    {"晓悠": "zh-CN-XiaoyouNeural"},    # Female
    {"晓甄": "zh-CN-XiaozhenNeural"},   # Female
    {"晓晓": "zh-CN-XiaoxiaoNeural"},   # Female
    
    
    {"云希": "zh-CN-YunxiNeural"}, # Male
    {"云健": "zh-CN-YunjianNeural"}, # Male
    {"云扬": "zh-CN-YunyangNeural"}, # Male
    {"云夏": "zh-CN-YunxiaNeural"}, # Male ？？？ 女的？？？
    {"云杰": "zh-CN-YunjieNeural"}, # Male
    {"云泽": "zh-CN-YunzeNeural"},  # Male
    {"云登": "zh-CN-henan-YundengNeural"},  # Male
    {"云野": "zh-CN-YunyeNeural"},  # Male
    {"云逸": "zh-CN-YunyiMultilingualNeural"},  # Male
    {"云枫": "zh-CN-YunfengNeural"},    # Male
    {"云皓": "zh-CN-YunhaoNeural"}, # Male
]
role = ["YoungAdultFemale", "YoungAdultMale", "OlderAdultFemale", "OlderAdultMale", "SeniorFemale", "SeniorMale", "Girl", "Boy" ]
style = [ "embarrassed", "calm", "fearful", "cheerful", "disgruntled", "serious", "angry", "sad", "depressed", "affectionate", "gentle", "envious" ]


def get_ssml(speaker, text, role="YoungAdultMale", style="calm"):
    """
    取得发音人字符串
    
    Params:
        speaker: 发音人名字
        text: 需要发音的文本
        role: 发音人角色类型
        style: 语气
    Return:
        ssml text
    """
    return f"""
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
<voice name="{speaker}">
<mstts:express-as role="{role}" style="{style}">
<prosody rate="+20.00%">
{text}
</prosody>
</mstts:express-as>
</voice>
</speak>
"""


url = "https://ttspro.cn/getSpeek.php"


def covert_text_to_sound(text, output, speaker):
    """生成语音
    
    Params:
        text: 待生成语音的文本
        output： 语音文件保存路径
        speaker： 发音人名字， 可选值是speaker的value
    Returns:
        none
    """
    ssml = get_ssml(speaker, text, role="YoungAdultMale", style="calm")
    body["ssml"] = ssml
    
    response = requests.post(url, data=body, headers=HEADERS)
    
    if response.status_code == 200:
        logger.info(f"TTSpro生成语音成功: {response.text}")
        output_folder = os.path.dirname(output)
        os.makedirs(output_folder, exist_ok=True)
        with open(output, 'wb') as file:
            file.write(response.content)
    else:
        logger.error(f"TTSpro请求失败，状态码: {response.status_code}")
        logger.debug(f"SSML内容: {ssml}")
        logger.debug(f"响应内容: {response.content}")


if __name__ == "__main__":
    covert_text_to_sound("如今宋江已经占了俺四座大郡", "output/如今宋江已经占了俺四座大郡.mp3", speaker="zh-CN-XiaomoNeural")

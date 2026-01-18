from typing import List, Optional, Union

from character import Character
from libs.RenderHelper import RenderHelper

def Do(images : List[str], sorted_char_list : List[Character]):
    """向视频中插入一段背景音

    Params:
        images: 全部背景图片
        sorted_char_list: 排序后的角色

    Example:
        -
        名称: BGM
        字幕:
            - ['','', 'bgm', 'resources/ShengYin/bgm.mp3']
    """
    RenderHelper.render_characters_on_frames(images, sorted_char_list)
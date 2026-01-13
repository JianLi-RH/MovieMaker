from typing import List, Optional, Union

from character import Character
from libs import AudioHelper, ImageHelper

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
    l = len(images)
    for i in range(0, l):
        big_image = None
        for _char in sorted_char_list:
            if _char.display:
                _, big_image = ImageHelper.paint_char_on_image(image=images[i], 
                                                                image_obj=big_image,
                                                                char=_char, 
                                                                save=False,
                                                                gif_index=i)
        if big_image:
            big_image.save(images[i])
            big_image.close()
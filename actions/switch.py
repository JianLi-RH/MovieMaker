from typing import List, Optional, Union


from actions import get_char
from character import Character
import config_reader
from libs import AudioHelper, ImageHelper
    
def Do(*, action: any, images : List[str], sorted_char_list : List[Character]):
    """场景切换
    
    Params:
        action: Action instance
        images: 全部背景图片
        sorted_char_list: 排序后的角色
    
    Example:
        -
        名称: 转场
        背景: 背景  # 作为背景的角色名
        方式: 旋转缩小  # 转场方式， 目前支持： 旋转缩小
        字幕: 
            - ['','', 'bgm', 'resources/ShengYin/bgm.mp3']
    
    """     
    l = len(images)
    bg = get_char(action.obj.get("背景"), action.chars)
    other_chars = list(filter(lambda c: id(c) != id(bg), sorted_char_list))
    
    method = action.obj.get("方式", "旋转缩小")
    
    # steps = int(self.timespan * self.activity.fps)
    if method == "旋转缩小":
        degree = config_reader.round_per_second * 360   # 每秒旋转度数
        degree_per_step = degree / action.activity.fps    # 每一帧旋转度数
        step_x = config_reader.g_width / l / 2
        step_y = config_reader.g_height / l / 2
    
        for i in range(0, l):
            turn_image = None   # 需要旋转的图片
            for _char in other_chars:
                if _char.display:
                    _, turn_image = ImageHelper.merge_two_image(small_image=_char.image, 
                                                                size=_char.size,
                                                                pos=_char.pos,
                                                                big_image=bg.image,
                                                                big_image_obj=turn_image,
                                                                rotate=_char.rotate,
                                                                save=False)
            
            if turn_image:
                size = turn_image.size
                ratio = 1 - (i + 1)/ l
                new_size = [int(size[0] * ratio), int(size[1] * ratio)]
                if new_size[0] <= 0 or new_size[1] <= 0:
                    continue
                _, turn_image = ImageHelper.merge_two_image(small_image=turn_image, 
                                            size=new_size, 
                                            pos=[step_x * i, step_y * i], 
                                            big_image=images[i], 
                                            rotate=degree_per_step*i,
                                            save=False)

                turn_image.save(images[i])
                turn_image.close()
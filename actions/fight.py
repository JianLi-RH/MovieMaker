import random
from typing import List, Optional, Union


from actions import get_char, logger, walk
from character import Character
import config_reader
from exceptions import (
    CharacterNotFoundError,
    InsufficientCharactersError,
    MissingActionParameterError,
    InvalidSubtitleFormatError,
    TTSException
)

from libs.RenderHelper import RenderHelper
    
def Do(*, action: any, images : List[str], sorted_char_list : List[Character]):
    """一组随机的打斗动作， 
        因为不能保证相同渲染顺序的动作不使用同一个角色，所以不可以使用delay模式
    
    Params:
        images: 全部背景图片
        sorted_char_list: 排序后的角色
    
    Example:
    -
    名称: 打斗
    角色: 武松 西门庆 刀 剑 (前两个是人物，后面两个是武器，武器可以省略)
    幅度: 小    # 小， 中， 大
    字幕: 
    - ['','', '', 'resources/ShengYin/游戏中打斗声音音效.mp3']
    渲染顺序: 6
    
    Return:
        NA
    """
    str_chars = action.obj.get("角色")
    chars = [get_char(x, action.chars) for x in str_chars.split(" ")]
    if len(chars) < 2:
        logger.error(f"打斗动作角色数量不足: {len(chars)}")
        raise InsufficientCharactersError("打斗", 2, len(chars))
    chars = sorted(chars, key=lambda x: x.pos[0])
    
    amplitude = action.obj.get("幅度", "中")
    amplitude_value = 100
    if amplitude == "小":
        amplitude_value = 50
    elif amplitude == "中":
        amplitude_value = 100
    else:
        amplitude_value = 200

    delay_positions = []
    
    random_list1 = [random.randint(-amplitude_value, amplitude_value) for _ in range(3)]
    random_list2 = [random.randint(-amplitude_value, amplitude_value) for _ in range(3)]
    
    pos1 = (random_list1[0], random_list2[0])
    pos2 = (random_list1[1], random_list2[1])
    pos3 = (random_list1[2], random_list2[2])
    
    for i in range(0, len(chars)):
        action.char = chars[i]
        initial_pos = action.char.pos # 起始位置
        # 固定变化的3个位置
        if i % 2 == 0:
            xy_arr = (pos1, pos2, pos3)
        else:
            xy_arr = ((-pos1[0], -pos1[1]), (-pos2[0], -pos2[1]), (-pos3[0], -pos3[1]))
            
        action.obj["结束位置"] = [
            [action.char.pos[0] + xy_arr[0][0], action.char.pos[1] + xy_arr[0][1]],
            [action.char.pos[0] + xy_arr[1][0], action.char.pos[1] + xy_arr[1][1]],
            [action.char.pos[0] + xy_arr[2][0], action.char.pos[1] + xy_arr[2][1]],
            initial_pos]# 使角色恢复起始位置
        action.obj["方式"] = "旋转"
        pos = walk.Do(action=action, images=images, sorted_char_list=sorted_char_list, delay_mode=True)
        delay_positions.append({
            "char": action.char, 
            "position": pos
        })
    
    
    # Use RenderHelper for position-tracked rendering
    RenderHelper.render_with_position_tracking(images, delay_positions, sorted_char_list)
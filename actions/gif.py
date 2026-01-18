from typing import List, Optional, Union

from character import Character
from libs.RenderHelper import RenderHelper

    
def Do(*, action: any, images : List[str], sorted_char_list : List[Character], delay_mode : bool = False):
    """向视频中插入一段gif
    
    Params:
        action: Action instance
        images: 全部背景图片
        sorted_char_list: 排序后的角色
        delay_mode: 延迟绘制其他角色
    
    Example:
    -
    名称: gif
    素材: resources/SuCai/说话声/1.gif
    发音人引擎: 
    字幕: 
    - ['','', '小女孩哭泣声', 'resources/ShengYin/小女孩哭泣声.mp3']
    位置: [0.6, 0.2]
    图层: 100
    角度: 左右
    大小: [300, 300]
    
    Return:
        [[tmp_pos, tmp_size, rotate, img], [tmp_pos, tmp_size, rotate, img]]
    """
    action.obj.update({"名字": f"gif_{len(sorted_char_list)}", "显示": "是"})
    _char  = Character(action.obj)
    
    # 将GIF标记添加在显示列表中，用来设置显示顺序
    added_index = -1
    for i in range(len(sorted_char_list)):
        if sorted_char_list[i].index > _char.index:
            added_index = i
            sorted_char_list.insert(i, _char)
            break
    if added_index == -1:
        added_index = len(sorted_char_list)
        sorted_char_list.append(_char)

    l = len(images)
    delay_pos = []

    if delay_mode:
        # Build delay position list for GIF frames
        for i in range(0, l):
            j = i % len(_char.gif_frames)
            delay_pos.append((_char.pos, _char.size, _char.rotate, _char.gif_frames[j]))
    else:
        # Use RenderHelper for frame-by-frame rendering
        RenderHelper.render_characters_on_frames(images, sorted_char_list)
        # 恢复列表
        sorted_char_list.pop(added_index)

    return delay_pos
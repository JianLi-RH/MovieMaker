from typing import List, Optional, Union

from character import Character
from libs.RenderHelper import RenderHelper

def Do(*, action: any, images : List[str], sorted_char_list : List[Character], delay_mode : bool = False):
    """让角色转动，如左右转身，上下翻转，指定角度翻转
    
        延迟模式下返回角色运行轨迹, 否则返回空[]
    
    Example:            
        -
        名称: 转身
        角色: 镇关西
        持续时间: 
        角度: 270 # 左右, 上下， 45(逆时针角度), -45(顺时针) -- 如果是数字的话，会从初始位置旋转到给定角度
        字幕:
        - ['','', '啊啊啊', 'resources/ShengYin/惨叫-男1.mp3']
        渲染顺序: 0
        -
        名称: 转身
        角色: 鲁智深
        持续时间: 
        角度: [0, -30] # 转动一个范围
        比例: 1
        字幕:
        - ['','', '听说菜园里来了个新和尚', '水浒传/第九回/泼皮偷菜/听说菜园里来了个新和尚.mp3']
        渲染顺序: 1
        -
        名称: 转身
        角色: 鲁智深
        持续时间: 
        角度: [[0, -30],[-30, 0],[0, -30]] # 多角度转动，通常用于来回转动
        比例: 1
        字幕:
        - ['','', '听说菜园里来了个新和尚', '水浒传/第九回/泼皮偷菜/听说菜园里来了个新和尚.mp3']
        渲染顺序: 1
        
    Params:
        images: 全部背景图片
        sorted_char_list: 排序后的角色
        delay_mode: 延迟绘制其他角色
    Return:
        [[tmp_pos, tmp_size, rotate, img], [tmp_pos, tmp_size, rotate, img]]
    """
    
    str_degree = action.obj.get("角度", 0)
    delay_positions = []
    total_feames = len(images)
    action.char.display = True # 强制显示当前角色
    
    if isinstance(str_degree, int):
        str_degree = [action.char.rotate, str_degree]
    
    if isinstance(str_degree, list):
        # 连续转动
        start_rotate = action.char.rotate
        if isinstance(str_degree[0], list):
            steps = len(str_degree)
            step_frames = int(total_feames / steps)
            for i in range(steps):
                start = str_degree[i][0]
                end = str_degree[i][1]
                if i == (steps - 1):
                    # 最后一步占用剩余的全部图片
                    step_frames = total_feames - step_frames * i
                degree_step = (start - end) / step_frames
                for i in range(step_frames):
                    start_rotate += degree_step
                    delay_positions.append([action.char.pos, action.char.size, start_rotate])
            pass
        else:
            degree_step = (str_degree[1] - str_degree[0]) / total_feames
            for i in range(total_feames):
                start_rotate += degree_step
                delay_positions.append([action.char.pos, action.char.size, start_rotate])
    else:
        for i in range(total_feames):
            delay_positions.append([action.char.pos, action.char.size, action.char.rotate])
    
    if delay_mode:
        return delay_positions

    # Update character properties and render each frame
    for i in range(total_feames):
        # Update the turning character's properties for this frame
        for _char in sorted_char_list:
            if _char.name == action.char.name:
                RenderHelper.apply_character_properties(_char, delay_positions[i])

        # Render this specific frame with updated properties
        _, big_image = RenderHelper.render_characters_on_frame(
            images[i],
            sorted_char_list,
            gif_index=i
        )
        if big_image:
            big_image.save(images[i])
            big_image.close()

    return []
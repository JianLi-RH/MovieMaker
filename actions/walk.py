import random
from typing import List, Optional, Union
from PIL import Image, ImageOps


from actions import disappear, get_char, logger
from character import Character
import config_reader
from exceptions import (
    CharacterNotFoundError,
    InsufficientCharactersError,
    MissingActionParameterError,
    InvalidSubtitleFormatError,
    TTSException
)

from libs import AudioHelper, ImageHelper
import utils
    
def Do(*, action: any, images : List[str], sorted_char_list : List[Character], delay_mode : bool = False):
    """角色移动
        延迟模式下返回角色运行轨迹, 否则返回空[]
    
    Params:
        action: Action instance
        images: 全部背景图片
        sorted_char_list: 排序后的角色
        delay_mode: 延迟绘制其他角色
    
    Example:
        -
        名称: 行进
        角色: 鲁智深
        持续时间: 
        开始位置: 
        结束位置: [-0.2, 0.55]
        开始角度: 
        结束角度: 左右
        x: 
        y: 
        结束消失: 是
        结束图层: 8
        延迟: 
        比例:   # 比例变化，开始比例 - 结束比例
        方式:   # 自然 / 旋转 / 眩晕 / 45 -- 如果是数字的话，会从初始位置旋转到给定角度 , 最后恢复原样
        字幕: #Yunyang, Male
            - ['','', '跑路', 'resources/ShengYin/卡通搞笑逃跑音效.mp3']
        渲染顺序: 6
    
    Return:
        [[tmp_pos, tmp_size, rotate, img], [tmp_pos, tmp_size, rotate, img]]
    """
    if not action.char:
        logger.error(f"行进动作缺少角色，动作名称：{action.name}")
        raise CharacterNotFoundError("未指定角色")
    
    if action.obj.get("开始角度") != None:
        action.char.rotate = action.obj.get("开始角度")
        action.char = get_char(action.char.name, action.chars)
    
    start_pos = action.obj["开始位置"] if action.obj.get("开始位置", None) else action.char.pos
    start_pos = utils.covert_pos(start_pos)
    start_rotate = action.char.rotate
    # end_pos_list可以是一个固定位置， 如 [230, 120]，
    # 也可以是一组位置坐标， 如 [[230, 120]， [330, 180]， [450, 320]]
    end_pos_list = action.obj.get("结束位置", None)
    if not end_pos_list:
        act_obj = action.obj
        if not act_obj.get("x") and not act_obj.get("y"):
            logger.error("行进动作缺少必需参数：结束位置、x或y")
            raise MissingActionParameterError("行进", "结束位置/x/y")
        else:
            end_pos = action.char.pos[:]
            if act_obj["x"] != None:
                x = float(act_obj["x"])
                if abs(float(act_obj["x"])) <= 1:
                    x *= config_reader.g_width
                end_pos[0] += int(x)
            if act_obj["y"] != None:
                y = float(act_obj["y"])
                if abs(float(act_obj["y"])) < 1:
                    y *= config_reader.g_height
                end_pos[1] += int(y)
                
            end_pos_list = end_pos
    # ratio： 显示比例，可以有以下几种形式：
    # 0.4   --> 相对于开始时，最终的显示比例
    # [1, 0.4] --> 变化前后的显示比例
    # [[120, 200], [10, 12]] --> 变化前后的具体像素
    ratio = action.obj["比例"] if action.obj.get("比例") else 1
    mode = action.obj.get("方式", None)

    # 延迟执行动作，
    # 通常用在delay模式下，等待其他角色执行动作后再执行
    delay = action.obj.get("延迟", 0)
    if delay and utils.is_float(delay):
        delay_images_length = int(delay * config_reader.fps)
    else:
        delay_images_length = 0
        
    walk_images = images[delay_images_length:]

    img1 = Image.open(action.char.image)
    img_w, img_h = img1.size    # 角色图片的原始尺寸
    img1.close()
    
    # 计算每一帧的大小变化
    if isinstance(ratio, list):
        if isinstance(ratio[0], list) and isinstance(ratio[1], list): # [(180,220), (80,100)] -- 变化前后的具体像素
            ratio_x = (ratio[1][0] - ratio[0][0]) / len(walk_images)
            ratio_y = (ratio[1][1] - ratio[0][1]) / len(walk_images)
            start_size = ratio[0]
        else:   # [0.2, 0.2] -- 百分比
            ratio_x = (ratio[1] - ratio[0]) / len(walk_images)
            ratio_y = ratio_x
            start_size = [ratio[0] * img_w, ratio[0] * img_h]
    else:
        try:
            # ratio是最终显示比例， 如 0.4
            ratio = float(ratio)
        except:
            ratio = 1 # 默认比例不变
        ratio_x = (ratio - 1) / len(walk_images)
        ratio_y = ratio_x
        start_size = action.char.size
    
    # 强制转化为二维数组，使移动不止是直线运动
    if not isinstance(end_pos_list[0], list):
        if not isinstance(end_pos_list, float):
            action.char = get_char(action.char.name, action.chars)
        end_pos_list = [end_pos_list]

    steps = len(end_pos_list)
    frames = int(1/steps * len(walk_images)) # 平均分配每一个路线需要的帧数
    
    # mode ["自然", "旋转", "眩晕", 数字]:
    step_rotates = []
    total_image = len(walk_images)
    if mode == "旋转":
        _step_rotate = 360 * config_reader.round_per_second / action.activity.fps  # 每秒旋转圈数
        step_rotates = [action.char.rotate + num * _step_rotate for num in range(0, total_image)]
    elif mode == "眩晕":
        rotate_per_image = 45 / (action.activity.fps / 4) # 45度角来回摆动
        initial_degree = action.char.rotate
        for i in range(1, total_image + 1):
            if i % action.activity.fps > (action.activity.fps / 4) and i % action.activity.fps <= (action.activity.fps - action.activity.fps / 4):
                initial_degree += rotate_per_image
            else:
                initial_degree -= rotate_per_image
            step_rotates.append(initial_degree)
    elif isinstance(mode, int):
        _step_rotate = mode / action.timespan / action.activity.fps
        step_rotates = [action.char.rotate + num * _step_rotate for num in range(0, total_image)]
    else:
        step_rotates = [action.char.rotate] * total_image
    step_rotates[-1] = action.char.rotate # 最后一张图片恢复角色角度
        
    step_size = []
    for i in range(0, total_image):
        tmp_size = [int(start_size[0] * (1 + ratio_x * i)), int(start_size[1] * (1 + ratio_y * i))]
        step_size.append(tmp_size)
    
    step_pos = []
    current_pos = start_pos[:]
    for i in range(steps):    # 例如：[[120, 200], [10, 12]]
        if i == steps - 1:
            # 最后一步包含剩余的全部图片
            frames = len(walk_images) - (steps - 1) * frames

        end_pos = utils.covert_pos(end_pos_list[i])
        # 每一步在x,y方向的进度
        step_x = (end_pos[0] - current_pos[0]) / frames
        step_y = (end_pos[1] - current_pos[1]) / frames
        
        for j in range(0, frames):
            tmp_pos = [int(current_pos[0] + step_x * j), int(current_pos[1] + step_y * j)]
            step_pos.append(tmp_pos)
        current_pos = end_pos # 重新设置轨迹的开始坐标
    
    pos = [] # 每一个元素：(tmp_pos, tmp_size, rotate)
    total_image_length = len(images)
    for i in range(total_image_length):
        if i < delay_images_length:
            if action.char.display:
                pos.append((start_pos, start_size, start_rotate))
            else:
                pos.append(())
        else:
            # 重新开始计数
            new_step = i - delay_images_length
            pos.append((step_pos[new_step], step_size[new_step], step_rotates[new_step]))
    
    action.char.display = True # 强制显示当前角色
    
    if action.obj.get("结束角度") != None:
        basename = os.path.basename(action.char.image)
        if "rotate_" in basename and action.obj.get("结束角度") == "左右":
            pos[-1] = (pos[-1][0], pos[-1][1], 0)
        else:
            pos[-1] = (pos[-1][0], pos[-1][1], action.obj.get("结束角度"))
    
    if delay_mode:
        if action.obj.get("结束角度"):
            action.char.rotate = action.obj.get("结束角度")
        if action.obj.get("结束图层"):
            action.char.render_index = action.obj.get("结束图层")
        action.char.pos = pos[-1][0]
        action.char.size = pos[-1][1]
        action.char = get_char(action.char.name, action.chars)
        return pos
    
    for i in range(total_image_length):
        if i == (total_image_length - 1):
            if action.obj.get("结束角度"):
                action.char.rotate = action.obj.get("结束角度")
                action.char = get_char(action.char.name, action.chars)
            if action.obj.get("结束图层"):
                action.char.render_index = action.obj.get("结束图层")
                action.char = get_char(action.char.name, action.chars)
        
        big_image = None
        for _char in sorted_char_list:
            if _char.name == action.char.name:
                _char.pos = pos[i][0]
                _char.size = pos[i][1]
                _char.rotate = pos[i][2]
            if _char.display:
                _, big_image = ImageHelper.paint_char_on_image(char=_char, 
                                                                image=images[i],
                                                                image_obj=big_image,
                                                                save=False,
                                                                gif_index=i)
        if big_image:
            big_image.save(images[i])
            big_image.close()
    
    if action.obj.get("结束消失", "否") == "是":
        disappear.Do(action)
        
    return []
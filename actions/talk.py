from typing import List, Optional, Union


from actions import get_char, camera
from character import Character
from libs import ImageHelper
import utils
    
def Do(*, action: any, images : List[str], sorted_char_list : List[Character], delay_mode : bool = False):
    """角色说话
        
    Params:
        action: Action instance
        images: 背景图片
        sorted_char_list: 排序后的角色
        delay_mode: 延迟绘制其他角色
    
    Example:
    -
    名称: 说话
    角色: 鲁智深
    焦点: [0.05, 0.65]  # 焦点 和 变化 不能同时设置，变化的优先级更高
    角色名牌: 是
    高亮: 是
    变化:  # 可以是： 1, 空值, 这种情况人物会上下跳动5个像素; 2, (0 - 1)数字实现拉近效果; 3, 近景； 4, 一组新图片； 5, 震惊
    字幕: #Yunyang, Male
        - ['','', '你这斯诈死', '水浒传/第四回/打死镇关西/你这斯诈死.mp3']
        - ['','', '等我回家再与你理会', '水浒传/第四回/打死镇关西/等我回家再与你理会.mp3']
    渲染顺序: 0
    -
    名称: 说话
    角色: 宋江
    焦点: 
    高亮: 
    角色名牌: 是
    变化: 
        - 水浒传/人物/宋江3.png
        - 水浒传/人物/宋江4.png
    字幕: 
    - ['','', '宋江在此谢谢各位好汉相救', '水浒传/第一百六回/商议报仇/宋江在此谢谢各位好汉相救.mp3']
    - ['','', '只恨黄文炳至今逍遥自在', '水浒传/第一百六回/商议报仇/只恨黄文炳至今逍遥自在.mp3']
    渲染顺序: 1

    Return:
        [[tmp_pos, tmp_size, rotate, img], [tmp_pos, tmp_size, rotate, img]]
    """
    if delay_mode:
        return [(action.char.pos, action.char.size, action.char.rotate) for i in range(len(images))]
    
    # 强制显示角色
    action.char.display = True
    
    hightlight = action.obj.get("高亮") == "是"
    gif_index = 0
    
    # 为角色说话做准备
    pos = action.char.pos[:]
    size = action.char.size[:]
    initial = True
    img_index = 0
    initial_char_img = action.char.image
    char_images = action.obj.get("变化") # 只有当变化是多个图片时才有用
            
    # for img in images:
    total_image = len(images)
    for i in range(total_image):
        img = images[i]
        big_image = None
        if hightlight:
            big_image = ImageHelper.dark_image(img)
        
        if not action.obj.get("变化", None) and not action.obj.get("焦点", None):
            # 当没有设置 变化 和 焦点 的时候
            # 让角色说话的时候有上下跳动的感觉 
            if initial:
                action.char.pos[1] -= 5
            else:
                action.char.pos[1] += 5
            initial = not initial
        elif isinstance(action.obj.get("变化"), list):
            # 当 变化 是一组图片的时候
            # 使用多个图片，实现角色说话的效果
            if img_index == len(char_images):
                img_index = 0
            action.char.image = char_images[img_index]
            img_index += 1
        elif action.obj.get("变化") == "震惊":
            # 角色最多拉长当前y坐标的50%
            action.char.pos[1] -= pos[1] * 0.5 * i / total_image
            action.char.size[1] += pos[1] * 0.5 * i / total_image
        
        for _char in sorted_char_list:
            if _char.display:
                dark = False
                if hightlight and _char.name != action.char.name:
                    dark = True
                _, big_image = ImageHelper.paint_char_on_image(image=img, 
                                                                image_obj=big_image,
                                                                char=_char, 
                                                                save=False,
                                                                gif_index=gif_index,
                                                                dark=dark)
                
                if _char.name == action.char.name and action.obj.get("角色名牌"):
                    big_image = ImageHelper.display_char_name(action.char, big_image, name=action.obj.get("角色名牌"))

        if big_image:
            big_image.save(img)
            big_image.close()
        gif_index += 1

    action.char.pos = pos
    action.char.size = size
    action.char.image = initial_char_img

    if action.obj.get("变化", None):
        if isinstance(action.obj.get("变化"), float):
            # 图片有缩放的时候才需要调用镜头方法
            camera.Do(action=action, images=images, add_chars=False)
        elif action.obj.get("变化") == "近景":
            for img in images:
                ImageHelper.cut_image(img, action.char)
            
    elif action.obj.get("焦点", None):
        if isinstance(action.obj.get("焦点"), str):
            _focusChar = get_char(action.obj.get("焦点"), action.chars)
            if _focusChar:
                x = _focusChar.pos[0] - 50 if _focusChar.pos[0] > 50 else 0
                y = _focusChar.pos[1] - 50 if _focusChar.pos[1] > 50 else 0
                focus = [x, y]
        else:
            focus = utils.covert_pos(action.obj.get("焦点", None))

        if focus:
            for img in images:
                ImageHelper.cut_image_by_focus(img, focus)
    return []
from typing import List, Optional, Union

from libs import AudioHelper, ImageHelper
import utils

            
def Do(*, images : List[str], action: any, add_chars : bool=True):
    """
    处理 `镜头` 相关的动作，例如切换焦点，镜头拉近、拉远
    ***一个活动中不能有两个`镜头`动作***
    
    Params:
        images: 一组背景图片
        action: Action instance
        add_chars: 如果仅仅针对背景图片切换镜头则设置False, 如果动作包含角色，需要设置True
    
    Example:
    -
        名称: 镜头
        角色: 高俅
        持续时间: 
        焦点: [0.53, 0.68]
        变化: 0.3
        字幕: 
        - ['','', '有如此大船', '水浒传/第二百一十九回/叶春/有如此大船.mp3']
        - ['','', '梁山可破矣', '水浒传/第二百一十九回/叶春/梁山可破矣.mp3']
        渲染顺序: 12
    """
    length = len(images)    # 总帧数
    if not action.activity.scenario.focus:
        action.activity.scenario.focus = "中心"
    original_center = utils.covert_pos(action.activity.scenario.focus)  # 原有的焦点

    if action.obj.get("焦点", None):
        new_center = utils.covert_pos(action.obj.get("焦点"))
    else: 
        if action.char:
            x, y = action.char.pos
            w, h = action.char.size
            new_center = [(x + w / 2), (y + h / 2)]
        else:
            new_center = original_center

    step_x = (new_center[0] - original_center[0]) / length
    step_y = (new_center[1] - original_center[1]) / length

    ratio = action.obj.get("变化")
    if isinstance(ratio, float):
        ratio = [1, ratio]
    from_ratio = ratio[0]
    to_ratio = ratio[1]
    ratio_step = (to_ratio - from_ratio) / length
    
    action.activity.scenario.ratio = to_ratio
    
    if add_chars:
        # 单独调用镜头动作的时候，需要绘制角色
        gif_index = 0
        for img in images:
            big_image = None
            for _char in action.activity.scenario.chars:
                if _char.display:
                    _, big_image = ImageHelper.paint_char_on_image(image=img, 
                                                                image_obj=big_image,
                                                                char=_char, 
                                                                save=False,
                                                                gif_index=gif_index,
                                                                dark=False)
        
            if big_image:
                big_image.save(img)
                big_image.close()
            gif_index += 1

    for i in range(0, length):
        tmp_ratio = from_ratio + ratio_step * i
        x = original_center[0] + step_x * i
        y = original_center[1] + step_y * i

        tmp_img = ImageHelper.zoom_in_out_image(images[i], center=(x, y), ratio=tmp_ratio)
        images[i] = tmp_img
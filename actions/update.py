from actions import get_char

import utils


def Do(action: any):
    """更新某个角色
    
    Params:
        action: Action instance
        images: 全部背景图片
        sorted_char_list: 排序后的角色
    
    Example:
    -
        名称: 更新
        角色: 鲁智深
        素材: 水浒传/人物/鲁智深1.png
        角度: 左右
        透明度: 0.2
        字幕: #Kangkang, Male
            - ['','', '啪啪啪', 'resources/ShengYin/打耳光.mp3']
        渲染顺序: 2
    """
    keys = action.obj.keys()
    if "素材" in keys:
        action.char.image = action.obj.get("素材", None)
    if "位置" in keys:
        action.char.pos = utils.covert_pos(action.obj.get("位置", None))
    if "大小" in keys:
        action.char.size = action.obj.get("大小")
    if "角度" in keys:
        action.char.rotate = action.obj.get("角度")
    if "透明度" in keys:
        action.char.transparency = action.obj.get("透明度")
    if "显示" in keys:
        action.char.display = True if action.obj.get("显示") == '是' else False
    if "图层" in keys:
        action.char.index = int(action.obj.get("图层", 0))
        
    action.char = get_char(action.char.name, action.chars)
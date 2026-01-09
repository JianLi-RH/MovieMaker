from actions import get_char, get_logger



def Do(action: any):
    """让角色消失
    
    Params:
        action: Action instance
    
    Example:
        -
        名称: 消失
        角色: 花荣 宋江 燕顺 王英 郑天寿
        渲染顺序: 1
        -
        名称: 消失
        角色: 花荣
        渲染顺序: 2
    """
    if ' ' in action.obj.get("角色"):
        str_chars = action.obj.get("角色")
        for str_char in str_chars.split(" "):
            c = get_char(str_char)
            if c:
                c.display = False
    else:
        action.char.display = False
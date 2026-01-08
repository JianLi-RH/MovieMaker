import os

from typing import List, Optional, Union
from PIL import Image, ImageOps

from character import *
from logging_config import get_logger
from exceptions import (
    CharacterNotFoundError,
    InsufficientCharactersError,
    MissingActionParameterError,
    InvalidSubtitleFormatError,
    TTSException
)


# 获取日志记录器
logger = get_logger(__name__)

def get_char(name: str, chars: List[Character]):
    """查找指定名称的角色
    
    Params:
        name: 待查找的角色名
        chars: 角色列表
        
    Return:
        Character
    """
    if not name:
        return None
    if ' ' in name:
        # 打斗等组合动作可以同时操作多个角色
        # 因此不能在这里获取角色
        return None
    for c in chars:
        if c.name == name:
            if c.rotate == "左右" and not c.name.lower().startswith("gif"):
                basename = os.path.basename(c.image)
                if "rotate_" in basename:
                    basename = basename.replace("rotate_", "")
                else:
                    basename = f"rotate_{basename}"
                new_path = os.path.join(os.path.dirname(c.image), basename)
                if not os.path.exists(new_path):
                    im_mirror = ImageOps.mirror(Image.open(c.image))
                    im_mirror.save(new_path)
                c.image = new_path
                c.rotate = 0
            elif c.rotate == "上下":
                c.rotate = 180

            return c

    return None
#!/usr/bin/python3
"""
这个类用来解析script.yaml中的`场景:`
"""
import os
import shutil

import activity
import character
import copy
import config_reader
from libs import ImageHelper, SuCaiHelper


class Scenario:
    """The scenario class"""

    def __create_bg_image(self, original_image):
        """根据场景中的背景图创建新的背景

        Params:
            original_image: 原始图片
        Return:
            处理好的图片
        """
        if original_image.lower().endswith(".gif"):
            return original_image
        new_path = os.path.join(config_reader.output_dir, os.path.basename(original_image))
        if self.dark: # 先不判断值
            if isinstance(self.dark, int):
                obj = ImageHelper.dark_image(original_image, reduce_light=self.dark)
            else:
                obj = ImageHelper.dark_image(original_image)
            obj.save(new_path)
        else:
            shutil.copy(original_image, new_path)
        ImageHelper.resize_image(new_path)
        return ImageHelper.zoom_in_out_image(new_path, self.focus, self.ratio)

    def __init__(self, obj, preview=False):
        """初始化场景
        
        Params:
            obj: yaml对象
            preview： 是否仅用于预览
        Returns:
            none
        """
        
        self.name = obj.get("名字", None)
        self.focus = obj.get("焦点", "中心")    # 镜头对准的中心点
        self.ratio = float(obj.get("比例", 1)) # 显示背景图片的比例 （注意总大小仍然在config.ini中配置）
        self.dark = obj.get("天色", None)   # 增加背景图片暗度
        self.background_image = self.__create_bg_image(SuCaiHelper.get_material(obj.get("背景")))
        self.bgm = obj.get("背景音乐", None)
        __chars = []
        __char_obj = obj.get("角色") if obj.get("角色") else []
        for char_obj in __char_obj:
            _pos = char_obj.get("位置", None)
            if isinstance(_pos, list) and isinstance(_pos[0], list):
                i = 0
                for p in _pos:
                    _obj = copy.deepcopy(char_obj)
                    _obj["名字"] = char_obj.get("名字") + str(i)
                    _obj["位置"] = p
                    __chars.append(character.Character(_obj))
                    i += 1
            else:
                _char = character.Character(char_obj)
                __chars.append(_char)
        self.chars = sorted(__chars, key=lambda x: x.index)
        self.activities = []
        if not preview:
            for a in obj.get("活动", None):
                self.activities.append(activity.Activity(self, a))
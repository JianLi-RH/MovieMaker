#!/usr/bin/python3
"""
这个类用来解析script.yaml中的`场景:`
"""
import os
import shutil

import activity
import character
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
        self.background_image = self.__create_bg_image(obj.get("背景", None))
        self.bgm = obj.get("背景音乐", None)
        __chars = [character.Character(char) for char in obj.get("角色", [])]
        self.chars = sorted(__chars, key=lambda x: x.index)
        self.activities = []
        if not preview:
            for a in obj.get("活动", None):
                self.activities.append(activity.Activity(self, a))
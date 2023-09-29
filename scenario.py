***REMOVED***.10
"""
这个类用来解析script.yaml中的`场景:`
"""
***REMOVED***

import activity
import character
import config_reader
from libs import ImageHelper, SuCaiHelper


class Scenario:
    """The scenario class"""

    def __create_bg_image(self, origin_img):
***REMOVED***根据场景中的背景图创建新的背景

***REMOVED***
            origin_img: 原始图片
        Return:
            处理好的图片
***REMOVED***
        original_image = SuCaiHelper.get_sucai(origin_img)
        if original_image.lower().endswith(".gif"):
            return original_image
        new_path = os.path.join(config_reader.output_dir, os.path.basename(original_image))
        return ImageHelper.zoom_in_out_image(original_image, self.focus, self.ratio, new_path)

    def __init__(self, obj):
        self.name = obj.get("名字", None)
        self.focus = obj.get("焦点", "中心")    ***REMOVED*** 镜头对准的中心点
        self.ratio = obj.get("比例", 1) ***REMOVED*** 显示背景图片的比例 （注意总大小仍然在config.ini中配置）
        self.background_image = self.__create_bg_image(obj.get("背景", None))
        self.bgm = SuCaiHelper.get_shengyin(obj.get("背景音乐", None))

        self.chars = []
        chars = obj.get("角色", None)
        if chars:
            for c in obj.get("角色", None):
                self.chars.append(character.Character(c))

        self.activitys = []
        for a in obj.get("活动", None):
            self.activitys.append(activity.Activity(self, a))
***REMOVED***.10
"""
这个类用来解析script.yaml中的`场景:`
"""
import activity
import character
from libs import SuCaiHelper


class Scenario:
    """The scenario class"""

    def __init__(self, obj):
        self.background_image = SuCaiHelper.get_sucai(obj.get("背景", None))
        self.focus = obj.get("焦点", "中心")    ***REMOVED*** 镜头对准的中心点
        self.ratio = obj.get("比例", 1) ***REMOVED*** 显示背景图片的比例 （注意总大小仍然在config.ini中配置）

        self.chars = []
        for c in obj.get("角色", None):
            self.chars.append(character.Character(c))

        self.activitys = []
        for a in obj.get("活动", None):
            self.activitys.append(activity.Activity(self, a))
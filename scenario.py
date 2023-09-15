***REMOVED***.10
"""
这个类用来解析script.yaml中的`场景:`
"""
***REMOVED***

import yaml

import activity
import character
import config_reader
from libs import SuCaiHelper, VideoHelper


class Scenario:
    """The scenario class"""

    def __init__(self, obj):
        self.background_image = SuCaiHelper.get_sucai(obj["背景"])
        self.focus = obj.get("焦点", "中心")    ***REMOVED*** 镜头对准的中心点
        self.ratio = obj.get("比例", 1) ***REMOVED*** 显示背景图片的比例 （注意总大小仍然在config.ini中配置）

        self.chars = []
        for c in obj.get("角色"):
            self.chars.append(character.Character(c))

        self.activitys = []
        for a in obj["活动"]:
            self.activitys.append(activity.Activity(self, a))

***REMOVED***
    with open('script.yaml', 'r') as file:
        script = yaml.safe_load(file)

        scenarios = script["场景"]
        videos = []
        for i in range(0, len(scenarios)):
            scenario = Scenario(scenarios[i])
            for j in range(0, len(scenario.activitys)):
                video = scenario.activitys[j].to_video()
                videos.append(video)

        VideoHelper.concatenate_videos(*videos).write_videofile(os.path.join(config_reader.output_dir, "final.mp4"))
    pass
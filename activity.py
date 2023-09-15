"""
这个类用来解析script.yaml中的`活动:`
"""
import yaml

import utils
from action import *
from libs import SuCaiHelper


class Activity:
    """The Activity(活动) class"""

    def __create_bg_image(self):
        original_image = self.scenario.background_image
        if original_image.lower().endswith(".gif"):
            return original_image
        focus = self.scenario.focus
        ratio = self.scenario.ratio
        return ImageHelper.zoom_in_out_image(original_image, focus, ratio)

    def __check_images(self):
***REMOVED***第一次执行action的时候, images会是空的, 所以需要生成一组图片

        Return:
            一组图片
***REMOVED***
        path = os.path.join(config_reader.output_dir, self.name)
        if not os.path.exists(path):
            os.mkdir(path)

        images = []
        background_image = self.__create_bg_image()
        if background_image.lower().endswith(".gif"):
            bg_frames = ImageHelper.get_frames_from_gif(background_image)

            for i in range(0, self.total_frame):
                index = i % len(bg_frames)
                ext = bg_frames[index].split('.')[-1]
                new_path = os.path.join(path, f"{i***REMOVED***.{ext***REMOVED***")
                shutil.copy(bg_frames[index], new_path)
                Image.open(new_path).resize((config_reader.g_width, config_reader.g_height)).save(new_path)
                images.append(new_path)
        else:
            ext = background_image.split('.')[-1]
            for i in range(0, self.total_frame):
                new_path = os.path.join(path, f"{i***REMOVED***.{ext***REMOVED***")
                shutil.copy(background_image, new_path)
                Image.open(new_path).resize((config_reader.g_width, config_reader.g_height)).save(new_path)
                images.append(path)

        return images

    def __init__(self, scenario, obj):
***REMOVED***
        初始化Activity

        Param:
            scenario: Scenario对象实例
            obj: script里面的脚本片段
***REMOVED***
        self.scenario = scenario
        self.timespan = utils.get_time(obj.get("持续时间"))   ***REMOVED*** 单位：秒
        self.total_frame = int(self.timespan * config_reader.fps)   ***REMOVED*** 根据当前活动的总时长，得到当前活动所需的视频帧数
        self.name = obj.get("名字")
        self.description = obj.get("描述", "")
        self.bgm = SuCaiHelper.get_shengyin(obj.get("背景音乐", None))
        self.subtitle = obj.get("字幕", None)
        self.actions = []
        for action in obj["动作"]:
            self.actions.append(Action(self, action, self.timespan))

    def to_video(self):
***REMOVED***
        将‘活动’转换成视频

        Return:
            视频片段clip
***REMOVED***
        images = self.__check_images()

        char_in_actions = []
        for action in self.actions:
            if action.char:
                action.char.display = True
                char_in_actions.append(action.char.name)
            images = action.to_video(images)

        ***REMOVED*** 先在背景图片上显示非action的角色 （这样的好处是action的角色可以覆盖这种角色）
        for char in self.scenario.chars:
            if not char.name in char_in_actions:
                if char.display:
                    for i in range(len(images)):
                        images[i] = ImageHelper.merge_two_image(images[i], char.image, char.size, char.pos, overwrite=True)

        ***REMOVED*** 先把图片转换成视频
        video = VideoHelper.create_video_clip_from_images(images, self.timespan)
        if self.bgm:
            video = VideoHelper.add_audio_to_video(video, self.bgm)

        if self.subtitle:
            pass

        return video

***REMOVED***
    with open('script.yaml', 'r') as file:
       script = yaml.safe_load(file)

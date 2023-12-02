"""
这个类用来解析script.yaml中的`动作:`
"""
import shutil

from moviepy.editor import *
from PIL import Image, ImageOps

import config_reader
import utils
from character import *
from libs import ImageHelper, SuCaiHelper, VideoHelper


class Action:
    """The Action(动作) class"""

    def __get_char(self, name):
        """查找指定名称的角色"""
        for c in self.activity.scenario.chars:
            if c.name == name:
                return c
        return None

    def __display(self, images):
        """将当前动作的角色显示在背景上"""
        self.char.display = True
        return images

    def __disappear(self, images):
        """让角色消失"""
        self.char.display = False
        return images

    def __camera(self, images):
        """
        处理 `镜头` 相关的动作，例如切换焦点，镜头拉近、拉远
        ***一个活动中不能有两个`镜头`动作***
        """
        original_center = utils.covert_pos(self.activity.scenario.focus)  # 原有的焦点
        self.activity.scenario.focus = self.obj.get("焦点", "中心") # 新焦点
        center = utils.covert_pos(self.activity.scenario.focus)

        step_x = (center[0] - original_center[0]) / self.activity.total_frame
        step_y = (center[1] - original_center[1]) / self.activity.total_frame

        from_ratio=self.obj.get("变化")[0]
        to_ratio=self.obj.get("变化")[1]
        self.activity.scenario.ratio = to_ratio

        for i in range(0, self.activity.total_frame):
            if from_ratio > to_ratio:
                # 缩小
                tmp_ratio = from_ratio - (from_ratio - to_ratio) * i / self.activity.total_frame
            else:
                # 放大
                tmp_ratio = from_ratio + (to_ratio - from_ratio) * i / self.activity.total_frame

            x = original_center[0] + step_x * i
            y = original_center[1] + step_y * i

            tmp_img = ImageHelper.zoom_in_out_image(images[i], center=(x, y), ratio=tmp_ratio)
            images[i] = tmp_img

        return images

    def __turn(self, images):
        """让角色转动，如左右转身，上下翻转，指定角度翻转"""
        str_degree = self.obj.get("度数", 0)
        if str_degree == "左右":
            im_mirror = ImageOps.mirror(Image.open(self.char.image))
            basename = os.path.basename(self.char.image)
            new_path = os.path.join(os.path.dirname(images[-1]), basename)
            im_mirror.save(new_path)
            self.char.image = new_path
        elif str_degree == "上下":
            self.char.rotate = 180
        else:
            self.char.rotate = int(str_degree)
        l = len(images)
        for i in range(0, l):
            ImageHelper.merge_two_image(
                    images[i],
                    self.char.image,
                    pos=self.char.pos,
                    size=self.char.size,
                    rotate=self.char.rotate,
                    overwrite=True
                )
        return images

    def __walk(self, images):
        """角色移动

        Params:
            previous_video: 上一个视频片段
        Return:
            全部图片地址
        """
        start_pos = self.obj["开始位置"] if self.obj.get("开始位置", None) else self.char.pos
        start_pos = utils.covert_pos(start_pos)
        end_pos = utils.covert_pos(self.obj["结束位置"])
        ratio = self.obj["比例"]
        mode = self.obj["方式"]

        pos = [] # 每一个元素：(tmp_pos, tmp_size, rotate)
        img1 = Image.open(self.char.image)
        img_w, img_h = img1.size    # 角色图片的原始尺寸

        # 每一步在x,y方向的进度以及缩放比例
        step_x = (end_pos[0] - start_pos[0]) / self.activity.total_frame
        step_y = (end_pos[1] - start_pos[1]) / self.activity.total_frame
        if not ratio[0]:
            ratio[0] = self.char.size
        if isinstance(ratio[0], list): # [(100,120), (100,120) -- 具体像素
            step_ration_x = (ratio[1][0] - ratio[0][0]) / self.activity.total_frame
            step_ration_y = (ratio[1][1] - ratio[0][1]) / self.activity.total_frame
            start_size = ratio[0]
        else:   # [0.2, 0.2] -- 百分比
            step_ration_x = (ratio[1] - ratio[0]) / self.activity.total_frame * img_w
            step_ration_y = (ratio[1] - ratio[0]) / self.activity.total_frame * img_h
            start_size = (ratio[0] * img_w, ratio[0] * img_h)
        step_ration = (step_ration_x, step_ration_y)

        if mode in ["自然", "旋转"]:
            for i in range(0, self.activity.total_frame):
                tmp_size = (int(start_size[0] + step_ration[0] * i), int(start_size[1] + step_ration[1] * i))
                tmp_pos = (int(start_pos[0] + step_x * i), int(start_pos[1] + step_y * i))
                rotate = None
                if mode == "旋转":
                    step_rotate = 360 / self.activity.total_frame * int(config_reader.round_per_second)  # 每秒转5圈
                    rotate = step_rotate * i
                    if i == self.activity.total_frame - 1:
                        # 最后一圈摆正
                        rotate = 0
                pos.append((tmp_pos, tmp_size, rotate))

        image_clips = []
        path = os.path.join(config_reader.output_dir, self.activity.name)
        if not os.path.exists(path):
            os.mkdir(path=path)
        for i in range(0, self.activity.total_frame):
            self.char.pos = pos[i][0]
            self.char.size = pos[i][1]
            rotate = None
            if len(pos[i]) == 3:
                rotate = pos[i][2]
            j = i % self.activity.total_frame
            img = ImageHelper.merge_two_image(images[j], self.char.image, pos=self.char.pos, size=self.char.size, rotate=rotate)
            ext = img.split('.')[-1]
            _path = os.path.join(path, f"{i}.{ext}")
            if os.path.exists(_path):
                os.remove(_path)
            shutil.move(img, _path)
            image_clips.append(_path)
        return image_clips

    def __gif(self, images):
        """向视频中插入一段gif
        """
        gif_images = ImageHelper.get_frames_from_gif(self.obj.get("素材"))

        img1 = Image.open(images[0])
        img_w, img_h = img1.size
        pos = self.obj.get("位置")
        pos[0] = pos[0] if pos[0] > 1 else int(pos[0] * img_w)
        pos[1] = pos[1] if pos[1] > 1 else int(pos[1] * img_h)

        gif1 = Image.open(gif_images[0])
        gif_w, gif_h = gif1.size
        gif_ratio = self.obj.get("比例")

        str_degree = self.obj.get("度数", 0)

        l = len(images)
        for i in range(0, l):
            j = i % len(gif_images)

            if str_degree == "左右":
                im_mirror = ImageOps.mirror(Image.open(gif_images[j]))
                basename = os.path.basename(gif_images[j])
                new_path = os.path.join(os.path.dirname(images[-1]), basename)
                im_mirror.save(new_path)
                gif_images[j] = new_path
                rotate = 0
            elif str_degree == "上下":
                rotate = 180
            else:
                rotate = int(str_degree)

            ImageHelper.merge_two_image(
                    images[i],
                    gif_images[j],
                    pos=pos,
                    size=(int(gif_w * gif_ratio), int(gif_h * gif_ratio)),
                    rotate=rotate,
                    overwrite=True
                )
        return images

    def __init__(self, activity, obj, timespan):
        self.activity = activity
        self.obj = obj
        if self.obj.get("名称", None) != '更新':
            self.char = self.__get_char(self.obj.get("角色", None))
        else:
            self.char = None
        self.timespan = timespan

    def to_video(self, images):
        """
        根据当前动作脚本生成视频所需的图片

        Params:
            images: a list of images
        Return:
            一组视频所需的图片
        """

        action = self.obj.get("名称")
        if action == "显示":
            return self.__display(images)
        if action == "消失":
            return self.__disappear(images)
        elif action == "镜头":
            return self.__camera(images)
        elif action == "行进":
            return self.__walk(images)
        elif action == "转身":
            return self.__turn(images)
        elif action == "gif":
            return self.__gif(images)
        pass


if __name__ == "__main__":
    pass
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
***REMOVED***查找指定名称的角色"""
        for c in self.activity.scenario.chars:
            if c.name == name:
                return c
        return None

    def __display(self, images):
***REMOVED***将当前动作的角色显示在背景上"""
        self.char.display = True
        return images

    def __disappear(self, images):
***REMOVED***让角色消失"""
        self.char.display = False
        return images

    def __camera(self, images):
***REMOVED***
        处理 `镜头` 相关的动作，例如切换焦点，镜头拉近、拉远
        ***一个活动中不能有两个`镜头`动作***
***REMOVED***
        original_center = utils.covert_pos(self.activity.scenario.focus)  ***REMOVED*** 原有的焦点
        self.activity.scenario.focus = self.obj.get("焦点", "中心") ***REMOVED*** 新焦点
        center = utils.covert_pos(self.activity.scenario.focus)

        step_x = (center[0] - original_center[0]) / self.activity.total_frame
        step_y = (center[1] - original_center[1]) / self.activity.total_frame

        from_ratio=self.obj.get("变化")[0]
        to_ratio=self.obj.get("变化")[1]
        self.activity.scenario.ratio = to_ratio

        for i in range(0, self.activity.total_frame):
            if from_ratio > to_ratio:
                ***REMOVED*** 缩小
                tmp_ratio = from_ratio - (from_ratio - to_ratio) * i / self.activity.total_frame
***REMOVED***
                ***REMOVED*** 放大
                tmp_ratio = from_ratio + (to_ratio - from_ratio) * i / self.activity.total_frame

            x = original_center[0] + step_x * i
            y = original_center[1] + step_y * i

            tmp_img = ImageHelper.zoom_in_out_image(images[i], center=(x, y), ratio=tmp_ratio)
            ImageHelper.resize_image(tmp_img)
            images[i] = tmp_img

        return images

    def __turn(self, images):
***REMOVED***让角色转动，如左右转身，上下翻转，指定角度翻转"""
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
***REMOVED***角色移动

***REMOVED***
            previous_video: 上一个视频片段
        Return:
            全部图片地址
***REMOVED***
        start_pos = self.obj["开始位置"] if self.obj.get("开始位置", None) else self.char.pos
        start_pos = utils.covert_pos(start_pos)
        ***REMOVED*** end_pos_list可以是一个固定位置， 如 [230, 120]，
        ***REMOVED*** 也可以是一组位置坐标， 如 [[230, 120]， [330, 180]， [450, 320]]
        end_pos_list = self.obj["结束位置"]
        ***REMOVED*** ratio： 显示比例，可以有以下几种形式：
        ***REMOVED*** 0.4   --> 相对于开始时，最终的显示比例
        ***REMOVED*** [1, 0.4] --> 变化前后的显示比例
        ***REMOVED*** [[120, 200], [10, 12]] --> 变化前后的具体像素
        ratio = self.obj["比例"] 
        mode = self.obj["方式"]

        pos = [] ***REMOVED*** 每一个元素：(tmp_pos, tmp_size, rotate)
        img1 = Image.open(self.char.image)
        img_w, img_h = img1.size    ***REMOVED*** 角色图片的原始尺寸
        
        ***REMOVED*** 强制转化为二维数组，使移动不止是直线运动
        if not isinstance(end_pos_list[0], list):
            end_pos_list = [end_pos_list]

        steps = len(end_pos_list)
        frames = int(self.activity.total_frame / steps) ***REMOVED*** 每一个路线需要的帧数
        print("ratio: ", ratio)
        for end_pos in end_pos_list:
            end_pos = utils.covert_pos(end_pos)
            ***REMOVED*** 每一步在x,y方向的进度以及缩放比例
            step_x = (end_pos[0] - start_pos[0]) / frames
            step_y = (end_pos[1] - start_pos[1]) / frames
        
            if isinstance(ratio, list):
                if isinstance(ratio[0], list) and isinstance(ratio[1], list): ***REMOVED*** [(180,220), (80,100)] -- 变化前后的具体像素
                    step_ration_x = (ratio[1][0] - ratio[0][0]) / steps / frames
                    step_ration_y = (ratio[1][1] - ratio[0][1]) / steps/ frames
                    start_size = ratio[0]
    ***REMOVED***   ***REMOVED*** [0.2, 0.2] -- 百分比
                    step_ration_x = (ratio[1] - ratio[0]) / steps / frames * img_w
                    step_ration_y = (ratio[1] - ratio[0]) / steps / frames * img_h
                    start_size = (ratio[0] * img_w, ratio[0] * img_h)
***REMOVED***
                if not isinstance(ratio, float): ***REMOVED*** ratio是最终显示比例， 如 0.4
            ***REMOVED***
                        ratio = float(ratio)
                    except:
                        ratio = 1 ***REMOVED*** 默认比例不变
                tmp_ratio = [self.char.size, [self.char.size[0] * ratio, self.char.size[1] * ratio, ]]
                step_ration_x = (tmp_ratio[1][0] - tmp_ratio[0][0]) / steps / frames
                step_ration_y = (tmp_ratio[1][1] - tmp_ratio[0][1]) / steps / frames
                start_size = self.char.size

            ***REMOVED*** mode ["自然", "旋转"]:
            for i in range(0, frames):
                tmp_pos = (int(start_pos[0] + step_x * i), int(start_pos[1] + step_y * i))
                tmp_size = (int(start_size[0] + step_ration_x * i), int(start_size[1] + step_ration_y * i))
                rotate = None
                if mode == "旋转":
                    step_rotate = 360 / frames * int(config_reader.round_per_second)  ***REMOVED*** 每秒旋转圈数
                    rotate = step_rotate * i
                    if i == frames - 1:
                        ***REMOVED*** 最后一圈摆正
                        rotate = 0
                pos.append((tmp_pos, tmp_size, rotate))

            start_pos = end_pos ***REMOVED*** 重新设置轨迹的开始坐标
        
        ***REMOVED*** print("位置序列： ", pos)
        image_clips = []
        path = os.path.join(config_reader.output_dir, self.activity.name)
        if not os.path.exists(path):
            os.mkdir(path=path)
        for i in range(0, self.activity.total_frame):
            if i < len(pos):
                ***REMOVED*** 由于前面使用int填充每个step的frames，所以最后一个step可能数量不足
                ***REMOVED*** 会导致最后几帧没有动作
                ***REMOVED*** 所以使用最后一个动作进行填充
                self.char.pos = pos[i][0]
                self.char.size = pos[i][1]
                rotate = pos[i][2]
            img = ImageHelper.merge_two_image(images[i], self.char.image, pos=self.char.pos, size=self.char.size, rotate=rotate)
            ext = img.split('.')[-1]
            _path = os.path.join(path, f"{i***REMOVED***.{ext***REMOVED***")
            shutil.move(img, _path)
            image_clips.append(_path)
                
        return image_clips

    def __gif(self, images):
***REMOVED***向视频中插入一段gif
***REMOVED***
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
***REMOVED***
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
***REMOVED***
        根据当前动作脚本生成视频所需的图片

***REMOVED***
            images: a list of images
        Return:
            一组视频所需的图片
***REMOVED***

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


***REMOVED***
    pass
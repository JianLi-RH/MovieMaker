"""
这个类用来解析script.yaml中的`动作:`
"""
***REMOVED***
***REMOVED***

from moviepy.editor import *
from PIL import Image, ImageOps

import config_reader
import utils
from character import *
from libs import AudioHelper, ImageHelper


class Action:
    """The Action(动作) class"""

    def __get_char(self, name):
***REMOVED***查找指定名称的角色"""
        if not name:
            return None
        for c in self.activity.scenario.chars:
            if c.name == name:
                if c.rotate == "左右":
                    basename = os.path.basename(c.image)
                    new_path = os.path.join(os.path.dirname(c.image), f"rotate_{basename***REMOVED***")
                    if not os.path.exists(new_path):
                        im_mirror = ImageOps.mirror(Image.open(c.image))
                        im_mirror.save(new_path)
                    c.image = new_path
                    c.rotate = 0
                elif c.rotate == "上下":
                    c.rotate = 180
                    
                return c
        return None

    def __display(self):
***REMOVED***将当前动作的角色显示在背景上"""
        self.char.display = True

    def __disappear(self):
***REMOVED***让角色消失"""
        self.char.display = False

    def __camera(self, images):
***REMOVED***
        处理 `镜头` 相关的动作，例如切换焦点，镜头拉近、拉远
        ***一个活动中不能有两个`镜头`动作***
***REMOVED***
        length = len(images)    ***REMOVED*** 总帧数
        original_center = utils.covert_pos(self.activity.scenario.focus)  ***REMOVED*** 原有的焦点
        self.activity.scenario.focus = self.obj.get("焦点", None) ***REMOVED*** 新焦点
        if not self.activity.scenario.focus:
            if self.char:
                x, y = self.char.pos
                w, h = self.char.size
                self.activity.scenario.focus = [(x + w / 2), (y + h / 2)]
***REMOVED***
                self.activity.scenario.focus = "中心"
        
        center = utils.covert_pos(self.activity.scenario.focus)

        step_x = (center[0] - original_center[0]) / length
        step_y = (center[1] - original_center[1]) / length

        ratio = self.obj.get("变化")
        if isinstance(ratio, float):
            ratio = [1, ratio]
        from_ratio = ratio[0]
        to_ratio = ratio[1]
        ration_step = (to_ratio - from_ratio) / length
        
        
        self.activity.scenario.ratio = to_ratio

        for i in range(0, length):
            tmp_ratio = from_ratio + ration_step * i
            x = original_center[0] + step_x * i
            y = original_center[1] + step_y * i

            tmp_img = ImageHelper.zoom_in_out_image(images[i], center=(x, y), ratio=tmp_ratio)
            images[i] = tmp_img

    def __turn(self, images, sorted_char_list, delay_mode: bool):
***REMOVED***让角色转动，如左右转身，上下翻转，指定角度翻转
        
            延迟模式下返回角色运行轨迹, 否则返回空[]
        
        Example:            
          -
            名称: 转身
            角色: 镇关西
            持续时间: 
            角度: 270 ***REMOVED*** 左右, 上下， 45(逆时针角度), -45(顺时针) -- 如果是数字的话，会从初始位置旋转到给定角度
            字幕:
              - ['','', '啊啊啊', 'resources/ShengYin/惨叫-男1.mp3']
            渲染顺序: 0
          -
            名称: 转身
            角色: 鲁智深
            持续时间: 
            角度: [0, -30] ***REMOVED*** 转动一个范围
            比例: 1
            字幕:
            - ['','', '听说菜园里来了个新和尚', '水浒传/第九回/泼皮偷菜/听说菜园里来了个新和尚.mp3']
            渲染顺序: 1
            
***REMOVED***
            images: 全部背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
        Return:
            [[tmp_pos, tmp_size, rotate], [tmp_pos, tmp_size, rotate]]
***REMOVED***
        
        str_degree = self.obj.get("角度", 0)
        delay_positions = []
        total_feames = len(images)
        
        if isinstance(str_degree, int):
            str_degree = [self.char.rotate, str_degree]
        
        if isinstance(str_degree, list):
            ***REMOVED*** 连续转动
            degree_step = (str_degree[1] - str_degree[0]) / total_feames
            start_rotate = self.char.rotate
            for i in range(total_feames):
                delay_positions.append([self.char.pos, self.char.size, start_rotate])
                start_rotate += degree_step
        else:
            for i in range(total_feames):
                delay_positions.append([self.char.pos, self.char.size, self.char.rotate])
        
        if delay_mode:
            return delay_positions

        for i in range(total_feames):
            big_image = None
            for _char in sorted_char_list:
                if _char.display:
                    if _char.name == self.char.name:
                        _, big_image = ImageHelper.merge_two_image(big_image=images[i], 
                                                                            big_image_obj=big_image,
                                                                            small_image=_char.image,
                                                                            pos=delay_positions[i][0],
                                                                            size=delay_positions[i][1],
                                                                            rotate=delay_positions[i][2],
                                                                            save=False)
        ***REMOVED***
                        _, big_image = ImageHelper.paint_char_on_image(char=_char, 
                                                                       image=images[i], 
                                                                       image_obj=big_image,
                                                                       save=False)
            if big_image:
                big_image.save(images[i])
                big_image.close()
        return []

    def __walk(self, images, sorted_char_list, delay_mode: bool):
***REMOVED***角色移动
            延迟模式下返回角色运行轨迹, 否则返回空[]
        
        Example:
          -
            名称: 行进
            角色: 鲁智深
            持续时间: 
            开始位置: 
            结束位置: [-0.2, 0.55]
            比例:   ***REMOVED*** 比例变化，开始比例 - 结束比例
            方式:   ***REMOVED*** 自然 / 旋转 / 45 -- 如果是数字的话，会从初始位置旋转到给定角度 , 最后恢复原样
            字幕: ***REMOVED***Yunyang, Male
              - ['','', '跑路', 'resources/ShengYin/卡通搞笑逃跑音效.mp3']
            渲染顺序: 6
        
***REMOVED***
            images: 全部背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
        Return:
            [[tmp_pos, tmp_size, rotate], [tmp_pos, tmp_size, rotate]]
***REMOVED***
        if not self.char:
            raise Exception("角色不存在")
        
        start_pos = self.obj["开始位置"] if self.obj.get("开始位置", None) else self.char.pos
        start_pos = utils.covert_pos(start_pos)
        ***REMOVED*** end_pos_list可以是一个固定位置， 如 [230, 120]，
        ***REMOVED*** 也可以是一组位置坐标， 如 [[230, 120]， [330, 180]， [450, 320]]
        end_pos_list = self.obj["结束位置"]
        ***REMOVED*** ratio： 显示比例，可以有以下几种形式：
        ***REMOVED*** 0.4   --> 相对于开始时，最终的显示比例
        ***REMOVED*** [1, 0.4] --> 变化前后的显示比例
        ***REMOVED*** [[120, 200], [10, 12]] --> 变化前后的具体像素
        ratio = self.obj["比例"] if self.obj["比例"] else 1
        mode = self.obj["方式"]
        
        self.char.display = True ***REMOVED*** 强制显示当前角色

        pos = [] ***REMOVED*** 每一个元素：(tmp_pos, tmp_size, rotate)
        img1 = Image.open(self.char.image)
        img_w, img_h = img1.size    ***REMOVED*** 角色图片的原始尺寸
        img1.close()
        
        ***REMOVED*** 计算每一帧的大小变化
        if isinstance(ratio, list):
            if isinstance(ratio[0], list) and isinstance(ratio[1], list): ***REMOVED*** [(180,220), (80,100)] -- 变化前后的具体像素
                ratio_x = (ratio[1][0] - ratio[0][0]) / len(images)
                ratio_y = (ratio[1][1] - ratio[0][1]) / len(images)
                start_size = ratio[0]
***REMOVED***   ***REMOVED*** [0.2, 0.2] -- 百分比
                ratio_x = (ratio[1] - ratio[0]) / len(images)
                ratio_y = ratio_x
                start_size = (ratio[0] * img_w, ratio[0] * img_h)
        else:
    ***REMOVED***
                ***REMOVED*** ratio是最终显示比例， 如 0.4
                ratio = float(ratio)
            except:
                ratio = 1 ***REMOVED*** 默认比例不变
            ratio_x = (ratio - 1) / len(images)
            ratio_y = ratio_x
            start_size = self.char.size
        
        ***REMOVED*** 强制转化为二维数组，使移动不止是直线运动
        if not isinstance(end_pos_list[0], list):
            end_pos_list = [end_pos_list]

        steps = len(end_pos_list)
        frames = int(1/steps * len(images)) ***REMOVED*** 平均分配每一个路线需要的帧数
        
        for i in range(steps):    ***REMOVED*** 例如：[[120, 200], [10, 12]]
            if i == steps - 1:
                ***REMOVED*** 最后一步包含剩余的全部图片
                frames = len(images) - (steps - 1) * frames

            end_pos = utils.covert_pos(end_pos_list[i])
            ***REMOVED*** 每一步在x,y方向的进度
            step_x = (end_pos[0] - start_pos[0]) / frames
            step_y = (end_pos[1] - start_pos[1]) / frames

            ***REMOVED*** mode ["自然", "旋转", 数字]:
            rotate = self.char.rotate
            step_rotate = 0
            if mode == "旋转":
                step_rotate = 360 * config_reader.round_per_second / self.activity.fps  ***REMOVED*** 每秒旋转圈数
            if isinstance(mode, int):
                step_rotate = mode / self.timespan / self.activity.fps
            
            for j in range(0, frames):
                tmp_pos = (int(start_pos[0] + step_x * j), int(start_pos[1] + step_y * j))
                m = i * steps + j
                tmp_size = (int(start_size[0] * (1 + ratio_x * m)), int(start_size[1] * (1 + ratio_y * m)))
                if i == steps - 1 and j > frames - 2:
                    ***REMOVED*** 最后一圈最后一帧恢复原样
                    rotate = self.char.rotate
                pos.append((tmp_pos, tmp_size, rotate))
                rotate += step_rotate
                rotate = rotate % 360

            start_pos = end_pos ***REMOVED*** 重新设置轨迹的开始坐标
        
        if delay_mode:
            return pos
        
        for i in range(len(images)):
            big_image = None
            for _char in sorted_char_list:
                if _char.name == self.char.name:
                    _char.pos = pos[i][0]
                    _char.size = pos[i][1]
                    _char.rotate = pos[i][2]
                if _char.display:
                    _, big_image = ImageHelper.paint_char_on_image(char=_char, 
                                                                   image=images[i],
                                                                   image_obj=big_image,
                                                                   save=False)
            if big_image:
                big_image.save(images[i])
                big_image.close()

        return []

    def __gif(self, images, sorted_char_list, delay_mode):
***REMOVED***向视频中插入一段gif
        
        Example:
          -
            名称: gif
            素材: resources/SuCai/说话声/1.gif
            字幕: 
              - ['','', '小女孩哭泣声', 'resources/ShengYin/小女孩哭泣声.mp3']
            位置: [0.6, 0.2]
            图层: 100
            角度: 左右
            大小: [300, 300]
        
***REMOVED***
            images: 全部背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
***REMOVED***
        index = self.obj.get("图层") if self.obj.get("图层") else sys.maxsize ***REMOVED*** 默认将gif显示在最上层
        ***REMOVED*** 将GIF标记添加在显示列表中，用来设置显示顺序
        for i in range(len(sorted_char_list)):
            if sorted_char_list[i].index > index:
                sorted_char_list.insert(i, "GIF")
                break
        if "GIF" not in sorted_char_list:
            sorted_char_list.append("GIF")
            
        gif_images = ImageHelper.get_frames_from_gif(self.obj.get("素材"))

        img1 = Image.open(images[0])
        img_w, img_h = img1.size
        img1.close()
        pos = self.obj.get("位置")
        pos[0] = pos[0] if pos[0] > 1 else int(pos[0] * img_w)
        pos[1] = pos[1] if pos[1] > 1 else int(pos[1] * img_h)

        gif1 = Image.open(gif_images[0])
        size = self.obj.get("大小") if self.obj.get("大小") else gif1.size
        gif1.close()
        str_degree = self.obj.get("角度") if self.obj.get("角度") else 1

        l = len(images)
        if delay_mode:
            return [(pos, size, str_degree) for i in range(l)]
        
        for i in range(0, l):
            j = i % len(gif_images)

            if str_degree == "左右":
                _img = Image.open(gif_images[j])
                im_mirror = ImageOps.mirror(_img)
                _img.close()
                basename = os.path.basename(gif_images[j])
                new_path = os.path.join(os.path.dirname(images[-1]), basename)
                im_mirror.save(new_path)
                im_mirror.close()
                gif_images[j] = new_path
                rotate = 0
            elif str_degree == "上下":
                rotate = 180
***REMOVED***
                rotate = int(str_degree)

            big_image = None
            for _char in sorted_char_list:
                if _char == "GIF":
                    _, big_image = ImageHelper.merge_two_image(big_image=images[i],
                                                                big_image_obj=big_image,
                                                                small_image=gif_images[j],
                                                                pos=pos,
                                                                size=size,
                                                                rotate=rotate,
                                                                save=False)
    ***REMOVED***
                    if _char.display and not delay_mode:
                        ***REMOVED*** 这里存在一个显示层级的bug
                        _, big_image = ImageHelper.paint_char_on_image(image=images[i], 
                                                                       image_obj=big_image,
                                                                       char=_char, 
                                                                       save=False)
            if big_image:
                big_image.save(images[i])
                big_image.close()
        ***REMOVED*** 恢复列表
        sorted_char_list.remove("GIF")
    
    def __talk(self, images, sorted_char_list, delay_mode):
***REMOVED***角色说话
        
        Example:
          -
            名称: 说话
            角色: 鲁智深
            焦点: 
            变化: 
            字幕: ***REMOVED***Yunyang, Male
              - ['','', '你这斯诈死', '水浒传/第四回/打死镇关西/你这斯诈死.mp3']
              - ['','', '等我回家再与你理会', '水浒传/第四回/打死镇关西/等我回家再与你理会.mp3']
            渲染顺序: 5
            
***REMOVED***
            images: 背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
        Return:
            [[tmp_pos, tmp_size, rotate], [tmp_pos, tmp_size, rotate]]
***REMOVED***
        if delay_mode:
            return [(self.char.pos, self.char.size, self.char.rotate) for i in range(len(images))]
        
        for img in images:
            big_image = None
            for _char in sorted_char_list:
                if _char.display:
                    t = datetime.datetime.now()
                    _, big_image = ImageHelper.paint_char_on_image(image=img, 
                                                                   image_obj=big_image,
                                                                   char=_char, 
                                                                   save=False)

            if big_image:
                big_image.save(img)
                big_image.close()

        if self.obj.get("变化", None):
            ***REMOVED*** 图片有缩放的时候才需要调用镜头方法
            self.__camera(images)
        
        return []
    
    def __update(self):
***REMOVED***更新某个角色
        
        Example:
          -
            名称: 更新
            角色: 鲁智深
            素材: 水浒传/人物/鲁智深1.png
            角度: 左右
            字幕: ***REMOVED***Kangkang, Male
              - ['','', '啪啪啪', 'resources/ShengYin/打耳光.mp3']
            渲染顺序: 2
***REMOVED***
        keys = self.obj.keys()
        if "素材" in keys:
            self.char.image = self.obj.get("素材", None)
        if "位置" in keys:
            self.char.pos = utils.covert_pos(self.obj.get("位置", None))
        if "大小" in keys:
            self.char.size = self.obj.get("大小")
        if "角度" in keys:
            self.char.rotate = self.obj.get("角度")
        if "显示" in keys:
            self.char.display = True if self.obj.get("显示") == '是' else False
        if "图层" in keys:
            self.char.index = int(self.obj.get("图层", 0))
            
        self.char = self.__get_char(self.char.name)
    
    def __get_subtitle(self):
***REMOVED***获取动作的字幕
        
        return:
            (字幕颜色, 字幕)
            字幕是一组列表，如下：
            [0, 1, '小二', 'resources/ShengYin/武松/酒馆里/小二.mp3', 'ws', 'resources/SuCai/武松/说话/武松说话.gif']
            [1, 2.5, '小二', 'resources/ShengYin/武松/酒馆里/小二.mp3', 'ws']
***REMOVED***
        subtitle_color = self.obj.get("字幕颜色") if self.obj.get("字幕颜色") else None
        subtitles = self.obj.get("字幕") if self.obj.get("字幕") else []
        start, end = 0, 0
        for subtitle in subtitles:
            sPath = subtitle[3]
            if not os.path.exists(sPath):
                ***REMOVED*** 使用科大讯飞接口生成语音
        ***REMOVED***
                    speaker = self.obj.get("发音人") if self.name == "gif" else self.char.speaker
                    AudioHelper.covert_text_to_sound(subtitle[2], sPath, speaker)
        ***REMOVED***
                    print(f"Convert text failed: ", subtitle[2])
                    raise(e)
                    
            _length = AudioFileClip(sPath).duration
            end = start + _length
            subtitle[0] = start
            subtitle[1] = end
            start = end
            
        return subtitle_color, subtitles
        
    def __add_subtitle(self, images):
***REMOVED***向背景图片添加字幕
        
***REMOVED***
            images: 背景图片
***REMOVED***
        pic_number = len(images)
        for subtitle in self.subtitle:
            start = subtitle[0]
            end = subtitle[1]
            cur_images = images[int(start/self.timespan*pic_number):int(end/self.timespan*pic_number)]
            for img in cur_images:
                ImageHelper.add_text_to_image(img, subtitle[2], overwrite_image=True, color=self.subtitle_color)
        pass

    def set_timespan(self, timespan):
        self.timespan = timespan

    def __init__(self, activity, obj):
***REMOVED***
        初始化Action
***REMOVED***
        self.activity = activity
        self.obj = obj
        self.name = self.obj.get("名称")
        self.char = self.__get_char(self.obj.get("角色"))
        self.render_index = self.obj.get("渲染顺序") if self.obj.get("渲染顺序") else 0    ***REMOVED*** 动作执行的顺序，数值一样的同时执行， 从小到达执行
        self.subtitle_color, self.subtitle = self.__get_subtitle()
        if self.subtitle_color == None and self.activity.subtitle_color:
            ***REMOVED*** 当动作没有设置字幕颜色时，使用活动的字幕颜色覆盖动作的字幕颜色
            self.subtitle_color = self.activity.subtitle_color
        keep = utils.get_time(obj.get("持续时间", 0))   ***REMOVED*** 优先级最高
        if keep > 0:
            self.timespan = keep
        elif self.subtitle:
            self.timespan = self.subtitle[-1][1] if self.subtitle else 0
        elif self.activity.bgm:
            ***REMOVED*** 以活动的背景声音长度作为动作的长度
            self.timespan = AudioFileClip(self.activity.bgm).duration
        elif self.activity.keep:
            ***REMOVED*** 以活动的持续时间作为动作的长度
            self.timespan = utils.get_time(obj.get("持续时间", None))
        else:
            self.timespan = 0

    def to_videoframes(self, images, sorted_char_list, delay_mode: bool):
***REMOVED***
        根据当前动作脚本更新图片列表，生成视频最终所需的图片

***REMOVED***
            images: a list of images
            sorted_char_list: 活动中的角色列表 (已排序)
            delay_mode: 延迟绘制其他角色
        Returns:
            延迟模式下不更新图片，返回当前角色的运行轨迹, 例如：
            {
                "char": self.char, 
                "position": delay_positions
        ***REMOVED***
***REMOVED***
***REMOVED***
            
            start = datetime.datetime.now()
            delay_positions = []
            action = self.obj.get("名称")
            if action == "显示":
                self.__display()
            elif action == "消失":
                self.__disappear()
            elif action == "镜头":  ***REMOVED*** 还需要验证
                self.__camera(images)
            elif action == "行进":
                delay_positions = self.__walk(images, sorted_char_list, delay_mode)
            elif action == "说话":
                delay_positions = self.__talk(images, sorted_char_list, delay_mode)
            elif action == "转身":
                delay_positions = self.__turn(images, sorted_char_list, delay_mode)
            elif action == "gif":
                self.__gif(images, sorted_char_list, delay_mode)
            elif action == "更新":
                self.__update()
            pass

            duration = datetime.datetime.now() - start
            print(f"执行动作动【{self.name***REMOVED*** - {self.render_index***REMOVED***】， 共花费：{duration.seconds***REMOVED***秒")
        
            start = datetime.datetime.now()
            self.__add_subtitle(images)
            duration = datetime.datetime.now() - start
            print(f"添加动作字幕【{self.name***REMOVED*** - {self.render_index***REMOVED***】， 共花费：{duration.seconds***REMOVED***秒")
            return {
                "char": self.char, 
                "position": delay_positions
        ***REMOVED***
***REMOVED***
            print(f"Error: 动作名： {self.name***REMOVED*** - 渲染顺序： {self.render_index***REMOVED***")
            raise(e)

***REMOVED***
    pass
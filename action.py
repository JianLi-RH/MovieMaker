"""
这个类用来解析script.yaml中的`动作:`
"""
import sys
import datetime

from moviepy.editor import *
from PIL import Image, ImageOps

import config_reader
import utils
from character import *
from libs import AudioHelper, ImageHelper


class Action:
    """The Action(动作) class"""

    def __get_char(self, name):
        """查找指定名称的角色"""
        if not name:
            return None
        for c in self.activity.scenario.chars:
            if c.name == name:
                if c.rotate == "左右" and c.name.lower() != "gif":
                    basename = os.path.basename(c.image)
                    new_path = os.path.join(os.path.dirname(c.image), f"rotate_{basename}")
                    if not os.path.exists(new_path):
                        im_mirror = ImageOps.mirror(Image.open(c.image))
                        im_mirror.save(new_path)
                    c.image = new_path
                    c.rotate = 0
                elif c.rotate == "上下":
                    c.rotate = 180
                    
                return c
        raise Exception(f"角色【{name}】不存在")
    
    def __bgm(self, images, sorted_char_list):
        """向视频中插入一段背景音
        
        Example:
          -
            名称: BGM
            字幕: 
              - ['','', 'bgm', 'resources/ShengYin/bgm.mp3']
        
        Params:
            images: 全部背景图片
            sorted_char_list: 排序后的角色
        """     
        l = len(images)
        for i in range(0, l):
            big_image = None
            for _char in sorted_char_list:
                if _char.display:
                    _, big_image = ImageHelper.paint_char_on_image(image=images[i], 
                                                                    image_obj=big_image,
                                                                    char=_char, 
                                                                    save=False,
                                                                    gif_index=i)
            if big_image:
                big_image.save(images[i])
                big_image.close()

    def __display(self):
        """将当前动作的角色显示在背景上"""
        self.char.display = True

    def __disappear(self):
        """让角色消失"""
        self.char.display = False

    def __camera(self, images):
        """
        处理 `镜头` 相关的动作，例如切换焦点，镜头拉近、拉远
        ***一个活动中不能有两个`镜头`动作***
        """
        length = len(images)    # 总帧数
        if not self.activity.scenario.focus:
            self.activity.scenario.focus = "中心"
        original_center = utils.covert_pos(self.activity.scenario.focus)  # 原有的焦点

        if self.obj.get("焦点", None):
            new_center = utils.covert_pos(self.obj.get("焦点"))
        else: 
            if self.char:
                x, y = self.char.pos
                w, h = self.char.size
                new_center = [(x + w / 2), (y + h / 2)]
            else:
                new_center = original_center

        step_x = (new_center[0] - original_center[0]) / length
        step_y = (new_center[1] - original_center[1]) / length

        ratio = self.obj.get("变化")
        if isinstance(ratio, float):
            ratio = [1, ratio]
        from_ratio = ratio[0]
        to_ratio = ratio[1]
        ratio_step = (to_ratio - from_ratio) / length
        
        self.activity.scenario.ratio = to_ratio

        for i in range(0, length):
            tmp_ratio = from_ratio + ratio_step * i
            x = original_center[0] + step_x * i
            y = original_center[1] + step_y * i

            tmp_img = ImageHelper.zoom_in_out_image(images[i], center=(x, y), ratio=tmp_ratio)
            images[i] = tmp_img

    def __turn(self, images, sorted_char_list, delay_mode: bool):
        """让角色转动，如左右转身，上下翻转，指定角度翻转
        
            延迟模式下返回角色运行轨迹, 否则返回空[]
        
        Example:            
          -
            名称: 转身
            角色: 镇关西
            持续时间: 
            角度: 270 # 左右, 上下， 45(逆时针角度), -45(顺时针) -- 如果是数字的话，会从初始位置旋转到给定角度
            字幕:
              - ['','', '啊啊啊', 'resources/ShengYin/惨叫-男1.mp3']
            渲染顺序: 0
          -
            名称: 转身
            角色: 鲁智深
            持续时间: 
            角度: [0, -30] # 转动一个范围
            比例: 1
            字幕:
            - ['','', '听说菜园里来了个新和尚', '水浒传/第九回/泼皮偷菜/听说菜园里来了个新和尚.mp3']
            渲染顺序: 1
            
        Params:
            images: 全部背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
        Return:
            [[tmp_pos, tmp_size, rotate], [tmp_pos, tmp_size, rotate]]
        """
        
        str_degree = self.obj.get("角度", 0)
        delay_positions = []
        total_feames = len(images)
        self.char.display = True # 强制显示当前角色
        
        if isinstance(str_degree, int):
            str_degree = [self.char.rotate, str_degree]
        
        if isinstance(str_degree, list):
            # 连续转动
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
                        _char.pos = delay_positions[i][0]
                        _char.size = delay_positions[i][1]
                        _char.rotate = delay_positions[i][2]

                    _, big_image = ImageHelper.paint_char_on_image(char=_char, 
                                                                    image=images[i], 
                                                                    image_obj=big_image,
                                                                    save=False,
                                                                    gif_index=i)
            if big_image:
                big_image.save(images[i])
                big_image.close()
        return []

    def __walk(self, images, sorted_char_list, delay_mode: bool):
        """角色移动
            延迟模式下返回角色运行轨迹, 否则返回空[]
        
        Example:
          -
            名称: 行进
            角色: 鲁智深
            持续时间: 
            开始位置: 
            结束位置: [-0.2, 0.55]
            比例:   # 比例变化，开始比例 - 结束比例
            方式:   # 自然 / 旋转 / 45 -- 如果是数字的话，会从初始位置旋转到给定角度 , 最后恢复原样
            字幕: #Yunyang, Male
              - ['','', '跑路', 'resources/ShengYin/卡通搞笑逃跑音效.mp3']
            渲染顺序: 6
        
        Params:
            images: 全部背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
        Return:
            [[tmp_pos, tmp_size, rotate], [tmp_pos, tmp_size, rotate]]
        """
        if not self.char:
            raise Exception("角色不存在")
        
        start_pos = self.obj["开始位置"] if self.obj.get("开始位置", None) else self.char.pos
        start_pos = utils.covert_pos(start_pos)
        # end_pos_list可以是一个固定位置， 如 [230, 120]，
        # 也可以是一组位置坐标， 如 [[230, 120]， [330, 180]， [450, 320]]
        end_pos_list = self.obj.get("结束位置", None)
        if not end_pos_list:
            raise Exception(f"'结束位置'不能为空")
        # ratio： 显示比例，可以有以下几种形式：
        # 0.4   --> 相对于开始时，最终的显示比例
        # [1, 0.4] --> 变化前后的显示比例
        # [[120, 200], [10, 12]] --> 变化前后的具体像素
        ratio = self.obj["比例"] if self.obj.get("比例") else 1
        mode = self.obj.get("方式", None)
        
        self.char.display = True # 强制显示当前角色

        pos = [] # 每一个元素：(tmp_pos, tmp_size, rotate)
        img1 = Image.open(self.char.image)
        img_w, img_h = img1.size    # 角色图片的原始尺寸
        img1.close()
        
        # 计算每一帧的大小变化
        if isinstance(ratio, list):
            if isinstance(ratio[0], list) and isinstance(ratio[1], list): # [(180,220), (80,100)] -- 变化前后的具体像素
                ratio_x = (ratio[1][0] - ratio[0][0]) / len(images)
                ratio_y = (ratio[1][1] - ratio[0][1]) / len(images)
                start_size = ratio[0]
            else:   # [0.2, 0.2] -- 百分比
                ratio_x = (ratio[1] - ratio[0]) / len(images)
                ratio_y = ratio_x
                start_size = (ratio[0] * img_w, ratio[0] * img_h)
        else:
            try:
                # ratio是最终显示比例， 如 0.4
                ratio = float(ratio)
            except:
                ratio = 1 # 默认比例不变
            ratio_x = (ratio - 1) / len(images)
            ratio_y = ratio_x
            start_size = self.char.size
        
        # 强制转化为二维数组，使移动不止是直线运动
        if not isinstance(end_pos_list[0], list):
            end_pos_list = [end_pos_list]

        steps = len(end_pos_list)
        frames = int(1/steps * len(images)) # 平均分配每一个路线需要的帧数
        
        for i in range(steps):    # 例如：[[120, 200], [10, 12]]
            if i == steps - 1:
                # 最后一步包含剩余的全部图片
                frames = len(images) - (steps - 1) * frames

            end_pos = utils.covert_pos(end_pos_list[i])
            # 每一步在x,y方向的进度
            step_x = (end_pos[0] - start_pos[0]) / frames
            step_y = (end_pos[1] - start_pos[1]) / frames

            # mode ["自然", "旋转", 数字]:
            rotate = self.char.rotate
            step_rotate = 0
            if mode == "旋转":
                step_rotate = 360 * config_reader.round_per_second / self.activity.fps  # 每秒旋转圈数
            if isinstance(mode, int):
                step_rotate = mode / self.timespan / self.activity.fps
            
            for j in range(0, frames):
                tmp_pos = (int(start_pos[0] + step_x * j), int(start_pos[1] + step_y * j))
                m = i * steps + j
                tmp_size = (int(start_size[0] * (1 + ratio_x * m)), int(start_size[1] * (1 + ratio_y * m)))
                if i == steps - 1 and j > frames - 2:
                    # 最后一圈最后一帧恢复原样
                    rotate = self.char.rotate
                pos.append((tmp_pos, tmp_size, rotate))
                rotate += step_rotate
                rotate = rotate % 360

            start_pos = end_pos # 重新设置轨迹的开始坐标
        
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
                                                                   save=False,
                                                                   gif_index=i)
            if big_image:
                big_image.save(images[i])
                big_image.close()

        return []

    def __gif(self, images, sorted_char_list, delay_mode):
        """向视频中插入一段gif
        
        Example:
          -
            名称: gif
            素材: resources/SuCai/说话声/1.gif
            发音人引擎: 
            字幕: 
              - ['','', '小女孩哭泣声', 'resources/ShengYin/小女孩哭泣声.mp3']
            位置: [0.6, 0.2]
            图层: 100
            角度: 左右
            大小: [300, 300]
        
        Params:
            images: 全部背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
        """
        self.obj.update({"名字": "gif", "显示": "是"})
        gif_char = Character(self.obj)
        gif_images = gif_char.gif_frames
        
        # 将GIF标记添加在显示列表中，用来设置显示顺序
        added_index = -1
        for i in range(len(sorted_char_list)):
            if sorted_char_list[i].index > gif_char.index:
                added_index = i
                sorted_char_list.insert(i, gif_char)
                break
        if added_index == -1:
            added_index = len(sorted_char_list)
            sorted_char_list.append(gif_char)
            
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
            else:
                rotate = int(str_degree)

            big_image = None
            for _char in sorted_char_list:
                if _char.name.lower() == "gif":
                    _, big_image = ImageHelper.merge_two_image(big_image=images[i],
                                                                big_image_obj=big_image,
                                                                small_image=gif_images[j],
                                                                pos=pos,
                                                                size=size,
                                                                rotate=rotate,
                                                                save=False)
                else:
                    if _char.display and not delay_mode:
                        # 这里存在一个显示层级的bug
                        _, big_image = ImageHelper.paint_char_on_image(image=images[i], 
                                                                       image_obj=big_image,
                                                                       char=_char, 
                                                                       save=False,
                                                                       gif_index=i)
            if big_image:
                big_image.save(images[i])
                big_image.close()
        # 恢复列表
        sorted_char_list.pop(added_index)
    
    def __talk(self, images, sorted_char_list, delay_mode):
        """角色说话
        
        Example:
          -
            名称: 说话
            角色: 鲁智深
            高亮: 是
            变化:  # 可以是： 0 - 1数字； 近景；
            字幕: #Yunyang, Male
              - ['','', '你这斯诈死', '水浒传/第四回/打死镇关西/你这斯诈死.mp3']
              - ['','', '等我回家再与你理会', '水浒传/第四回/打死镇关西/等我回家再与你理会.mp3']
            渲染顺序: 5
            
        Params:
            images: 背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
        Return:
            [[tmp_pos, tmp_size, rotate], [tmp_pos, tmp_size, rotate]]
        """
        if delay_mode:
            return [(self.char.pos, self.char.size, self.char.rotate) for i in range(len(images))]
        
        hightlight = self.obj.get("高亮") == "是"
        gif_index = 0
        for img in images:
            big_image = None
            if hightlight:
                big_image = ImageHelper.dark_image(img)
            for _char in sorted_char_list:
                if _char.display:
                    dark = False
                    if hightlight and _char.name != self.char.name:
                        dark = True
                    _, big_image = ImageHelper.paint_char_on_image(image=img, 
                                                                   image_obj=big_image,
                                                                   char=_char, 
                                                                   save=False,
                                                                   gif_index=gif_index,
                                                                   dark=dark)

            if big_image:
                big_image.save(img)
                big_image.close()
            gif_index += 1

        if self.obj.get("变化", None):
            if isinstance(self.obj.get("变化"), float):
                # 图片有缩放的时候才需要调用镜头方法
                self.__camera(images)
            elif self.obj.get("变化") == "近景":
                for img in images:
                    ImageHelper.cut_image(img, self.char)
        return []
    
    def __update(self):
        """更新某个角色
        
        Example:
          -
            名称: 更新
            角色: 鲁智深
            素材: 水浒传/人物/鲁智深1.png
            角度: 左右
            字幕: #Kangkang, Male
              - ['','', '啪啪啪', 'resources/ShengYin/打耳光.mp3']
            渲染顺序: 2
        """
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
        """获取动作的字幕
        
        return:
            (字幕颜色, 字幕)
            字幕是一组列表，如下：
            [0, 1, '小二', 'resources/ShengYin/武松/酒馆里/小二.mp3', 'ws', 'resources/SuCai/武松/说话/武松说话.gif']
            [1, 2.5, '小二', 'resources/ShengYin/武松/酒馆里/小二.mp3', 'ws']
        """
        subtitle_color = self.obj.get("字幕颜色") if self.obj.get("字幕颜色") else None
        subtitles = self.obj.get("字幕") if self.obj.get("字幕") else []
        if not isinstance(subtitles, list):
            raise Exception("字幕错误: ", subtitles)
        start, end = 0, 0
        for subtitle in subtitles:
            sPath = subtitle[3]
            if not os.path.exists(sPath):
                # 使用科大讯飞接口生成语音
                try:
                    speaker = self.obj.get("发音人") if self.name == "gif" else self.char.speaker
                    ttsengine = self.obj.get("发音人引擎") if self.name == "gif" else self.char.tts_engine
                    AudioHelper.covert_text_to_sound(subtitle[2], sPath, speaker, ttsengine=ttsengine)
                except Exception as e:
                    print(f"Convert text failed: ", subtitle[2])
                    raise(e)
                    
            _length = AudioFileClip(sPath).duration
            end = start + _length
            subtitle[0] = start
            subtitle[1] = end
            start = end
            
        return subtitle_color, subtitles
        
    def __add_subtitle(self, images):
        """向背景图片添加字幕
        
        Params:
            images: 背景图片
        """
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
        """
        初始化Action
        """
        self.activity = activity
        self.obj = obj
        self.name = self.obj.get("名称")
        self.char = self.__get_char(self.obj.get("角色"))
        self.render_index = self.obj.get("渲染顺序") if self.obj.get("渲染顺序") else 0    # 动作执行的顺序，数值一样的同时执行， 从小到达执行
        self.subtitle_color, self.subtitle = self.__get_subtitle()
        if self.subtitle_color == None and self.activity.subtitle_color:
            # 当动作没有设置字幕颜色时，使用活动的字幕颜色覆盖动作的字幕颜色
            self.subtitle_color = self.activity.subtitle_color
        keep = utils.get_time(obj.get("持续时间", 0))   # 优先级最高
        if keep > 0:
            self.timespan = keep
        elif self.subtitle:
            self.timespan = self.subtitle[-1][1] if self.subtitle else 0
        elif self.activity.bgm:
            # 以活动的背景声音长度作为动作的长度
            self.timespan = AudioFileClip(self.activity.bgm).duration
        elif self.activity.keep:
            # 以活动的持续时间作为动作的长度
            self.timespan = utils.get_time(obj.get("持续时间", None))
        else:
            self.timespan = 0

    def to_videoframes(self, images, sorted_char_list, delay_mode: bool):
        """
        根据当前动作脚本更新图片列表，生成视频最终所需的图片

        Params:
            images: a list of images
            sorted_char_list: 活动中的角色列表 (已排序)
            delay_mode: 延迟绘制其他角色
        Returns:
            延迟模式下不更新图片，返回当前角色的运行轨迹, 例如：
            {
                "char": self.char, 
                "position": delay_positions
            }
        """
        try:
            
            start = datetime.datetime.now()
            delay_positions = []
            action = self.obj.get("名称").lower()
            if action in ["行进", "说话", "转身", "gif", "bgm"] and (len(images) == 0 or self.timespan == 0):
                raise Exception(f"动作[{action}]执行时间不能为0")

            if action == "显示":
                self.__display()
            elif action == "消失":
                self.__disappear()
            elif action == "镜头":  # 还需要验证
                self.__camera(images)
            elif action == "行进":
                delay_positions = self.__walk(images, sorted_char_list, delay_mode)
            elif action == "说话":
                delay_positions = self.__talk(images, sorted_char_list, delay_mode)
            elif action == "转身":
                delay_positions = self.__turn(images, sorted_char_list, delay_mode)
            elif action == "gif":
                self.__gif(images, sorted_char_list, delay_mode)
            elif action == "bgm":
                self.__bgm(images, sorted_char_list)
            elif action == "更新":
                self.__update()
                # 重新排序所有角色
                sorted_char_list.sort(key=lambda x: x.index)
            pass

            duration = datetime.datetime.now() - start
            print(f"执行动作动【{self.name} - {self.render_index}】， 共花费：{duration.seconds}秒")
        
            start = datetime.datetime.now()
            self.__add_subtitle(images)
            duration = datetime.datetime.now() - start
            print(f"添加动作字幕【{self.name} - {self.render_index}】， 共花费：{duration.seconds}秒")
            return {
                "char": self.char, 
                "position": delay_positions
            }
        except Exception as e:
            print(f"Error: 动作名： {self.name} - 渲染顺序： {self.render_index}")
            raise(e)

if __name__ == "__main__":
    pass
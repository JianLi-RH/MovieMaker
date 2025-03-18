"""
这个类用来解析script.yaml中的`动作:`
"""
import os
import datetime

from moviepy import *
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
        if ' ' in name:
            # 打斗等组合动作可以同时操作多个角色
            # 因此不能在这里获取角色
            return None
        for c in self.activity.scenario.chars:
            if c.name == name:
                if c.rotate == "左右" and not c.name.lower().startswith("gif"):
                    basename = os.path.basename(c.image)
                    if "rotate_" in basename:
                        basename = basename.replace("rotate_", "")
                    else:
                        basename = f"rotate_{basename}"
                    new_path = os.path.join(os.path.dirname(c.image), basename)
                    if not os.path.exists(new_path):
                        im_mirror = ImageOps.mirror(Image.open(c.image))
                        im_mirror.save(new_path)
                    c.image = new_path
                    c.rotate = 0
                elif c.rotate == "上下":
                    c.rotate = 180
                    
                return c
        raise Exception(f"角色【{name}】不存在, 渲染顺序：{self.render_index}")
    
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
        """将当前动作的角色显示在背景上
        
        Example:
          -
            名称: 显示
            角色: 花荣 宋江 燕顺 王英 郑天寿
            渲染顺序: 1
          -
            名称: 显示
            角色: 花荣
            渲染顺序: 2
        """
        if ' ' in self.obj.get("角色"):
            str_chars = self.obj.get("角色")
            for str_char in str_chars.split(" "):
                c = self.__get_char(str_char)
                if c:
                    c.display = True
        else:
            self.char.display = True

    def __disappear(self):
        """让角色消失
        
        Example:
          -
            名称: 消失
            角色: 花荣 宋江 燕顺 王英 郑天寿
            渲染顺序: 1
          -
            名称: 消失
            角色: 花荣
            渲染顺序: 2
        """
        if ' ' in self.obj.get("角色"):
            str_chars = self.obj.get("角色")
            for str_char in str_chars.split(" "):
                c = self.__get_char(str_char)
                if c:
                    c.display = False
        else:
            self.char.display = False

    def __camera(self, images, add_chars=False):
        """
        处理 `镜头` 相关的动作，例如切换焦点，镜头拉近、拉远
        ***一个活动中不能有两个`镜头`动作***
        
        Example:
        -
          名称: 镜头
          持续时间: 1
          焦点: 中心
          变化: 
          渲染顺序: 0
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
        
        if add_chars:
            # 单独调用镜头动作的时候，需要绘制角色
            gif_index = 0
            for img in images:
                big_image = None
                for _char in self.activity.scenario.chars:
                    if _char.display:
                        _, big_image = ImageHelper.paint_char_on_image(image=img, 
                                                                    image_obj=big_image,
                                                                    char=_char, 
                                                                    save=False,
                                                                    gif_index=gif_index,
                                                                    dark=False)
            
                big_image.save(img)
                big_image.close()
                gif_index += 1

        for i in range(0, length):
            tmp_ratio = from_ratio + ratio_step * i
            x = original_center[0] + step_x * i
            y = original_center[1] + step_y * i

            tmp_img = ImageHelper.zoom_in_out_image(images[i], center=(x, y), ratio=tmp_ratio)
            images[i] = tmp_img

    def __fight(self, images, sorted_char_list):
        """一组随机的打斗动作， 
            因为不能保证相同渲染顺序的动作不使用同一个角色，所以不可以使用delay模式
        
        Example:
        -
        名称: 打斗
        角色: 武松 西门庆 刀 剑 (前两个是人物，后面两个是武器，武器可以省略)
        字幕: 
        - ['','', '', 'resources/ShengYin/游戏中打斗声音音效.mp3']
        渲染顺序: 6
        
        Params:
            images: 全部背景图片
            sorted_char_list: 排序后的角色
        Return:
            NA
        """
        str_chars = self.obj.get("角色")
        chars = [self.__get_char(x) for x in str_chars.split(" ")]
        if len(chars) < 2 :
            raise Exception("打斗动作至少包含两个角色")
        chars = sorted(chars, key=lambda x: x.pos[0])

        delay_positions = []
        for i in range(0, len(chars)):
            self.char = chars[i]
            initial_pos = self.char.pos # 起始位置
            # 固定变化的3个位置
            if i % 2 == 0:
                x_arr = [200, -100, 200]
                y_arr = [200, -200, 200]
            else:
                x_arr = [-200, 100, -200]
                y_arr = [-200, 200, -200]
                
            self.obj["结束位置"] = [
                [self.char.pos[0] + x_arr[0], self.char.pos[1] + y_arr[0]],
                [self.char.pos[0] + x_arr[1], self.char.pos[1] + y_arr[1]],
                [self.char.pos[0] + x_arr[2], self.char.pos[1] + y_arr[2]],
                initial_pos]# 使角色恢复起始位置
            self.obj["方式"] = "旋转"
            pos = self.__walk(images, sorted_char_list=sorted_char_list,delay_mode=True)
            delay_positions.append({
                "char": self.char, 
                "position": pos
            })
        
        
        for j in range(len(images)):   # 在每张图片上绘制全部角色
            big_image = None
            for _char in sorted_char_list:
                if not _char.display:
                    continue
                for char_pos in delay_positions:
                    if _char == char_pos["char"]:
                        delay_pos = char_pos["position"][j]
                        _char.pos = delay_pos[0]
                        _char.size = delay_pos[1]
                        _char.rotate = delay_pos[2]
                        
                        if len(delay_pos) > 3:
                            _char.image = delay_pos[3]
                        break
                _, big_image = ImageHelper.paint_char_on_image(char=_char, 
                                                                image=images[j],
                                                                image_obj=big_image,
                                                                save=False,
                                                                gif_index=j)

            if big_image:
                big_image.save(images[j])
                big_image.close()
        pass

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
        Return:
            [[tmp_pos, tmp_size, rotate, img], [tmp_pos, tmp_size, rotate, img]]
        """
        self.obj.update({"名字": f"gif_{len(sorted_char_list)}", "显示": "是"})
        self.char  = Character(self.obj)
        
        # 将GIF标记添加在显示列表中，用来设置显示顺序
        added_index = -1
        for i in range(len(sorted_char_list)):
            if sorted_char_list[i].index > self.char.index:
                added_index = i
                sorted_char_list.insert(i, self.char)
                break
        if added_index == -1:
            added_index = len(sorted_char_list)
            sorted_char_list.append(self.char)

        l = len(images)
        delay_pos = []
        for i in range(0, l):
            j = i % len(self.char.gif_frames)
            if delay_mode:
                delay_pos.append((self.char.pos, self.char.size, self.char.rotate, self.char.gif_frames[j]))
                continue
                
            big_image = None
            for _char in sorted_char_list:
                if _char.display:
                    # 这里存在一个显示层级的bug
                    _, big_image = ImageHelper.paint_char_on_image(image=images[i], 
                                                                    image_obj=big_image,
                                                                    char=_char, 
                                                                    save=False,
                                                                    gif_index=i)
            
            if big_image and not delay_mode:
                big_image.save(images[i])
                big_image.close()
        
        if not delay_mode:
            # 恢复列表
            sorted_char_list.pop(added_index)
        return delay_pos

    def __talk(self, images, sorted_char_list, delay_mode):
        """角色说话
        
        Example:
        -
        名称: 说话
        角色: 鲁智深
        焦点: [0.05, 0.65]  # 焦点 和 变化 不能同时设置，变化的优先级更高
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
            [[tmp_pos, tmp_size, rotate, img], [tmp_pos, tmp_size, rotate, img]]
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
                self.__camera(images, add_chars=False)
            elif self.obj.get("变化") == "近景":
                for img in images:
                    ImageHelper.cut_image(img, self.char)
        elif self.obj.get("焦点", None):
            focus = utils.covert_pos(self.obj.get("焦点", None))
            for img in images:
                ImageHelper.cut_image_by_focus(img, focus)
            
        return []
    
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
          -
            名称: 转身
            角色: 鲁智深
            持续时间: 
            角度: [[0, -30],[-30, 0],[0, -30]] # 多角度转动，通常用于来回转动
            比例: 1
            字幕:
            - ['','', '听说菜园里来了个新和尚', '水浒传/第九回/泼皮偷菜/听说菜园里来了个新和尚.mp3']
            渲染顺序: 1
            
        Params:
            images: 全部背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
        Return:
            [[tmp_pos, tmp_size, rotate, img], [tmp_pos, tmp_size, rotate, img]]
        """
        
        str_degree = self.obj.get("角度", 0)
        delay_positions = []
        total_feames = len(images)
        self.char.display = True # 强制显示当前角色
        
        if isinstance(str_degree, int):
            str_degree = [self.char.rotate, str_degree]
        
        if isinstance(str_degree, list):
            # 连续转动
            start_rotate = self.char.rotate
            if isinstance(str_degree[0], list):
                steps = len(str_degree)
                step_frames = int(total_feames / steps)
                for i in range(steps):
                    start = str_degree[i][0]
                    end = str_degree[i][1]
                    if i == (steps - 1):
                        # 最后一步占用剩余的全部图片
                        step_frames = total_feames - step_frames * i
                    degree_step = (start - end) / step_frames
                    for i in range(step_frames):
                        start_rotate += degree_step
                        delay_positions.append([self.char.pos, self.char.size, start_rotate])
                pass
            else:
                degree_step = (str_degree[1] - str_degree[0]) / total_feames
                for i in range(total_feames):
                    start_rotate += degree_step
                    delay_positions.append([self.char.pos, self.char.size, start_rotate])
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

    def __update(self):
        """更新某个角色
        
        Example:
          -
            名称: 更新
            角色: 鲁智深
            素材: 水浒传/人物/鲁智深1.png
            角度: 左右
            透明度: 0.2
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
        if "透明度" in keys:
            self.char.transparency = self.obj.get("透明度")
        if "显示" in keys:
            self.char.display = True if self.obj.get("显示") == '是' else False
        if "图层" in keys:
            self.char.index = int(self.obj.get("图层", 0))
            
        self.char = self.__get_char(self.char.name)
    
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
            开始角度: 
            结束角度: 左右
            结束消失: 是
            比例:   # 比例变化，开始比例 - 结束比例
            方式:   # 自然 / 旋转 / 眩晕 / 45 -- 如果是数字的话，会从初始位置旋转到给定角度 , 最后恢复原样
            字幕: #Yunyang, Male
              - ['','', '跑路', 'resources/ShengYin/卡通搞笑逃跑音效.mp3']
            渲染顺序: 6
        
        Params:
            images: 全部背景图片
            sorted_char_list: 排序后的角色
            delay_mode: 延迟绘制其他角色
        Return:
            [[tmp_pos, tmp_size, rotate, img], [tmp_pos, tmp_size, rotate, img]]
        """
        if not self.char:
            raise Exception("角色不存在")
        
        if self.obj.get("开始角度"):
            self.char.rotate = self.obj.get("开始角度")
            self.char = self.__get_char(self.char.name)
        
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
        
        # mode ["自然", "旋转", "眩晕", 数字]:
        step_rotates = []
        total_image = len(images)
        if mode == "旋转":
            _step_rotate = 360 * config_reader.round_per_second / self.activity.fps  # 每秒旋转圈数
            step_rotates = [self.char.rotate + num * _step_rotate for num in range(0, total_image)]
        elif mode == "眩晕":
            rotate_per_image = 45 / (self.activity.fps / 4) # 45度角来回摆动
            initial_degree = self.char.rotate
            for i in range(1, total_image + 1):
                if i % self.activity.fps > (self.activity.fps / 4) and i % self.activity.fps <= (self.activity.fps - self.activity.fps / 4):
                    initial_degree += rotate_per_image
                else:
                    initial_degree -= rotate_per_image
                step_rotates.append(initial_degree)
        elif isinstance(mode, int):
            _step_rotate = mode / self.timespan / self.activity.fps
            step_rotates = [self.char.rotate + num * _step_rotate for num in range(0, total_image)]
        else:
            step_rotates = [self.char.rotate] * total_image
        step_rotates[-1] = self.char.rotate # 最后一张图片恢复角色角度
            
        step_size = []
        for i in range(0, total_image):
            tmp_size = (int(start_size[0] * (1 + ratio_x * i)), int(start_size[1] * (1 + ratio_y * i)))
            step_size.append(tmp_size)
        
        step_pos = []
        for i in range(steps):    # 例如：[[120, 200], [10, 12]]
            if i == steps - 1:
                # 最后一步包含剩余的全部图片
                frames = len(images) - (steps - 1) * frames

            end_pos = utils.covert_pos(end_pos_list[i])
            # 每一步在x,y方向的进度
            step_x = (end_pos[0] - start_pos[0]) / frames
            step_y = (end_pos[1] - start_pos[1]) / frames
            
            for j in range(0, frames):
                tmp_pos = (int(start_pos[0] + step_x * j), int(start_pos[1] + step_y * j))
                step_pos.append(tmp_pos)
            start_pos = end_pos # 重新设置轨迹的开始坐标
        
        pos = [] # 每一个元素：(tmp_pos, tmp_size, rotate)
        for i in range(0, total_image):
            pos.append((step_pos[i], step_size[i], step_rotates[i]))
     
        if delay_mode:
            if self.obj.get("结束角度"):
                self.char.rotate = self.obj.get("结束角度")
                self.char = self.__get_char(self.char.name)
                pos[-1] = (pos[-1][0], pos[-1][1], self.char.rotate)

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
    
        if self.obj.get("结束角度"):
            self.char.rotate = self.obj.get("结束角度")
            self.char = self.__get_char(self.char.name)
        
        if self.obj.get("结束消失", None) == "是":
            self.__disappear()
            
        return []

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
            sPath = subtitle[3] # ["start", "end"， “text”， “music file”, xxx, xxx]
            if not os.path.exists(sPath):
                # 使用科大讯飞接口生成语音
                try:
                    speaker = self.obj.get("发音人") if self.name == "gif" else self.char.speaker
                    ttsengine = self.obj.get("发音人引擎") if self.name == "gif" else self.char.tts_engine
                    AudioHelper.covert_text_to_sound(subtitle[2], sPath, speaker, ttsengine=ttsengine)
                except Exception as e:
                    print(f"Convert text failed: ", subtitle)
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
        
        通用属性：
        -
          名称:         # 动作名称
          角色:         # 角色列表中存在的角色“名字”
          字幕颜色:     # 当前动作使用的字母颜色，如: black。如果没设置的话，会使用活动中的字幕颜色
          渲染顺序:     # 当前动作在本次活动中的渲染顺序，默认是0。可以设置为整数，浮点数等数值类型
        """
        self.activity = activity
        self.obj = obj
        self.name = self.obj.get("名称")
        self.render_index = float(self.obj.get("渲染顺序")) if self.obj.get("渲染顺序") else 0.0    # 动作执行的顺序，数值一样的同时执行， 从小到达执行
        self.char = self.__get_char(self.obj.get("角色"))
        self.subtitle_color, self.subtitle = self.__get_subtitle()
        if self.subtitle_color == None and self.activity.subtitle_color:
            # 当动作没有设置字幕颜色时，使用活动的字幕颜色覆盖动作的字幕颜色
            self.subtitle_color = self.activity.subtitle_color
        keep = utils.get_time(obj.get("持续时间", 0))   # 优先级最高
        if keep > 0:
            self.timespan = keep
        elif self.subtitle:
            self.timespan = self.subtitle[-1][1] if self.subtitle else 0 # 最后一个字幕的第二个字段就是全部字幕的时长
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
                "position": delay_positions,
                "disappear_end": True  # 结束后隐藏角色
            }
        """
        try:
            
            start = datetime.datetime.now()
            
            # [[tmp_pos, tmp_size, rotate], [tmp_pos, tmp_size, rotate]] 
            # [[tmp_pos, tmp_size, rotate, img], [tmp_pos, tmp_size, rotate, img]]
            delay_positions = []
            action = self.obj.get("名称").lower()

            if action == "bgm":
                self.__bgm(images, sorted_char_list)
            elif action == "消失":
                self.__disappear()
            elif action == "显示":
                self.__display()
            elif action == "镜头":  # 还需要验证
                self.__camera(images, add_chars=True)
            elif action == "更新":
                self.__update()
                # 重新排序所有角色
                sorted_char_list.sort(key=lambda x: x.index)
            elif action == "打斗":
                self.__fight(images, sorted_char_list)
            elif action == "gif":
                delay_positions = self.__gif(images, sorted_char_list, delay_mode)
            elif action == "说话":
                delay_positions = self.__talk(images, sorted_char_list, delay_mode)
            elif action == "转身":
                delay_positions = self.__turn(images, sorted_char_list, delay_mode)
            elif action == "行进":
                delay_positions = self.__walk(images, sorted_char_list, delay_mode)
            pass

            duration = datetime.datetime.now() - start
            print(f"执行动作动【{self.name} - {self.render_index}】， 共花费：{duration.seconds}秒")
        
            start = datetime.datetime.now()
            self.__add_subtitle(images)
            duration = datetime.datetime.now() - start
            print(f"添加动作字幕【{self.name} - {self.render_index}】， 共花费：{duration.seconds}秒")
            result = {
                "char": self.char, 
                "position": delay_positions
            }
            if self.obj.get("结束消失", None) == "是":
                result["disappear_end"] = True
            return result
            
        except Exception as e:
            print(f"Error: 动作名： {self.name} - 渲染顺序： {self.render_index}")
            raise(e)

if __name__ == "__main__":
    pass
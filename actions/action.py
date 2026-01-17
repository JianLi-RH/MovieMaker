"""
这个类用来解析script.yaml中的`动作:`
"""
import os
import datetime
import json
import random
import re

from moviepy import *
from PIL import Image, ImageOps
from pydub import AudioSegment

import config_reader
import utils
from character import *
from libs import AudioHelper, ImageHelper
from exceptions import (
    CharacterNotFoundError,
    InsufficientCharactersError,
    MissingActionParameterError,
    InvalidSubtitleFormatError,
    TTSException
)

from actions import get_char, logger
from actions import (
                    bgm, 
                    camera, 
                    disappear, 
                    display, 
                    gif, 
                    stop, 
                    switch, 
                    talk, 
                    turn, 
                    update,
                    walk
                )


class Action:
    """The Action(动作) class"""

    def __fight(self, images, sorted_char_list):
        """一组随机的打斗动作， 
            因为不能保证相同渲染顺序的动作不使用同一个角色，所以不可以使用delay模式
        
        Example:
        -
        名称: 打斗
        角色: 武松 西门庆 刀 剑 (前两个是人物，后面两个是武器，武器可以省略)
        幅度: 小    # 小， 中， 大
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
        chars = [get_char(x, self.chars) for x in str_chars.split(" ")]
        if len(chars) < 2:
            logger.error(f"打斗动作角色数量不足: {len(chars)}")
            raise InsufficientCharactersError("打斗", 2, len(chars))
        chars = sorted(chars, key=lambda x: x.pos[0])
        
        amplitude = self.obj.get("幅度", "中")
        amplitude_value = 100
        if amplitude == "小":
            amplitude_value = 50
        elif amplitude == "中":
            amplitude_value = 100
        else:
            amplitude_value = 200

        delay_positions = []
        
        random_list1 = [random.randint(-amplitude_value, amplitude_value) for _ in range(3)]
        random_list2 = [random.randint(-amplitude_value, amplitude_value) for _ in range(3)]
        
        pos1 = (random_list1[0], random_list2[0])
        pos2 = (random_list1[1], random_list2[1])
        pos3 = (random_list1[2], random_list2[2])
        
        for i in range(0, len(chars)):
            self.char = chars[i]
            initial_pos = self.char.pos # 起始位置
            # 固定变化的3个位置
            if i % 2 == 0:
                xy_arr = (pos1, pos2, pos3)
            else:
                xy_arr = ((-pos1[0], -pos1[1]), (-pos2[0], -pos2[1]), (-pos3[0], -pos3[1]))
                
            self.obj["结束位置"] = [
                [self.char.pos[0] + xy_arr[0][0], self.char.pos[1] + xy_arr[0][1]],
                [self.char.pos[0] + xy_arr[1][0], self.char.pos[1] + xy_arr[1][1]],
                [self.char.pos[0] + xy_arr[2][0], self.char.pos[1] + xy_arr[2][1]],
                initial_pos]# 使角色恢复起始位置
            self.obj["方式"] = "旋转"
            pos = walk.Do(action=self, images=images, sorted_char_list=sorted_char_list, delay_mode=True)
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
            logger.error(f"字幕格式错误，应为列表类型: {type(subtitles)}")
            raise InvalidSubtitleFormatError(subtitles, "字幕必须是列表格式")
        end = 0
        for subtitle in subtitles:
            sPath = subtitle[3] # ["start", "end"， “text”， “music file”, xxx, xxx]
            if not os.path.exists(sPath):
                # 使用科大讯飞接口生成语音
                try:
                    speaker = self.obj.get("发音人") if self.name == "gif" or self.name == "BGM" else self.char.speaker
                    ttsengine = self.obj.get("发音人引擎") if self.name == "gif" or self.name == "BGM" else self.char.tts_engine
                    logger.debug(f"生成TTS音频: {subtitle[2]} -> {sPath}")
                    AudioHelper.covert_text_to_sound(subtitle[2], sPath, speaker, ttsengine=ttsengine)
                except Exception as e:
                    logger.debug(f"字幕信息: {subtitle}")
                    logger.debug(f"渲染顺序: {self.render_index}")
                    logger.debug(f"动作对象: {json.dumps(self.obj, indent=4, ensure_ascii=False)}")
                    logger.error(f"TTS转换失败: {subtitle}")
                    if self.char:
                        logger.debug(f"角色信息: {json.dumps(self.char.__dict__, indent=4, ensure_ascii=False, default=str)}")
                    raise TTSException(subtitle[2], str(e), ttsengine)
            try:
                _length = AudioFileClip(sPath).duration
            except:
                try:
                    _audio = AudioSegment.from_file(sPath)
                    _length = len(_audio) / 1000.0
                except Exception as e:
                    logger.error(f"获取音频长度失败: {sPath}")
                    raise
            if not subtitle[0]:
                # 字母设置了开始时间
                subtitle[0] = end
            else:
                subtitle[0] = float(subtitle[0])
            subtitle[1] = float(subtitle[0]) + _length

            end = subtitle[1]
            
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
          名称:        # 动作名称
          角色:        # 角色列表中存在的角色“名字”
          字幕颜色:     # 当前动作使用的字母颜色，如: black。如果没设置的话，会使用活动中的字幕颜色
          持续时间:     # 当前动作的持续时间，单位秒
          渲染顺序:     # 当前动作在本次活动中的渲染顺序，默认是0。可以设置为整数，浮点数等数值类型
        """
        start = datetime.datetime.now()
        self.activity = activity
        self.chars = self.activity.scenario.chars
        self.obj = obj
        self.name = self.obj.get("名称")
        self.render_index = float(self.obj.get("渲染顺序")) if self.obj.get("渲染顺序") else 0.0    # 动作执行的顺序，数值一样的同时执行， 从小到达执行
        
        if self.obj.get("角色") and len(self.obj.get("角色")) > 0:
            self.char = get_char(self.obj.get("角色"), self.chars)
            if  not self.char and not re.search(r'[ ,]', self.obj.get("角色")) :
                logger.error(f"角色不存在({self.obj.get("角色")}), 渲染顺序：{self.render_index}")
                raise CharacterNotFoundError(self.obj.get("角色"), self.render_index)

        self.subtitle_color, self.subtitle = self.__get_subtitle()
        if self.subtitle_color == None and self.activity.subtitle_color:
            # 当动作没有设置字幕颜色时，使用活动的字幕颜色覆盖动作的字幕颜色
            self.subtitle_color = self.activity.subtitle_color
        keep = utils.get_time(obj.get("持续时间", 0))   # 优先级最高
        if keep > 0:
            self.timespan = keep
        elif self.subtitle:
            self.timespan = self.subtitle[-1][1] if self.subtitle else 0 # 最后一个字幕的第二个字段就是全部字幕的时长
        # elif self.activity.bgm:
        #     # 以活动的背景声音长度作为动作的长度
        #     self.timespan = AudioFileClip(self.activity.bgm).duration
        elif self.activity.keep:
            # 以活动的持续时间作为动作的长度
            self.timespan = utils.get_time(obj.get("持续时间", None))
        else:
            self.timespan = 0
        
        duration = datetime.datetime.now() - start
        logger.debug(f"初始化Action【{self.name}】， 共花费：{duration.seconds}秒")

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
                bgm.Do(images, sorted_char_list)
            elif action == "转场":
                switch.Do(action=self, images=images, sorted_char_list=sorted_char_list)
            elif action == "静止":
                stop.Do(images, sorted_char_list)
            elif action == "消失":
                disappear.Do(self)
            elif action == "显示":
                display.Do(self)
            elif action == "镜头":  # 还需要验证
                camera.Do(action=self, images=images, add_chars=True)
            elif action == "更新":
                update.Do(self)
                # 重新排序所有角色
                sorted_char_list.sort(key=lambda x: x.index)
            elif action == "打斗":
                self.__fight(images, sorted_char_list)
            elif action == "gif":
                delay_positions = gif.Do(action=self, images=images, sorted_char_list=sorted_char_list, delay_mode=delay_mode)
            elif action == "说话":
                delay_positions = talk.Do(action=self, images=images, sorted_char_list=sorted_char_list, delay_mode=delay_mode)
            elif action == "转身":
                delay_positions = turn.Do(action=self, images=images, sorted_char_list=sorted_char_list, delay_mode=delay_mode)
            elif action == "行进":
                delay_positions = walk.Do(action=self, images=images, sorted_char_list=sorted_char_list, delay_mode=delay_mode)
            elif action == "队列":
                # 这是一个特殊动作， 在活动（activaty）中会被转换成一组walk 动作
                # example:
                # -
                #     名称: 队列
                #     角色: 卢俊义 枪1 朱武 关胜 刀1 林冲 秦明 呼延灼 董平 徐宁 钩镰枪 杨志 索超 张清 朱仝 史进
                #     开始位置: 
                #     开始角度: 
                #     结束位置: # 可以使用“结束位置”统一设置全部角色的结束位置，也可以使用xy设置各个角色的位移
                #     x:      # 整数， -100, 100; [-1, 1] 之间的小数（包括-1, 1）, 乘以宽度得出移动距离
                #     y:      # 整数， -100, 100; [-1, 1] 之间的小数（包括-1, 1）, 乘以高度得出移动距离
                #     结束消失: 是
                #     比例: 
                #     字幕: 
                #     - ['','', '', 'resources/ShengYin/跑步声.mp3']
                #     方式: 
                #     渲染顺序: 1
                pass
            pass

            duration = datetime.datetime.now() - start
            logger.debug(f"执行动作【{self.name} - {self.render_index}】， 共花费：{duration.seconds}秒")

            start = datetime.datetime.now()
            self.__add_subtitle(images)
            duration = datetime.datetime.now() - start
            logger.debug(f"添加动作字幕【{self.name} - {self.render_index}】， 共花费：{duration.seconds}秒")
            result = {
                "char": self.char if hasattr(self, "char") else None, 
                "position": delay_positions
            }
            if self.obj.get("结束消失", "否") == "是":
                result["disappear_end"] = True
            return result
            
        except Exception as e:
            logger.error(f"动作执行失败: 动作名={self.name}, 渲染顺序={self.render_index}")
            logger.debug(f"动作对象: {json.dumps(self.obj, indent=4, ensure_ascii=False)}")
            raise

if __name__ == "__main__":
    pass
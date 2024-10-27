"""
这个类用来解析script.yaml中的`活动:`
"""
import math
import queue
import shutil
import tempfile
import threading

import yaml

import config_reader
import utils
from action import *
from libs import SuCaiHelper

sem=threading.Semaphore(10)
q = queue.Queue(10)
def worker():
    with sem:
        while True:
            text, images, subtitle_mode, text_list = q.get()
            if text:
                print("生成字幕：", text)
                for img in images:
                    ImageHelper.add_text_to_image(img, text, overwrite_image=True, mode=subtitle_mode, text_list=text_list)
            q.task_done()

class Activity:
    """The Activity(活动) class"""

    def __check_images(self):
***REMOVED***第一次执行action的时候, images会是空的, 所以需要生成一组图片

        Return:
            一组图片
***REMOVED***
        path = os.path.join(config_reader.output_dir, self.name)
        os.makedirs(path, exist_ok=True)
        print("背景图片将被保存在：", path)

        images = []
        background_image = self.scenario.background_image ***REMOVED*** 已经resize之后的图片
        if background_image.lower().endswith(".gif"):
            bg_frames = ImageHelper.get_frames_from_gif(background_image)
            l = len(bg_frames)
            ext = bg_frames[0].split('.')[-1]

            for i in range(0, self.total_frame):
                index = i % l
                new_path = os.path.join(path, f"{i***REMOVED***.{ext***REMOVED***")
                shutil.copy(bg_frames[index], new_path)
                ImageHelper.resize_image(new_path)
                images.append(new_path)
        else:
            ext = background_image.split('.')[-1]
            for i in range(0, self.total_frame):
                new_path = os.path.join(path, f"{i***REMOVED***.{ext***REMOVED***")
                shutil.copy(background_image, new_path)
                images.append(new_path)

        print("准备背景图片结束，共计", self.total_frame, "张图片")
        return images

    def __get_render_list(self):
***REMOVED***获取渲染列表
        index小的action最先显示
        不在rendered_action_list里的角色全程显示
        
        Return:
            rendered_action_list: [[{index:0, action: xxx***REMOVED***, {index:0, action: yyy***REMOVED***], [{"index": 1, "action": zzz***REMOVED***]]
***REMOVED***
        rendered_action_list = []
        for act in self.actions:
            render = {"index": act.render_index, "action": act***REMOVED***
            actions = next(filter(lambda x: x[0].get("index", 0) == render.get("index", 0), rendered_action_list), [])
            if actions:
                actions.append(render)
***REMOVED***
                rendered_action_list.append([render])

        if rendered_action_list:
            rendered_action_list.sort(key=lambda x: int(x[0].get("index", 0)))
        return rendered_action_list

    def __get_timespan(self, obj):
***REMOVED***获取活动总时间，单位秒

        Pramas:
            obj: 活动对象的yaml
        Return:
            活动总时长。单位秒
***REMOVED***
        ***REMOVED*** 在活动节点中设置的时间，与具体动作无关
        keep = utils.get_time(obj.get("持续时间", None))
        ***REMOVED*** 活动背景音乐的时长，当没有设置`持续时间`和字幕的时候会根据背景音乐长度设置总时长
        bgm_length = AudioFileClip(self.bgm).duration if self.bgm else 0

        ***REMOVED*** 活动字幕的时长
        subtitle_length = 0.0
        if self.subtitle:
            if isinstance(self.subtitle, str):
                ***REMOVED*** 处理字幕文件
                self.subtitle = utils.get_sub_title_list(self.subtitle)
            for sb in self.subtitle:
                if len(sb) > 3 and sb[3]:
                    sPath = SuCaiHelper.get_sucai(sb[3])
                    subtitle_length += AudioFileClip(sPath).duration

        ***REMOVED*** 全部动作的长度
        action_length = 0.0
        calculated_index = []   ***REMOVED*** save all actions length, for example: {'index': 0, 'action': action***REMOVED***
        for act in self.actions:
            same_index_action = next(filter(lambda x: x["index"] == act.render_index, calculated_index), None)
            if same_index_action:
                if same_index_action["action"].timespan < act.timespan:
                    same_index_action['action'] = act
***REMOVED***
                calculated_index.append({'index': act.render_index, 'action': act***REMOVED***)
        action_length = sum([l["action"].timespan for l in calculated_index])
        
        for action in self.actions:
            ***REMOVED*** 使用同级别最长timespan的timespan设置没有timespan的动作的timespan
            if action.timespan == 0:
                same_level_action = next(filter(lambda x: x["index"] == action.render_index, calculated_index), None)
                if same_level_action:
                    action.set_timespan(same_level_action["action"].timespan)

        return max([keep, bgm_length, subtitle_length, action_length])

    def __init__(self, scenario, obj):
***REMOVED***
        初始化Activity

        Param:
            scenario: Scenario对象实例
            obj: script里面的脚本片段
***REMOVED***
        self.scenario = scenario
        self.name = obj.get("名字")
        self.description = obj.get("描述", "")
        self.subtitle = obj.get("字幕") if obj.get("字幕") else []
        self.subtitle_mode = obj.get("字幕样式", 'normal')
        self.bgm = SuCaiHelper.get_sucai(obj.get("背景音乐", None))
        self.actions = [Action(self, action) for action in obj.get("动作", [])]
        self.timespan = self.__get_timespan(obj)    ***REMOVED*** 活动的总长度
        self.fps = int(obj.get("fps", None)) if obj.get("fps", None) else config_reader.fps
        self.total_frame = math.ceil(self.timespan * self.fps)   ***REMOVED*** 根据当前活动的总时长，得到当前活动所需的视频总帧数


    def to_video(self):
***REMOVED***
        将‘活动’转换成视频

        Return:
            视频片段clip
***REMOVED***
        images = self.__check_images()
        action_list = self.__get_render_list()

        if self.subtitle:
            ***REMOVED*** 添加字幕
            previous_end = 0
            l = len(self.subtitle)
            for i in range(0, l):
                if self.subtitle[i][0]:
                    start = utils.get_time(self.subtitle[i][0])
    ***REMOVED***
                    if previous_end > 0:
                        start = previous_end
        ***REMOVED***
                        start = 0
                self.subtitle[i][0] = start
                start_num = int(start/self.timespan*len(images))

                if self.subtitle[i][1]:
                    end = utils.get_time(self.subtitle[i][1])
    ***REMOVED***
                    if len(self.subtitle[i]) > 3 and self.subtitle[i][3]:
                        sPath = SuCaiHelper.get_sucai(self.subtitle[i][3])
                        end = start + utils.get_audio_length(sPath)
        ***REMOVED***
                        ***REMOVED*** 只有最后一个字幕才可以同时没有结束时间与声音文件
                        end = self.timespan
                self.subtitle[i][1] = end
                previous_end = end

                if i == len(self.subtitle) -1:
                    ***REMOVED*** 最后一段字幕，
                    end_number = len(images)
    ***REMOVED***
                    end_number = int(end/self.timespan * len(images))

                ***REMOVED*** 添加一个表示图片位置的元素到字幕列表的最后
                self.subtitle[i].append((start_num, end_number))

        start = 0 ***REMOVED*** 每个action的开始位置 （图片下标）
        for actions in action_list:
            delay_mode = len(actions) > 1   ***REMOVED*** 当同时运行多个动作的时候，需要在所有动作执行结束再绘制其他角色
            video_start = start/len(images) ***REMOVED*** action在整段视频中的开始位置，方便后面添加声音
            delay_start = start
            action_ends = [0]
            delay_positions = []
            for act in actions:
                ***REMOVED*** 注意：一个活动（activity）中不能有两个`镜头`动作(action)
                print("生成动作：", act["action"].name)
                act["start"] = video_start
                
                if act["action"].name in ["显示", "消失"]:
                    delay_mode = False
                    action_ends.append(start)
                    act["action"].to_videoframes(images, self.scenario.chars, delay_mode)
                    continue
                
                current_atc_end = start + math.ceil(act["action"].timespan * self.fps)
                action_ends.append(current_atc_end)
                current_image_list = images[start : current_atc_end]
                temp_delay_positions = act["action"].to_videoframes(current_image_list, self.scenario.chars, delay_mode)
                
                if delay_mode:
                    delay_positions.append({"char": act["action"].char.name, "position": temp_delay_positions***REMOVED***)

            if delay_mode:
                delay_images = images[delay_start : max(action_ends)]
                delay_action_char = [pos["char"] for pos in delay_positions]
                i = 0
                for img_path in delay_images:   ***REMOVED*** 在每张图片上绘制全部角色
                    for _char in self.scenario.chars:
                        if _char.name in delay_action_char:
                            delay_pos_list = next(filter(lambda x: x["char"] == _char.name, delay_positions))
                            delay_pos = delay_pos_list["position"][i]
                            _char.pos = delay_pos[0]
                            _char.size = delay_pos[1]
                            _char.rotate = delay_pos[2]

                        ImageHelper.paint_char_on_image(img_path, char=_char, overwrite=True)
                    i += 1
            start = max(action_ends)

        if self.subtitle:
            print("self.subtitle: \n", self.subtitle)
            ***REMOVED*** daemon：结束主进程的时候可以同时结束子线程
            threading.Thread(target=worker, daemon=True).start()
            l = len(self.subtitle)
            for i in range(0, l):
                ***REMOVED*** 创建新线程
                start_num = self.subtitle[i][-1][0]
                end_number = self.subtitle[i][-1][1]
                print(f"start_num: {start_num***REMOVED***, end_number: {end_number***REMOVED***")
                tmp_images = images[start_num : end_number]
                text_list = [x[2] for x in self.subtitle[0 if i < 2 else i - 1 : i + 2]]    ***REMOVED*** 最多显示3行文字
                q.put((self.subtitle[i][2], tmp_images, self.subtitle_mode, text_list))

        ***REMOVED*** 等待所有线程完成
        q.join()
        draw_char_actions = set([act["action"].name for act_in_same_level in action_list for act in act_in_same_level]) - set({"显示", "消失"***REMOVED***)
        if not draw_char_actions:
            ***REMOVED*** 如果所有的动作都没有绘制角色，则统一绘制一次
            for img in images:
                for _char in self.scenario.chars:
                    if _char.display:
                        ImageHelper.paint_char_on_image(img, char=_char, overwrite=True)

        ***REMOVED*** 先把图片转换成视频
        video = VideoHelper.create_video_clip_from_images(images)
        if self.bgm:
    ***REMOVED***添加活动背景音乐"""
            print("添加背景音乐：", self.bgm)
            video = VideoHelper.add_audio_to_video(video, self.bgm)
        if self.subtitle:
            ***REMOVED*** 添加字幕声音 -- 活动的字幕
            audio_list = [AudioFileClip(SuCaiHelper.get_sucai(st[3])).set_start(st[0]) for st in self.subtitle if len(st) > 3 and st[3]]
            if audio_list:
                fd, tmp_audio_path = tempfile.mkstemp(suffix=".mp3")
                print(f"把声音组装起来保存到{tmp_audio_path***REMOVED***")
                concatenate_audioclips(audio_list).write_audiofile(tmp_audio_path)
                video = VideoHelper.add_audio_to_video(video, tmp_audio_path, start=self.subtitle[0][0])
        
        video_total_length = video.duration
        for actions in action_list:
            ***REMOVED*** 添加动作的声音
            action_ends = []
            start = actions[0]["start"] * video_total_length
            for act in actions:
                if act["action"].subtitle:
                    action_ends.append(act["action"].subtitle[-1][1])
                    for subtitle in act["action"].subtitle:
                        video = VideoHelper.add_audio_to_video(video, subtitle[3], start=(start + subtitle[0]))
        return video

***REMOVED***
    with open('script.yaml', 'r') as file:
       script = yaml.safe_load(file)

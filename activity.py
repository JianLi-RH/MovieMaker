"""
这个类用来解析script.yaml中的`活动:`
"""
import math
import queue
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
        for a in self.actions:
            render = {"index": None, "action": None***REMOVED***
            if a.obj.get("名称", None) == "镜头":
                ***REMOVED*** 镜头相关动作会改变背景图片尺寸，但是不会改变角色位置，所以镜头需要最后进行渲染
                render = {"index": sys.maxsize, "action": a***REMOVED***
            elif a.obj.get("名称", None) == "更新":
                ***REMOVED*** 更新角色总是最早执行
                render = {"index": -(sys.maxsize - 1), "action": a***REMOVED***
            elif a.obj.get("名称", None) == "显示":
                ***REMOVED*** 显示角色
                c = next(filter(lambda x:x.name == a.obj.get("角色", None), self.scenario.chars))
                c.display = True
                continue
            elif a.obj.get("名称", None) == "消失":
                ***REMOVED*** 隐藏角色
                c = next(filter(lambda x:x.name == a.obj.get("角色", None), self.scenario.chars))
                c.display = False
                continue
***REMOVED***
                render = {"index": a.render_index, "action": a***REMOVED***
            
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
        actions = [Action(self, action) for  action in obj.get("动作", [])] ***REMOVED*** 不需要总时长
        action_length = 0.0
        calculated_index = []   ***REMOVED*** save all actions length, for example: {'index': 0, 'length': 5***REMOVED***
        for act in actions:
            same_index_action = next(filter(lambda x: x["index"] == act.render_index, calculated_index), None)
            if same_index_action:
                if same_index_action['length'] < act.timespan:
                    same_index_action['index'] = act.render_index
                    same_index_action['length'] = act.timespan
***REMOVED***
                calculated_index.append({'index': act.render_index, 'length': act.timespan***REMOVED***)
        action_length = sum([l["length"] for l in calculated_index])

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
        self.actions = []
        self.timespan = self.__get_timespan(obj)
        self.fps = int(obj.get("fps", None)) if obj.get("fps", None) else config_reader.fps
        self.total_frame = math.ceil(self.timespan * self.fps)   ***REMOVED*** 根据当前活动的总时长，得到当前活动所需的视频帧数
        for action in obj.get("动作", []):
            self.actions.append(Action(self, action, self.timespan))

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

        start, end = 0, 0
        for actions in action_list:
            delay_char = len(actions) > 1   ***REMOVED*** 当同时运行多个动作的时候，需要在所有动作执行结束再绘制其他角色
            char_not_in_action = self.scenario.chars[:]
            delay_start = start
            action_ends = []
            for act in actions:
                ***REMOVED*** 注意：一个活动（activity）中不能有两个`镜头`动作（action）
                print("生成动作：", act["action"].obj.get("名称"))
                current_atc_end = start + math.ceil(act["action"].timespan * self.fps)
                action_ends.append(current_atc_end)
                current_image_list = images[start : current_atc_end]
                act["action"].to_videoframes(current_image_list, self.scenario.chars, delay_char)
                
                if delay_char:
                    char_not_in_action = list(filter(lambda x: x.name != act["action"].char.name, char_not_in_action))
            end = max(action_ends)
            if delay_char:
                ***REMOVED*** 有bug, 如果角色的图层在动作的角色下面，那么就会被错误的放在动作上面
                for img_path in images[delay_start : end]:
                    for _char in char_not_in_action:
                        ImageHelper.paint_char_on_image(img_path, char=_char, overwrite=True)
            start = end

        if self.subtitle:
            print("self.subtitle: \n", self.subtitle)
            ***REMOVED*** daemon结束主进程的时候可以同时结束子线程
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
        
        start = 0
        for actions in action_list:
            ***REMOVED*** 添加动作的声音
            action_ends = []
            for act in actions:
                if act["action"].subtitle:
                    action_ends.append(act["action"].subtitle[-1][1])
                    for subtitle in act["action"].subtitle:
                        video = VideoHelper.add_audio_to_video(video, subtitle[3], start=start)
            start += max(action_ends)
        return video

***REMOVED***
    with open('script.yaml', 'r') as file:
       script = yaml.safe_load(file)

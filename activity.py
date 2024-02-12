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
                    ImageHelper.add_text_to_image(img, text, overwrite_image=False, mode=subtitle_mode, text_list=text_list)
            q.task_done()

class Activity:
    """The Activity(活动) class"""

    def __check_images(self):
        """第一次执行action的时候, images会是空的, 所以需要生成一组图片

        Return:
            一组图片
        """
        path = os.path.join(config_reader.output_dir, self.name)
        if not os.path.exists(path):
            os.mkdir(path)

        images = []
        background_image = self.scenario.background_image # 已经resize之后的图片
        if background_image.lower().endswith(".gif"):
            bg_frames = ImageHelper.get_frames_from_gif(background_image)
            ImageHelper.resize_images(bg_frames)
            l = len(bg_frames)
            ext = bg_frames[0].split('.')[-1]

            for i in range(0, self.total_frame):
                index = i % l
                new_path = os.path.join(path, f"{i}.{ext}")
                shutil.copy(bg_frames[index], new_path)
                images.append(new_path)
        else:
            ext = background_image.split('.')[-1]
            for i in range(0, self.total_frame):
                new_path = os.path.join(path, f"{i}.{ext}")
                shutil.copy(background_image, new_path)
                images.append(new_path)

        print("准备背景图片结束，共计", self.total_frame, "张图片")
        return images

    def __get_display_list(self):
        """获取显示列表， index小的最先显示"""
        display_list = []
        char_in_actions = []
        for a in self.actions:
            if a.obj.get("名称", None) == "镜头":
                # 镜头相关动作会改变背景图片尺寸，但是不会改变角色位置，所以镜头需要最后进行渲染
                display_list.append({"index": 999, "action": a})
            elif a.obj.get("名称", None) == "更新":
                # 更新角色总是最早执行
                display_list.append({"index": -999, "action": a})
            else:
                if a.char:
                    char_in_actions.append(a.char.name)
                    display_list.append({"index": a.char.index, "action": a})
                else:
                    display_list.append({"index": -1, "action": a})

        for char in self.scenario.chars:
            if not char.name in char_in_actions:
                display_list.append({"index": char.index, "char": char})

        if display_list:
            display_list.sort(key=lambda x: int(x.get("index", 0)))
        return display_list

    def __get_timespan(self, obj):
        """获取活动总时间，单位秒

        Pramas:
            obj: 活动对象的yaml
        Return:
            活动总时长。单位秒
        """
        keep = utils.get_time(obj.get("持续时间", None))
        bgm_length = AudioFileClip(self.bgm).duration if self.bgm else 0

        subtitle_length = 0.0
        if self.subtitle:
            if isinstance(self.subtitle, str):
                # 处理字幕文件
                self.subtitle = utils.get_sub_title_list(self.subtitle)
            for sb in self.subtitle:
                if len(sb) > 3 and sb[3]:
                    sPath = SuCaiHelper.get_sucai(sb[3])
                    subtitle_length += AudioFileClip(sPath).duration

        return max([keep, bgm_length, subtitle_length])

    def __init__(self, scenario, obj):
        """
        初始化Activity

        Param:
            scenario: Scenario对象实例
            obj: script里面的脚本片段
        """
        self.scenario = scenario
        self.name = obj.get("名字")
        self.description = obj.get("描述", "")
        self.subtitle = obj.get("字幕") if obj.get("字幕", None) else []
        self.subtitle_mode = obj.get("字幕样式", 'normal')
        self.bgm = SuCaiHelper.get_sucai(obj.get("背景音乐", None))
        self.actions = []
        self.timespan = self.__get_timespan(obj)
        self.fps = int(obj.get("fps", None)) if obj.get("fps", None) else config_reader.fps
        self.total_frame = math.ceil(self.timespan * self.fps)   # 根据当前活动的总时长，得到当前活动所需的视频帧数
        if obj.get("动作", None):
            for action in obj["动作"]:
                self.actions.append(Action(self, action, self.timespan))

    def to_video(self):
        """
        将‘活动’转换成视频

        Return:
            视频片段clip
        """
        images = self.__check_images()
        display_list = self.__get_display_list()

        if self.subtitle:
            # 添加字幕
            previous_end = 0
            l = len(self.subtitle)
            for i in range(0, l):
                if self.subtitle[i][0]:
                    start = utils.get_time(self.subtitle[i][0])
                else:
                    if previous_end > 0:
                        start = previous_end
                    else:
                        start = 0
                self.subtitle[i][0] = start
                start_num = int(start/self.timespan*len(images))

                if self.subtitle[i][1]:
                    end = utils.get_time(self.subtitle[i][1])
                else:
                    if len(self.subtitle[i]) > 3 and self.subtitle[i][3]:
                        sPath = SuCaiHelper.get_sucai(self.subtitle[i][3])
                        end = start + utils.get_audio_length(sPath)
                    else:
                        # 只有最后一个字幕才可以同时没有结束时间与声音文件
                        end = self.timespan
                self.subtitle[i][1] = end
                previous_end = end

                if i == len(self.subtitle) -1:
                    # 最后一段字幕，
                    end_number = len(images)
                else:
                    end_number = int(end/self.timespan * len(images))

                # 添加一个表示图片位置的元素到字幕列表的最后
                self.subtitle[i].append((start_num, end_number))

        for display in display_list:
            if 'action' in display:
                # 注意：一个活动（activity）中不能有两个`镜头`动作（action）
                if display["action"].obj.get("名称", None) == "更新":
                    new_char = display["action"].obj.get("角色", None)
                    new_char_name = new_char.get("名字", None)
                    for c in self.scenario.chars:
                        if c.name == new_char_name:
                            if new_char.get("素材", None):
                                c.image = SuCaiHelper.get_sucai(new_char.get("素材"))
                            if new_char.get("位置", None):
                                c.pos = utils.covert_pos(new_char.get("位置", None))
                            if new_char.get("大小", None):
                                c.size = new_char.get("大小")
                            if new_char.get("角度", None):
                                c.rotate = new_char.get("角度")
                            if new_char.get("显示", None):
                                c.display = True if new_char.get("显示", None) == '是' else False
                            if new_char.get("显示", None):
                                c.index = int(new_char.get("图层", 0))
                            break
                    continue

                if display["action"].char and display["action"].char.name != "消失":
                    display["action"].char.display = True
                print("生成动作图片， 动作：", display["action"].obj.get("名称"))
                images = display["action"].to_video(images)
            if 'char' in display:
                if display["char"].display:
                    char = display["char"]
                    print("生成角色图片， 角色：", char.name)
                    image_with_subtitle = []
                    for st in self.subtitle:
                        if len(st) > 4 and char.name == st[4]:
                            start_num = st[-1][0]
                            end_number = st[-1][1]
                            tmp_images = images[start_num : end_number]
                            image_with_subtitle += tmp_images
                            _img = SuCaiHelper.get_sucai(st[5])
                            ImageHelper.add_gif_to_images(tmp_images, _img, pos=char.pos, size=char.size)

                    for img in images:
                        if not img in image_with_subtitle:
                            ImageHelper.merge_two_image(img, char.image, char.size, char.pos, overwrite=True)

        if self.subtitle:
            print("self.subtitle: \n", self.subtitle)
            # daemon结束主进程的时候可以同时结束子线程
            threading.Thread(target=worker, daemon=True).start()
            l = len(self.subtitle)
            for i in range(0, l):
                # 创建新线程
                start_num = self.subtitle[i][-1][0]
                end_number = self.subtitle[i][-1][1]
                print(f"start_num: {start_num}, end_number: {end_number}")
                tmp_images = images[start_num : end_number]
                text_list = [x[2] for x in self.subtitle[0 if i < 2 else i - 2 : i + 3]]    # 最多显示5行文字
                q.put((self.subtitle[i][2], tmp_images, self.subtitle_mode, text_list))

        # 等待所有线程完成
        q.join()

        # 先把图片转换成视频
        video = VideoHelper.create_video_clip_from_images(images, self.fps)
        if self.bgm:
            """添加活动背景音乐"""
            print("添加背景音乐：", self.bgm)
            video = VideoHelper.add_audio_to_video(video, self.bgm)
        if self.subtitle:
            # 添加字幕声音
            audio_list = [AudioFileClip(SuCaiHelper.get_sucai(st[3])).set_start(st[0]) for st in self.subtitle if len(st) > 3 and st[3]]
            if audio_list:
                fd, tmp_audio_path = tempfile.mkstemp(suffix=".mp3")
                print(f"把声音组装起来保存到{tmp_audio_path}")
                concatenate_audioclips(audio_list).write_audiofile(tmp_audio_path)
                video = VideoHelper.add_audio_to_video(video, tmp_audio_path, start=self.subtitle[0][0])

        return video

if __name__ == "__main__":
    with open('script.yaml', 'r') as file:
       script = yaml.safe_load(file)

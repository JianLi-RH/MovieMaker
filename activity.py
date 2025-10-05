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
from libs import VideoHelper

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

    def __convert_queue_to_walk_list(self, action_list: list):
        """convert queue to walk action list
        
        Example:
          -
            名称: 队列
            角色: 卢俊义 枪1 朱武 关胜 刀1 林冲 秦明 呼延灼 董平 徐宁 钩镰枪 杨志 索超 张清 朱仝 史进
            开始位置: 
            开始角度: 
            结束位置: 
            x:      # 整数， -100, 100
            y:      # 整数， -100, 100
            结束消失: 是
            比例: 
            字幕: 
            - ['','', '', 'resources/ShengYin/跑步声.mp3']
            方式: 
            渲染顺序: 27
        
        Param:
            action_list: action list
        """
        actions = []
        
        for act in action_list:
            if act.name == "队列":
                chars = act.obj.get("角色").split(" ")
                import copy
                first = True
                for char in chars:
                    act_obj = copy.deepcopy(act.obj)
                    act_obj["名称"] = "行进"
                    act_obj["角色"] = char
                    if not act_obj["结束位置"]:
                        if not act_obj["x"] and not act_obj["y"]:
                            raise Exception("必须给出队列的结束位置")
                        
                        char_obj = self.__get_char(char)
                        end_pos = char_obj.pos[:]
                        if act_obj["x"]:
                            end_pos[0] += int(act_obj["x"])
                        if act_obj["y"]:
                            end_pos[1] += int(act_obj["y"])
                        
                        act_obj["结束位置"] = end_pos
                        
                    new_act = Action(self, act_obj)
                    if not first:
                        new_act.subtitle = []
                    else:
                        first = False
                    actions.append(new_act)
            else:
                actions.append(act)
        
        return actions

    def __check_images(self):
        """第一次执行action的时候, images会是空的, 所以需要生成一组图片

        Return:
            一组图片
        """
        path = os.path.join(config_reader.output_dir, self.name)
        os.makedirs(path, exist_ok=True)
        print("背景图片将被保存在：", path)

        images = []
        background_image = self.scenario.background_image # 已经resize之后的图片
        if background_image.lower().endswith(".gif"):
            bg_frames = ImageHelper.get_frames_from_gif(background_image)
            l = len(bg_frames)
            ext = bg_frames[0].split('.')[-1]

            for i in range(0, self.total_frame):
                index = i % l
                new_path = os.path.join(path, f"{i}.{ext}")
                shutil.copy(bg_frames[index], new_path)
                ImageHelper.resize_image(new_path)
                images.append(new_path)
        else:
            ext = background_image.split('.')[-1]
            for i in range(0, self.total_frame):
                new_path = os.path.join(path, f"{i}.{ext}")
                shutil.copy(background_image, new_path)
                images.append(new_path)

        print("准备背景图片结束，共计", self.total_frame, "张图片")
        return images

    def __get_char(self, name):
        """查找指定名称的角色"""
        if not name:
            return None
        if ' ' in name:
            # 打斗等组合动作可以同时操作多个角色
            # 因此不能在这里获取角色
            return None
        for c in self.scenario.chars:
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
        raise Exception(f"角色【{name}】不存在")

    def __get_render_list(self):
        """获取渲染列表
        index小的action最先显示
        不在rendered_action_list里的角色全程显示
        
        Return:
            rendered_action_list: [[{index:0, action: xxx}, {index:0, action: yyy}], [{"index": 1, "action": zzz}]]
        """
        rendered_action_list = []
        for act in self.actions:
            render = {"index": act.render_index, "action": act}
            actions = next(filter(lambda x: x[0].get("index", 0) == render.get("index", 0), rendered_action_list), [])
            if actions:
                actions.append(render)
            else:
                rendered_action_list.append([render])
        
        # 保证同一渲染顺序的动作都有执行时间   
        for act_list in rendered_action_list:
            if len(act_list) > 1:
                max_timespan = max([x["action"].timespan for x in act_list])
                # if max_timespan == 0:
                #     # 当没有设置动作时间时，默认1秒钟
                #     max_timespan = 1
                for act in act_list:
                    if act["action"].timespan < max_timespan:
                        act["action"].timespan = max_timespan

        if rendered_action_list:
            rendered_action_list.sort(key=lambda x: int(x[0].get("index", 0)))
        return rendered_action_list

    def __get_timespan(self):
        """获取活动总时间，单位秒

        Pramas:
        Return:
            活动总时长。单位秒
        """
        # 活动背景音乐的时长，当没有设置`持续时间`和字幕的时候会根据背景音乐长度设置总时长
        bgm_length = AudioFileClip(self.bgm).duration if self.bgm else 0

        # 活动字幕的时长
        subtitle_length = 0.0
        if self.subtitle:
            if isinstance(self.subtitle, str):
                # 处理字幕文件
                self.subtitle = AudioHelper.get_sub_title_list(self.subtitle)
            for sb in self.subtitle:
                sPath = sb[3]
                if not os.path.exists(sPath):
                    # 使用科大讯飞接口生成语音
                    try:
                        speaker = self.obj.get("发音人", "")
                        ttsengine = self.obj.get("发音人引擎", "")
                        AudioHelper.covert_text_to_sound(sb[2], sPath, speaker, ttsengine=ttsengine)
                    except Exception as e:
                        print(f"Convert text failed: ", sb[2])
                        raise(e)
                subtitle_length += AudioFileClip(sPath).duration

        # 全部动作的长度
        action_length = 0.0
        calculated_index = []   # save all actions length, for example: {'index': 0, 'action': action}
        for act in self.actions:
            same_index_action = next(filter(lambda x: x["index"] == act.render_index, calculated_index), None)
            if same_index_action:
                if same_index_action["action"].timespan < act.timespan:
                    same_index_action['action'] = act
                if act.timespan == 0:
                    act.timespan = same_index_action["action"].timespan
            else:
                calculated_index.append({'index': act.render_index, 'action': act})
        action_length = sum([l["action"].timespan for l in calculated_index])

        return max([self.keep, bgm_length, subtitle_length, action_length])

    def __pre_check(self):
        """预检测yaml文件"""
        chars = [c.name for c in self.scenario.chars]
        for acts in self.action_list:
            
            for act in acts:
                if act.get("obj") and act.obj.get("角色") and act.obj.get("角色") not in chars:
                    raise Exception(f"角色【{act.obj.get("角色")}】不存在, 渲染顺序：{act.render_index}")
            
            if len(acts) > 1:
                # deply模式检测
                act_names = [x["action"] for x in acts if x["action"].name in ["显示", "消失", "镜头", "更新"]]
                if act_names:
                    raise Exception(f"动作[{act_names[0].name}]不能使用delay模式, action index: {act_names[0].render_index}")

                # 执行时间检测
                action_time = [x["action"].timespan for x in acts]
                max_timespan = max(action_time)
                if max_timespan == 0:
                    raise Exception(f"动作[{acts[0]["action"].name}]执行时间不能为0, action index: {acts[0]["action"].render_index}")
            else:
                if acts[0]["action"].name not in ["显示", "消失", "镜头", "更新"] and acts[0]["action"].timespan == 0:
                    raise Exception(f"动作[{acts[0]["action"].name}]执行时间不能为0, action index: {acts[0]["action"].render_index}")


    def __init__(self, scenario, obj):
        """
        初始化Activity

        Param:
            scenario: Scenario对象实例
            obj: script里面的脚本片段
        """
        self.scenario = scenario
        self.obj = obj
        self.name = obj.get("名字")
        self.description = obj.get("描述", "")
        self.subtitle = obj.get("字幕") if obj.get("字幕") else []
        self.subtitle_color = obj.get("字幕颜色")
        self.subtitle_mode = obj.get("字幕样式", 'normal')
        
        # 在活动节点中设置的时间，与具体动作无关
        self.keep = utils.get_time(obj.get("持续时间", None))
        self.bgm = obj.get("背景音乐", None)
        self.actions = [Action(self, action) for action in obj.get("动作")] if obj.get("动作") else []
        self.actions = self.__convert_queue_to_walk_list(self.actions)
        
        self.timespan = self.__get_timespan()    # 活动的总长度
        self.fps = int(obj.get("fps")) if obj.get("fps") else config_reader.fps
        self.total_frame = math.ceil(self.timespan * self.fps)   # 根据当前活动的总时长，得到当前活动所需的视频总帧数
        self.action_list = self.__get_render_list()
        
        self.__pre_check()


    def to_video(self):
        """
        将‘活动’转换成视频

        Return:
            视频片段clip
        """
        images = self.__check_images()

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
                        end = start + utils.get_audio_length(self.subtitle[i][3])
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

        start = 0 # 每个action的开始位置 （图片下标）
        for i in range(len(self.action_list)):
            actions = self.action_list[i]
            delay_mode = len(actions) > 1   # 当同时运行多个动作的时候，需要在所有动作执行结束再绘制其他角色
            video_start = start/len(images) # action在整段视频中的开始位置，方便后面添加声音
            # delay_start = start
            action_ends = [0]
            delay_positions = []  # 被推迟的全部角色轨迹序列
            
            current_atc_end = start + round(actions[0]["action"].timespan * self.fps)
            action_ends.append(current_atc_end)
            if current_atc_end >= len(images):
                delay_images = images[start:]
            else:
                delay_images = images[start:current_atc_end]
                
            for act in actions:
                if delay_mode and act["action"].name.lower() in ["更新", "显示", "消失", "镜头", "BGM"]:
                    raise Exception("动作【" + act["action"].name + "】不能使用delay模式（不能和其它动作同时运行）")
                # 注意：一个活动（activity）中不能有两个`镜头`动作(action)
                act["start"] = video_start  # 给action增加一个start属性

                # current_atc_end = start + round(act["action"].timespan * self.fps)
                # action_ends.append(current_atc_end)
                # if current_atc_end >= len(images):
                #     current_image_list = images[start:]
                # else:
                #     current_image_list = images[start:current_atc_end]
                # temp_delay_positions = act["action"].to_videoframes(current_image_list, self.scenario.chars, delay_mode)
                temp_delay_positions = act["action"].to_videoframes(delay_images, self.scenario.chars, delay_mode)
                
                if delay_mode:
                    delay_positions.append(temp_delay_positions)

            if delay_mode:
                # delay_images = images[delay_start : max(action_ends)]
                if delay_images:
                    for j in range(len(delay_images)):   # 在每张图片上绘制全部角色
                        big_image = None
                        for _char in self.scenario.chars:
                            if isinstance(_char, Character) and not _char.display:
                                continue
                            for char_pos in delay_positions:
                                if _char == char_pos["char"]:
                                    if len(char_pos["position"]) > j:
                                        delay_pos = char_pos["position"][j]
                                    elif len(char_pos["position"]) > 0: 
                                        delay_pos = char_pos["position"][-1]
                                    else:
                                        print("_char: ", _char.name)
                                        continue
                                    
                                    _char.pos = delay_pos[0]
                                    _char.size = delay_pos[1]
                                    _char.rotate = delay_pos[2]
                                    
                                    if len(delay_pos) > 3:
                                        _char.image = delay_pos[3]
                                    break
                                    
                            
                            _, big_image = ImageHelper.paint_char_on_image(char=_char, 
                                                                            image=delay_images[j],
                                                                            image_obj=big_image,
                                                                            save=False,
                                                                            gif_index=j)

                        if big_image:
                            big_image.save(delay_images[j])
                            big_image.close()
                
                for char_pos in delay_positions:
                    # 结束后隐藏角色
                    if char_pos.get("disappear_end", None):
                        char_pos["char"].display = False
            
            # 检查遗漏的背景图片
            if i == (len(self.action_list) - 1) and max(action_ends) < len(images):
                # 当执行最后一个动作的时候， 最后一个绘制角色的图片不是全部背景图片的最后一张的时候
                # 把剩余的背景图片都绘制上角色
                missed_images = images[max(action_ends):]
                print(missed_images)
                gif_index = 0
                for img in missed_images:
                    big_image = None
                    for _char in self.scenario.chars:
                        if _char.display:
                            _, big_image = ImageHelper.paint_char_on_image(char=_char, 
                                                                           image=img,
                                                                           image_obj=big_image,
                                                                           save=False,
                                                                           gif_index=gif_index)
                    if big_image:
                        big_image.save(img)
                        big_image.close()
                    gif_index += 1

            for _char in self.scenario.chars:
                # 防止gif对象继续存在与其他动作中，所以需要在执行结束删除它
                if _char.name.lower().startswith("gif_"):
                    self.scenario.chars.remove(_char)
                    break
            start = max(action_ends)

        draw_char_actions = set([act["action"].name for act_in_same_level in self.action_list for act in act_in_same_level]) - set({"显示", "消失"})
        if not draw_char_actions:
            # 如果所有的动作都没有绘制角色，则统一绘制一次
            for img in images:
                big_image = None
                for _char in self.scenario.chars:
                    if _char.display:
                        _, big_image = ImageHelper.paint_char_on_image(char=_char, 
                                                                      image=img, 
                                                                      image_obj=big_image,
                                                                      save=False)
                if big_image:
                    big_image.save(img)
                    big_image.close()
                    
        if self.subtitle:
            print("self.subtitle: \n", self.subtitle)
            # daemon：结束主进程的时候可以同时结束子线程
            threading.Thread(target=worker, daemon=True).start()
            l = len(self.subtitle)
            for i in range(0, l):
                # 创建新线程
                start_num = self.subtitle[i][-1][0]
                end_number = self.subtitle[i][-1][1]
                print(f"start_num: {start_num}, end_number: {end_number}")
                tmp_images = images[start_num : end_number]
                text_list = [x[2] for x in self.subtitle[0 if i < 2 else i - 1 : i + 2]]    # 最多显示3行文字
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
            # 添加字幕声音 -- 活动的字幕
            audio_list = [AudioFileClip(st[3]).with_start(st[0]) for st in self.subtitle if len(st) > 3 and st[3]]
            if audio_list:
                fd, tmp_audio_path = tempfile.mkstemp(suffix=".mp3")
                print(f"把声音组装起来保存到{tmp_audio_path}")
                concatenate_audioclips(audio_list).write_audiofile(tmp_audio_path)
                video = VideoHelper.add_audio_to_video(video, tmp_audio_path, start=self.subtitle[0][0])
        
        video_total_length = video.duration
        for actions in self.action_list:
            # 添加动作的声音
            action_ends = []
            start = actions[0]["start"] * video_total_length
            for act in actions:
                if act["action"].subtitle:
                    action_ends.append(act["action"].subtitle[-1][1])
                    for subtitle in act["action"].subtitle:
                        video = VideoHelper.add_audio_to_video(video, subtitle[3], start=(start + subtitle[0]))
        return video

if __name__ == "__main__":
    with open('script.yaml', 'r') as file:
       script = yaml.safe_load(file)

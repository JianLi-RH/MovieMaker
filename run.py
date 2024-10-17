#!/usr/bin/python3

'''
这是程序入口，可以通过以下几种方式生成视频：
    1. 执行整个script.yaml文件，生成final.mp4
    python run.py -o "final.mp4"
    2. 执行script.yaml文件中的某一个场景，生成final.mp4
    python run.py -o "final.mp4" -c '场景1'
    3. 执行script.yaml文件中的某一个场景，生成final.mp4
    python run.py -o "final.mp4" -c '场景1' -s '武松打虎.yaml'

    生成的final.mp4文件将会被保存在config_reader.output_dir下面
'''

import getopt
import os
import sys

import yaml
from moviepy.editor import VideoFileClip

import config_reader
from libs import VideoHelper
from scenario import Scenario

def connect_videos(final_video_name: str, videos=[], script='script.yaml', delete_old = False):
    """拼接多个视频文件

    Params:
        final_video_name: 输出的视频文件名
        videos: 视频文件列表
        script: 脚本文件，当没有提供videos时，根据脚本文件读取对应的场景视频
        delete_old: 是否删除旧的视频文件
    """
    if not videos:
        with open(script, 'r') as file:
            script = yaml.safe_load(file)

            scenarios = script["场景"]
            videos = [os.path.join(config_reader.output_dir, x.get("名字") + config_reader.video_format) for x in scenarios]
        
    final_videos = []
    for f in videos:
        final_videos.append(VideoFileClip(f))
    final = VideoHelper.concatenate_videos(*final_videos)
    if delete_old:
        for f in videos:
            if os.path.exists(f):
                os.remove(f)
            else:
                print(f"WARN: {f} 不存在")
    p = os.path.join(config_reader.output_dir, final_video_name)
    final.write_videofile(p)
    return p

def run(output=None, script='script.yaml', scenario=None):
    """创建视频

    Params:
        output: 输出的视频文件名
        script: 脚本文件的路径
        scenario: 需要创建视频的场景，没指定的话将对整个script.yaml进行生成
    """
    with open(script, 'r') as file:
        script = yaml.safe_load(file)

        scenarios = script["场景"]
        if scenario:
            scenarios = list(filter(lambda x: x.get("名字", None) == scenario, scenarios))
        final_videos_files = []
        for scenario_obj in scenarios:
            scenario = Scenario(scenario_obj)
            videos = [activity.to_video() for activity in scenario.activities]
            new_video = VideoHelper.concatenate_videos(*videos)
            if scenario.bgm:
                new_video = VideoHelper.add_audio_to_video(new_video, scenario.bgm)
            scenario_file = os.path.join(config_reader.output_dir, f"{scenario.name}.{config_reader.video_format}")
            new_video.set_fps(config_reader.fps)
            new_video.write_videofile(scenario_file)
            final_videos_files.append(scenario_file)

        if not output:
            if scenario:
                output = os.path.join(config_reader.output_dir, f"{scenario.name}.{config_reader.video_format}")
            else:
                script = script.split('.')[0]
                output = os.path.join(config_reader.output_dir, f"{script}.{config_reader.video_format}")
        connect_videos(output, final_videos_files, delete_old=True)
    return 0

def main(argv):
    """
    执行run()生成视频
    """
    options = "o:s:c:"
    opts , args = getopt.getopt(argv, options)
    print(f"arguments: {opts}")

    output, scenario, script = '', '', ''
    for currentArgument, currentValue in opts:
        if currentArgument in ("-o", "--output"):
            output = currentValue.strip()
        if currentArgument in ("-c", "--scenario"):
            scenario = currentValue.strip()
        if currentArgument in ("-s", "--script"):
            script = currentValue.strip()
    
    if not output:
        if scenario:
            output = scenario + config_reader.video_format
        else:
            output = script.split('.') + config_reader.video_format

    return run(output=output, scenario=scenario, script=script)

if __name__ == "__main__":
    import datetime
    print(datetime.datetime.now())
    if len(sys.argv) > 1:
        result = main(sys.argv[1:])
    else:
        result = run(script='script/水浒传/水浒传第三回.yaml', scenario="杀退官兵")
    print(datetime.datetime.now())
    sys.exit(result)
    # videos=["output/京城外.mp4", "output/路上.mp4", "output/龙虎山下.mp4", "output/请张真人.mp4"]
    # connect_videos("水浒传第二回.mp4", script="水浒传第二回.yaml", delete_old=False)
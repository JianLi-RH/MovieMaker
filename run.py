#!/usr/bin/python3

'''
这是程序入口，可以通过以下几种方式生成视频：
    1. 执行整个 demo/水浒传.yaml 文件，生成完整的视频
    python run.py -o "水浒传.mp4" -s 'demo/水浒传.yaml'
    2. 执行 demo/水浒传.yaml 文件中的 毒杀武大 场景，生成单一场景视频
    python run.py -o "水浒传.mp4" -c '毒杀武大' -s 'demo/水浒传.yaml'

    生成的视频文件将会被保存在config_reader.output_dir下面
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
        final_video_name: 输出的视频文件名（包含全路径）
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
    final.write_videofile(final_video_name)
    return final_video_name

def run(script, output=None, scenario=None):
    """创建视频

    Params:
        script: 脚本文件的路径
        output: 输出的视频文件名
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
            videos = [act.to_video() for act in scenario.activities]
            new_video = VideoHelper.concatenate_videos(*videos)
            if scenario.bgm:
                new_video = VideoHelper.add_audio_to_video(new_video, scenario.bgm)
            scenario_file = os.path.join(config_reader.output_dir, f"{scenario.name}{config_reader.video_format}")
            new_video.set_fps(config_reader.fps)
            new_video.write_videofile(scenario_file)
            final_videos_files.append(scenario_file)

        if not output:
            if scenario:
                output = f"{scenario.name}{config_reader.video_format}"
            else:
                script = script.split('.')[0]
                output = f"{script}{config_reader.video_format}"
        output = os.path.join(config_reader.output_dir, output)
        
        print(f"视频文件将会被输出到: {output}")
        connect_videos(output, videos=final_videos_files, delete_old=False)
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
    
    if not script or not os.path.exists(script):
        raise Exception("必须给出脚本文件")
    
    if not output:
        if scenario:
            output = scenario + config_reader.video_format
        else:
            output = script.split('.') + config_reader.video_format

    return run(output=output, scenario=scenario, script=script)

if __name__ == "__main__":
    script_name="水浒传.yaml"
    
    if len(sys.argv) > 1:
        result = main(sys.argv[1:])
    else:
        result = run(script=f"demo/{script_name}", scenario="商议对策")
    sys.exit(result)
    
    # connect_videos(f"{script_name}.mp4", script=f"script/水浒传/{script_name}", delete_old=False)
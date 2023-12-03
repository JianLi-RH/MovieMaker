***REMOVED***.10

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
***REMOVED***
***REMOVED***

import yaml
from moviepy.editor import VideoFileClip

import config_reader
from libs import VideoHelper
from scenario import Scenario


def run(output, script='script.yaml', scenario=None):
    """创建视频

    Params:
        output: 输出的视频文件名
        scenario: 需要创建视频的场景，没指定的话将对整个script.yaml进行生成
    """
    with open(script, 'r') as file:
        script = yaml.safe_load(file)

        scenarios = script["场景"]
        if scenario:
            scenarios = [x for x in scenarios if x.get("名字", None) == scenario]
        final_videos_files = []
        for i in range(0, len(scenarios)):
            scenario = Scenario(scenarios[i])
            videos = []
            for j in range(0, len(scenario.activities)):
                video = scenario.activities[j].to_video()
                if video:
                    videos.append(video)

            if videos:
                new_video = VideoHelper.concatenate_videos(*videos)
***REMOVED***
                continue
            if scenario.bgm:
                new_video = VideoHelper.add_audio_to_video(new_video, scenario.bgm)
            scenario_file = os.path.join(config_reader.output_dir, f"{scenario.name***REMOVED***.mp4")
            new_video.write_videofile(scenario_file)
            final_videos_files.append(scenario_file)

        if final_videos_files:
            final_videos = []
            for f in final_videos_files:
                final_videos.append(VideoFileClip(f))
            final = VideoHelper.concatenate_videos(*final_videos)
            for f in final_videos_files:
                os.remove(f)
            final.write_videofile(os.path.join(config_reader.output_dir, output))
    return 0

def main(argv):
    """
    执行run()生成视频
    """
    options = "o:s:c"
    long_options = ["output = ", "scenario = ", "script = "]
    arguments, values = getopt.getopt(argv, options, long_options)

    output = ''
    scenario = ''
    script = ''
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-o", "--output"):
            output = currentValue.strip()
        if currentArgument in ("-c", "--scenario"):
            scenario = currentValue.strip()
        if currentArgument in ("-s", "--script"):
            script = currentValue.strip()
    return run(output=output, scenario=scenario, script=script)

***REMOVED***
    ***REMOVED***
    print(datetime.datetime.now())
    result = main(sys.argv[1:])
    ***REMOVED*** result = run("酒馆里.mp4", script='武松打虎.yaml', scenario="酒馆里")
    print(datetime.datetime.now())
    sys.exit(result)
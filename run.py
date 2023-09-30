***REMOVED***.10
import getopt
***REMOVED***
***REMOVED***

import yaml

import config_reader
from libs import VideoHelper
from scenario import Scenario


def run(output, scenario=None):
    """创建视频

    Params:
        output: 输出的视频文件名
        scenario: 需要创建视频的场景，没指定的话将对整个script.yaml进行生成
    """
    with open('script.yaml', 'r') as file:
        script = yaml.safe_load(file)

        scenarios = script["场景"]
        if scenario:
            scenarios = [x for x in scenarios if x.get("名字", None) == scenario]
        videos = []
        for i in range(0, len(scenarios)):
            scenario = Scenario(scenarios[i])
            for j in range(0, len(scenario.activitys)):
                video = scenario.activitys[j].to_video()
                if video:
                    videos.append(video)

            if scenario.bgm:
                video = VideoHelper.add_audio_to_video(video, scenario.bgm)

        if videos:
            VideoHelper.concatenate_videos(*videos).write_videofile(os.path.join(config_reader.output_dir, output))
    pass

def main(argv):
    """
    执行run()生成视频
    """
    options = "o:s:"
    long_options = ["output = ", "scenario = "]
    arguments, values = getopt.getopt(argv, options, long_options)

    output = ''
    scenario = ''
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-o", "--output"):
            output = currentValue.strip()
        if currentArgument in ("-s", "--scenario"):
            scenario = currentValue.strip()
    run(output=output, scenario=scenario)
***REMOVED***
    ***REMOVED*** python run.py -o "final.mp4"
    ***REMOVED*** python run.py -o "final.mp4" -s '场景1'
    ***REMOVED*** main(sys.argv[1:])
    ***REMOVED***
    print(datetime.datetime.now())
    run("final.mp4", '场景1')
    print(datetime.datetime.now())
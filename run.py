***REMOVED***.10
***REMOVED***

import yaml

import config_reader
from libs import VideoHelper
from scenario import Scenario


def run(output):
    with open('script.yaml', 'r') as file:
        script = yaml.safe_load(file)

        scenarios = script["场景"]
        videos = []
        for i in range(0, len(scenarios)):
            scenario = Scenario(scenarios[i])
            for j in range(0, len(scenario.activitys)):
                video = scenario.activitys[j].to_video()
                if video:
                    videos.append(video)

        if videos:
            VideoHelper.concatenate_videos(*videos).write_videofile(os.path.join(config_reader.output_dir, output))
    pass

***REMOVED***
    run("final.mp4")
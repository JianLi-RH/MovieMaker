import yaml

***REMOVED*** Global settings
config = yaml.safe_load(open("global_config.yaml"))
output_dir = config["output_dir"]
sucai_dir = config["sucai_dir"]
system_font_dir = config["system_font_dir"]
font = config["font"]
video_format = ".mp4"


***REMOVED*** Personal settings
config = yaml.safe_load(open("config.yaml"))
fps = int(config["fps"])    ***REMOVED*** 每秒显示的帧数
watermark = config["watermark"] ***REMOVED*** 水印
g_width = int(config["g_width"])
g_height = int(config["g_height"])
round_per_second = config["round_per_second"]
font_size = int(config["font_size"])
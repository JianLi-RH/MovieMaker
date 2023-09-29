import configparser

config = configparser.ConfigParser()
config.read('config.ini')
config = config["DEFAULT"]

fps = int(config["fps"])    ***REMOVED*** 每秒显示的帧数
watermark = config["watermark"] ***REMOVED*** 水印
g_width = int(config["g_width"])
g_height = int(config["g_height"])
output_dir = config["output_dir"]
sucai_dir = config["sucai_dir"]
round_per_second = config["round_per_second"]
font = config["font"]
font_size = int(config["font_size"])
system_font_dir = config["system_font_dir"]
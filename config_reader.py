#!/usr/bin/python3
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# Global settings
config = load(open("global_config.yaml"), Loader=Loader)
output_dir = config["output_dir"]
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

sucai_dir = config["sucai_dir"]
system_font_dir = config["system_font_dir"]
font = config["font"]
video_format = ".mp4"
tts_engine = config["tts_engine"]


# Personal settings
config = load(open("config.yaml"), Loader=Loader)
fps = int(config["fps"])    # 每秒显示的帧数
watermark = config["watermark"] # 水印
g_width = int(config["g_width"])
g_height = int(config["g_height"])
round_per_second = config["round_per_second"]
font_size = int(config["font_size"])
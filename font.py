#!/usr/bin/python3.10
import os

from fontTools.ttLib import TTFont
from moviepy.editor import *

import config_reader

# 指定系统字体目录的路径
system_font_dir = config_reader.system_font_dir
if not os.path.exists(os.path.join(config_reader.output_dir, 'fonts')):
    os.mkdir(os.path.join(config_reader.output_dir, 'fonts'))

for dirpath, dirnames, filenames in os.walk("fonts"):
    for filepath in filenames:
        if os.path.basename(filepath).lower().endswith(".ttf"):
            # 字体文件的路径
            font_file_path = os.path.join(dirpath, filepath)

            font = TTFont(font_file_path)
            font.save(os.path.join(config_reader.output_dir, 'fonts', os.path.basename(filepath)))

TextClip.list('font')
TextClip.search('Courier', 'font')
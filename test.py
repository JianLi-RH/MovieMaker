from libs import VideoHelper

VideoHelper.add_watermark("output/final.mp4", "resources/SuCai/watermark.gif", (200, 200), (100, 120)).write_videofile("output/gif.mp4")
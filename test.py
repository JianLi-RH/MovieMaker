***REMOVED***.10
from libs import VideoHelper

***REMOVED*** VideoHelper.add_watermark("output/final.mp4", "resources/SuCai/watermark.gif", (200, 200), (100, 120)).write_videofile("output/gif.mp4")

text = """Thanks for your answers."""
VideoHelper.add_subtitile("output/final.mp4", text=text, time_span=(0, 4))
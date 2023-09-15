***REMOVED***.10
***REMOVED***

sys.path.append('../')
***REMOVED***

from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

import config_reader
import utils

try:
    from libs import ImageHelper, SuCaiHelper
except ImportError:
    import ImageHelper
    import SuCaiHelper


def __get_video_clip(video):
    """根据给出的视频文件地址或VideoFileClip对象返回一个VideoFileClip实例

    Params:
        video: video file or file path
    Return:
        Returns a Clip instance
    """
    if isinstance(video, str):
        videoclip= VideoFileClip(video)
    else:
        videoclip = video
    return videoclip

def __get_images_when_zoom_in_out_camera(origin_image_path, center, from_ratio, to_ratio, duration):
    """
    zoom in or zoom out. 拉近、拉远镜头

    Params:
        origin_image_path: the origin image file path.
        center: the focus point of camera (zoom in / zoom out by this point),
            it format will be like: (123, 234) or (0.2, 0.4) or (123, 0.3)
        from_ratio: 起始的缩放比例. like: 0.1, 0.9
        to_ratio: 结束的缩放比例， like: 0.1, 0.9
        duration: in seconds to zoom in or zoom out camera.
    Return:
        Instance of video.
    """

    total = duration * int(config["fps"])
    images = []
    for i in range(0, total):
        if from_ratio > to_ratio:
            ***REMOVED*** 缩小
            tmp_ratio = from_ratio - (from_ratio - to_ratio) * i / total
        else:
            ***REMOVED*** 放大
            tmp_ratio = from_ratio + (to_ratio - from_ratio) * i / total
        tmp_img = ImageHelper.zoom_in_out_image(origin_image_path, center=center, ratio=tmp_ratio)
        images.append(tmp_img)
    return images

def add_watermark(video, gif_path, pos, size):
    """
    Add watermark to a video.

    Params:
        video: video file path or a instance of VideoFileClip
        gif_path: the gif path which will be used as watermark
    Return:
        A new video clip.
    """
    clip = __get_video_clip(video)
    watermark = (VideoFileClip(gif_path, has_mask=True)
                    .loop()  ***REMOVED*** loop gif
                    .set_duration(clip.duration)  ***REMOVED*** 水印持续时间
                    .resize(height=size[1], )  ***REMOVED*** 水印的高度，会等比缩放
                    .margin(left=pos[0], top=pos[1], opacity=0)  ***REMOVED*** 水印边距和透明度
                    .set_pos(("left", "top")))  ***REMOVED*** 水印的位置

    return CompositeVideoClip([clip, watermark])

def add_subtitile(video, text, time_span):
    """
    Add subtitle to a video.

    Params:
        video: video file path or a instance of VideoFileClip
        text: the subtitle will be added to the video
        time_span: time span, like (0, 4)
    Return:
        A new video clip.
    """
    if isinstance(video, str):
        clip= VideoFileClip(video)
    else:
        clip = video

    generator = lambda txt: TextClip(txt, font=config["font"], fontsize=24, color='white')

    subs = [(time_span, text)]
    ***REMOVED*** subs = [((0, 4), 'subs1'),
    ***REMOVED***     ((4, 9), 'subs2')]
    subtitles = SubtitlesClip(subs, generator)
    result = CompositeVideoClip([clip, subtitles.set_pos(('center','bottom'))])
    result.fps = clip.fps
    return result

def get_video_section(file_path, start, end):
    """
    Get video section.

    Params:
        file_path: video file path.
        start: start time by second.
        end: end time by second.

    Return:
        Returns a Clip instance playing the content of the current clip
    """
    if os.path.exists(file_path):
        return VideoFileClip(file_path).subclip(start, end)
    else:
        raise Exception(f"Could not find video file on {file_path***REMOVED***")

def add_audio_to_video(video, audio_file):
    """
    Add audio to a video

    Params:
        video: video file or file path
        audio_file: audio file
    Return:
        Returns a Clip instance
    """
    if not os.path.exists(audio_file):
        raise FileExistsError("Could not find the audio file")

    audioclip = AudioFileClip(audio_file)
    a_du = audioclip.duration

    v = __get_video_clip(video)
    v_du = v.duration
    if a_du > v_du:
        audioclip = audioclip.subclip(0, v_du)
    return v.set_audio(audioclip)

def create_video_clip_from_images(images, duration, size=None, fps=None):
    """
    Create a video clip from images

    Params:
        images: a list of image file path.
        duration: the video length, like 5秒, 1分10秒
        size: the video size, like (200, 500)
    Return:
        Instance of VideoClip.
    """
    if not fps:
        fps = int(config_reader.fps)

    time_length = utils.get_time(duration)

    clips = [ImageClip(m).set_fps(fps).set_duration(time_length/len(images)) for m in images]
    concat_clip = concatenate_videoclips(clips, method="compose")
    return concat_clip

def composite_videos(main_video, sub_video, sub_video_start_time = 0, sub_video_position = None, sub_video_size = None):
    """
    Composite two videos

    Examples for position:
        clip2.set_position((45,150)) ***REMOVED*** x=45, y=150 , in pixels
        clip2.set_position("center") ***REMOVED*** automatically centered
        ***REMOVED*** clip2 is horizontally centered, and at the top of the picture
        clip2.set_position(("center","top"))
        ***REMOVED*** clip2 is vertically centered, at the left of the picture
        clip2.set_position(("left","center"))
        ***REMOVED*** clip2 is at 40% of the width, 70% of the height of the screen:
        clip2.set_position((0.4,0.7), relative=True)
        ***REMOVED*** clip2's position is horizontally centered, and moving down !
        clip2.set_position(lambda t: ('center', 50+t) )

    Params:
        main_video: the main video, sub_video will put on it
        sub_video: a smaller video, it will be part of the main video.
        sub_video_start_time: the start time of sub video.
        position: top-left pixel of the clips,
        width:
        height:
    Return:
        A new video clip.
    """
    main_clip = __get_video_clip(main_video).resize(width=config_reader.g_width, height=config_reader.g_height)
    sub_clip = __get_video_clip(sub_video)
    sub_clip.set_start(sub_video_start_time)
    if sub_video_position:
        sub_clip = sub_clip.set_position(sub_video_position)
    if sub_video_size:
        sub_clip = sub_clip.resize(sub_video_size)

    return CompositeVideoClip([main_clip, sub_clip], size=(config_reader.g_width, config_reader.g_height))

def concatenate_videos(*videos):
    """
    Concatenate videos

    Params:
        videos: a list of videos
    Return:
        A new video clip.
    """
    new_videos = []
    for v in videos:
        new_videos.append(__get_video_clip(v))

    final_clip = concatenate_videoclips(new_videos)

    return final_clip

def insert_image_to_video(video, image_path, position, duration, size=None):
    """将图片插入到视频

    Params:
         video: video file or file path
         image_path: image file path
         position: 位置（图片的左上角）, (50, 100)
         duration: the video length, like 5秒, 1分10秒
         size: 图片尺寸： [50, 100], [0.5, 0.5]
    Return:
        A new video clip.
    """
    clip = __get_video_clip(video)
    image_clips = []
    image = ImageClip(image_path)

    outer_x, outer_y = clip.size
    pos_x = position[0] if position[0] > 1 else outer_x * position[0]
    pos_y = position[1] if position[1] > 1 else outer_y * position[1]
    image = image.set_position((pos_x, pos_y))

    timespan = utils.get_time(duration)
    image = image.set_duration(timespan)

    image_clips.append(image)
    ***REMOVED*** if size:
    ***REMOVED***     i = Image.open(image_path)
    ***REMOVED***     x, y = i.size

    ***REMOVED***     x = x * size[0] if size[0] < 1 else size[0]
    ***REMOVED***     y = y * size[1] if size[1] < 1 else size[1]
    ***REMOVED***     image.resize(weight=x,height=y)

    return CompositeVideoClip([clip] + image_clips)
    pass

def zoom_in_out_camera(origin_image_path, center, from_ratio, to_ratio, duration):
    """
    zoom in or zoom out. 拉近、拉远镜头

    Params:
        origin_image_path: the origin image file path.
        center: the focus point of camera (zoom in / zoom out by this point),
            it format will be like: (123, 234) or (0.2, 0.4) or (123, 0.3)
        from_ratio: 起始的缩放比例. like: 0.1, 0.9
        to_ratio: 结束的缩放比例， like: 0.1, 0.9
        duration: in seconds to zoom in or zoom out camera.
    Return:
        A list of images.
    """
    images = __get_images_when_zoom_in_out_camera(origin_image_path, center, from_ratio=from_ratio, to_ratio=to_ratio, duration=duration)
    ***REMOVED*** return create_video_clip_from_images(images=images, duration=duration)
    return images

***REMOVED***
    ***REMOVED*** duration = 5
    ***REMOVED*** images = __get_images_when_zoom_in_out_camera("JiChuSuCai/BeiJing/1.jpg", (0.2, 0.1), 0.5, duration)
    ***REMOVED*** create_video_clip_from_images(images=images, duration=duration).write_videofile("zoom_images.mp4")

    ***REMOVED*** zoom_in_out_camera("JiChuSuCai/BeiJing/1.jpg", (0.2, 0.1), 0.6, 1, 3).write_videofile("zoom_out_images.mp4")
    ***REMOVED*** zoom_in_out_camera("JiChuSuCai/BeiJing/1.jpg", (0.2, 0.1), 0.9, 0.5, 3).write_videofile("zoom_in_images.mp4")

    ***REMOVED*** images = [
    ***REMOVED***     "JiChuSuCai/JiaoTongGongJu/MoTuoChe/1.png",
    ***REMOVED***     "JiChuSuCai/JiaoTongGongJu/MoTuoChe/2.png",
    ***REMOVED***     "JiChuSuCai/JiaoTongGongJu/MoTuoChe/3.png",
    ***REMOVED***     "JiChuSuCai/JiaoTongGongJu/MoTuoChe/4.png"
    ***REMOVED*** ]
    ***REMOVED*** create_video_clip_from_images(images, "10秒").write_videofile("images.mp4")
    ***REMOVED*** concatenate_videos("test.mp4", "29.mp4").write_videofile("my_concatenation.mp4")

    add_watermark("output/final.mp4", "resources/SuCai/watermark.gif").write_videofile("output/gif.mp4")
    ***REMOVED*** text = """Thanks for your answers."""
    ***REMOVED*** add_subtitile("output/images1.mp4", text, (0, 5)).write_videofile("output/images2.mp4")

    ***REMOVED*** insert_image_to_video("output/test1.mp4", "resources/JiChuSuCai/JiaoTongGongJu/MoTuoChe/1.png", (0.2, 0.5), 1, [80, 60]).write_videofile("output/images2.mp4")

    ***REMOVED*** add_audio_to_video("29.mp4", "JiChuSuCai/ShengYin/1.王琪 - 可可托海的牧羊人.mp3", start=30, end=37).write_videofile("test1.mp4")
    ***REMOVED*** composite_videos("test1.mp4", "29.mp4", sub_video_position="center", sub_video_size=(350, 350)).write_videofile("my_concatenation.mp4")
    pass
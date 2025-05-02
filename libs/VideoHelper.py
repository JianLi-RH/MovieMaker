#!/usr/bin/python3
import sys

sys.path.append('../')
import os

# from moviepy.editor import *
from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip

try:
    import config_reader
except ImportError:
    from MovieMaker import config_reader

try:
    import utils
except ImportError:
    from MovieMaker import utils

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

    total = duration * config_reader.fps
    images = []
    for i in range(0, total):
        if from_ratio > to_ratio:
            # 缩小
            tmp_ratio = from_ratio - (from_ratio - to_ratio) * i / total
        else:
            # 放大
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
                    .loop()  # loop gif
                    .with_duration(clip.duration)  # 水印持续时间
                    .resize(height=size[1], )  # 水印的高度，会等比缩放
                    .margin(left=pos[0], top=pos[1], opacity=0)  # 水印边距和透明度
                    .with_pos(("left", "top")))  # 水印的位置

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
    clip = __get_video_clip(video)

    generator = lambda txt: TextClip(txt, font='lohit-odia', size=(config_reader.g_width, config_reader.g_height), fontsize=24, color='white')

    subs = [(time_span, text)]
    subtitles = SubtitlesClip(subs, generator)
    result = CompositeVideoClip([clip, subtitles.with_position(('center','bottom'))])
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
        raise Exception(f"Could not find video file on {file_path}")

def add_audio_to_video(video, audio_file, start=None):
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

    start = start if start else 0
    audios = [audioclip.with_start(start)]
    if v.audio:
        audios.append(v.audio)
    new_audioclip = CompositeAudioClip(audios)
    return v.with_audio(new_audioclip)

def create_video_clip_from_images(images, fps=config_reader.fps):
    """
    Create a video clip from images

    Params:
        images: a list of image file path.
        fps: frame per second.
    Return:
        Instance of VideoClip.
    """
    clips = []
    for img in images:
        tmp_clip = ImageClip(img).with_duration(1/fps)
        tmp_clip.fps=fps
        clips.append(tmp_clip)
    concat_clip = concatenate_videoclips(clips, method="compose")
    return concat_clip

def composite_videos(main_video, sub_video, sub_video_start_time = 0, sub_video_position = None, sub_video_size = None):
    """
    Composite two videos

    Examples for position:
        clip2.with_position((45,150)) # x=45, y=150 , in pixels
        clip2.with_position("center") # automatically centered
        # clip2 is horizontally centered, and at the top of the picture
        clip2.with_position(("center","top"))
        # clip2 is vertically centered, at the left of the picture
        clip2.with_position(("left","center"))
        # clip2 is at 40% of the width, 70% of the height of the screen:
        clip2.with_position((0.4,0.7), relative=True)
        # clip2's position is horizontally centered, and moving down !
        clip2.with_position(lambda t: ('center', 50+t) )

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
    sub_clip.with_start(sub_video_start_time)
    if sub_video_position:
        sub_clip = sub_clip.with_position(sub_video_position)
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
    image = image.with_position((pos_x, pos_y))

    timespan = utils.get_time(duration)
    image = image.with_duration(timespan)

    image_clips.append(image)
    # if size:
    #     i = Image.open(image_path)
    #     x, y = i.size

    #     x = x * size[0] if size[0] < 1 else size[0]
    #     y = y * size[1] if size[1] < 1 else size[1]
    #     image.resize(weight=x,height=y)

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
    # return create_video_clip_from_images(images=images, duration=duration)
    return images

if __name__ == "__main__":
    # duration = 5
    # images = __get_images_when_zoom_in_out_camera("JiChuSuCai/BeiJing/1.jpg", (0.2, 0.1), 0.5, duration)
    # create_video_clip_from_images(images=images, duration=duration).write_videofile("zoom_images.mp4")

    # zoom_in_out_camera("JiChuSuCai/BeiJing/1.jpg", (0.2, 0.1), 0.6, 1, 3).write_videofile("zoom_out_images.mp4")
    # zoom_in_out_camera("JiChuSuCai/BeiJing/1.jpg", (0.2, 0.1), 0.9, 0.5, 3).write_videofile("zoom_in_images.mp4")

    # images = [
    #     "JiChuSuCai/JiaoTongGongJu/MoTuoChe/1.png",
    #     "JiChuSuCai/JiaoTongGongJu/MoTuoChe/2.png",
    #     "JiChuSuCai/JiaoTongGongJu/MoTuoChe/3.png",
    #     "JiChuSuCai/JiaoTongGongJu/MoTuoChe/4.png"
    # ]
    # create_video_clip_from_images(images, "10秒").write_videofile("images.mp4")
    # concatenate_videos("test.mp4", "29.mp4").write_videofile("my_concatenation.mp4")

    # add_watermark("output/final.mp4", "resources/SuCai/watermark.gif").write_videofile("output/gif.mp4")

    # insert_image_to_video("output/test1.mp4", "resources/JiChuSuCai/JiaoTongGongJu/MoTuoChe/1.png", (0.2, 0.5), 1, [80, 60]).write_videofile("output/images2.mp4")

    # add_audio_to_video("29.mp4", "JiChuSuCai/ShengYin/1.王琪 - 可可托海的牧羊人.mp3", start=30, end=37).write_videofile("test1.mp4")
    # composite_videos("test1.mp4", "29.mp4", sub_video_position="center", sub_video_size=(350, 350)).write_videofile("my_concatenation.mp4")

    pass
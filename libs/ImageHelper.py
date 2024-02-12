import os
import sys

sys.path.append('../')
from moviepy.editor import ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont, ImageSequence

Image.MAX_IMAGE_PIXELS = None

import config_reader
import utils


def add_text_to_image(image, text, overwrite_image = False, mode='normal', text_list=None):
    """
    Add text to image

    Params:
        image: image file path.
        text: a text string
        overwrite_image: 是否覆盖原图
        mode: 文字显示方式，
            normal: 图片底部显示
        text_list:
            当mode是list的时候，需要显示一组字幕，最多显示5行文字
    Return:
        return image
    """
    font_size = config_reader.font_size
    im = Image.open(image)
    m = ImageDraw.Draw(im)
    # Add Text to an image
    x, y = im.size
    if not mode or mode == 'normal' or mode == 'bottom':
        x = x/2 - len(text) * font_size / 2
        y = y - font_size - 20
    elif mode == 'top':
        x = x/2 - len(text) * font_size / 2
        y = font_size + 20
    elif mode == 'middle':
        x = x/2 - len(text) * font_size / 2
        y = (y - font_size) / 2

    if mode == 'list':
        height = (font_size + 20) * len(text_list)    # 20是行间距
        start_y = (y - height + 20) / 2

        l = len(text_list)
        for i in range(0, l):
            if text_list[i] != text:
                tmp_font_size = font_size - 20 if font_size > 50 else font_size
                color = 'black'
            else:
                tmp_font_size = font_size
                color = 'red'
            tmp_x = (x - len(text_list[i]) * tmp_font_size) / 2
            if i != 0:
                # 这行代码必须放在mf前面
                start_y = start_y + m.size + 20

            font = ImageFont.truetype(config_reader.font, tmp_font_size)
            left, top, right, bottom = m.textbbox((tmp_x, start_y), text, font=font)
            m.rectangle((left-5, top-5, right+5, bottom+5), fill=color)
            m.text((tmp_x, start_y), text_list[i], fill=color, align="center", font=font)
    else:
        font = ImageFont.truetype(config_reader.font, font_size)
        left, top, right, bottom = m.textbbox((x, y), text, font=font)
        m.rectangle((left-5, top-5, right+5, bottom+5), fill='black')
        m.text((x, y), text, fill='white', align="center", font=font)

    if overwrite_image:
        im.save(image)
    else:
        # Display edited image on which we have added the text
        im.show()

def zoom_in_out_image(origin_image_path, center, ratio, new_path=None):
    """
    zoom in or zoom out. 拉近、拉远镜头 (覆盖原图), 也可切换焦点

    Params:
        origin_image_path: the origin image file path.
        center: the focus point of camera (zoom in / zoom out by this point),
            it format will be like: (123, 234) or (0.2, 0.4) or (123, 0.3)
        ratio: zoom in, zoom out ratio, in percentage. like: 0.1, 0.9
        new_path: 如果new_path是None就直接修改当前图片，否则在new_path保存新图片
    Return:
        新图片路径
    """
    im = Image.open(origin_image_path)
    x_center, y_center = utils.covert_pos(center)

    left = x_center - config_reader.g_width * ratio / 2
    top = y_center - config_reader.g_height * ratio / 2
    right = x_center + config_reader.g_width * ratio / 2
    bottom = y_center + config_reader.g_height * ratio / 2
    new_im = im.crop((left, top, right, bottom))
    new_im = new_im.resize((config_reader.g_width, config_reader.g_height)) # 将缩放后的图片重新放大为完全尺寸
    if not new_path:
        new_path = origin_image_path
    new_im.save(new_path)
    return new_path

def get_frames_from_gif(gif):
    """从gif图片中取得每一帧的图片

    Params:
        gif: gif图片地址
    Return:
        gif图片每一帧的存储路径
    """
    if not gif.lower().endswith(".gif"):
        raise Exception(f"{gif} is not a gif picture.")
    output_path = os.path.join(config_reader.output_dir, os.path.basename(gif).lower().replace('.gif', ''))
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    frames = []
    with Image.open(gif) as im:
        i = 0
        for frame in  ImageSequence.Iterator(im):
            tmp_path = f"{output_path}/{i}.png"
            i += 1
            frame.save(tmp_path)
            frames.append(tmp_path)
    return frames

def resize_images(images):
    """重新设置图片尺寸

    Params:
        images: 一组图片
    """
    for img in images:
        Image.open(img).resize((config_reader.g_width, config_reader.g_height)).save(img)

def merge_two_image(big_image, small_image, size, pos, rotate=None, overwrite=False):
    """将小图片粘贴到大图片上

    Params:
        big_image: 大图片，第二张图片会先是在大图片上
        small_image: 小图片，会先是在大图片上
        size: 小图片的显示尺寸, 比如： (100, 120)
        pos: 小图片的显示位置，比如： (300, 400)或者(0.4, 0.5)
    Return:
        返回新图片的地址
    """
    mode1 = 'RGBA' if big_image.endswith('.png') else 'RGB'
    img1 = Image.open(big_image).copy().convert(mode1) # 防止覆盖原图
    img1 = img1.resize((config_reader.g_width, config_reader.g_height))

    mode2 = 'RGBA' if small_image.endswith('.png') else 'RGB'

    if isinstance(size, str):
        if ',' in size:
            wh = size.split(',')
            size = (int(wh[0]), int(wh[1]))
        else:
            print("size 不合法： ", size)
            return ''
    img2 = Image.open(small_image).resize(size).convert(mode2)
    if rotate:
        img2 = img2.rotate(rotate, expand = 1)

    left, top = utils.covert_pos(pos)

    if mode2 == 'RGBA':
        img1.paste(img2, (left, top), img2)
    else:
        img1.paste(img2, (left, top))
    # img1.show()
    if overwrite:
        img1.save(big_image)
        return big_image
    else:
        if isinstance(img1, str):
            return img1
        else:
            new_path = os.path.join(os.path.dirname(big_image), "tmp_"+os.path.basename(big_image))
            img1.save(new_path)
            return new_path

def add_gif_to_images(images, gif, pos, size):
    """将gif添加到一组图片上

    Params:
        images: 一组图片
        gif: gif文件路径
        size: 小图片的显示尺寸, 比如： (100, 120)
        pos: 小图片的显示位置，比如： (300, 400)或者(0.4, 0.5)
    """
    frames = get_frames_from_gif(gif=gif)
    l = len(images)
    for i in range(0, l):
        merge_two_image(images[i], frames[i % len(frames)], size=size, pos=pos, overwrite=True)

def create_text_png(text, size=None, font = None):
    """
    根据文字创建一个png图片
    """
    size = size if size else (config_reader.g_width, 120)
    im = Image.new(mode='RGBA', size=size)
    draw_table = ImageDraw.Draw(im=im)
    font = font if font else 'fonts/QingNiaoHuaGuangJianMeiHei/QingNiaoHuaGuangJianMeiHei-2.ttf'
    draw_table.text(xy=(0,0), text=text, fill='#008B8B', font=ImageFont.truetype(font=font, size=50))
    im.show()

def create_gif(images, file_name = None):
    """使用一组png图片生成一个gif图片
    https://blog.51cto.com/tinkzy/6561120

    Params:
        images: 一组png图片
    Return:
        gif图片路径
    """
    file_name = file_name if file_name else f"{utils.get_random_str(8)}.gif"
    gif = os.path.join(config_reader.output_dir, file_name)
    img = Image.open(images[0])
    gif_frames = [img]
    for filename in images[1:]:
        img = Image.open(filename)
        gif_frames.append(img)
    gif_frames[0].save(gif, save_all=True, append_images=gif_frames[1:], duration=len(images), loop=0)
    return gif

if __name__ == "__main__":
    add_text_to_image("resources/JiChuSuCai/BeiJing/太空.jpg", r'中文阿斯asdsad顿萨杜萨的', save_image=False)
    # zoom_in_out_image("resources/JiChuSuCai/BeiJing/1.jpg", (0.5, 0.5), 0.9)
    # test("resources/JiChuSuCai/BeiJing/1.jpg", "resources/SuCai/watermark.gif")
    # get_frames_from_gif("resources/SuCai/watermark.gif")
    # merge_two_image("resources/JiChuSuCai/BeiJing/1.jpg", "output/watermark.gif/0.png", size=(100, 100), pos=(100, 20), rotate=45)
    pass
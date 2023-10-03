***REMOVED***
***REMOVED***

sys.path.append('../')

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
    ***REMOVED*** Add Text to an image
    x, y = im.size
    if mode == 'normal' or mode == 'bottom':
        x = x/2 - len(text) * font_size / 2
        y = y - font_size - 20
    elif mode == 'top':
        x = x/2 - len(text) * font_size / 2
        y = font_size + 20
    elif mode == 'middle':
        x = x/2 - len(text) * font_size / 2
        y = (y - font_size) / 2

    if mode == 'list':
        height = (font_size + 20) * len(text_list)    ***REMOVED*** 20是行间距
        start_y = (y - height + 20) / 2

        for i in range(0, len(text_list)):
            if text_list[i] != text:
                tmp_font_size = font_size - 20 if font_size > 50 else font_size
                color =(255,255,255)
***REMOVED***
                tmp_font_size = font_size
                color =(255,0,0)
            tmp_x = (x - len(text_list[i]) * tmp_font_size) / 2
            if i != 0:
                ***REMOVED*** 这行代码必须放在mf前面
                start_y = start_y + mf.size + 20

            mf = ImageFont.truetype(config_reader.font, tmp_font_size)
            m.text((tmp_x, start_y), text_list[i], color, align="center", font=mf)
    else:
        mf = ImageFont.truetype(config_reader.font, font_size)
        m.text((x, y), text, (255,255,255), align="center", font=mf)

    if overwrite_image:
        im.save(image)
    else:
        ***REMOVED*** Display edited image on which we have added the text
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

    left = x_center * (1 - ratio)
    top = y_center * (1 - ratio)
    right = config_reader.g_width * ratio
    bottom = config_reader.g_height * ratio
    new_im = im.resize((config_reader.g_width, config_reader.g_height)) ***REMOVED*** 将缩放后的图片重新放大为完全尺寸
    new_im = new_im.crop((left, top, right, bottom))
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
    output_path = os.path.join(config_reader.output_dir, os.path.basename(gif))
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    frames = []
    with Image.open(gif) as im:
        i = 0
        for frame in  ImageSequence.Iterator(im):
            tmp_path = f"{output_path***REMOVED***/{i***REMOVED***.png"
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
    img1 = Image.open(big_image).copy().convert(mode1) ***REMOVED*** 防止覆盖原图
    img1 = img1.resize((config_reader.g_width, config_reader.g_height))

    mode2 = 'RGBA' if small_image.endswith('.png') else 'RGB'
    img2 = Image.open(small_image).resize(size).convert(mode2)
    if rotate:
        img2 = img2.rotate(rotate, expand = 1)

    left, top = utils.covert_pos(pos)

    if mode2 == 'RGBA':
        img1.paste(img2, (left, top), img2)
    else:
        img1.paste(img2, (left, top))
    ***REMOVED*** img1.show()
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

def create_text_png(text, size=None, font = None):
    """
    根据文字创建一个png图片
    """
    size = size if size else (config_reader.g_width, 120)
    im = Image.new(mode='RGBA', size=size)
    draw_table = ImageDraw.Draw(im=im)
    font = font if font else 'fonts/QingNiaoHuaGuangJianMeiHei/QingNiaoHuaGuangJianMeiHei-2.ttf'
    draw_table.text(xy=(0,0), text=text, fill='***REMOVED***008B8B', font=ImageFont.truetype(font=font, size=50))
    im.show()


***REMOVED***
    add_text_to_image("resources/JiChuSuCai/BeiJing/太空.jpg", r'中文阿斯asdsad顿萨杜萨的', save_image=False)
    ***REMOVED*** zoom_in_out_image("resources/JiChuSuCai/BeiJing/1.jpg", (0.5, 0.5), 0.9)
    ***REMOVED*** test("resources/JiChuSuCai/BeiJing/1.jpg", "resources/SuCai/watermark.gif")
    ***REMOVED*** get_frames_from_gif("resources/SuCai/watermark.gif")
    ***REMOVED*** merge_two_image("resources/JiChuSuCai/BeiJing/1.jpg", "output/watermark.gif/0.png", size=(100, 100), pos=(100, 20), rotate=45)
    pass
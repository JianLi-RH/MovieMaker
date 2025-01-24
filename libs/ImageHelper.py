import os
import sys
import yaml

sys.path.append('../')
from PIL import Image, ImageDraw, ImageFont, ImageSequence, ImageOps
Image.MAX_IMAGE_PIXELS = 7680000

import config_reader
from scenario import Scenario
import utils


def add_text_to_image(image, text, color = 'white', overwrite_image = False, mode='normal', text_list=None):
    """
    Add text to image

    Params:
        image: image file path.
        text: a text string
        color: 字幕颜色 （list模式不适用）
        overwrite_image: 是否覆盖原图
        mode: 文字显示方式，
            normal: 图片底部显示
        text_list:
            当mode是list的时候，需要显示一组字幕，最多显示5行文字
    Return:
        None
    """
    if not text:
        return
    font_size = config_reader.font_size
    im = Image.open(image)
    m = ImageDraw.Draw(im)
    # Add Text to an image
    x, y = im.size
    if not mode or mode == 'normal' or mode == 'bottom':
        x = (x - len(text) * font_size) / 2
        y = y - font_size - 20 # 距离底边20个像素
    elif mode == 'top':
        x = (x - len(text) * font_size) / 2
        y = 20
    elif mode == 'middle':
        x = (x - len(text) * font_size) / 2
        y = (y - font_size) / 2
        
    if x < 0:
        x = 0

    if mode == 'list':
        height = font_size * (len(text_list) - 1) * 0.8 + font_size   # 20是行间距, height是总的文本高度
        start_y = (y - height) / 2

        l = len(text_list)
        for i in range(0, l):
            if text_list[i] != text:
                tmp_font_size = font_size * 0.8 # 非当前文字缩小显示
                color = 'black'
            else:
                tmp_font_size = font_size
                color = 'red'
            tmp_x = (x - len(text_list[i]) * tmp_font_size) / 2

            # 这行代码必须放在mf前面
            if i > 0:
                start_y = start_y + font_size

            font = ImageFont.truetype(config_reader.font, tmp_font_size)
            left, top, right, bottom = m.textbbox((tmp_x, start_y), text, font=font)
            m.rectangle((left-5, top-5, right+5, bottom+5), outline=None, width=0)
            m.text((tmp_x, start_y), text_list[i], fill=color, align="center", font=font)
    else:
        font = ImageFont.truetype(config_reader.font, font_size)
        left, top, right, bottom = m.textbbox((x, y), text, font=font)
        m.rectangle((left-5, top-5, right+5, bottom+5), outline=None, width=0)
        m.text((x, y), text, fill=color, align="center", font=font)

    if overwrite_image:
        im.save(image)
    else:
        # Display edited image on which we have added the text
        im.show()
    im.close()

def cut_image(image, char):
    """根据角色裁剪图片 （直接修改图片）
    
    Params:
        image: the origin image file path.
        char: 角色实例
    Return:
        none
    """
    if isinstance(image, str):
        im = Image.open(image)
    else:
        im = image
    
    w = config_reader.g_width
    h = config_reader.g_height
    c_w, c_h = char.size
    c_x, c_y = char.pos
    
    x_ratio = (c_w + 50) / w
    y_ratio = (c_h + 50) / h
    
    left = c_x * (1 - x_ratio)
    if (w - c_x - c_w) < 0:
        # 角色的一部分在屏幕右边
        # 加负数，向左移动
        left + (w - c_x - c_w) * (1 - x_ratio)
        right = 1
    else:
        right = c_x + c_w + (w - c_x - c_w) * x_ratio

    top = c_y * (1 - y_ratio)
    if (h - c_y - c_h) < 0:
        # 角色的一部分在屏幕下面
        # 加负数，向上移动
        top + (h - c_y - c_h) * (1 - y_ratio)
        bottom = h
    else:
        bottom = c_y + c_h + (h - c_y - c_h) * y_ratio

    im = im.crop((left, top, right, bottom))
    im.resize((config_reader.g_width, config_reader.g_height)).save(image)

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
    if ratio == 1:
        return origin_image_path
    
    im = Image.open(origin_image_path)
    x_center, y_center = utils.covert_pos(center)

    left = x_center - config_reader.g_width * ratio / 2
    left = left if left > 0 else 0
    top = y_center - config_reader.g_height * ratio / 2
    top = top if top > 0 else 0
    right = x_center + config_reader.g_width * ratio / 2
    right = right if right < config_reader.g_width else config_reader.g_width
    bottom = y_center + config_reader.g_height * ratio / 2
    bottom = bottom if bottom < config_reader.g_height else config_reader.g_height
    im = im.crop((left, top, right, bottom))
    if not new_path:
        new_path = origin_image_path
    im.resize((config_reader.g_width, config_reader.g_height)).save(new_path)
    im.close()
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
    output_path = os.path.join(config_reader.output_dir, "gif", os.path.basename(gif).lower().replace('.gif', ''))
    os.makedirs(output_path, exist_ok=True)
    frames = []
    with Image.open(gif) as im:
        i = 0
        for frame in  ImageSequence.Iterator(im):
            tmp_path = f"{output_path}/{i}-gif.png"
            i += 1
            frame.save(tmp_path)
            frames.append(tmp_path)
    return frames

def resize_image(image):
    """重新设置图片尺寸

    Params:
        image: 图片地址
    """
    im = Image.open(image)
    im.resize((config_reader.g_width, config_reader.g_height)).save(image)
    im.close()

def paint_char_on_image(char, 
                        image=None, 
                        image_obj=None, 
                        overwrite=False, 
                        save=False, 
                        gif_index=0, 
                        dark=False):
    """Paint a char on image
    
    Params:
        char: 角色
        image: 背景图片
        image_obj: 背景图片内存对象 （当需要连续修改同一张图片时建议使用内存对象）
        overwrite: 是否覆盖大图
        save: 是否保存图片
        gif_index: 如果角色素材是gif图片，则显示指定下标的frame
        dark: 设置角色为灰色显示
    Returns:
        (返回新图片的地址, image_obj)
    """
    if not char.image.lower().endswith(".gif"):
        small_image = char.image
    else:
        if not char.gif_frames:
            char.gif_frames = get_frames_from_gif(char.image) 
        small_image = char.gif_frames[gif_index % len(char.gif_frames)]

    reduce_light = 100 if dark else 0
    alpha = char.transparency if char.transparency is not None else 1
    if reduce_light != 0 or alpha != 1:
        small_image = dark_image(small_image, reduce_light=reduce_light, alpha=alpha)
    
    return merge_two_image(small_image=small_image, 
                           size=char.size, 
                           pos=char.pos, 
                           big_image=image, 
                           big_image_obj=image_obj,
                           rotate=char.rotate, 
                           overwrite=overwrite,
                           save=save)

def merge_two_image(small_image, 
                    size, 
                    pos, 
                    big_image=None, 
                    big_image_obj=None, 
                    rotate=None, 
                    overwrite=False,
                    save=False):
    """将小图片粘贴到大图片上

    Params:
        small_image: 小图片，会先是在大图片上/ 可以是图片地址，也可以是Image对象
        size: 小图片的显示尺寸, 比如： (100, 120)
        pos: 小图片的显示位置，比如： (300, 400)或者(0.4, 0.5)
        big_image: 大图片，第二张图片会先是在大图片上
        big_image_obj: 大图片的内存对象
        rotate: 小图片的显示角度，如 0~360的数字，或者"左右"
        overwrite: 是否覆盖大图
        save: 是否保存图片
    Return:
        (返回新图片的地址, image_obj)
    """
    if big_image_obj:
        img1 = big_image_obj
    else:
        mode1 = 'RGBA' if big_image.endswith('.png') else 'RGB'
        img1 = Image.open(big_image).copy().convert(mode1) # 防止覆盖原图
        img1 = img1.resize((config_reader.g_width, config_reader.g_height))

    if isinstance(small_image, str):
        small_image = Image.open(small_image)
    mode2 = 'RGBA' if small_image.filename.endswith('.png') else 'RGB'

    size = utils.covert_pos(size) # 可以使用小数（百分比）表示图片尺寸
    if isinstance(small_image, str):
        img2 = Image.open(small_image).resize(size).convert(mode2)
    else:
        img2 = small_image.resize(size).convert(mode2)
    if rotate:
        if rotate == "左右":
            im_mirror = ImageOps.mirror(img2)
            img2.close()
            if isinstance(small_image, str):
                basename = os.path.basename(small_image)
            else:
                basename = os.path.basename(small_image.filename)
            new_path = os.path.join(os.path.dirname(big_image), basename)
            im_mirror.save(new_path)
            img2 = Image.open(new_path)
        else:
            img2 = img2.rotate(rotate, expand = 1)

    left, top = utils.covert_pos(pos)

    if mode2 == 'RGBA':
        img1.paste(img2, (left, top), img2)
    else:
        img1.paste(img2, (left, top))
    img2.close()
    if not save:
        return None, img1

    if overwrite:
        img1.save(big_image)
        return big_image, img1
    else:
        # if isinstance(img1, str):
        #     return img1
        # else:
            new_path = os.path.join(os.path.dirname(big_image), "tmp_"+os.path.basename(big_image))
            img1.save(new_path)
            return new_path, img1

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

def dark_image(image, reduce_light=100, alpha=1):
    """使图片变暗
    
    Params:
        image: 图片地址或者PIL.Image.Image对象
        reduce_light: 亮度减少的数值
        alpha: 透明度
    Returns:
        image_obj内存对象
    """
    image_obj = image
    if not isinstance(image, Image.Image):
        image_obj = Image.open(image)
    total_w, total_h = image_obj.size
    for i in range(0, total_w):
        for j in range(0, total_h):
            # 获取当前像素的颜色值
            pixel_color = image_obj.getpixel((i, j))
            if isinstance(pixel_color, int):
                # png图像的没有颜色的部位
                if image_obj._mode == "RGBA":
                    new_color = (0,0,0,0)
                else:
                    new_color = (0,0,0)
            else:
            # 调整每个颜色通道的亮度（这里简单地减小亮度，可以根据需要调整系数）
                if image_obj._mode == "RGBA":
                    new_color = (max(0, pixel_color[0] - reduce_light), max(0, pixel_color[1] - reduce_light), max(0, pixel_color[2] - reduce_light), int(pixel_color[3] * alpha))
                else:
                    new_color = (max(0, pixel_color[0] - reduce_light), max(0, pixel_color[1] - reduce_light), max(0, pixel_color[2] - reduce_light))
            # 设置新的颜色值  
            image_obj.putpixel((i, j), new_color)
    return image_obj
    
def hightlight_char(image_obj, char):
    """高亮显示当前角色
    
    Params:
        image_obj: 背景图片内存对象 （当需要连续修改同一张图片时建议使用内存对象）
        char: 角色
    Returns:
        None (直接编辑image_obj内存对象)
    """
    total_w, total_h = image_obj.size
    x, y = char.pos
    w, h = char.size
    for i in range(0, total_w):
        for j in range(0, total_h):
            if i > x and i < (x + w) and j > y and j < (y + h):
                continue
            # 获取当前像素的颜色值
            pixel_color = image_obj.getpixel((i, j))
            # 调整每个颜色通道的亮度（这里简单地减小亮度，可以根据需要调整系数）
            new_color = (max(0, pixel_color[0] - 100), max(0, pixel_color[1] - 100), max(0, pixel_color[2] - 100))
            # 设置新的颜色值  
            image_obj.putpixel((i, j), new_color)    
    return image_obj

def preview(scenario, script, bg_img=None, char_name_list=None):
    """
    预览角色在背景图上的显示效果
    
    Params:
        scenario: 场景名
        script: 脚本文件路径
        bg_img背景图片，如果没指定背景图片则使用场景的背景图
        char_name_list： 一组角色名，如果没制定则使用场景中的角色
    Return:
        gif图片路径
    """
    import shutil
    with open(script, 'rb') as file:
        script = yaml.safe_load(file)

    scenarios = list(filter(lambda x: x.get("名字", None) == scenario, script["场景"]))
    if not scenarios:
        raise Exception("场景不存在")
    scenario_obj = scenarios[0]
    scenario = Scenario(scenario_obj, preview=True)
    if not bg_img:
        bg_img = scenario.background_image
    chars = scenario.chars
    if not char_name_list:
        char_name_list = [c.name for c in chars]
    
    file_name = os.path.basename(bg_img)
    new_bg_folder = os.path.join(config_reader.output_dir, "tmp")
    os.makedirs(new_bg_folder, exist_ok=True)
    file_path = os.path.join(new_bg_folder, file_name)
    shutil.copyfile(bg_img, file_path)
    resize_image(file_path)

    image_obj = None
    for char in chars:
        if char.display and char.name in char_name_list:
            _, image_obj = paint_char_on_image(char=char, image=file_path, image_obj=image_obj, overwrite=True)
    
    image_obj.save(file_path)
    image_obj.close() 
    return file_path
    

if __name__ == "__main__":
    # add_text_to_image("resources/JiChuSuCai/BeiJing/太空.jpg", r'中文阿斯asdsad顿萨杜萨的', save_image=False)
    # zoom_in_out_image("resources/JiChuSuCai/BeiJing/1.jpg", (0.5, 0.5), 0.9)
    # test("resources/JiChuSuCai/BeiJing/1.jpg", "resources/SuCai/watermark.gif")
    # get_frames_from_gif("resources/SuCai/watermark.gif")
    # merge_two_image("resources/JiChuSuCai/BeiJing/1.jpg", "output/watermark.gif/0.png", size=(100, 100), pos=(100, 20), rotate=45)
    pass
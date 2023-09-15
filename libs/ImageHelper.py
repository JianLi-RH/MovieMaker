***REMOVED***

from PIL import Image, ImageDraw, ImageFont

import config_reader
import utils

def add_text_to_image(image, text, save_image = False):
    """
    Add text to image

    Params:
        image: image file path.
        text: a text string

    Return:
        return image
    """
    i = Image.open(image)
    m = ImageDraw.Draw(i)
    mf = ImageFont.truetype(config_reader.font, 25)
    ***REMOVED*** Add Text to an image
    x, y = i.size
    m.text((x/2 - len(text) * 10, y-50), text, (255,255,255), align="center", font=mf)

    if save_image:
        ***REMOVED*** Save the image on which we have added the text
        file_name = os.path.basename(image)
        i.save(os.path.join(config_reader.output_dir, file_name))
    else:
        ***REMOVED*** Display edited image on which we have added the text
        i.show()

def zoom_in_out_image(origin_image_path, center, ratio):
    """
    zoom in or zoom out. 拉近、拉远镜头 (覆盖原图)

    Params:
        origin_image_path: the origin image file path.
        center: the focus point of camera (zoom in / zoom out by this point),
            it format will be like: (123, 234) or (0.2, 0.4) or (123, 0.3)
        ratio: zoom in, zoom out ratio, in percentage. like: 0.1, 0.9

    Return:
        Instance of Image.
    """
    im = Image.open(origin_image_path)
    x_center, y_center = utils.covert_pos(center)

    left = x_center * (1 - ratio)
    top = y_center * (1 - ratio)
    right = config_reader.g_width * ratio
    bottom = config_reader.g_height * ratio
    new_im = im.crop((left, top, right, bottom))
    new_im = new_im.resize((config_reader.g_width, config_reader.g_height)) ***REMOVED*** 将缩放后的图片重新放大为完全尺寸

    ***REMOVED*** dir_name = os.path.dirname(origin_image_path)
    ***REMOVED*** base_name = os.path.basename(origin_image_path)
    ***REMOVED*** split_tup = os.path.splitext(base_name)
    ***REMOVED*** new_path = os.path.join(dir_name, f"{ratio***REMOVED***{split_tup[1]***REMOVED***")
    new_im.save(origin_image_path)
    return origin_image_path

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
        num_key_frames = im.n_frames
        for i in range(num_key_frames):
            im.seek(im.n_frames // num_key_frames * i)
            tmp_path = f"{output_path***REMOVED***/{i***REMOVED***.png"
            im.save(tmp_path)
            frames.append(tmp_path)
    return frames

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
    if overwrite:
        img1 = Image.open(big_image)
    else:
        img1 = Image.open(big_image).copy() ***REMOVED*** 防止覆盖原图
    img1 = img1.resize((config_reader.g_width, config_reader.g_height))
    img2 = Image.open(small_image).resize(size).convert('RGBA')
    if rotate:
        img2 = img2.rotate(rotate, expand = 1)

    outer_x, outer_y = img1.size
    left = pos[0] if pos[0] > 1 else outer_x * pos[0]
    top = pos[1] if pos[1] > 1 else outer_y * pos[1]

    img1.paste(img2, (left, top), img2)
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

def test(img1, img2):
    img = Image.open(img1).convert("RGBA")
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle(((100, 80), (520, 350)), fill=185)

    x,y = img.size
    img2 = Image.open(img2).convert("RGBA").resize((x,y))

    img3 = Image.composite(img2, img, mask=mask)
    img3.show()

***REMOVED***
    ***REMOVED*** add_text_to_image("resources/JiChuSuCai/BeiJing/1.jpg", r'中文阿斯asdsad顿萨杜萨的', save_image=True)
    ***REMOVED*** zoom_in_out_image("resources/JiChuSuCai/BeiJing/1.jpg", (0.5, 0.5), 0.9)
    ***REMOVED*** test("resources/JiChuSuCai/BeiJing/1.jpg", "resources/SuCai/watermark.gif")
    ***REMOVED*** get_frames_from_gif("resources/SuCai/watermark.gif")
    merge_two_image("resources/JiChuSuCai/BeiJing/1.jpg", "output/watermark.gif/0.png", size=(100, 100), pos=(100, 20), rotate=45)
    pass
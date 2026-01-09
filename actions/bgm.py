from libs import AudioHelper, ImageHelper

def Do(images, sorted_char_list):
    """向视频中插入一段背景音
    
    Params:
        images: a list of big images
        sorted_char_list: sorted char list
    
    Example:
        -
        名称: BGM
        字幕: 
            - ['','', 'bgm', 'resources/ShengYin/bgm.mp3']
    
    Params:
        images: 全部背景图片
        sorted_char_list: 排序后的角色
    """     
    l = len(images)
    for i in range(0, l):
        big_image = None
        for _char in sorted_char_list:
            if _char.display:
                _, big_image = ImageHelper.paint_char_on_image(image=images[i], 
                                                                image_obj=big_image,
                                                                char=_char, 
                                                                save=False,
                                                                gif_index=i)
        if big_image:
            big_image.save(images[i])
            big_image.close()
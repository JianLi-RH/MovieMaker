from libs import AudioHelper, ImageHelper
            
            
def Do(images, sorted_char_list):
    """场景静止一段时间
    
    Params:
        images: 全部背景图片
        sorted_char_list: 排序后的角色
    
    Example:
    -
        名称: 静止
        持续时间: 2
        字幕: 
        - ['','', '', 'resources/ShengYin/回忆转场.mp3']
        渲染顺序: 1
    """ 
    l = len(images)
    big_image = None
    for _char in sorted_char_list:
        if _char.display:
            _, big_image = ImageHelper.paint_char_on_image(image=images[0], 
                                                            image_obj=big_image,
                                                            char=_char, 
                                                            save=False,
                                                            gif_index=0)

    for i in range(0, l):
        big_image.save(images[i])
    big_image.close()
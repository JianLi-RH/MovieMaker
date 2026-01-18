from libs.RenderHelper import RenderHelper


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
    RenderHelper.create_static_frame(images, sorted_char_list)
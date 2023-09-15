
import numbers
import config_reader

def get_time(script_time):
    """
    将脚本秒时的时间转换成数字，以秒为单位

    Params:
        script_time: 脚本时间，如: 3秒, 2分5秒, 2 (default is second)

    Return:
        以秒为单位的时间
    """
    if isinstance(script_time, numbers.Number):
        return script_time

    time_number = 0
    if "分" in script_time:
        _time = script_time.split("分")
        time_number += int(_time[0]) * 60

        if len(_time) > 1:
            script_time = _time[1]

    if "秒" in script_time:
        script_time = script_time.replace("秒", '')
        time_number += float(script_time)

    return time_number

def covert_pos(pos):

    if pos == '中心':
        pos = [0.5, 0.5]

    x_center, y_center = pos
    if x_center == '中心':
        x_center = 0.5
    elif x_center == '左侧':
        x_center = 0
    elif x_center == '右侧':
        x_center = 1

    if y_center == '中心':
        y_center = 0.5
    elif y_center == '顶侧':
        y_center = 0
    elif y_center == '底部':
        y_center = 1

    if x_center < 1:
        x_center = config_reader.g_width * x_center
    if y_center < 1:
        y_center = config_reader.g_height * y_center

    return (x_center, y_center)
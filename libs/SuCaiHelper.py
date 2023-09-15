***REMOVED***.10
***REMOVED***

import config_reader

def get_sucai(args):
    """
    Get sucai file path.

    Params:
        args: sucai path, like [`JiaoTongGongJu`, `MoTuoChe`]

    Return:
        The path of sucai.
    """
    if isinstance(args, str) and os.path.exists(args):
        return args

    sucai_dir = config_reader.sucai_dir
    return os.path.join(sucai_dir, *args)

def get_shengyin(music):
    """
    Get music file path.

    Params:
        music: music file name.

    Return:
        The path of music.
    """
    if music:
        if isinstance(music, str) and os.path.exists(music):
            return music
        return os.path.join("resources", "ShengYin", music)
    else:
        return None

***REMOVED***
    pass
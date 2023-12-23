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
    sucai_dir = config_reader.sucai_dir
    if not args:
        return None

    if isinstance(args, str):
        if os.path.exists(args):
            return args
        else:
            return os.path.join(sucai_dir, args)

    return os.path.join(sucai_dir, *args)


***REMOVED***
    pass
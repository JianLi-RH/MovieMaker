#!/usr/bin/python3.10
import os

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


if __name__ == "__main__":
    pass
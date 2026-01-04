#!/usr/bin/python3

'''
这是程序入口，可以通过以下几种方式生成视频：
    1. 执行整个 demo/水浒传.yaml 文件，生成完整的视频
    python run.py -o "水浒传.mp4" -s 'demo/水浒传.yaml'
    2. 执行 demo/水浒传.yaml 文件中的 毒杀武大 场景，生成单一场景视频
    python run.py -o "水浒传.mp4" -c '商议对策' -s 'demo/水浒传.yaml'

    生成的视频文件将会被保存在config_reader.output_dir下面
'''

import getopt
import os
import sys

import yaml
from moviepy import VideoFileClip, video
from moviepy.video.VideoClip import VideoClip
from typing import List, Optional, Union

import config_reader
from libs import VideoHelper
from scenario import Scenario
from logging_config import setup_default_logging, get_logger
from exceptions import ScriptNotFoundException, ScriptValidationError
from validation import validate_script_resources, validate_config

# 初始化日志系统
setup_default_logging()
logger = get_logger(__name__)

def connect_videos(
    final_video_name: str,
    videos: Optional[List[Union[str, VideoClip]]] = None,
    script: str = 'script.yaml',
    delete_old: bool = False
) -> str:
    """拼接多个视频文件

    Params:
        final_video_name: 输出的视频文件名（包含全路径）
        videos: 视频文件列表，默认为None
        script: 脚本文件，当没有提供videos时，根据脚本文件读取对应的场景视频
        delete_old: 是否删除旧的视频文件

    Returns:
        str: 生成的视频文件路径
    """
    if videos is None:
        videos = []

    logger.info(f"开始拼接视频文件，输出: {final_video_name}")

    script_name = os.path.basename(script).split('.')[0]
    if not videos:
        logger.debug(f"从脚本文件读取场景列表: {script}")
        with open(script, 'r') as file:
            script = yaml.safe_load(file)

            scenarios = script["场景"]
            videos = [os.path.join(config_reader.output_dir, script_name, x.get("名字") + config_reader.video_format) for x in scenarios]
            logger.info(f"发现 {len(videos)} 个场景视频需要拼接")

    final_videos = []
    for i, f in enumerate(videos, 1):
        logger.debug(f"加载视频 {i}/{len(videos)}: {f}")
        if isinstance(f, video.VideoClip.VideoClip):
            final_videos.append(f)
        else:
            final_videos.append(VideoFileClip(f))

    logger.info(f"拼接 {len(final_videos)} 个视频片段")
    final = VideoHelper.concatenate_videos(*final_videos)

    if delete_old:
        logger.info("删除旧视频文件")
        for f in videos:
            if os.path.exists(f):
                os.remove(f)
                logger.debug(f"已删除: {f}")
            else:
                logger.warning(f"文件不存在，无法删除: {f}")

    # 避免出现同名文件导致"xxx bytes wanted but 0 bytes read"错误
    # 更新文件名
    if os.path.exists(final_video_name):
        logger.debug(f"删除已存在的输出文件: {final_video_name}")
        os.remove(final_video_name)
    if config_reader.output_dir not in final_video_name:
        final_video_name = os.path.join(config_reader.output_dir, final_video_name)

    logger.info(f"写入最终视频文件: {final_video_name}")
    final.write_videofile(final_video_name)
    logger.info(f"视频拼接完成: {final_video_name}")

    return final_video_name

def run(script: str, output: Optional[str] = None, scenario: Optional[str] = None) -> int:
    """创建视频

    Params:
        script: 脚本文件的路径
        output: 输出的视频文件名
        scenario: 需要创建视频的场景，没指定的话将对整个script.yaml进行生成

    Returns:
        int: 返回0表示成功
    """
    logger.info(f"开始处理脚本: {script}")

    # 为每个脚本分配一个输出路径
    script_name = os.path.basename(script).split('.')[0]
    config_reader.output_dir = os.path.join(config_reader.output_dir, script_name)
    os.makedirs(config_reader.output_dir, exist_ok=True)
    logger.debug(f"输出目录: {config_reader.output_dir}")

    with open(script, 'rb') as file:
        script_data = yaml.safe_load(file)

        scenarios = script_data["场景"]
        total_scenarios = len(scenarios)

        if scenario:
            scenarios = list(filter(lambda x: x.get("名字", None) == scenario, scenarios))
            logger.info(f"筛选场景: {scenario}")

        logger.info(f"共有 {len(scenarios)} 个场景需要处理（总共 {total_scenarios} 个场景）")

        final_videos_files = []
        for idx, scenario_obj in enumerate(scenarios, 1):
            scenario_name = scenario_obj.get("名字", f"场景{idx}")
            logger.info(f"处理场景 {idx}/{len(scenarios)}: {scenario_name}")

            scenario_instance = Scenario(scenario_obj)
            logger.debug(f"场景包含 {len(scenario_instance.activities)} 个活动")

            videos = [act.to_video() for act in scenario_instance.activities]
            new_video = VideoHelper.concatenate_videos(*videos)

            if scenario_instance.bgm:
                logger.debug(f"添加背景音乐: {scenario_instance.bgm}")
                new_video = VideoHelper.add_audio_to_video(new_video, scenario_instance.bgm)

            new_video.with_fps(config_reader.fps)
            final_videos_files.append(new_video)
            logger.info(f"场景 {scenario_name} 处理完成")

        if not output:
            if scenario:
                output = f"{scenario_instance.name}{config_reader.video_format}"
            else:
                output = f"{script_name}{config_reader.video_format}"
        output = os.path.join(config_reader.output_dir, output)

        logger.info(f"视频文件将会被输出到: {output}")
        connect_videos(output, videos=final_videos_files, delete_old=False)
        logger.info("视频生成完成！")

    return 0

def main(argv: List[str]) -> int:
    """
    执行run()生成视频

    Params:
        argv: 命令行参数列表

    Returns:
        int: 返回0表示成功
    """
    logger.info("MovieMaker 视频生成系统启动")

    options = "o:s:c:"
    opts , args = getopt.getopt(argv, options)
    logger.debug(f"命令行参数: {opts}")

    output, scenario, script = '', '', ''
    for currentArgument, currentValue in opts:
        if currentArgument in ("-o", "--output"):
            output = currentValue.strip()
            logger.debug(f"输出文件: {output}")
        if currentArgument in ("-c", "--scenario"):
            scenario = currentValue.strip()
            logger.debug(f"指定场景: {scenario}")
        if currentArgument in ("-s", "--script"):
            script = currentValue.strip()
            logger.debug(f"脚本文件: {script}")

    if not script:
        logger.error("缺少必需参数: 脚本文件路径")
        raise ScriptNotFoundException("必须使用 -s 参数指定脚本文件")

    if not os.path.exists(script):
        logger.error(f"脚本文件不存在: {script}")
        raise ScriptNotFoundException(script)

    # 验证配置
    logger.info("验证配置参数")
    config_data = {
        "fps": config_reader.fps,
        "g_width": config_reader.g_width,
        "g_height": config_reader.g_height,
        "font_size": config_reader.font_size,
        "font": config_reader.font,
        "output_dir": config_reader.output_dir,
        "sucai_dir": config_reader.sucai_dir,
        "tts_engine": config_reader.tts_engine,
    }
    config_errors = validate_config(config_data)
    if config_errors:
        logger.error("配置验证失败:")
        for error in config_errors:
            logger.error(f"  - {error}")
        raise ScriptValidationError(config_errors)

    # 验证脚本资源
    logger.info("验证脚本资源文件")
    resources_valid, missing_resources = validate_script_resources(script)
    if not resources_valid:
        logger.error(f"发现 {len(missing_resources)} 个缺失的资源文件")
        logger.warning("建议：请检查并添加缺失的资源文件，或从脚本中移除对这些资源的引用")
        logger.warning("继续执行可能导致视频生成失败")

        # 询问用户是否继续（在命令行模式下）
        # 在自动化场景中，可以设置环境变量 MOVIEMAKER_SKIP_VALIDATION=true 跳过验证
        skip_validation = os.getenv("MOVIEMAKER_SKIP_VALIDATION", "false").lower() == "true"
        if not skip_validation:
            logger.info("提示：设置环境变量 MOVIEMAKER_SKIP_VALIDATION=true 可跳过资源验证")
            # 注：在实际使用中，这里可以添加用户交互确认

    if not output:
        if scenario:
            output = scenario + config_reader.video_format
        else:
            output = os.path.basename(script).replace(".yaml", "") + config_reader.video_format
        logger.debug(f"自动生成输出文件名: {output}")

    logger.info(f"配置信息 - 输出: {output}, 场景: {scenario or '全部'}, 脚本: {script}")
    logger.info("开始视频生成流程")
    return run(output=output, scenario=scenario, script=script)

if __name__ == "__main__":
    try:
        file="水浒传第三百三十七回"
        if len(sys.argv) > 1:
            result = main(sys.argv[1:])
        else:
            logger.info("使用默认配置运行")
            result = run(script=f"script/水浒传/{file}.yaml", scenario="躲避")
        logger.info(f"程序执行完成，退出码: {result}")
        sys.exit(result)
    except Exception as e:
        logger.exception(f"程序执行失败: {e}")
        sys.exit(1)

    # connect_videos(f"output/{file}/{file}.mp4", script=f"script/水浒传/{file}.yaml")


# source .venv/bin/activate
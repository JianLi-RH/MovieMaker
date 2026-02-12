"""
资源验证模块 / Resource Validation Module

本模块提供资源文件验证功能，确保所有必需的资源在视频生成前都存在
This module provides resource validation to ensure all required resources exist before video generation
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
import yaml

from logging_config import get_logger
from exceptions import (
    MissingResourcesException,
    ImageNotFoundException,
    AudioNotFoundException,
    ScriptNotFoundException,
    FontNotFoundException,
    InvalidConfigurationError,
    ScriptValidationError,
    ValueOutOfRangeError
)
from constants import (
    MIN_FPS, MAX_FPS,
    MIN_TRANSPARENCY, MAX_TRANSPARENCY,
    MIN_ZOOM_RATIO, MAX_ZOOM_RATIO,
    IMAGE_FORMAT_PNG, IMAGE_FORMAT_JPG, IMAGE_FORMAT_JPEG, IMAGE_FORMAT_GIF,
    AUDIO_FORMAT_MP3,
    VIDEO_FORMAT_MP4
)

logger = get_logger(__name__)


# ============================================================================
# 资源路径验证 / Resource Path Validation
# ============================================================================

def validate_file_exists(file_path: str, resource_type: str = "文件") -> bool:
    """
    验证文件是否存在 / Validate if file exists

    Args:
        file_path: 文件路径
        resource_type: 资源类型名称（用于错误消息）

    Returns:
        bool: 文件是否存在

    Raises:
        ResourceNotFoundException: 如果文件不存在
    """
    if not file_path:
        return False

    path = Path(file_path)
    if not path.exists():
        logger.warning(f"{resource_type}不存在: {file_path}")
        return False

    if not path.is_file():
        logger.warning(f"{resource_type}不是文件: {file_path}")
        return False

    return True


def validate_directory_exists(dir_path: str) -> bool:
    """
    验证目录是否存在 / Validate if directory exists

    Args:
        dir_path: 目录路径

    Returns:
        bool: 目录是否存在
    """
    if not dir_path:
        return False

    path = Path(dir_path)
    return path.exists() and path.is_dir()


def validate_image_file(image_path: str) -> bool:
    """
    验证图片文件是否存在且格式正确 / Validate image file exists and has correct format

    Args:
        image_path: 图片文件路径

    Returns:
        bool: 图片文件是否有效
    """
    if not validate_file_exists(image_path, "图片文件"):
        return False

    # 检查文件扩展名
    valid_extensions = {IMAGE_FORMAT_PNG, IMAGE_FORMAT_JPG, IMAGE_FORMAT_JPEG, IMAGE_FORMAT_GIF, '.webp'}
    ext = Path(image_path).suffix.lower()

    if ext not in valid_extensions:
        logger.warning(f"不支持的图片格式: {image_path} (扩展名: {ext})")
        return False

    return True


def validate_audio_file(audio_path: str) -> bool:
    """
    验证音频文件是否存在且格式正确 / Validate audio file exists and has correct format

    Args:
        audio_path: 音频文件路径

    Returns:
        bool: 音频文件是否有效
    """
    if not validate_file_exists(audio_path, "音频文件"):
        return False

    # 检查文件扩展名
    valid_extensions = {AUDIO_FORMAT_MP3, '.wav', '.m4a', '.aac', '.flac', '.ogg'}
    ext = Path(audio_path).suffix.lower()

    if ext not in valid_extensions:
        logger.warning(f"不支持的音频格式: {audio_path} (扩展名: {ext})")
        return False

    return True


# ============================================================================
# 脚本资源验证 / Script Resource Validation
# ============================================================================

def validate_script_resources(script_path: str) -> Tuple[bool, List[str]]:
    """
    验证脚本中引用的所有资源 / Validate all resources referenced in script

    Args:
        script_path: 脚本文件路径

    Returns:
        Tuple[bool, List[str]]: (是否全部有效, 缺失资源列表)

    Raises:
        ScriptNotFoundException: 如果脚本文件不存在
    """
    if not validate_file_exists(script_path, "脚本文件"):
        raise ScriptNotFoundException(script_path)

    logger.info(f"开始验证脚本资源: {script_path}")

    missing_resources: Set[str] = set()

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"YAML解析错误: {e}")
        raise

    if not script_data or "场景" not in script_data:
        logger.error("脚本文件缺少'场景'字段")
        return False, ["脚本结构无效：缺少'场景'字段"]

    scenarios = script_data.get("场景", []) or []
    logger.info(f"脚本包含 {len(scenarios)} 个场景")

    for scenario_idx, scenario in enumerate(scenarios, 1):
        scenario_name = scenario.get("名字", f"场景{scenario_idx}")
        logger.debug(f"验证场景 {scenario_idx}: {scenario_name}")

        # 验证背景图片
        background = scenario.get("背景")
        if background:
            if isinstance(background, list):
                # 背景是GIF帧序列
                for bg_frame in background:
                    if not validate_image_file(bg_frame):
                        missing_resources.add(bg_frame)
            else:
                # 单个背景图片
                if not validate_image_file(background):
                    missing_resources.add(background)
        else:
            logger.warning(f"场景 {scenario_name} 没有指定背景")

        # 验证场景BGM
        scenario_bgm = scenario.get("背景音乐")
        if scenario_bgm and not validate_audio_file(scenario_bgm):
            missing_resources.add(scenario_bgm)

        # 验证角色资源
        characters = scenario.get("角色", []) or []
        logger.debug(f"场景 {scenario_name} 包含 {len(characters)} 个角色")

        for char in characters:
            char_name = char.get("名字", "未命名角色")
            char_image = char.get("素材")

            if char_image:
                if not validate_image_file(char_image):
                    missing_resources.add(char_image)
                    logger.debug(f"角色 {char_name} 的素材缺失: {char_image}")
            else:
                logger.warning(f"角色 {char_name} 没有指定素材")

        # 验证活动资源
        activities = scenario.get("活动", []) or []
        logger.debug(f"场景 {scenario_name} 包含 {len(activities)} 个活动")

        for activity_idx, activity in enumerate(activities, 1):
            activity_name = activity.get("名字", f"活动{activity_idx}")

            # 验证活动BGM
            activity_bgm = activity.get("背景音乐")
            if activity_bgm and not validate_audio_file(activity_bgm):
                missing_resources.add(activity_bgm)

            # 验证字幕音频
            subtitles = activity.get("字幕", []) or []
            if isinstance(subtitles, str):
                # 字幕文件路径
                if not validate_file_exists(subtitles, "字幕文件"):
                    missing_resources.add(subtitles)
            elif isinstance(subtitles, list):
                for subtitle in subtitles:
                    if isinstance(subtitle, list) and len(subtitle) >= 4:
                        audio_path = subtitle[3]
                        if audio_path and not validate_audio_file(audio_path):
                            missing_resources.add(audio_path)

                    # 检查是否有GIF素材（索引5）
                    if isinstance(subtitle, list) and len(subtitle) >= 6:
                        gif_path = subtitle[5]
                        if gif_path and not validate_image_file(gif_path):
                            missing_resources.add(gif_path)

            # 验证动作资源
            actions = activity.get("动作", []) or []
            for action in actions:
                action_name = action.get("名称", "未命名动作")

                # GIF动作
                if action_name == "gif":
                    gif_material = action.get("素材")
                    if gif_material and not validate_image_file(gif_material):
                        missing_resources.add(gif_material)

                # 更新动作可能包含新的素材
                if action_name == "更新":
                    new_material = action.get("素材")
                    if new_material and not validate_image_file(new_material):
                        missing_resources.add(new_material)

    missing_list = sorted(list(missing_resources))

    if missing_list:
        logger.warning(f"发现 {len(missing_list)} 个缺失的资源文件")
        for resource in missing_list[:10]:  # 只显示前10个
            logger.warning(f"  - {resource}")
        if len(missing_list) > 10:
            logger.warning(f"  ... 还有 {len(missing_list) - 10} 个")
        return False, missing_list
    else:
        logger.info("所有资源验证通过！")
        return True, []


# ============================================================================
# 配置验证 / Configuration Validation
# ============================================================================

def validate_config(config_data: Dict[str, Any]) -> List[str]:
    """
    验证配置参数 / Validate configuration parameters

    Args:
        config_data: 配置字典

    Returns:
        List[str]: 验证错误列表（空列表表示全部有效）
    """
    errors = []

    # 验证FPS
    fps = config_data.get("fps")
    if fps is not None:
        if not isinstance(fps, (int, float)):
            errors.append(f"FPS必须是数字，当前值: {fps}")
        elif fps < MIN_FPS or fps > MAX_FPS:
            errors.append(f"FPS必须在 {MIN_FPS}-{MAX_FPS} 之间，当前值: {fps}")

    # 验证分辨率
    width = config_data.get("g_width")
    height = config_data.get("g_height")

    if width is not None and (not isinstance(width, int) or width <= 0):
        errors.append(f"宽度必须是正整数，当前值: {width}")

    if height is not None and (not isinstance(height, int) or height <= 0):
        errors.append(f"高度必须是正整数，当前值: {height}")

    # 验证字体大小
    font_size = config_data.get("font_size")
    if font_size is not None and (not isinstance(font_size, int) or font_size <= 0):
        errors.append(f"字体大小必须是正整数，当前值: {font_size}")

    # 验证字体文件
    font = config_data.get("font")
    if font and not validate_file_exists(font, "字体文件"):
        errors.append(f"字体文件不存在: {font}")

    # 验证输出目录
    output_dir = config_data.get("output_dir")
    if output_dir:
        output_path = Path(output_dir)
        if output_path.exists() and not output_path.is_dir():
            errors.append(f"输出路径不是目录: {output_dir}")

    # 验证素材目录
    sucai_dir = config_data.get("sucai_dir")
    if sucai_dir and not validate_directory_exists(sucai_dir):
        errors.append(f"素材目录不存在: {sucai_dir}")

    # 验证TTS引擎
    tts_engine = config_data.get("tts_engine")
    valid_engines = {"xunfei", "chat", "ttspro"}
    if tts_engine and tts_engine not in valid_engines:
        errors.append(f"不支持的TTS引擎: {tts_engine}，有效值: {', '.join(valid_engines)}")

    return errors


def validate_character_properties(char_data: Dict[str, Any]) -> List[str]:
    """
    验证角色属性 / Validate character properties

    Args:
        char_data: 角色数据字典

    Returns:
        List[str]: 验证错误列表
    """
    errors = []
    char_name = char_data.get("名字", "未命名角色")

    # 验证位置
    position = char_data.get("位置")
    if position:
        if not isinstance(position, list) or len(position) != 2:
            errors.append(f"角色 {char_name} 的位置格式错误，应为 [x, y]")
        else:
            for i, coord in enumerate(position):
                coord_name = "X" if i == 0 else "Y"
                if not isinstance(coord, (int, float)):
                    errors.append(f"角色 {char_name} 的{coord_name}坐标必须是数字")

    # 验证大小
    size = char_data.get("大小")
    if size:
        if not isinstance(size, list) or len(size) != 2:
            errors.append(f"角色 {char_name} 的大小格式错误，应为 [width, height]")
        else:
            for i, dim in enumerate(size):
                dim_name = "宽度" if i == 0 else "高度"
                if not isinstance(dim, (int, float)) or dim <= 0:
                    errors.append(f"角色 {char_name} 的{dim_name}必须是正数")

    # 验证透明度
    transparency = char_data.get("透明度")
    if transparency is not None:
        if not isinstance(transparency, (int, float)):
            errors.append(f"角色 {char_name} 的透明度必须是数字")
        elif transparency < MIN_TRANSPARENCY or transparency > MAX_TRANSPARENCY:
            errors.append(f"角色 {char_name} 的透明度必须在 {MIN_TRANSPARENCY}-{MAX_TRANSPARENCY} 之间")

    # 验证图层
    layer = char_data.get("图层")
    if layer is not None and not isinstance(layer, int):
        errors.append(f"角色 {char_name} 的图层必须是整数")

    return errors


# ============================================================================
# 完整性验证 / Comprehensive Validation
# ============================================================================

def validate_all(
    script_path: str,
    config_data: Optional[Dict[str, Any]] = None,
    strict: bool = False
) -> Tuple[bool, List[str]]:
    """
    完整验证所有资源和配置 / Comprehensive validation of all resources and configuration

    Args:
        script_path: 脚本文件路径
        config_data: 配置数据（可选）
        strict: 严格模式（如果为True，任何警告都会导致验证失败）

    Returns:
        Tuple[bool, List[str]]: (验证是否通过, 错误/警告列表)
    """
    logger.info("开始完整性验证")
    all_errors = []

    # 验证脚本资源
    try:
        resources_valid, missing_resources = validate_script_resources(script_path)
        if not resources_valid:
            all_errors.extend([f"缺失资源: {r}" for r in missing_resources])
    except Exception as e:
        logger.error(f"脚本资源验证失败: {e}")
        all_errors.append(f"脚本验证错误: {str(e)}")
        return False, all_errors

    # 验证配置
    if config_data:
        config_errors = validate_config(config_data)
        if config_errors:
            all_errors.extend([f"配置错误: {e}" for e in config_errors])

    # 判断是否通过
    if all_errors:
        logger.error(f"验证失败，发现 {len(all_errors)} 个问题")
        return False, all_errors
    else:
        logger.info("完整性验证通过！")
        return True, []


def validate_and_raise(
    script_path: str,
    config_data: Optional[Dict[str, Any]] = None,
    strict: bool = False
) -> None:
    """
    验证并在失败时抛出异常 / Validate and raise exception on failure

    Args:
        script_path: 脚本文件路径
        config_data: 配置数据（可选）
        strict: 严格模式

    Raises:
        ScriptValidationError: 如果验证失败
    """
    valid, errors = validate_all(script_path, config_data, strict)

    if not valid:
        raise ScriptValidationError(errors, script_path)


# ============================================================================
# 安全路径验证 / Safe Path Validation
# ============================================================================

def validate_safe_path(file_path: str, base_dir: str) -> bool:
    """
    验证路径是否在允许的基础目录内（防止路径遍历攻击）
    Validate path is within allowed base directory (prevent path traversal attacks)

    Args:
        file_path: 要验证的文件路径
        base_dir: 允许的基础目录

    Returns:
        bool: 路径是否安全
    """
    try:
        resolved_path = Path(file_path).resolve()
        resolved_base = Path(base_dir).resolve()

        # 检查路径是否以基础目录开头
        return str(resolved_path).startswith(str(resolved_base))
    except Exception as e:
        logger.warning(f"路径验证失败: {file_path}, 错误: {e}")
        return False


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符 / Sanitize filename by removing unsafe characters

    Args:
        filename: 原始文件名

    Returns:
        str: 清理后的文件名
    """
    # 移除路径分隔符和其他不安全字符
    unsafe_chars = ['/', '\\', '..', '\0', '\n', '\r']
    sanitized = filename

    for char in unsafe_chars:
        sanitized = sanitized.replace(char, '_')

    return sanitized

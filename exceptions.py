"""
自定义异常类 / Custom Exception Classes

本文件定义了MovieMaker项目中使用的所有自定义异常
This file defines all custom exceptions used in the MovieMaker project
"""

from typing import Optional, List, Any


# ============================================================================
# 基础异常类 / Base Exception Classes
# ============================================================================

class MovieMakerException(Exception):
    """
    MovieMaker项目的基础异常类 / Base exception class for MovieMaker project
    所有自定义异常都应继承此类
    """
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# ============================================================================
# 资源相关异常 / Resource Related Exceptions
# ============================================================================

class ResourceNotFoundException(MovieMakerException):
    """
    资源文件未找到异常 / Resource file not found exception
    """
    def __init__(self, resource_path: str, resource_type: str = "file"):
        message = f"{resource_type}未找到: {resource_path}"
        details = {
            "resource_path": resource_path,
            "resource_type": resource_type
        }
        super().__init__(message, details)
        self.resource_path = resource_path
        self.resource_type = resource_type


class ImageNotFoundException(ResourceNotFoundException):
    """图片文件未找到异常 / Image file not found exception"""
    def __init__(self, image_path: str):
        super().__init__(image_path, "图片文件")


class AudioNotFoundException(ResourceNotFoundException):
    """音频文件未找到异常 / Audio file not found exception"""
    def __init__(self, audio_path: str):
        super().__init__(audio_path, "音频文件")

        
class VideoNotFoundException(ResourceNotFoundException):
    """视频文件未找到异常 / Video file not found exception"""
    def __init__(self, video_path: str):
        super().__init__(video_path, "视频文件")


class ScriptNotFoundException(ResourceNotFoundException):
    """脚本文件未找到异常 / Script file not found exception"""
    def __init__(self, script_path: str):
        super().__init__(script_path, "脚本文件")


class FontNotFoundException(ResourceNotFoundException):
    """字体文件未找到异常 / Font file not found exception"""
    def __init__(self, font_path: str):
        super().__init__(font_path, "字体文件")


class MissingResourcesException(MovieMakerException):
    """
    缺少多个资源文件异常 / Missing multiple resources exception
    """
    def __init__(self, missing_resources: List[str]):
        message = f"缺少 {len(missing_resources)} 个资源文件"
        details = {"missing_resources": missing_resources}
        super().__init__(message, details)
        self.missing_resources = missing_resources

    def __str__(self) -> str:
        resource_list = "\n  - ".join(self.missing_resources)
        return f"{self.message}:\n  - {resource_list}"


# ============================================================================
# 角色相关异常 / Character Related Exceptions
# ============================================================================

class CharacterException(MovieMakerException):
    """角色相关异常基类 / Base class for character-related exceptions"""
    pass


class CharacterNotFoundError(CharacterException):
    """
    角色未找到异常 / Character not found exception
    """
    def __init__(self, char_name: str, render_index: Optional[float] = None, activity_name: Optional[str] = None):
        message = f"角色【{char_name}】不存在"
        details = {"char_name": char_name}
        if render_index is not None:
            message += f", 渲染顺序：{render_index}, 活动：{activity_name}"
            details["render_index"] = render_index
        super().__init__(message, details)
        self.char_name = char_name
        self.render_index = render_index


class InvalidCharacterPropertyError(CharacterException):
    """
    角色属性无效异常 / Invalid character property exception
    """
    def __init__(self, char_name: str, property_name: str, property_value: Any, reason: str = ""):
        message = f"角色【{char_name}】的属性【{property_name}】值无效: {property_value}"
        if reason:
            message += f" - {reason}"
        details = {
            "char_name": char_name,
            "property_name": property_name,
            "property_value": property_value,
            "reason": reason
        }
        super().__init__(message, details)


class InsufficientCharactersError(CharacterException):
    """
    角色数量不足异常 / Insufficient characters exception
    """
    def __init__(self, action_name: str, required: int, actual: int):
        message = f"动作【{action_name}】需要至少 {required} 个角色，实际只有 {actual} 个"
        details = {
            "action_name": action_name,
            "required": required,
            "actual": actual
        }
        super().__init__(message, details)


# ============================================================================
# 配置相关异常 / Configuration Related Exceptions
# ============================================================================

class ConfigurationException(MovieMakerException):
    """配置相关异常基类 / Base class for configuration-related exceptions"""
    pass


class InvalidConfigurationError(ConfigurationException):
    """
    配置无效异常 / Invalid configuration exception
    """
    def __init__(self, config_key: str, config_value: Any, reason: str = ""):
        message = f"配置项【{config_key}】值无效: {config_value}"
        if reason:
            message += f" - {reason}"
        details = {
            "config_key": config_key,
            "config_value": config_value,
            "reason": reason
        }
        super().__init__(message, details)


class MissingConfigurationError(ConfigurationException):
    """
    缺少必需配置异常 / Missing required configuration exception
    """
    def __init__(self, config_key: str):
        message = f"缺少必需的配置项: {config_key}"
        details = {"config_key": config_key}
        super().__init__(message, details)


# ============================================================================
# 脚本相关异常 / Script Related Exceptions
# ============================================================================

class ScriptException(MovieMakerException):
    """脚本相关异常基类 / Base class for script-related exceptions"""
    pass


class ScriptValidationError(ScriptException):
    """
    脚本验证错误 / Script validation error
    """
    def __init__(self, validation_errors: List[str], script_path: Optional[str] = None):
        message = f"脚本验证失败，发现 {len(validation_errors)} 个错误"
        details = {
            "validation_errors": validation_errors,
            "error_count": len(validation_errors)
        }
        if script_path:
            details["script_path"] = script_path
        super().__init__(message, details)
        self.validation_errors = validation_errors

    def __str__(self) -> str:
        errors_list = "\n  - ".join(self.validation_errors)
        return f"{self.message}:\n  - {errors_list}"


class ScriptParseError(ScriptException):
    """
    脚本解析错误 / Script parse error
    """
    def __init__(self, script_path: str, parse_error: str):
        message = f"脚本解析失败: {script_path}"
        details = {
            "script_path": script_path,
            "parse_error": parse_error
        }
        super().__init__(message, details)


class InvalidScriptStructureError(ScriptException):
    """
    脚本结构无效异常 / Invalid script structure exception
    """
    def __init__(self, expected_field: str, actual_structure: Optional[str] = None):
        message = f"脚本结构无效，缺少必需字段: {expected_field}"
        details = {"expected_field": expected_field}
        if actual_structure:
            details["actual_structure"] = actual_structure
        super().__init__(message, details)


# ============================================================================
# 场景相关异常 / Scenario Related Exceptions
# ============================================================================

class ScenarioException(MovieMakerException):
    """场景相关异常基类 / Base class for scenario-related exceptions"""
    pass


class ScenarioNotFoundError(ScenarioException):
    """
    场景未找到异常 / Scenario not found exception
    """
    def __init__(self, scenario_name: str):
        message = f"场景【{scenario_name}】不存在"
        details = {"scenario_name": scenario_name}
        super().__init__(message, details)


class InvalidScenarioError(ScenarioException):
    """
    场景配置无效异常 / Invalid scenario exception
    """
    def __init__(self, scenario_name: str, reason: str):
        message = f"场景【{scenario_name}】配置无效: {reason}"
        details = {
            "scenario_name": scenario_name,
            "reason": reason
        }
        super().__init__(message, details)


# ============================================================================
# 动作相关异常 / Action Related Exceptions
# ============================================================================

class ActionException(MovieMakerException):
    """动作相关异常基类 / Base class for action-related exceptions"""
    pass


class UnsupportedActionError(ActionException):
    """
    不支持的动作类型异常 / Unsupported action type exception
    """
    def __init__(self, action_name: str, supported_actions: Optional[List[str]] = None):
        message = f"不支持的动作类型: {action_name}"
        details = {"action_name": action_name}
        if supported_actions:
            message += f"，支持的动作类型: {', '.join(supported_actions)}"
            details["supported_actions"] = supported_actions
        super().__init__(message, details)


class InvalidActionParameterError(ActionException):
    """
    动作参数无效异常 / Invalid action parameter exception
    """
    def __init__(self, action_name: str, parameter_name: str, parameter_value: Any, reason: str = ""):
        message = f"动作【{action_name}】的参数【{parameter_name}】无效: {parameter_value}"
        if reason:
            message += f" - {reason}"
        details = {
            "action_name": action_name,
            "parameter_name": parameter_name,
            "parameter_value": parameter_value,
            "reason": reason
        }
        super().__init__(message, details)


class MissingActionParameterError(ActionException):
    """
    缺少动作参数异常 / Missing action parameter exception
    """
    def __init__(self, action_name: str, parameter_name: str):
        message = f"动作【{action_name}】缺少必需参数: {parameter_name}"
        details = {
            "action_name": action_name,
            "parameter_name": parameter_name
        }
        super().__init__(message, details)


class ActionExecutionError(ActionException):
    """
    动作执行错误 / Action execution error
    """
    def __init__(self, action_name: str, error_message: str, render_index: Optional[float] = None):
        message = f"动作【{action_name}】执行失败: {error_message}"
        details = {
            "action_name": action_name,
            "error_message": error_message
        }
        if render_index is not None:
            details["render_index"] = render_index
        super().__init__(message, details)


# ============================================================================
# 视频处理相关异常 / Video Processing Related Exceptions
# ============================================================================

class VideoException(MovieMakerException):
    """视频处理相关异常基类 / Base class for video processing exceptions"""
    pass


class VideoGenerationError(VideoException):
    """
    视频生成错误 / Video generation error
    """
    def __init__(self, error_message: str, video_path: Optional[str] = None):
        message = f"视频生成失败: {error_message}"
        details = {"error_message": error_message}
        if video_path:
            details["video_path"] = video_path
        super().__init__(message, details)


class VideoConcatenationError(VideoException):
    """
    视频拼接错误 / Video concatenation error
    """
    def __init__(self, error_message: str, video_count: Optional[int] = None):
        message = f"视频拼接失败: {error_message}"
        details = {"error_message": error_message}
        if video_count is not None:
            details["video_count"] = video_count
        super().__init__(message, details)


class InvalidVideoParameterError(VideoException):
    """
    视频参数无效异常 / Invalid video parameter exception
    """
    def __init__(self, parameter_name: str, parameter_value: Any, reason: str = ""):
        message = f"视频参数【{parameter_name}】无效: {parameter_value}"
        if reason:
            message += f" - {reason}"
        details = {
            "parameter_name": parameter_name,
            "parameter_value": parameter_value,
            "reason": reason
        }
        super().__init__(message, details)


# ============================================================================
# 音频处理相关异常 / Audio Processing Related Exceptions
# ============================================================================

class AudioException(MovieMakerException):
    """音频处理相关异常基类 / Base class for audio processing exceptions"""
    pass


class TTSException(AudioException):
    """
    文字转语音异常 / Text-to-speech exception
    """
    def __init__(self, text: str, error_message: str, engine: Optional[str] = None):
        message = f"TTS转换失败: {error_message}"
        details = {
            "text": text,
            "error_message": error_message
        }
        if engine:
            message += f" (引擎: {engine})"
            details["engine"] = engine
        super().__init__(message, details)


class AudioProcessingError(AudioException):
    """
    音频处理错误 / Audio processing error
    """
    def __init__(self, audio_path: str, error_message: str):
        message = f"音频处理失败: {audio_path} - {error_message}"
        details = {
            "audio_path": audio_path,
            "error_message": error_message
        }
        super().__init__(message, details)


class UnsupportedAudioFormatError(AudioException):
    """
    不支持的音频格式异常 / Unsupported audio format exception
    """
    def __init__(self, audio_path: str, format_type: str):
        message = f"不支持的音频格式: {format_type} ({audio_path})"
        details = {
            "audio_path": audio_path,
            "format_type": format_type
        }
        super().__init__(message, details)


# ============================================================================
# 图像处理相关异常 / Image Processing Related Exceptions
# ============================================================================

class ImageException(MovieMakerException):
    """图像处理相关异常基类 / Base class for image processing exceptions"""
    pass


class ImageProcessingError(ImageException):
    """
    图像处理错误 / Image processing error
    """
    def __init__(self, image_path: str, error_message: str):
        message = f"图像处理失败: {image_path} - {error_message}"
        details = {
            "image_path": image_path,
            "error_message": error_message
        }
        super().__init__(message, details)


class InvalidImageDimensionsError(ImageException):
    """
    图像尺寸无效异常 / Invalid image dimensions exception
    """
    def __init__(self, image_path: str, width: int, height: int, reason: str = ""):
        message = f"图像尺寸无效: {image_path} ({width}x{height})"
        if reason:
            message += f" - {reason}"
        details = {
            "image_path": image_path,
            "width": width,
            "height": height,
            "reason": reason
        }
        super().__init__(message, details)


class UnsupportedImageFormatError(ImageException):
    """
    不支持的图像格式异常 / Unsupported image format exception
    """
    def __init__(self, image_path: str, format_type: str):
        message = f"不支持的图像格式: {format_type} ({image_path})"
        details = {
            "image_path": image_path,
            "format_type": format_type
        }
        super().__init__(message, details)


# ============================================================================
# 验证相关异常 / Validation Related Exceptions
# ============================================================================

class ValidationException(MovieMakerException):
    """验证相关异常基类 / Base class for validation exceptions"""
    pass


class ValueOutOfRangeError(ValidationException):
    """
    值超出范围异常 / Value out of range exception
    """
    def __init__(self, value_name: str, value: Any, min_value: Any, max_value: Any):
        message = f"值【{value_name}】超出范围: {value} (有效范围: {min_value} - {max_value})"
        details = {
            "value_name": value_name,
            "value": value,
            "min_value": min_value,
            "max_value": max_value
        }
        super().__init__(message, details)


class InvalidTypeError(ValidationException):
    """
    类型无效异常 / Invalid type exception
    """
    def __init__(self, value_name: str, expected_type: str, actual_type: str):
        message = f"类型错误【{value_name}】: 期望 {expected_type}, 实际 {actual_type}"
        details = {
            "value_name": value_name,
            "expected_type": expected_type,
            "actual_type": actual_type
        }
        super().__init__(message, details)


# ============================================================================
# 字幕相关异常 / Subtitle Related Exceptions
# ============================================================================

class SubtitleException(MovieMakerException):
    """字幕相关异常基类 / Base class for subtitle exceptions"""
    pass


class InvalidSubtitleFormatError(SubtitleException):
    """
    字幕格式无效异常 / Invalid subtitle format exception
    """
    def __init__(self, subtitle_data: Any, reason: str = ""):
        message = f"字幕格式无效: {subtitle_data}"
        if reason:
            message += f" - {reason}"
        details = {
            "subtitle_data": subtitle_data,
            "reason": reason
        }
        super().__init__(message, details)


class SubtitleTimingError(SubtitleException):
    """
    字幕时间错误 / Subtitle timing error
    """
    def __init__(self, start_time: float, end_time: float, reason: str = ""):
        message = f"字幕时间错误: 开始={start_time}, 结束={end_time}"
        if reason:
            message += f" - {reason}"
        details = {
            "start_time": start_time,
            "end_time": end_time,
            "reason": reason
        }
        super().__init__(message, details)

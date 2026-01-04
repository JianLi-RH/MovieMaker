"""
常量定义 / Constants Definition

本文件包含项目中使用的所有魔法数字和常量配置
This file contains all magic numbers and constant configurations used in the project
"""

# ============================================================================
# 图像处理常量 / Image Processing Constants
# ============================================================================

# 图像尺寸相关 / Image Size Related
MAX_IMAGE_PIXELS = 7680000  # PIL 最大图片像素限制
IMAGE_CROP_PERCENTAGE = 0.3  # 默认裁剪百分比
IMAGE_PADDING = 100  # 图片边距（像素）
IMAGE_EDGE_THRESHOLD = 50  # 边缘检测阈值（像素）

# 文字和字幕相关 / Text and Subtitle Related
DEFAULT_FONT_SIZE = 50  # 默认字体大小
SUBTITLE_FONT_SIZE_SMALL = 30  # 小字体大小
SUBTITLE_BOTTOM_MARGIN = 20  # 字幕距离底部边距
SUBTITLE_BORDER_PADDING = 5  # 字幕边框内边距
SUBTITLE_NON_CURRENT_SCALE = 0.8  # 非当前字幕的缩放比例
SUBTITLE_LINE_SPACING_RATIO = 0.8  # 字幕行间距比例
MAX_SUBTITLE_LINES = 3  # 最多同时显示的字幕行数
NAME_TAG_MAX_SIZE = 80  # 角色名牌最大字体大小
NAME_TAG_SIZE_RATIO = 0.25  # 角色名牌字体大小比例（相对于角色宽度）
NAME_TAG_BORDER_WIDTH = 1  # 角色名牌边框宽度

# 透明度和光线 / Transparency and Light
DEFAULT_TRANSPARENCY = 1.0  # 默认透明度（完全不透明）
FULL_TRANSPARENT = 0.0  # 完全透明
REDUCE_LIGHT_VALUE = 100  # 降低亮度值（用于暗化效果）

# 图像变化和动画 / Image Transform and Animation
DEFAULT_ZOOM_RATIO = 1.0  # 默认缩放比例
CENTER_POSITION = "中心"  # 默认中心位置
ROTATE_180 = 180  # 180度旋转（上下翻转）
ROTATE_PREFIX = "rotate_"  # 旋转图片文件前缀

# ============================================================================
# 视频处理常量 / Video Processing Constants
# ============================================================================

# 默认FPS设置 / Default FPS Settings
DEFAULT_FPS = 24  # 默认帧率
MIN_FPS = 1  # 最小帧率
MAX_FPS = 120  # 最大帧率

# 音频相关 / Audio Related
DEFAULT_AUDIO_FACTOR = 0.2  # 背景音乐音量衰减因子
AUDIO_START_OFFSET = 0  # 音频开始偏移（毫秒）

# 水印相关 / Watermark Related
DEFAULT_WATERMARK_SIZE = [120, 120]  # 默认水印尺寸

# ============================================================================
# 动作和动画常量 / Action and Animation Constants
# ============================================================================

# 打斗动作幅度 / Fight Action Amplitude
FIGHT_AMPLITUDE_SMALL = 50  # 小幅度
FIGHT_AMPLITUDE_MEDIUM = 100  # 中幅度
FIGHT_AMPLITUDE_LARGE = 200  # 大幅度
FIGHT_RANDOM_POSITIONS = 3  # 打斗动作随机位置数量

# 镜头移动 / Camera Movement
CAMERA_DEFAULT_FROM_RATIO = 1.0  # 镜头默认起始比例
CAMERA_CENTER_OFFSET = 0.5  # 镜头中心偏移比例

# 行进动作 / Walk Action
WALK_JUMP_OFFSET = 5  # 跳跃偏移像素
WALK_SHAKE_ROTATION = 45  # 眩晕旋转角度
WALK_ROTATION_FRACTION = 4  # 旋转分数（用于计算每帧旋转角度）
WALK_CLOSE_UP_RATIO = 0.5  # 近景拉近比例

# 转场动作 / Scene Transition
TRANSITION_ROTATION_STEP_DIVISOR = 2  # 转场旋转步长除数
TRANSITION_SIZE_STEP_DIVISOR = 2  # 转场尺寸步长除数

# ============================================================================
# 线程和并发常量 / Threading and Concurrency Constants
# ============================================================================

MAX_TTS_WORKERS = 10  # 最大TTS工作线程数
TTS_QUEUE_SIZE = 10  # TTS任务队列大小
MIN_PARALLEL_ACTIONS = 2  # 最小并行动作数量（触发delay模式）

# ============================================================================
# 文件和路径相关 / File and Path Related
# ============================================================================

# 默认文件路径 / Default File Paths
DEFAULT_SCRIPT_PATH = 'script.yaml'  # 默认脚本文件路径
DEFAULT_FONT_PATH = 'fonts/QingNiaoHuaGuangJianMeiHei/QingNiaoHuaGuangJianMeiHei-2.ttf'  # 默认字体路径

# GIF相关 / GIF Related
GIF_PREFIX = "gif"  # GIF类型前缀
GIF_LOOP_COUNT = 0  # GIF循环次数（0表示无限循环）

# ============================================================================
# 颜色定义 / Color Definitions
# ============================================================================

COLOR_WHITE = (255, 255, 255)  # 白色
COLOR_BLACK = (0, 0, 0)  # 黑色
COLOR_CYAN = '#008B8B'  # 青色

# ============================================================================
# 角色和位置相关 / Character and Position Related
# ============================================================================

# 位置范围 / Position Range
POSITION_MIN_RATIO = -1.0  # 位置最小比例
POSITION_MAX_RATIO = 1.0  # 位置最大比例
POSITION_RATIO_THRESHOLD = 1.0  # 位置比例阈值（区分像素和比例）

# 角色默认值 / Character Defaults
DEFAULT_CHARACTER_SIZE_RATIO = 4  # 默认角色尺寸比例
DEFAULT_LAYER_INDEX = 0  # 默认图层索引
DEFAULT_DISPLAY = False  # 默认不显示

# ============================================================================
# 场景相关常量 / Scenario Related Constants
# ============================================================================

DEFAULT_SCENARIO_RATIO = 1.0  # 默认场景显示比例
SCENARIO_FOCUS_CENTER = "中心"  # 场景默认焦点

# ============================================================================
# 字幕样式 / Subtitle Styles
# ============================================================================

SUBTITLE_STYLE_NORMAL = "normal"  # 普通样式
SUBTITLE_STYLE_BOTTOM = "bottom"  # 底部样式
SUBTITLE_STYLE_TOP = "top"  # 顶部样式
SUBTITLE_STYLE_MIDDLE = "middle"  # 中间样式
SUBTITLE_STYLE_LIST = "list"  # 列表样式（最多显示3行）

# ============================================================================
# 动作类型常量 / Action Type Constants
# ============================================================================

ACTION_DISPLAY = "显示"  # 显示动作
ACTION_DISAPPEAR = "消失"  # 消失动作
ACTION_WALK = "行进"  # 行进动作
ACTION_FIGHT = "打斗"  # 打斗动作
ACTION_CAMERA = "镜头"  # 镜头动作
ACTION_GIF = "gif"  # GIF动作
ACTION_ROTATE = "转身"  # 转身动作
ACTION_TRANSITION = "转场"  # 转场动作
ACTION_BGM = "BGM"  # 背景音乐动作
ACTION_UPDATE = "更新"  # 更新动作
ACTION_QUEUE = "队列"  # 队列动作
ACTION_STILL = "静止"  # 静止动作

# ============================================================================
# 旋转方向常量 / Rotation Direction Constants
# ============================================================================

ROTATION_LEFT_RIGHT = "左右"  # 左右镜像
ROTATION_UP_DOWN = "上下"  # 上下镜像

# ============================================================================
# 动作方式常量 / Movement Style Constants
# ============================================================================

MOVEMENT_NATURAL = "自然"  # 自然移动
MOVEMENT_JUMP = "跳跃"  # 跳跃移动
MOVEMENT_ROTATE = "旋转"  # 旋转移动
MOVEMENT_DIZZY = "眩晕"  # 眩晕移动

# ============================================================================
# 特殊效果常量 / Special Effect Constants
# ============================================================================

EFFECT_CLOSE_UP = "近景"  # 近景特效
EFFECT_SHOCK = "震惊"  # 震惊特效

# ============================================================================
# 错误信息 / Error Messages
# ============================================================================

ERROR_CHARACTER_NOT_FOUND = "角色【{name}】不存在, 渲染顺序：{render_index}"
ERROR_SCRIPT_NOT_FOUND = "必须给出脚本文件"
ERROR_MIN_CHARACTERS_REQUIRED = "打斗动作需要至少两个角色"

# ============================================================================
# 验证范围 / Validation Ranges
# ============================================================================

# 时间相关 / Time Related
MIN_DURATION = 0.0  # 最小持续时间（秒）
MAX_DURATION = 3600.0  # 最大持续时间（秒）

# 比例相关 / Ratio Related
MIN_ZOOM_RATIO = 0.1  # 最小缩放比例
MAX_ZOOM_RATIO = 10.0  # 最大缩放比例

# 透明度范围 / Transparency Range
MIN_TRANSPARENCY = 0.0  # 最小透明度（完全透明）
MAX_TRANSPARENCY = 1.0  # 最大透明度（完全不透明）

# ============================================================================
# 文件格式 / File Formats
# ============================================================================

VIDEO_FORMAT_MP4 = ".mp4"  # MP4视频格式
VIDEO_FORMAT_AVI = ".avi"  # AVI视频格式
AUDIO_FORMAT_MP3 = ".mp3"  # MP3音频格式
IMAGE_FORMAT_PNG = ".png"  # PNG图片格式
IMAGE_FORMAT_JPG = ".jpg"  # JPG图片格式
IMAGE_FORMAT_JPEG = ".jpeg"  # JPEG图片格式
IMAGE_FORMAT_GIF = ".gif"  # GIF图片格式
SCRIPT_FORMAT_YAML = ".yaml"  # YAML脚本格式

# ============================================================================
# 索引和边界值 / Index and Boundary Values
# ============================================================================

FIRST_INDEX = 0  # 第一个索引
INVALID_INDEX = -1  # 无效索引
MIN_CHARACTERS_FOR_FIGHT = 2  # 打斗动作所需最小角色数

# ============================================================================
# 字幕相关索引 / Subtitle Related Indices
# ============================================================================

SUBTITLE_INDEX_START = 0  # 字幕开始时间索引
SUBTITLE_INDEX_END = 1  # 字幕结束时间索引
SUBTITLE_INDEX_TEXT = 2  # 字幕文本索引
SUBTITLE_INDEX_AUDIO = 3  # 字幕音频文件索引
SUBTITLE_INDEX_CHAR = 4  # 字幕角色索引
SUBTITLE_INDEX_GIF = 5  # 字幕GIF索引

# ============================================================================
# 数组位置索引 / Array Position Indices
# ============================================================================

POSITION_INDEX_X = 0  # X坐标索引
POSITION_INDEX_Y = 1  # Y坐标索引
SIZE_INDEX_WIDTH = 0  # 宽度索引
SIZE_INDEX_HEIGHT = 1  # 高度索引

# ============================================================================
# 延迟位置索引 / Delay Position Indices
# ============================================================================

DELAY_POS_POSITION = 0  # 位置
DELAY_POS_SIZE = 1  # 尺寸
DELAY_POS_ROTATE = 2  # 旋转角度
DELAY_POS_IMAGE = 3  # 图片路径

# ============================================================================
# 系统相关 / System Related
# ============================================================================

RANDOM_STRING_LENGTH = 8  # 随机字符串长度
UTF8_ENCODING = 'utf-8'  # UTF-8编码

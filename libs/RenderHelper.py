#!/usr/bin/python3
"""
RenderHelper - Centralized character rendering logic for MovieMaker

This module extracts and consolidates duplicated character rendering patterns
found across activity.py and action modules. It provides a clean API for:
- Single frame character rendering
- Batch frame rendering
- Position-tracked rendering (for animations)
- Static frame replication

Author: MovieMaker Team
"""
import sys
from typing import List, Optional, Tuple, Dict, Any

sys.path.append('../')
from PIL import Image

from logging_config import get_logger
logger = get_logger(__name__)

try:
    import ImageHelper
except ImportError:
    from libs import ImageHelper

try:
    from character import Character
except ImportError:
    from MovieMaker.character import Character


class RenderHelper:
    """Centralized character rendering utilities"""

    @staticmethod
    def render_characters_on_frame(
        image: str,
        char_list: List[Character],
        big_image_obj: Optional[Image.Image] = None,
        gif_index: int = 0,
        save: bool = False
    ) -> Tuple[str, Optional[Image.Image]]:
        """
        Render all visible characters onto a single frame.

        Params:
            image: Path to background image
            char_list: List of Character objects to render
            big_image_obj: Existing PIL Image object to paint on (or None to start fresh)
            gif_index: Index for GIF animation frames
            save: Whether to save the result immediately

        Returns:
            Tuple of (image_path, image_obj)

        Example:
            >>> _, img_obj = RenderHelper.render_characters_on_frame(
            ...     "bg.png", [char1, char2], gif_index=0
            ... )
        """
        logger.debug(f"渲染角色到单帧: image={image}, chars={len(char_list)}, gif_index={gif_index}")

        for char in char_list:
            if RenderHelper.should_render_character(char):
                _, big_image_obj = ImageHelper.paint_char_on_image(
                    char=char,
                    image=image,
                    image_obj=big_image_obj,
                    save=save,
                    gif_index=gif_index
                )

        return image, big_image_obj

    @staticmethod
    def render_characters_on_frames(
        images: List[str],
        char_list: List[Character],
        gif_index_function: Optional[callable] = None
    ) -> None:
        """
        Render characters across multiple frames (frame-by-frame rendering).

        This is the most common rendering pattern, used in walk, talk, fight, etc.
        Each frame gets a fresh render with the current character properties.

        Params:
            images: List of background image paths
            char_list: List of Character objects to render
            gif_index_function: Optional function(i) -> gif_index for custom indexing

        Returns:
            None (saves images directly)

        Example:
            >>> RenderHelper.render_characters_on_frames(
            ...     ["frame1.png", "frame2.png"], [char1, char2]
            ... )
        """
        logger.debug(f"批量渲染角色到 {len(images)} 帧")

        for i in range(len(images)):
            gif_index = gif_index_function(i) if gif_index_function else i
            big_image = None

            for char in char_list:
                if RenderHelper.should_render_character(char):
                    _, big_image = ImageHelper.paint_char_on_image(
                        char=char,
                        image=images[i],
                        image_obj=big_image,
                        save=False,
                        gif_index=gif_index
                    )

            if big_image:
                big_image.save(images[i])
                big_image.close()

    @staticmethod
    def render_with_position_tracking(
        images: List[str],
        delay_positions: List[Dict[str, Any]],
        char_list: List[Character],
        start_index: int = 0,
        gif_index_start: int = 0
    ) -> None:
        """
        Render characters with position tracking arrays (for delay mode animations).

        This handles complex rendering where character positions change per frame
        according to a delay_positions array structure. Used in activity.py delay
        mode and fight.py choreography.

        Params:
            images: List of background image paths
            delay_positions: List of dicts with structure:
                [{"char": Character, "position": [[pos, size, rotate, image?], ...]}, ...]
            char_list: List of all Character objects in scene
            start_index: Starting index in delay_positions (default 0)
            gif_index_start: Starting GIF index (default 0)

        Returns:
            None (saves images directly)

        Example:
            >>> delay_positions = [
            ...     {"char": char1, "position": [[pos1, size1, 0], [pos2, size2, 0]]},
            ...     {"char": char2, "position": [[pos3, size3, 0]]}
            ... ]
            >>> RenderHelper.render_with_position_tracking(
            ...     images, delay_positions, all_chars
            ... )
        """
        logger.debug(f"使用位置跟踪渲染 {len(images)} 帧，共 {len(delay_positions)} 个角色位置")

        for j in range(len(images)):
            big_image = None

            for char in char_list:
                # Skip Characters that are not displayed
                if isinstance(char, Character) and not char.display:
                    continue

                # Find and apply position data for this character
                position_data = RenderHelper.extract_position_data(
                    delay_positions, char, j + start_index
                )

                if position_data:
                    RenderHelper.apply_character_properties(
                        char, position_data, include_image=True
                    )

                # Render the character
                _, big_image = ImageHelper.paint_char_on_image(
                    char=char,
                    image=images[j],
                    image_obj=big_image,
                    save=False,
                    gif_index=j + gif_index_start
                )

            if big_image:
                big_image.save(images[j])
                big_image.close()

    @staticmethod
    def create_static_frame(
        images: List[str],
        char_list: List[Character],
        source_image_index: int = 0,
        gif_index: int = 0
    ) -> None:
        """
        Create a single rendered frame and replicate it across all images.

        Used for static scenes (stop, bgm) where the same frame is repeated
        multiple times with no animation.

        Params:
            images: List of background image paths to populate
            char_list: List of Character objects to render
            source_image_index: Index of source image to render on (default 0)
            gif_index: GIF index to use for rendering (default 0)

        Returns:
            None (saves images directly)

        Example:
            >>> RenderHelper.create_static_frame(
            ...     ["bg1.png", "bg2.png", "bg3.png"], [char1, char2]
            ... )
        """
        logger.debug(f"创建静态帧并复制到 {len(images)} 张图片")

        big_image = None

        # Render all characters onto the first frame
        for char in char_list:
            if RenderHelper.should_render_character(char):
                _, big_image = ImageHelper.paint_char_on_image(
                    image=images[source_image_index],
                    image_obj=big_image,
                    char=char,
                    save=False,
                    gif_index=gif_index
                )

        # Replicate the rendered frame to all images
        if big_image:
            for i in range(len(images)):
                big_image.save(images[i])
            big_image.close()

    @staticmethod
    def apply_character_properties(
        target_char: Character,
        position_data: Tuple,
        include_image: bool = False
    ) -> None:
        """
        Apply position/size/rotate/image properties to a character.

        Params:
            target_char: Character to modify
            position_data: Tuple of (pos, size, rotate[, image])
            include_image: Whether to apply image property (4th element)

        Returns:
            None (modifies character in-place)

        Example:
            >>> RenderHelper.apply_character_properties(
            ...     my_char, ([100, 200], [50, 50], 45), include_image=False
            ... )
        """
        if len(position_data) > 2:
            target_char.pos = position_data[0]
            target_char.size = position_data[1]
            target_char.rotate = position_data[2]

        if include_image and len(position_data) > 3:
            target_char.image = position_data[3]

    @staticmethod
    def extract_position_data(
        delay_positions: List[Dict[str, Any]],
        char: Character,
        frame_index: int
    ) -> Optional[Tuple]:
        """
        Extract position data for a character at a specific frame index.

        Handles array bounds checking and fallback to last known position.

        Params:
            delay_positions: List of position tracking dicts
            char: Character to find position data for
            frame_index: Frame index to extract

        Returns:
            Tuple of (pos, size, rotate[, image]) or None if not found

        Example:
            >>> pos_data = RenderHelper.extract_position_data(
            ...     delay_positions, my_char, frame_idx=5
            ... )
            >>> if pos_data:
            ...     print(f"Position: {pos_data[0]}, Size: {pos_data[1]}")
        """
        char_pos_entry = RenderHelper.find_character_in_positions(char, delay_positions)

        if not char_pos_entry:
            return None

        position_array = char_pos_entry.get("position", [])

        if not position_array:
            logger.warning(f"角色 {char.name} 没有位置信息")
            return None

        # Get position at frame_index, or fallback to last known position
        if len(position_array) > frame_index:
            delay_pos = position_array[frame_index]
        elif len(position_array) > 0:
            delay_pos = position_array[-1]  # Use last known position
            logger.debug(f"角色 {char.name} 使用最后已知位置 (frame {frame_index})")
        else:
            return None

        return delay_pos

    @staticmethod
    def find_character_in_positions(
        char: Character,
        delay_positions: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a character's entry in delay_positions array.

        Params:
            char: Character to search for
            delay_positions: List of position tracking dicts

        Returns:
            Dict with "char" and "position" keys, or None if not found

        Example:
            >>> entry = RenderHelper.find_character_in_positions(my_char, delay_positions)
            >>> if entry:
            ...     positions = entry["position"]
        """
        for char_pos in delay_positions:
            if char == char_pos.get("char"):
                return char_pos

        return None

    @staticmethod
    def should_render_character(char: Character) -> bool:
        """
        Determine if a character should be rendered.

        Params:
            char: Character to check

        Returns:
            True if character should be rendered, False otherwise

        Example:
            >>> if RenderHelper.should_render_character(my_char):
            ...     # render it
        """
        return hasattr(char, 'display') and char.display

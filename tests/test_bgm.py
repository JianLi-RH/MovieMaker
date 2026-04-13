import unittest
from unittest.mock import patch, MagicMock
from actions import bgm
from libs.RenderHelper import RenderHelper

class TestBgmAction(unittest.TestCase):
    @patch('libs.RenderHelper.RenderHelper.create_static_frame')
    def test_bgm_action_calls_create_static_frame(self, mock_render):
        # Given
        images = ["frame1.png", "frame2.png"]
        sorted_char_list = [MagicMock(), MagicMock()]

        # When
        bgm.Do(images, sorted_char_list)

        # Then
        mock_render.assert_called_once_with(images, sorted_char_list)

if __name__ == '__main__':
    unittest.main()

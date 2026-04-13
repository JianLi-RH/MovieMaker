import unittest
from unittest.mock import MagicMock, patch
from actions import stop
from libs.RenderHelper import RenderHelper

class TestStopAction(unittest.TestCase):
    @patch('libs.RenderHelper.RenderHelper.create_static_frame')
    def test_stop_action(self, mock_create_static_frame):
        # Given
        images = ["frame1.png", "frame2.png"]
        sorted_char_list = [MagicMock()]

        # When
        stop.Do(images, sorted_char_list)

        # Then
        mock_create_static_frame.assert_called_once_with(images, sorted_char_list)

if __name__ == '__main__':
    unittest.main()

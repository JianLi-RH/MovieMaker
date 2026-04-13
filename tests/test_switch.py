import unittest
from unittest.mock import MagicMock, patch
from actions import switch
from libs import ImageHelper

class TestSwitchAction(unittest.TestCase):
    @patch('libs.ImageHelper.merge_two_image')
    @patch('actions.switch.get_char')
    def test_switch_action(self, mock_get_char, mock_merge_two_image):
        # Given
        mock_action = MagicMock()
        mock_bg_char = MagicMock()
        mock_char1 = MagicMock()
        mock_char1.display = True

        mock_action.obj.get.side_effect = lambda key, default=None: {
            "背景": "bg_char",
            "方式": "旋转缩小"
        }.get(key, default)
        
        mock_get_char.return_value = mock_bg_char
        mock_action.chars = [mock_bg_char, mock_char1]
        
        # Mocking the return of merge_two_image to be a mock object that has a size attribute and a close method
        mock_image = MagicMock()
        mock_image.size = (100, 100)
        mock_merge_two_image.return_value = (None, mock_image)

        images = ["frame1.png", "frame2.png"]
        sorted_char_list = [mock_bg_char, mock_char1]

        # When
        switch.Do(action=mock_action, images=images, sorted_char_list=sorted_char_list)

        # Then
        self.assertEqual(mock_merge_two_image.call_count, 3)

if __name__ == '__main__':
    unittest.main()

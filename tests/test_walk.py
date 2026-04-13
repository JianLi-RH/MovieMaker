import unittest
from unittest.mock import MagicMock, patch
from actions import walk
from libs.RenderHelper import RenderHelper
from PIL import Image

class TestWalkAction(unittest.TestCase):
    @patch('actions.walk.get_char')
    @patch('PIL.Image.open')
    @patch('utils.covert_pos')
    def test_walk_action_delay_mode(self, mock_covert_pos, mock_image_open, mock_get_char):
        # Given
        mock_action = MagicMock()
        mock_char = MagicMock()
        mock_char.pos = [0, 0]
        mock_char.rotate = 0
        mock_char.size = [50, 50]
        mock_action.char = mock_char
        mock_action.obj = {
            "结束位置": [100, 100],
            "比例": 1
        }
        
        mock_covert_pos.side_effect = [[0, 0], [100, 100]] # start_pos and end_pos
        mock_image = MagicMock()
        mock_image.size = (50, 50)
        mock_image_open.return_value = mock_image
        mock_get_char.return_value = mock_char

        images = ["frame1.png", "frame2.png"]

        # When
        pos = walk.Do(action=mock_action, images=images, sorted_char_list=[], delay_mode=True)

        # Then
        self.assertEqual(len(pos), 2)
        # Check the calculated positions, sizes, and rotations
        # step_x = 50, step_y = 50
        # size and rotate are constant
        self.assertEqual(pos[0], ([0, 0], [50, 50], 0))
        self.assertEqual(pos[1], ([50, 50], [50, 50], 0))

if __name__ == '__main__':
    unittest.main()

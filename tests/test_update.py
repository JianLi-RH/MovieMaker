import unittest
from unittest.mock import MagicMock, patch
from actions import update
import utils

class TestUpdateAction(unittest.TestCase):
    @patch('utils.covert_pos')
    @patch('actions.update.get_char')
    def test_update_action(self, mock_get_char, mock_covert_pos):
        # Given
        mock_action = MagicMock()
        mock_char = MagicMock()
        mock_action.char = mock_char
        
        update_data = {
            "素材": "new_image.png",
            "位置": "new_pos",
            "大小": [150, 250],
            "角度": 45,
            "透明度": 0.5,
            "显示": "是",
            "图层": 5,
        }
        
        mock_action.obj.keys.return_value = update_data.keys()
        mock_action.obj.get.side_effect = lambda key, default=None: update_data.get(key, default)
        
        mock_covert_pos.return_value = "converted_pos"
        mock_get_char.return_value = mock_char # so the last line does not return a new object

        # When
        update.Do(action=mock_action)

        # Then
        self.assertEqual(mock_char.image, "new_image.png")
        self.assertEqual(mock_char.pos, "converted_pos")
        self.assertEqual(mock_char.size, [150, 250])
        self.assertEqual(mock_char.rotate, 45)
        self.assertEqual(mock_char.transparency, 0.5)
        self.assertTrue(mock_char.display)
        self.assertEqual(mock_char.index, 5)
        mock_covert_pos.assert_called_once_with("new_pos")

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch, call
from actions import fight, walk
from libs.RenderHelper import RenderHelper

class TestFightAction(unittest.TestCase):
    @patch('actions.fight.get_char')
    @patch('actions.walk.Do')
    @patch('libs.RenderHelper.RenderHelper.render_with_position_tracking')
    def test_fight_action(self, mock_render, mock_walk_do, mock_get_char):
        # Given
        mock_action = MagicMock()
        mock_char1 = MagicMock()
        mock_char1.pos = [100, 100]
        mock_char2 = MagicMock()
        mock_char2.pos = [200, 100]
        
        mock_action.obj.get.side_effect = lambda key, default=None: {
            "角色": "char1 char2",
            "幅度": "小"
        }.get(key, default)
        mock_action.chars = [mock_char1, mock_char2]

        mock_get_char.side_effect = [mock_char1, mock_char2]
        mock_walk_do.return_value = "some_positions"

        images = ["frame1.png", "frame2.png"]
        sorted_char_list = [mock_char1, mock_char2]

        # When
        fight.Do(action=mock_action, images=images, sorted_char_list=sorted_char_list)

        # Then
        self.assertEqual(mock_walk_do.call_count, 2)
        mock_render.assert_called_once()

if __name__ == '__main__':
    unittest.main()

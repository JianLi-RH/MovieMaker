import unittest
from unittest.mock import MagicMock, patch
from actions import turn
from libs.RenderHelper import RenderHelper

class TestTurnAction(unittest.TestCase):
    def test_turn_action_delay_mode_int_angle(self):
        # Given
        mock_action = MagicMock()
        mock_char = MagicMock()
        mock_char.rotate = 0
        mock_char.pos = (10, 20)
        mock_char.size = (100, 200)
        mock_action.char = mock_char
        mock_action.obj.get.return_value = 90 # angle
        images = ["frame1.png", "frame2.png"]

        # When
        delay_pos = turn.Do(action=mock_action, images=images, sorted_char_list=[], delay_mode=True)

        # Then
        self.assertEqual(len(delay_pos), 2)
        self.assertEqual(delay_pos[0], [(10, 20), (100, 200), 45.0])
        self.assertEqual(delay_pos[1], [(10, 20), (100, 200), 90.0])

    @patch('libs.RenderHelper.RenderHelper.render_characters_on_frame')
    def test_turn_action_no_delay_mode(self, mock_render):
        # Given
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            char_list = args[1]
            char = char_list[0]
            if call_count == 0:
                self.assertEqual(char.rotate, 45.0)
            elif call_count == 1:
                self.assertEqual(char.rotate, 90.0)
            call_count += 1
            return (None, MagicMock())

        mock_render.side_effect = side_effect

        mock_action = MagicMock()
        mock_char = MagicMock()
        mock_char.name = "test_char"
        mock_char.rotate = 0
        mock_char.pos = (10, 20)
        mock_char.size = (100, 200)
        mock_action.char = mock_char
        mock_action.obj.get.return_value = 90 # angle
        images = ["frame1.png", "frame2.png"]
        sorted_char_list = [mock_char]

        # When
        turn.Do(action=mock_action, images=images, sorted_char_list=sorted_char_list, delay_mode=False)

        # Then
        self.assertEqual(mock_render.call_count, 2)

if __name__ == '__main__':
    unittest.main()

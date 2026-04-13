import unittest
from unittest.mock import MagicMock, patch
from actions import talk
from libs import ImageHelper
from actions import camera

class TestTalkAction(unittest.TestCase):
    def test_talk_action_delay_mode(self):
        # Given
        mock_action = MagicMock()
        mock_char = MagicMock()
        mock_char.pos = (10, 20)
        mock_char.size = (100, 200)
        mock_char.rotate = 0
        mock_action.char = mock_char
        images = ["frame1.png", "frame2.png"]

        # When
        delay_pos = talk.Do(action=mock_action, images=images, sorted_char_list=[], delay_mode=True)

        # Then
        self.assertEqual(len(delay_pos), len(images))
        self.assertEqual(delay_pos[0], ((10, 20), (100, 200), 0))
        self.assertEqual(delay_pos[1], ((10, 20), (100, 200), 0))

    @patch('libs.ImageHelper.paint_char_on_image')
    def test_talk_action_no_change_or_focus(self, mock_paint):
        # Given
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            char = kwargs['char']
            if call_count == 0:
                self.assertEqual(char.pos[1], 15)
            elif call_count == 1:
                self.assertEqual(char.pos[1], 20)
            call_count += 1
            return (None, MagicMock())

        mock_paint.side_effect = side_effect
        
        mock_action = MagicMock()
        mock_char = MagicMock()
        mock_char.pos = [10, 20]
        mock_char.size = [100, 200]
        mock_char.display = True
        mock_action.char = mock_char
        mock_action.obj.get.return_value = None # No "变化" or "焦点"
        images = ["frame1.png", "frame2.png"]
        sorted_char_list = [mock_char]

        # When
        talk.Do(action=mock_action, images=images, sorted_char_list=sorted_char_list, delay_mode=False)

        # Then
        self.assertEqual(mock_paint.call_count, len(images))
        self.assertEqual(mock_char.pos, [10, 20]) # Restored at the end

if __name__ == '__main__':
    unittest.main()

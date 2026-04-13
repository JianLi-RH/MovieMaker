import unittest
from unittest.mock import MagicMock, patch
from actions import disappear

class TestDisappearAction(unittest.TestCase):
    def test_disappear_single_character(self):
        # Given
        mock_action = MagicMock()
        mock_char = MagicMock()
        mock_action.char = mock_char
        mock_action.obj.get.return_value = "some_character"

        # When
        disappear.Do(mock_action)

        # Then
        self.assertFalse(mock_char.display)

    def test_disappear_multiple_characters(self):
        # Given
        mock_action = MagicMock()
        mock_char1 = MagicMock()
        mock_char1.name = "char1"
        mock_char2 = MagicMock()
        mock_char2.name = "char2"
        
        def get_char_side_effect(char_name, chars):
            if char_name == "char1":
                return mock_char1
            if char_name == "char2":
                return mock_char2
            return None

        mock_action.obj.get.return_value = "char1 char2"
        mock_action.activity.scenario.chars = [mock_char1, mock_char2]
        
        with patch('actions.disappear.get_char', side_effect=get_char_side_effect) as mock_get_char:
            # When
            disappear.Do(mock_action)

            # Then
            self.assertFalse(mock_char1.display)
            self.assertFalse(mock_char2.display)

if __name__ == '__main__':
    unittest.main()

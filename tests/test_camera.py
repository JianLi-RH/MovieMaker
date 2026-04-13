import unittest
from unittest.mock import patch, MagicMock, ANY
from actions import camera
from libs import ImageHelper, RenderHelper
import utils

class TestCameraAction(unittest.TestCase):
    @patch('utils.covert_pos')
    @patch('libs.ImageHelper.zoom_in_out_image')
    @patch('libs.RenderHelper.RenderHelper.render_characters_on_frames')
    def test_camera_action_calls_helpers(self, mock_render_chars, mock_zoom, mock_covert_pos):
        # Given
        images = ["frame1.png", "frame2.png"]
        
        mock_action = MagicMock()
        mock_action.activity.scenario.focus = "中心"
        mock_action.activity.scenario.chars = [MagicMock()]
        mock_action.obj.get.side_effect = lambda key, default=None: {
            "焦点": [0.8, 0.8],
            "变化": 2.0
        }.get(key, default)
        mock_action.char = None

        mock_covert_pos.side_effect = [[500, 500], [800, 800]] # First call for original_center, second for new_center

        # When
        camera.Do(images=images, action=mock_action, add_chars=True)

        # Then
        mock_render_chars.assert_called_once_with(images, mock_action.activity.scenario.chars)
        self.assertEqual(mock_zoom.call_count, len(images))
        
        # Check the calls to zoom_in_out_image
        # step_x = (800 - 500) / 2 = 150
        # step_y = (800 - 500) / 2 = 150
        # ratio_step = (2.0 - 1.0) / 2 = 0.5
        # i = 0: center=(500.0, 500.0), ratio=1.0
        # i = 1: center=(650.0, 650.0), ratio=1.5
        mock_zoom.assert_any_call("frame1.png", center=(500.0, 500.0), ratio=1.0)
        mock_zoom.assert_any_call("frame2.png", center=(650.0, 650.0), ratio=1.5)

if __name__ == '__main__':
    unittest.main()

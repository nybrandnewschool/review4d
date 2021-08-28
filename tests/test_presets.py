import os
import unittest

import review4d

import c4d


class TestBuiltinPathPresets(unittest.TestCase):

    def test_desktop_preset(self):
        '''DesktopPreset generates path on desktop.'''

        file = '/some/long/filepath.c4d'
        expected = review4d.normalize(
            review4d.desktop_path,
            os.path.basename(file).replace('.c4d', '.mp4'),
        )
        result = review4d.get_preset_path('Desktop', file)
        self.assertEqual(result, expected)

    def test_default_user_previews_preset(self):
        '''UserPreviewsPreset generates path in users prefs/pv directory.'''

        file = '/some/other/filepath.c4d'
        expected = review4d.normalize(
            review4d.user_previews_path,
            'filepath.mp4',
        )
        result = review4d.get_preset_path('User Previews', file)
        self.assertEqual(result, expected)

    def test_custom_preset(self):
        '''CustomPreset returns None.'''

        expected = None
        result = review4d.get_preset_path(
            'Custom',
            '/any/old/path.c4d',
        )
        self.assertEqual(result, expected)

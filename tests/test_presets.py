import os
import unittest

import c4d

import review4d


class TestBuiltinPathPresets(unittest.TestCase):
    def setUp(self):
        self.doc = c4d.documents.BaseDocument()
        c4d.documents.InsertBaseDocument(self.doc)
        c4d.documents.SetActiveDocument(self.doc)
        self.render_settings = "temp"
        review4d.create_render_settings(self.render_settings, doc=self.doc)

    def tearDown(self) -> None:
        c4d.documents.KillDocument(self.doc)
        self.doc = None
        self.rdata = None

    def set_document_path(self, path):
        self.doc.SetDocumentName(os.path.basename(path))
        self.doc.SetDocumentPath(os.path.dirname(path))

    def get_document_path(self):
        return self.doc.GetDocumentPath()

    def get_document_name(self):
        return self.doc.GetDocumentName()

    def test_desktop_preset(self):
        """DesktopPreset generates path on desktop."""

        self.set_document_path("/some/long/filepath.c4d")
        expected = review4d.normalize(
            review4d.desktop_path,
            self.get_document_name().replace(".c4d", ".mp4"),
        )
        preset = review4d.get_preset_path("Desktop", self.get_document_path())
        result = review4d.expand_render_paths(preset, self.render_settings)[0]
        self.assertEqual(result, expected)

    def test_default_user_previews_preset(self):
        """UserPreviewsPreset generates path in users prefs/pv directory."""

        self.set_document_path("/some/other/filepath.c4d")
        expected = review4d.normalize(
            review4d.user_previews_path,
            self.get_document_name().replace(".c4d", ".mp4"),
        )
        preset = review4d.get_preset_path("User Previews", self.get_document_path())
        result = review4d.expand_render_paths(preset, self.render_settings)[0]
        self.assertEqual(result, expected)

    def test_custom_preset(self):
        """CustomPreset returns None."""

        expected = None
        result = review4d.get_preset_path(
            "Custom",
            "/any/old/path.c4d",
        )
        self.assertEqual(result, expected)

    def test_expand_render_paths(self):
        """Expand render paths with tokens and takes."""

        self.set_document_path("/some/document.c4d")

        # Test without takes.
        # 1 = Active Takes
        expected = ["/some/document.mp4"]
        result = review4d.expand_render_paths("/some/$prj.mp4", self.render_settings, 1)
        self.assertEqual(result, expected)

        # Create a take.
        take_data = self.doc.GetTakeData()
        main_take = take_data.GetMainTake()
        marked_take = take_data.AddTake("", main_take, main_take)
        marked_take.SetName("Marked")
        marked_take.SetChecked(True)
        main_take.SetChecked(False)

        # Test with ALL takes.
        # 2 = All Takes
        expected = [
            "/some/document_Main.mp4",
            "/some/document_Marked.mp4",
        ]
        result = review4d.expand_render_paths(
            "/some/$prj_$take.mp4",
            self.render_settings,
            2,
        )
        self.assertEqual(result, expected)

        # Test with MARKED takes.
        # 3 = Marked Takes
        expected = ["/some/document_Marked.mp4"]
        result = review4d.expand_render_paths(
            "/some/$prj_$take.mp4",
            self.render_settings,
            3,
        )
        self.assertEqual(result, expected)

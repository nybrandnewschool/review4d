import unittest


class TestImport(unittest.TestCase):

    def test_import(self):
        try:
            import review4d
        except ImportError:
            self.fail('Failed to import review4d.')

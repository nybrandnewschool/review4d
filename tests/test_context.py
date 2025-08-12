import unittest

import review4d


class TestBuiltinContextCollectors(unittest.TestCase):

    def test_untitled_document(self):
        '''Collect context from an untitled document.'''

        file = 'Untitled 1'
        expected = {
            'file': 'Untitled 1',
            'dirname': '',
            'filename': 'Untitled 1',
            'basename': 'Untitled_1',
            'version': '',
            'ext': '',
        }
        result = review4d.collect_context(file)
        for key in expected.keys():
            self.assertEqual(result.get(key), expected[key])

    def test_standard_file_path(self):
        '''Collect context from a standard document path.'''

        file = '/Project/work/c4d/Project.c4d'
        expected = {
            'file': '/Project/work/c4d/Project.c4d',
            'dirname': '/Project/work/c4d',
            'filename': 'Project.c4d',
            'basename': 'Project',
            'version': '',
            'ext': '.c4d',
        }
        result = review4d.collect_context(file)
        for key in expected.keys():
            self.assertEqual(result.get(key), expected[key])

    def test_versioned_file_path(self):
        '''Collect context from a versioned document path.'''

        file = '/Project/work/c4d/Project_v001.c4d'
        expected = {
            'file': '/Project/work/c4d/Project_v001.c4d',
            'dirname': '/Project/work/c4d',
            'filename': 'Project_v001.c4d',
            'basename': 'Project',
            'version': 'v001',
            'ext': '.c4d',
        }
        result = review4d.collect_context(file)
        for key in expected.keys():
            self.assertEqual(result.get(key), expected[key])

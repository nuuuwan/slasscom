import os
import unittest

from lumascape import Lumascape


class TestLumascape(unittest.TestCase):
    TEST_IMAGE_PATH_1 = os.path.join('tests', 'test_data', 'image1.jpg')
    TEST_IMAGE_PATH_2 = os.path.join('tests', 'test_data', 'image2.jpg')
    TEST_IMAGE_PATH_3 = os.path.join('tests', 'test_data', 'image3.png')

    def test_build(self):
        Lumascape(
            [
                ('group-1-1', self.TEST_IMAGE_PATH_1),
                ('group-1-2', self.TEST_IMAGE_PATH_1),
                ('group-1-3', self.TEST_IMAGE_PATH_1),
                ('group-1-4', self.TEST_IMAGE_PATH_1),
                ('group-2-1', self.TEST_IMAGE_PATH_2),
                ('group-2-2', self.TEST_IMAGE_PATH_2),
                ('group-3-1', self.TEST_IMAGE_PATH_3),
            ],
            get_name=lambda item: item[0],
            get_group=lambda item: item[0].split('-')[1],
            get_image_path=lambda item: item[1],
            size=(1600, 900),
        ).write(
            os.path.join('tests', 'test_data', 'test_lumascape_build.png')
        )

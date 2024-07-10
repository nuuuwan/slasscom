import unittest

from slasscom import DirectoryPage


class TestDirectoryPage(unittest.TestCase):
    def test_get_company_d_list(self):
        page = DirectoryPage()
        page.open()
        company_d_list = page.get_company_d_list()
        page.quit()
        self.assertEqual(len(company_d_list), 89)

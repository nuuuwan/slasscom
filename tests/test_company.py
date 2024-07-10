import unittest

from slasscom import Company


class TestCompany(unittest.TestCase):
    def test_list_all(self):
        company_list = Company.list_all()
        self.assertEqual(len(company_list), 89)

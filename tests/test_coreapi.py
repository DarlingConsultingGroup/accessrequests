
import unittest
import pathlib
if __name__ == "__main__":
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from tests.context import ServiceBusQueueTrigger1
else:
    from .context import ServiceBusQueueTrigger1
TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()

sp_id = 12
institution_type = "Bank"
modules = []
useremail = 'jcrowley@darlingconsulting.com'
action = "PUT"
bank_key = '439261312'
sp_id = '1001779'
institution_type = 'Credit Union'


class TestDCG_Core_API(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cor = ServiceBusQueueTrigger1.dcgcoreapi_calls.DCG_Core_API()

    def test_get_db_name(self):
        cor = self.cor.get_db_name(bank_key)
        self.assertIsNotNone(cor)
        self.assertIsInstance(cor,str)
        self.assertEqual(cor, "DDW_American_Federal_SB")

    def test_get_users_by_key(self):
        cor = self.cor.get_users_by_key(bank_key)
        self.assertIsNotNone(cor)
        self.assertIsInstance(cor, list)
        # self.assertEqual(cor["name"], "Opportunity Bank of Montana")

    # def test_user_modules_replace(self):
    #     cor = self.cor.user_modules_replace(modules, bank_key, useremail)
    #     self.assertIsNotNone(cor)
    #     self.assertIsInstance(cor,list)

    # def test_inst_meta_data(self):
    #     cor = self.cor.inst_meta_data(bank_key, sp_id, institution_type)
    #     self.assertIsNotNone(cor)
    #     self.assertIsInstance(cor,list)

    # def test_update_user_remove(self):
    #     cor = self.cor.update_user(action, useremail, bank_key)
    #     self.assertIsNotNone(cor)
    #     self.assertIsInstance(cor,list)

    # def test_update_user_add(self):
    #     cor = self.cor.update_user(action, useremail, bank_key)
    #     self.assertIsNotNone(cor)
    #     self.assertIsInstance(cor,list)


if __name__ == '__main__':
    unittest.main()



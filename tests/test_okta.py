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


appid = 'L360'
group = 'L360group'
okta_login = 'cbarry@darlingconsulting.com'

class TestOkta_API(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ok = ServiceBusQueueTrigger1.okta_calls.Okta_API()

    def test_get_user_id_okta(self):
        user_id_okta = self.ok.get_user_id_okta(okta_login)
        self.assertIsNotNone(user_id_okta)
        self.assertIsInstance(user_id_okta, dict)
        self.assertEqual(user_id_okta["id"], "00u78nvwrMxHvt5ep0y6")


    # def test_add_user_to_group(self):
    #     add_user_to_group = self.ok.add_user_to_group(self.user_id, group)
    #     self.assertIsNotNone(add_user_to_group)
    #     self.assertIsInstance(add_user_to_group,list)

    # def test_remove_user_from_group(self):
    #     remove_user_from_group = self.ok.remove_user_from_group(self.user_id, group)
    #     self.assertIsNotNone(remove_user_from_group)
    #     self.assertIsInstance(remove_user_from_group,list)

    # def test_assign_user_to_app_for_sso(self):
    #     assign_user_to_app_for_sso = self.ok.assign_user_to_app_for_sso(self.user_id, appid)
    #     self.assertIsNotNone(assign_user_to_app_for_sso)
    #     self.assertIsInstance(assign_user_to_app_for_sso,list)

    # def test_remove_user_from_app(self):
    #     remove_user_from_app = self.ok.remove_user_from_app(self.user_id, appid)
    #     self.assertIsNotNone(remove_user_from_app)
    #     self.assertIsInstance(remove_user_from_app,list)


if __name__ == '__main__':
    unittest.main()

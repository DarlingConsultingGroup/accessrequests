import unittest
import pathlib
import json
if __name__ == "__main__":
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from tests.context import ServiceBusQueueTrigger1
else:
    from .context import ServiceBusQueueTrigger1
from ServiceBusQueueTrigger1 import constants



TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()

access_id = 'a1r4u000002ttDJAAY'

class Testsalesforce_calls(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sf = ServiceBusQueueTrigger1.salesforce_calls.Salesforce_Api()  
        f = open('tests/access_request.json')
        cls.pre_saved_access_request_info = json.load(f)
        f.close()

    def test_get_access_request(self):
        get_access_request = self.sf.get_access_request(access_id)
        self.assertIsNotNone(get_access_request)
        self.assertIsInstance(get_access_request,dict)
        for i in constants.access_request_fields_used:
            self.assertEqual(get_access_request[i], self.pre_saved_access_request_info[i])

    # def test_get_access_request(self):
    #     get_access_request = self.sf.get_access_request(access_id)
    #     self.assertIsNotNone(get_access_request)
    #     self.assertIsInstance(get_access_request,dict)
    #     for i in constants.access_request_fields_used:
    #         self.assertEqual(get_access_request[i], self.pre_saved_access_request_info[i])



    # def test_update_access_request(self):
    #     update_access_request = self.sf.update_access_request(access_id, data)
    #     self.assertIsNotNone(update_access_request)
    #     self.assertIsInstance(update_access_request,list)

    # def test_update_contact(self):
    #     update_contact = self.sf.update_contact(contactid, data)
    #     self.assertIsNotNone(update_contact)
    #     self.assertIsInstance(update_contact,list)


if __name__ == '__main__':
    unittest.main()


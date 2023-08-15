

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
caselink = f"https://darlingconsulting.lightning.force.com/lightning/r/Case/{3452345}/view"
body = f'''Request received at: \n
Request finsished at:  \n
Requested from: {caselink}"
'''

class Testsend_email(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.email_alert = ServiceBusQueueTrigger1.send_email.email_alert("subjecttest", body, pers=True, auditemail="cdsc")

    def test_email_alert(self):
        self.assertIs(self.email_alert, True)


if __name__ == '__main__':
    unittest.main()
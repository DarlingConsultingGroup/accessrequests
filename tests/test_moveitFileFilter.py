

import unittest
import pathlib
import pandas as pd
if __name__ == "__main__":
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from tests.context import ServiceBusQueueTrigger1, moveitchecker
else:
    from .context import ServiceBusQueueTrigger1, moveitchecker
    
TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()




class TestmoveitFileFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mv = moveitchecker.moveitDepositChecker('0000-00-00')
        mv.logResults =  pd.read_csv(r'tests/testFilterData.csv').to_dict('records')
        mv.getDepositClientList(refresh=False)
        cls.mv = mv

    def test_filterResults(self):
        self.assertIs(len(self.mv.filterLogResults()), 41)


if __name__ == '__main__':
    unittest.main()
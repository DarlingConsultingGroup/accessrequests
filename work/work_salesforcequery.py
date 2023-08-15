import unittest
import pathlib
import pandas as pd
# from ServiceBusQueueTrigger1 import constants
from context import ServiceBusQueueTrigger1
import json

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()

sf = ServiceBusQueueTrigger1.salesforce_calls.Salesforce_Api()

query = "SELECT Field, OldValue, NewValue, CreatedDate FROM AccountHistory WHERE AccountId = '0017000000e3zyKAAQ'"

t = sf.query_salesforce(query)
print(t)

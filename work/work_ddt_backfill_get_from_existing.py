import unittest
import pathlib
import pandas as pd
# from ServiceBusQueueTrigger1 import constants
from context import ServiceBusQueueTrigger1
from ServiceBusQueueTrigger1.moveitbackfill import moveitbackfill
import json
import csv
import pandas as pd

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()

mv = moveitbackfill(site='dcgfile')
# mv = moveitbackfill(site='newfile')

folders = mv._get_pages('folders', pgnum=1, limit_page_count=3000000000)
pd.DataFrame(folders).to_csv('existingfolders.csv', index=False)


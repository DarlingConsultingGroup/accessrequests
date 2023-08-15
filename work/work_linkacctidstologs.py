import pathlib
from context import ServiceBusQueueTrigger1
from context import moveitchecker
import pandas as pd

from moveitchecker.utlities import currentEasternTimestampString
from moveitchecker.blobUpdater import blobUpdater
from moveitchecker.moveitDepositChecker import moveitDepositChecker


mv = moveitDepositChecker("2023-07-22 09:07:41")

# 2 dependencies for linking acct ids to move it resuts:
#   1. mock filter results
#   2. load deposit client list 
mv.logResults =  pd.read_csv(r'tests/testFilterData.csv').to_dict('records')
mv.getDepositClientList(refresh=False)


bs = mv.linkAccountIDToLogs()

access_by_folder_w_sfID.xlsx

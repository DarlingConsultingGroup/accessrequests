import pathlib
from context import ServiceBusQueueTrigger1
from context import moveitchecker
from moveitchecker.getDepositClients import moveitSalesforceData
from moveitchecker.moveitDepositChecker import moveitDepositChecker
from moveitchecker.utlities import currentEasternTimestampString
from moveitchecker.blobUpdater import blobUpdater
from ServiceBusQueueTrigger1.moveit_calls import moveit_api
import json
from datetime import datetime, timedelta
import pandas as pd
import logging
TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()



timestamp_str = "2023-07-13 12:29:01"

logs = moveitDepositChecker(timestamp_str)
logs.searchMoveitLogs()
logs.getDepositClientList(refresh=False)
logs.linkAccountIDToLogs()
logs.filterLogResults()
print(len(logs.logResults))
print(len(logs.filter_log_results))
logs.blobResultsOut
# logs.writeLogsToBlob()


print(f"log results from {timestamp_str} til {currentEasternTimestampString(lookbackMinutes=0)}: {len(logs.logResults)}. filtered results: {len(logs.filter_log_results)}")

if len(logs.filter_log_results) == 0:
    print(f"no new logs found since {timestamp_str}")
else:
    grouped = logs.linked_account_ID_to_filtered_logs.groupby('Account_ID_18__c')
    for name, group in grouped:
        logs.Account_18__c = group['Account_ID_18__c'].iloc[0]
        logs.Case_Comment__c = '\n'.join([i for i in group['fileName']])
        logs.moveIT_Folder_Name__c = group['folderPath'].iloc[0]
        logs.firstUploadTime = group['logTime'].min()
        logs.lastUploadTime = group['logTime'].max()
        logs.accountName = group['Name'].iloc[0]
        logs.moveIT_user_email__c = group['userLoginName'].iloc[0]
        logs.comment_test__c = currentEasternTimestampString(lookbackMinutes=0)

        if logs.checkCaseExists():
            try:
                logs.updateCase()
                print(f"log caseID updated: {logs.caseID} with {logs.Case_Comment__c} at {currentEasternTimestampString(lookbackMinutes=0)}")
            except Exception as e:
                print(f"log error updating case: {e}")
                raise
        else:
            try:
                logs.createCase()
                print(f"log case created for : {logs.accountName} with {logs.Case_Comment__c} at {currentEasternTimestampString(lookbackMinutes=0)}")
            except Exception as e:
                print(f"log error creating case: {e}")
                raise

# logs.writeLogsToBlob()
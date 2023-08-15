from datetime import datetime, timedelta
import logging
from moveitchecker.getDepositClients import moveitSalesforceData
from moveitchecker.moveitDepositChecker import moveitDepositChecker
from ServiceBusQueueTrigger1.moveit_calls import moveit_api
import azure.functions as func
from moveitchecker.utlities import currentEasternTimestampString
from moveitchecker.blobUpdater import blobUpdater


def main(mytimer: func.TimerRequest) -> None:


    bs = blobUpdater()
    timestamp_str = bs.readTimestampFile()
    logging.info(f'mvy log search starting from {timestamp_str}')

    logs = moveitDepositChecker(timestamp_str)
    logs.searchMoveitLogs()
    logs.getDepositClientList(refresh=True)
    logs.linkAccountIDToLogs()
    logs.filterLogResults()

    logging.info(f"mvy log results from {timestamp_str}: {len(logs.logResults)}. filtered results: {len(logs.filter_log_results)}")

    if len(logs.filter_log_results) > 0:
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
                    logging.info(f"mvy log caseID updated: {logs.caseID} with {logs.Case_Comment__c} at {currentEasternTimestampString(lookbackMinutes=0)}")
                except Exception as e:
                    logging.info(f"mvy log error updating case: {e}")
                    continue
            else:
                try:
                    logs.createCase()
                    logging.info(f"mvy log case created for : {logs.accountName} with {logs.Case_Comment__c} at {currentEasternTimestampString(lookbackMinutes=0)}")
                except Exception as e:
                    logging.info(f"mvy log error creating case: {e}")
                    continue

    logs.writeLogsToBlob()
    timedone = currentEasternTimestampString(lookbackMinutes=1)
    response = bs.writeTimestampFile(timedone)
    lastModifiedBlob = response["last_modified"].strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f'mvy log wrote {timedone} to blob at {lastModifiedBlob}')

# main(func.TimerRequest)






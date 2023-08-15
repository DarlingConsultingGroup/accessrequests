import pandas as pd
from ServiceBusQueueTrigger1.dcgcoreapi_calls import DCG_Core_API
from ServiceBusQueueTrigger1.moveit_calls import moveit_api
from moveitchecker.getDepositClients import moveitSalesforceData
from moveitchecker.blobUpdater import blobUpdater
import urllib.parse
import json
import logging



class moveitDepositChecker(moveitSalesforceData):

    def __init__(self, startdate):
        super().__init__()
        self.startdate = startdate
        self.logResults = []
        self.depositCleintDataframe = []
        self.targetFolderPaths = []
        self.file_name_contains = [
                                    "deposit",
                                    "D360",
                                    "DTA",
                                    "NMD",
                                    "DTMTMP",
                                    "CD",
                                    "DDDL",
                                    "COD",
                                    "ICS",
                                    "Dep",
                                    "DDD",
                                    "Intrafi",
                                    "SEN",
                                    "RMQ",
                                    "CDAR",
                                    "DTD",
                                    "SAV",
                                    "DDA",
                                    "Share",
                                    "Cert",
                                    "FB_Darling",
                                    # "SV",
                                    "Darling 360",
                                    "Darling360",
                                    "DCG Data Extract",
                                    "DD",
                                    "Sweep",
                                    "Pers & Org Numbers",
                                    "DCG FILES.zip",
                                    "DP360"
                                    ]
        self.filepath_doesnotcontain = [
                                        "IRR",
                                        "CECL",
                                        "Model Validation",
                                        "Liquidity Process Review",
                                        "Model Backtesting",
                                        "Model Integration",
                                        "MRM Process Review",
                                        "RMAV",
                                        "QRAS",
                                        "Data Audit"
                                        ]
                                
        self.blobResultsOut = []
        self.blobResultsIn = []
        self.filter_log_results = []


    def searchMoveitLogs(self):
        f = open('tests/access_request.json')
        pre_saved_access_request_info = json.load(f)
        mv = moveit_api(pre_saved_access_request_info)    
        logs = mv.get_logs(self.startdate)
        self.logResults = logs
        return logs


    def filterLogResults(self):
        filtered_results = []
        for x in self.logResults:
            folderMatch = any(substring.lower() in x['folderPath'].lower() for substring in self.targetFolderPaths)
            fileMatch = any(substring.lower() in x['fileName'].lower() for substring in self.file_name_contains)
            otherMatch = ".pdf" not in x['fileName'].lower() and 'darlingconsulting' not in x['userLoginName'].lower() and ".docx" not in x['fileName'].lower() 

            otherMatchFolders = all(substring.lower() not in x['folderPath'].lower() for substring in self.filepath_doesnotcontain)

            if fileMatch and otherMatch and folderMatch and otherMatchFolders: 
                filtered_results.append(x)
                self.blobResultsIn.append(x)
            else:
                self.blobResultsOut.append(x)

        self.filter_log_results = filtered_results
        self.linked_account_ID_to_filtered_logs = pd.DataFrame(self.filter_log_results)
        return filtered_results


    def writeLogsToBlob(self):
        blb = blobUpdater()

        if len(self.blobResultsIn) > 0:
            blb.updateBlobIn(self.blobResultsIn)
        if len(self.blobResultsOut) > 0:
            self.updatelastCaseCreatedDate()
            blb.updateBlobOut(self.blobResultsOut)
        return


    def updatelastCaseCreatedDate(self):
        if len(self.blobResultsOut) == 0:
            return
        df = pd.DataFrame(self.blobResultsOut)
        uniqueAccountIDs = list(df['Account_ID_18__c'].unique())
        if len(list(set(uniqueAccountIDs))) == 1 and list(set(uniqueAccountIDs)) == ['']:
            return
        lastUpdatedCaseDates = self.getLastCaseCreatedDate(uniqueAccountIDs)
        dictCaseDates = pd.DataFrame(lastUpdatedCaseDates)
        if dictCaseDates.empty:
            return
        dictCaseDates["Account_ID_18__c"] = dictCaseDates["Account_18__c"]
        merged_df = pd.merge(df, dictCaseDates, how='left', on='Account_ID_18__c')
        merged_df.drop(columns=['Name','attributes', 'Account_18__c'], inplace=True)
        merged_df.drop_duplicates(subset='id', inplace=True)
        merged_df.sort_values(by=['id'], inplace=True)
        self.blobResultsOut = merged_df.to_dict('records')


    def linkAccountIDToLogs(self):
        if len(self.logResults) == 0:
            return
        df = pd.DataFrame(self.logResults)
        df['folderPath'] = df['folderPath'].str.replace(' ','')
        df['Account_ID_18__c'] = ''
        df['accountNameSalesforce'] = ''
        df['d360Client'] = '0'

        for folderPath in self.targetFolderPaths:
            try:
                matching_rows = df[df['folderPath'].str.lower().str.contains(folderPath.lower())]
            except Exception as e:
                logging.error(f"Error: {e}")
                break
            if matching_rows.empty:
                continue
            correspondingrecord = self.depositCleintDataframe[self.depositCleintDataframe['folderPath'] == folderPath]
            correspondingAccountID = correspondingrecord['Account_ID_18__c']
            correspondingAccountName = correspondingrecord['Name']
            try:
                df.loc[matching_rows.index, 'Account_ID_18__c'] = correspondingAccountID.item()
                df.loc[matching_rows.index, 'Name'] = correspondingAccountName.item()
                df.loc[matching_rows.index, 'd360Client'] = "1"
            except ValueError:
                print(f"Error: {folderPath} has >1 matching Account_ID_18__c: {[i for i in correspondingAccountID.values]}")
                df.loc[matching_rows.index, 'Account_ID_18__c'] = correspondingAccountID.values[0]
                df.loc[matching_rows.index, 'Name'] = correspondingAccountName.values[0]
                df.loc[matching_rows.index, 'd360Client'] = "1"
        self.logResults = df.to_dict('records')
        return df

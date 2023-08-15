
import pandas as pd
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api
import json
import datetime

class moveitSalesforceData(Salesforce_Api):

    def __init__(self):
        self.sf = Salesforce_Api()
        self.Status = 'New'
        self.Support_Type__c = 'Data Processing'
        self.Subject = 'AUTO - D360 - Data Processing'
        self.Product__c = 'D360'
        self.Account_18__c = ''
        self.Case_Comment__c = ''
        self.moveIT_Folder_Name__c = ''
        self.caseID = ''
        self.firstUploadTime = ''
        self.lastUploadTime = ''
        self.Description = '' 
        self.accountName = ''
        self.moveIT_user_email__c = ''
        self.comment_test__c = ''     

    def getDepositClientList(self, refresh=False):
        if refresh:
            t = self.sf.query_salesforce(f"select Name, State__c, Cert_or_Charter__c, Account_ID_18__c from Account where Core_Deposit_Analytics__c = True")
            df = pd.DataFrame(t)
            df.drop(columns=['attributes'], inplace=True)
            # df["folderPath"] = df.apply(lambda row: f"{row['Name']} - {row['State__c']} - {row['Cert_or_Charter__c']}", axis=1)
            df["folderPath"] = df.apply(lambda row: f"{row['State__c']}-{row['Cert_or_Charter__c']}", axis=1)
            # remove whitespace from folderPath
            # add special HC cases
            df.loc[df['Name'] == 'Glacier Bank', 'folderPath'] = 'MT-HoldingCompany'
            df.loc[df['Name'] == 'Tompkins Community Bank', 'Account_ID_18__c'] = 'NY-HoldingCompany'

            df.to_csv('depositClients.csv', index=False)
        else:
            df = pd.read_csv('depositClients.csv')
        self.depositCleintDataframe = df
        self.targetFolderPaths = df['folderPath'].tolist()

        return df
        

    def createCase(self):
        # add a function to salesforce api to create a case
        data = {
            'Status': self.Status,
            'Support_Type__c': self.Support_Type__c,
            'Product__c': self.Product__c,
            'Subject': self.Subject,
            'AccountId': self.Account_18__c,
            'Case_Comment__c': self.Case_Comment__c,
            'moveIT_Folder_Name__c': self.moveIT_Folder_Name__c,
            'Description': f'Files uploaded to moveIT. See Comments below for filenames.',
            'moveIT_user_email__c': self.moveIT_user_email__c,
            'comment_test__c': self.comment_test__c                    

        }
        response = self.sf.create_case(data)
        return response


    def updateCase(self):
        data = {
            'Case_Comment__c': self.Case_Comment__c,
            'moveIT_Folder_Name__c': self.moveIT_Folder_Name__c,
            'moveIT_user_email__c': self.moveIT_user_email__c,                    
            'comment_test__c': self.comment_test__c                    

        }
        response = self.sf.update_case(self.caseID, data)
        return response


    def checkCaseExists(self):
        query = f"select Id from Case where Account_18__c = '{self.Account_18__c}' and Status != 'Closed' and Product__c = '{self.Product__c}' and Support_Type__c = '{self.Support_Type__c}' and CreatedDate = TODAY and CreatedById = '00570000001iVp0AAE'"
        result = self.sf.query_salesforce(query)
        if len(result) > 0:
            self.caseID = result[0]['Id']
            return True
        else:
            return False
        

    def getLastCaseCreatedDate(self, accountID):
        accountID = [i for i in accountID if i != '']
        formattedList = ','.join(f"'{x}'" for x in accountID[:3])
        query = f"select Account_18__c, CreatedDate from Case where Account_18__c in ({formattedList}) and Product__c = '{self.Product__c}' and Support_Type__c = '{self.Support_Type__c}' and CreatedById = '00570000001iVp0AAE'"
        result = self.sf.query_salesforce(query)
        return result

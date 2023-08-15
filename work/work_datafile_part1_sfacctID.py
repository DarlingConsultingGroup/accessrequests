import unittest
import pathlib
import pandas as pd
# from ServiceBusQueueTrigger1 import constants
from context import ServiceBusQueueTrigger1
import json
import csv


TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()



sf = ServiceBusQueueTrigger1.salesforce_calls.Salesforce_Api()

df = pd.read_excel("S:\Security\MOVEit Incident\MoveitFiles Complete 5302023.xlsx", sheet_name="Files_Folders")

df["folder_root"] = df["Folder"].astype(str).str.split("/").str[1]


folders_affected = df["folder_root"].unique().tolist()

acctIds = pd.DataFrame(columns=['folder', 'Account_ID_18__c'])

for folder in folders_affected:
    try:
        instName = folder.split(" - ")[0]
        state = folder.split(" - ")[1]
        cert = folder.split(" - ")[2]
    except:
        try:
            instName = folder.split("-")[0].strip()
            state = folder.split("-")[1].strip()
            cert = folder.split("-")[2].strip()
        except:
            new_row = {'folder': folder, 'Account_ID_18__c': 'not a standard folder name'}
            acctIds = acctIds.append(new_row, ignore_index=True)
            continue

    t = sf.query_salesforce(f"select Account_ID_18__c from Account where State__c = '{state}' and Cert_or_Charter__c = '{cert}' and Name = '{instName}'")
    if len(t) == 0:
        t = sf.query_salesforce(f"select Account_ID_18__c from Account where State__c = '{state}' and Cert_or_Charter__c = '{cert}'")
        if len(t) == 1:
            new_row = {'folder': folder, 'Account_ID_18__c': t[0]['Account_ID_18__c']}
            acctIds = acctIds.append(new_row, ignore_index=True)
            continue
        else:
            t = sf.query_salesforce(f"select Account_ID_18__c from Account where Name = '{instName}' and Cert_or_Charter__c = '{cert}'")
            if len(t) == 1:
                new_row = {'folder': folder, 'Account_ID_18__c': t[0]['Account_ID_18__c']}
                acctIds = acctIds.append(new_row, ignore_index=True)
                continue
            else:
                new_row = {'folder': folder, 'Account_ID_18__c': f'found {len(t)} matches'}
                acctIds = acctIds.append(new_row, ignore_index=True)
                continue
    else:
        new_row = {'folder': folder, 'Account_ID_18__c': t[0]['Account_ID_18__c']}
        acctIds = acctIds.append(new_row, ignore_index=True)


acctIds.to_csv('tests/foldersImpacted_to_sfAccount_ID_18__c.csv', index=False)

# t = sf.query_salesforce(f"select Name, State__c, Cert_or_Charter__c from Account where Core_Deposit_Analytics__c = True")

# df = pd.read_csv(r'tests/filenames.csv', encoding='latin-1')
# unique_ddwdb_names = df['DDWDBName'].unique()

# depositClients = {}
# for ddwdb_name in unique_ddwdb_names:
#     t = sf.query_salesforce(f"select Name, Deposits360__c from Data_Warehouse__c where Name = '{ddwdb_name}'")
    
#     try:
#         depositClients.update({ddwdb_name: t[0]["Deposits360__c"]})
#     except Exception as e:
#         print(f"{e}: {ddwdb_name}")
#         depositClients.update({ddwdb_name: False})

# df['d360file'] = df.apply(lambda row: '1' if row['FormatType'] == 'D' and depositClients[row['DDWDBName']] is True else 0)

# df.to_csv('tests/filenames2.csv', index=False)
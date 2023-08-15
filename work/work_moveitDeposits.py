import unittest
import pathlib
import pandas as pd
# from ServiceBusQueueTrigger1 import constants
from context import ServiceBusQueueTrigger1
import json

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()
f = open('tests/access_request.json')
pre_saved_access_request_info = json.load(f)

mv = ServiceBusQueueTrigger1.moveit_calls.moveit_api(pre_saved_access_request_info)
sf = ServiceBusQueueTrigger1.salesforce_calls.Salesforce_Api()

# results = mv.get_logs()

# import csv

t = sf.query_salesforce(f"select Name, State__c, Cert_or_Charter__c from Account where Core_Deposit_Analytics__c = True")


# keys = results[0].keys()
# with open('logs.csv', 'w', newline='') as output_file:
#     dict_writer = csv.DictWriter(output_file, keys)
#     dict_writer.writeheader()
#     for i in results:
#         try:
#             dict_writer.writerow(i)
#         except:
#             print(i)
#             continue


df = pd.read_csv(r'tests/filenames.csv', encoding='latin-1')
unique_ddwdb_names = df['DDWDBName'].unique()

depositClients = {}
for ddwdb_name in unique_ddwdb_names:
    t = sf.query_salesforce(f"select Name, Deposits360__c from Data_Warehouse__c where Name = '{ddwdb_name}'")
    
    try:
        depositClients.update({ddwdb_name: t[0]["Deposits360__c"]})
    except Exception as e:
        print(f"{e}: {ddwdb_name}")
        depositClients.update({ddwdb_name: False})


df['d360file'] = df.apply(lambda row: '1' if row['FormatType'] == 'D' and depositClients[row['DDWDBName']] is True else 0)

df.to_csv('tests/filenames2.csv', index=False)
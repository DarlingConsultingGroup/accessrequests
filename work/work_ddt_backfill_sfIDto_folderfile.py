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


df = pd.read_excel(r'R:/CBarry/access_by_folder_w_sfID.xlsx', sheet_name='access_by_folder')

df["root"] = df["oldFolderPath"].astype(str).str.split("/").str[1]


sf = ServiceBusQueueTrigger1.salesforce_calls.Salesforce_Api()

df["Account_ID_18__c"] = ''

for i in df["root"].unique():
    if len(i.split("-")) < 3:
        continue
    name = i.split("-")[0].rstrip()
    state = i.split("-")[1].strip()
    cert = i.split("-")[2].strip()

    query = f"SELECT Account_ID_18__c FROM Account WHERE State__c = '{state}' and Cert_or_Charter__c = '{cert}'"
    try:
        t = sf.query_salesforce(query)
    except Exception as e:
        print(f"error querying salesforce for {name} {state} {cert}")
        continue

    if len(t) == 0:
        print(f"no account found for {name} {state} {cert}")
        continue
    acct = t[0]["Account_ID_18__c"]
    df.loc[df["root"] == i, "Account_ID_18__c"] = acct

df.to_excel(r'R:/CBarry/access_by_folder_w_sfID.xlsx', sheet_name='access_by_folder', index=False)
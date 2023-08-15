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

for folder in folders_affected:
    files = pd.DataFrame(columns=['fileName', 'fullFolderPath'])
    files["fileName"] = df[df["folder_root"] == folder]["File Name"]
    files["fullFolderPath"] = df[df["folder_root"] == folder]["Folder"]
    files.to_csv(fr'S:\Security\MOVEit Incident\accounts\{folder}.csv', index=False)
    


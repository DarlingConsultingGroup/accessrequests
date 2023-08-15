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

# new move it highest level folder id = 979227779          
# old move it highest level folder id = 172364921          

folders = pd.read_csv('existingfolders.csv')
bank_root_folders = folders[folders['parentId'] == 172364921]
bank_sub_folders = folders[(folders['parentId'] != 172364921) & (folders['parentId'] != 0)]


# bank root folder level
# for index, row in bank_root_folders.iterrows():
#     parent = 979227779
#     foldername = row['name']
#     bank_root = mv.create_subfolder(foldername, parent)
#     try:
#         b = bank_root["id"]
#     except KeyError:
#         print(bank_root)
#         continue
#     maint = mv._change_maint_settings(bank_root["id"])
#     misc = mv._change_misc_settings(bank_root["id"])


# new_bank_rootfolders = pd.read_csv('folders.csv')

# sub folders below the bank level
for index, row in bank_root_folders.iterrows():
    parentfolderid = row['id']
    Upload = mv.create_subfolder("Upload", parentfolderid)
    bank_sub = mv.create_subfolder("Download", parentfolderid)
    print(f'Upload: {Upload}, bank_sub: {bank_sub}')



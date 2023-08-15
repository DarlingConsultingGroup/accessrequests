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
permissions_for_new_folder = []

for index, row in folders.iterrows():
    folderid = row['id']
    folderending = row['path'].split('/')[-1]
    foldebegin = row['path'].split('/')[1]

    acls = mv.get_folder_details_acls(folderid)

    try:
        acls["items"]
    except KeyError:
        print(f'KeyError for {row["path"]} with folderID {folderid}: {acls["detail"]}')
        continue
    if row['path'].split('/')[-1] == 'Upload' or row['path'].split('/')[-1] == 'Download':
        continue
    

    for accesser in acls["items"]:
        if 'report' in folderending.lower():
            if accesser["name"].split("-")[-1].replace(" ", "") in ["ALCO", "DCG"]:
                newGroupName = accesser["name"].replace("ALCO", "Download").replace("DCG", "Download")
            else:
                newGroupName = f'{accesser["name"]} - Download'
            newfolderpath = f"{foldebegin}/Download"

        elif 'data' in folderending.lower():
            if accesser["name"].split("-")[-1].replace(" ", "") in ["ALCO", "DCG"]:
                newGroupName = accesser["name"].replace("ALCO", "Upload").replace("DCG", "Upload")
            else:
                newGroupName = f'{accesser["name"]} - Upload'
            newfolderpath = f"{foldebegin}/Upload"
        else:
            newGroupName = ""
            newfolderpath = ""

        if accesser["name"] in ["ATG Group", "DCG - Analyst Managers", "DCG Executive Coordinators", "Judis Project Group", "Drews DCG Group"]:
            newGroupName = accesser["name"]

        tosave = {
            "oldFolderId": folderid,
            "oldFolderPath": row['path'],
            "oldGroupName": accesser["name"],
            "newFolderPath": newfolderpath,
            "newGroupName": newGroupName,
            "type": accesser["type"], 
            "id": accesser["id"], 
            "readFiles": accesser["permissions"]["readFiles"],
            "writeFiles": accesser["permissions"]["writeFiles"],
            "deleteFiles": accesser["permissions"]["deleteFiles"],
            "listFiles": accesser["permissions"]["listFiles"],
            "notify": accesser["permissions"]["notify"],
            "addDeleteSubfolders": accesser["permissions"]["addDeleteSubfolders"],
            "share": accesser["permissions"]["share"],
            "admin": accesser["permissions"]["admin"],
            "listUsers": accesser["permissions"]["listUsers"]
            }
        permissions_for_new_folder.append(tosave)

forsave = pd.DataFrame(permissions_for_new_folder)
forsave.to_csv('access_by_folder.csv', index=False)




















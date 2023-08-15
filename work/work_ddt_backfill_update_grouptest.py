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




# for each upload / download folder in new site, create a group with fixed permissions. 
# the users added to those groups, will be the client users that are from the old moveit site


# groups to create 
    # Affinity Federal Credit Union - NJ - 857 - Upload
    # Affinity Federal Credit Union - NJ - 857 - Download

# upload_create_group = mv.create_group('Affinity Federal Credit Union - NJ - 857 - Upload')
# download_create_group = mv.create_group('Affinity Federal Credit Union - NJ - 857 - Download')

# upload_group_to_folder = mv.add_group_to_folder(upload_create_group["id"], 981065586, {"notify": "true", "admin": "false", "write_and_delete": "true"})
# download_group_to_folder = mv.add_group_to_folder(download_create_group["id"], 980962290, {"notify": "true", "admin": "false", "write_and_delete": "false"})


# for each EXTERNAL user in Affinity Federal Credit Union - NJ - 857 (ID: 64501):
# mv = moveitbackfill(site='dcgfile')
# mebers = mv.get_members_by_groupid(64501)

# newmv = moveitbackfill(site='newfile')
# for i in mebers["items"]:
#     if "darling" in i["email"]:
#         continue
#     use = newmv.create_user(i["email"])
#     userlist = newmv._get_pages("users")
#     try:

#         newuserid = [b["id"] for b in userlist if b["email"]== i["email"]][0]
#         add = newmv.add_member_to_group(newuserid, 1)
#     except:
#         print(f"{use}")
#         continue


# for each EXTERNAL user in Affinity Federal Credit Union - NJ - 857 - ALCO (ID: 125301):
mv = moveitbackfill(site='dcgfile')
mebers = mv.get_members_by_groupid(125301)

newmv = moveitbackfill(site='newfile')
for i in mebers["items"]:
    if "darling" in i["email"]:
        continue
    use = newmv.create_user(i["email"])
    userlist = newmv._get_pages("users")
    try:
        newuserid = [b["id"] for b in userlist if b["email"]== i["email"]][0]
        add = newmv.add_member_to_group(newuserid, 2)
    except:
        print(f"{use}")
        continue
access_by_folder_w_sfID.xlsx





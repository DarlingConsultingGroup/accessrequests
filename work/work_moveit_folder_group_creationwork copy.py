import pathlib
from context import ServiceBusQueueTrigger1
# import datetime
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api
# from ServiceBusQueueTrigger1.read_and_push import read_and_push_accessrequest
from ServiceBusQueueTrigger1.moveit_calls import moveit_api
from ServiceBusQueueTrigger1.okta_calls import Okta_API
import json
import csv

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()


f = open('tests/access_request.json')
pre_saved_access_request_info = json.load(f)
f.close()


# ok = Okta_API()
# user = ok.get_user_id_okta("amerchant@axiombanking.com")

# get_users = ok.get_users('00uzddw95qnQZ6gIf0x7')

# logs = ok.get_logs()
# logs

mv = moveit_api(pre_saved_access_request_info)
# sf = Salesforce_Api()
# acct= "0017000000e3zPIAAY"

# print(ok.get_group('00g2wpcl5JLOEGGFUCCX'))
mv.user_id = 'a1'
te = mv.remove_member_from_group('64501')
print(te)

# t = mv.create_subfolder('test_bank_root_folder_settings')

# data = {"Auto_Completed_API__c": True}
# t = sf.update_access_request('a1r4u000003j9aAAAQ', data)
# print(t)


# t = sf.get_account(acct)
# with open('accts.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     for key, value in t.items():
#         writer.writerow([key, value])










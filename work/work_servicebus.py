import pathlib
from context import ServiceBusQueueTrigger1
# import datetime
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api
from ServiceBusQueueTrigger1.read_and_push import read_and_push_accessrequest
from ServiceBusQueueTrigger1.dcgcoreapi_calls import DCG_Core_API
import pickle

# dcg = DCG_Core_API()
# print(dcg.get_db_name(12))

import json

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()

# #setup
access_id = "a1r4u000003Dv54AAC"
sf = Salesforce_Api()
get_all_fields_from_sf = sf.get_access_request(access_id)

# # f = open('tests/access_request.json')
# # get_all_fields_from_sf = json.load(f)
# # f.close()


# ##############################################################################

read_and_push_accessrequest(get_all_fields_from_sf, access_id)

# caselink = f"https://darlingconsulting.lightning.force.com/lightning/r/Case/{caseid}/view"
# body = f'''Request received at: {timestamp_searched} \n\n 
# Request finsished at: {timestamp} \n\n 
# Requested from: {caselink}"
# '''

# email_alert(f"Account Okta Audit Results for {acctname[0]['Name']}", body, attachmentpath=filename, auditemail=email)
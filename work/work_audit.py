import pathlib
from context import ServiceBusQueueTrigger1
from ServiceBusQueueTrigger1.moveit_api import moveit_api
from ServiceBusQueueTrigger1.dcgcoreapi_calls import DCG_Core_API
from ServiceBusQueueTrigger1.okta_calls import Okta_API
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api
from ServiceBusQueueTrigger1.send_email import email_alert

import json
import csv
from datetime import datetime

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()

audit_master_list = []
timestamp_searched = datetime.now()

## account id recieved!!!   0017000001E1uZuAAJ
aactid = "0017000001E1uZuAAJ"
sf = Salesforce_Api()
user_list = sf.query_salesforce(f"select email, okta_login__c from Contact where Account.Id = '{aactid}' and Active_Contact__c = True")
acctname = sf.query_salesforce(f"select DCG_Account_Name__c from Account where Account.Id = '{aactid}'")


# usernames = [i["Okta_Login__c"] if i["Okta_Login__c"] else i["Email"] for i in user_list]


# for username in usernames:
#   if username is None:
#     continue
#   if username.split("@")[-1].lower() == 'darlingconsulting.com':
#     continue

#   ok = Okta_API()
#   okta_user = ok.get_user_id_okta(username)

#   okta_userid = okta_user.get("id", None)
#   okta_status = okta_user.get("status", "NULL")
#   okta_app_list = "NULL"

#   if okta_userid is not None:
#     apps = ok.get_user_applinks(okta_userid)
#     okta_app_list = [i["label"] for i in apps if i["label"] not in ['Help Center', 'About Deposits360°®', 'About Liquidity360°®', 'About Prepayments360°™', 'Cost Calculator', 'DCG Bulletins', 'Loan Pricing',  'Request Ticket', 'Web Rates']]
    
#   user_results = {
#     "username": username,
#     "okta_status": okta_status,
#     "okta_app_list": okta_app_list}

#   audit_master_list.append(user_results)


#send records bank, or send an email with a df to the requester
filename = f'toolsaudit_{timestamp_searched.strftime("%m.%d_%H.%M")}.csv'

with open(filename, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    spamwriter.writerow(["DCG_Account_Name__c:", acctname[0]['DCG_Account_Name__c']])
    spamwriter.writerow("")

    # writer = csv.DictWriter(csvfile, fieldnames = audit_master_list[0].keys())
    # writer.writeheader()
    # new_dict = [i for i in audit_master_list]
    # writer.writerows(new_dict)




timestamp = datetime.now()

email_alert(f"account okta audit results for {acctname[0]['DCG_Account_Name__c']}", f"request received at {timestamp_searched} and finsished at {timestamp}", pers=True, attachmentpath=filename)

print((timestamp - timestamp_searched))




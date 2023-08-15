import pathlib
from context import ServiceBusQueueTrigger1
# import datetime
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api
from ServiceBusQueueTrigger1.read_and_push import read_and_push_accessrequest
from ServiceBusQueueTrigger1.moveit_calls import moveit_api
from ServiceBusQueueTrigger1.okta_calls import Okta_API
from ServiceBusQueueTrigger1.dcgcoreapi_calls import DCG_Core_API
import json

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()
sf = Salesforce_Api()
dcg = DCG_Core_API()

t = sf.query_salesforce('''select BankKey__c, Cert_or_Charter__c, RecordTypeId, SNL_ID__c from Account where (BankKey__c != null) and (Cert_or_Charter__c != null) and (SNL_ID__c != null)''')


for i in t:

  resp = dcg.loans_post_inst_meta_data(i["BankKey__c"], i["SNL_ID__c"], i["RecordTypeId"], i["Cert_or_Charter__c"])

  


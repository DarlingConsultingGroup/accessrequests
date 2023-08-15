import logging
import azure.functions as func
import datetime
from ServiceBusQueueTrigger1.read_and_push import read_and_push_accessrequest
from ServiceBusQueueTrigger1.dcgcoreapi_calls import DCG_Core_API
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api
from ServiceBusQueueTrigger1.send_email import email_alert


def main(msg: func.ServiceBusMessage):
    logging.info('Python ServiceBus queue trigger processed message: %s', msg.get_body().decode('utf-8'))

    # bankname or whatever we want to process
    bankname, certid, acctid = msg.get_body().decode('utf-8').split(";")
    certid = certid.strip()
    acctid = acctid.strip()

    dcg = DCG_Core_API()
    getkey_response = dcg.get_bankkey_by_regid(certid)
    if getkey_response != None:
        if len(getkey_response) == 0:
            creat = dcg.create_bankkey(bankname)
            if creat == None:
                sf_message = {"BankKey__c": "error creating bankkey"}
                logging.info(f"create: {str(creat)}")

            else:
                sf_message = {"BankKey__c": creat["key"],
                            "dcg_displayname__c": creat["displayName"]}



        elif len(getkey_response) == 1:
            sf_message = {"BankKey__c": getkey_response[0]["key"],
                            "dcg_displayname__c": getkey_response[0]["displayName"]}
                            
                        
        else:
            sf_message = {"BankKey__c": "multiple keys match regid",
                            "dcg_displayname__c": str([i["displayName"] for i in getkey_response])[:250]}

    else:
        sf_message = {"BankKey__c": "error searching bankkey"}

    
    sf = Salesforce_Api()
    finish = sf.update_account(acctid, sf_message)
    if not finish:
        logging.error(f"error updating account in sf with: {str(sf_message)}")
        email_alert("error updating account in sf", f'data: {str(sf_message)} \n access request: bankkey update \n', pers=True)
    else:
        logging.info(f"done updating account in sf with: {str(sf_message)}")


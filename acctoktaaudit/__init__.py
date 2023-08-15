import logging
import azure.functions as func
from HttpTrigger1.salesforce_listener import salesforce_listener
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('account audit function processed a request.')
    data = req.get_body().decode()
    obm = salesforce_listener(data)

    parse_message = obm.get_accounts_to_send()
    acctid = parse_message[0]["sf:Account_18__c"]    
    email = parse_message[0]["sf:Created_by_email__c"]    
    caseid = parse_message[0]["sf:Id"]    


    # put the acct id and created by email on the queue
    connstr = os.environ['AC_SERVICE_BUS_CONNECTION_STR']
    queue_name = 'audit'

    with ServiceBusClient.from_connection_string(connstr) as client:
        with client.get_queue_sender(queue_name) as sender:
            single_message = ServiceBusMessage(f'{acctid},{email},{caseid}')
            sender.send_messages(single_message)
            
    logging.info(f'account audit function enqued a request for acctid: {acctid}, email: {email})')
    return obm.send_acknowledgment_to_sf()

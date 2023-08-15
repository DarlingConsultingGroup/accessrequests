import logging
import azure.functions as func
from HttpTrigger1.salesforce_listener import salesforce_listener
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('bankkey HTTP trigger function processed a request.')

    message = req.get_body().decode()
    obm = salesforce_listener(message)

    # what are we sending from salesforce? 
    # we just need to make sure we get to the data that we want, move the sf noise out of the way
    accounts_to_send = obm.get_accounts_to_send()    

    connstr = os.environ['AC_SERVICE_BUS_CONNECTION_STR']
    queue_name = 'bankkey'
    with ServiceBusClient.from_connection_string(connstr) as client:
        with client.get_queue_sender(queue_name) as sender:

            for account_info in accounts_to_send:
                acctinfo = f'{account_info["sf:Name"]}; {account_info["sf:Cert_or_Charter__c"]}; {account_info["sf:Id"]}'

                single_message = ServiceBusMessage(acctinfo)
                sender.send_messages(single_message)
    
    return obm.send_acknowledgment_to_sf()

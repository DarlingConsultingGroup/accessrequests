import logging
import azure.functions as func
import datetime
from ServiceBusQueueTrigger1.read_and_push import read_and_push_accessrequest
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api


def main(msg: func.ServiceBusMessage):
    logging.info('Python ServiceBus queue trigger processed message: %s', msg.get_body().decode('utf-8'))

    access_id = msg.get_body().decode('utf-8')
    sf = Salesforce_Api()
    get_all_fields_from_sf = sf.get_access_request(access_id)


    read_and_push_accessrequest(get_all_fields_from_sf, access_id)


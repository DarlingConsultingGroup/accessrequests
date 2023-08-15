import logging
import azure.functions as func
from . salesforce_listener import salesforce_listener
from . send_queue import send_que

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    data = req.get_body().decode()

    obm = salesforce_listener(data)
    access_request_id_list = obm.access_request_ids()    

    for access_id in access_request_id_list:
        send_que(access_id)        
    
    return obm.send_acknowledgment_to_sf()

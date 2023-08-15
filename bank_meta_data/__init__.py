import logging
import azure.functions as func
from HttpTrigger1.salesforce_listener import salesforce_listener
from ServiceBusQueueTrigger1.dcgcoreapi_calls import DCG_Core_API
from ServiceBusQueueTrigger1.send_email import email_alert

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    core_api = DCG_Core_API()

    data = req.get_body().decode()
    obm = salesforce_listener(data)
    accounts_to_send = obm.get_accounts_to_send()    

    for account_info in accounts_to_send:
        try:
            bank_key = account_info["sf:BankKey__c"]
            sp_id = account_info["sf:SNL_ID__c"]
            institution_type = account_info["sf:RecordTypeId"]
            regulatoryId = account_info["sf:Cert_or_Charter__c"]


            logging.info(f'api/insitute_meta_data working on ...{account_info}')
            res = core_api.loans_post_inst_meta_data(bank_key, sp_id, institution_type, regulatoryId)
            
            if res.status_code == 400:
                email_alert("api/insitute_meta_data 400 error", f'bankkey: {bank_key} \n sp_id: {sp_id} \n institution_type: {institution_type} \n regulatoryId: {regulatoryId} \n response: {res}')

        except Exception as e:
            email_alert("api/insitute_meta_data error", f'there was exception {e} in trying to add meta data for: {str(account_info)})')
            raise
        
    return obm.send_acknowledgment_to_sf()

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
            module = account_info["sf:Product_Name_formula__c"]

            logging.info(f'modules_add_insititue working on ...{account_info}')
            res = core_api.modules_add_insititue(module, bank_key)
    
            if res.status_code == 400:
                email_alert("modules_add_insititue 400 error", f'bankkey: {bank_key} \n module: {module} \n')

        except Exception as e:
            email_alert("modules_add_insititue error", f'there was exception {e} in trying to add module for: {str(account_info)})')
            raise
        
    return obm.send_acknowledgment_to_sf()

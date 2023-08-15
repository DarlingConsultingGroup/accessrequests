import logging
import azure.functions as func
from acctoktaauditbus.audit import audit_account

def main(msg: func.ServiceBusMessage):
    acctid_email_case = msg.get_body().decode('utf-8')
    logging.info(f'bus trigger for audit request triggered for acct: {acctid_email_case}')

    acctid,email,caseid = acctid_email_case.split(",")
    audit_response = audit_account(acctid,email,caseid)
    
    logging.info(audit_response)

    return

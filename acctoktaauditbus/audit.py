from ServiceBusQueueTrigger1.okta_calls import Okta_API
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api
from ServiceBusQueueTrigger1.send_email import email_alert
import csv
from datetime import datetime



def audit_account(aactid,email,caseid):
  audit_master_list = []
  timestamp_searched = datetime.now()

  sf = Salesforce_Api()
  user_list = sf.query_salesforce(f"select email, okta_login__c from Contact where Account.Id = '{aactid}' and Active_Contact__c = True")
  user_list = [i["Okta_Login__c"] if i["Okta_Login__c"] else i["Email"] for i in user_list]
  acctname = sf.query_salesforce(f"select Name from Account where Account.Id = '{aactid}'")


  for username in user_list:
    if username is None:
      continue
    if username.split("@")[-1].lower() == 'darlingconsulting.com':
      continue

    ok = Okta_API()
    okta_user = ok.get_user_id_okta(username)

    okta_userid = okta_user.get("id", None)
    okta_status = okta_user.get("status", "NULL")
    okta_app_list = "NULL"

    if okta_userid is not None:
      apps = ok.get_user_applinks(okta_userid)
      okta_app_list = [i["label"] for i in apps if i["label"] not in ['Help Center', 'About Deposits360°®', 'About Liquidity360°®', 'About Prepayments360°™', 'Cost Calculator', 'DCG Bulletins', 'Loan Pricing',  'Request Ticket', 'Web Rates']]
      
    user_results = {
      "username": username,
      "okta_status": okta_status,
      "okta_app_list": okta_app_list}

    audit_master_list.append(user_results)


  #send records bank, or send an email with a df to the requester
  filename = f'toolsaudit_{timestamp_searched.strftime("%m.%d_%H.%M")}.csv'
  with open(filename, 'w', newline='') as csvfile:
      acctname_writer = csv.writer(csvfile, delimiter=',')
      acctname_writer.writerow(["Name:", acctname[0]['Name']])
      acctname_writer.writerow("")

      writer = csv.DictWriter(csvfile, fieldnames = audit_master_list[0].keys())
      writer.writeheader()
      new_dict = [i for i in audit_master_list]
      writer.writerows(new_dict)

  timestamp = datetime.now()


  caselink = f"https://darlingconsulting.lightning.force.com/lightning/r/Case/{caseid}/view"
  body = f'''Request received at: {timestamp_searched} \n
  Request finsished at: {timestamp} \n
  Requested from: {caselink}"
  '''

  email_alert(f"Account Okta Audit Results for {acctname[0]['Name']}", body, attachmentpath=filename, auditemail=email)


  return f"took {timestamp - timestamp_searched} to process {len(audit_master_list)} users for {acctname[0]['Name']}"



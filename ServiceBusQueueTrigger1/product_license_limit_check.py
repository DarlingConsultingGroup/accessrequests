import time
import datetime
from datetime import datetime, timedelta
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api
from ServiceBusQueueTrigger1.send_email import email_alert
from ServiceBusQueueTrigger1 import constants


def is_license_limit_reached(get_all_fields_from_sf):
    '''check to see request does not put account over default product license limit. 
    
    returns limit -> bool, licenses -> int'''
    limit = False
    product = get_all_fields_from_sf["Product__c"]
    try:
        active_count_field = constants.default_license_limits[product][0]
        product_license_limit = constants.default_license_limits[product][1]
    except KeyError:
        return limit, 0
    sf = Salesforce_Api()
    case_details = sf.get_case(get_all_fields_from_sf["Case__c"])
    licenses = case_details[active_count_field]

    if not licenses:
        licenses = 0

    if licenses >= product_license_limit:
        limit = True
        if licenses - product_license_limit <= 1:
            contact_id = get_all_fields_from_sf["Contact__c"]
            contact_info = sf.get_contact(contact_id)
            is_contact_already_checked = contact_info[constants.contact_hasproduct_fields[product]]
            if is_contact_already_checked:
                limit = False
    return limit, licenses


def wait_and_check_license_limit(get_all_fields_from_sf, license_count):
    '''wait 30 seconds, checks for access reuqests that might affect the license limit, and then checks again
    
    send email, puts on hold, then exits if license limit reached. else returns none'''
    sf = Salesforce_Api()
    time.sleep(30)
    timefitler = datetime.now() - timedelta(hours=1)
    timefitler = str(timefitler.isoformat(timespec='seconds')) + "Z"

    requests_potentially_affect_license_limit = sf.query_salesforce("SELECT Id FROM Access_Request__c WHERE SystemModStamp > {} and Product__c = '{}' and Access_Request__c = 'Remove Access' and BankKey__c = '{}'".format(timefitler, get_all_fields_from_sf["Product__c"], get_all_fields_from_sf["BankKey__c"]))
    
    limit = True
    licenses = license_count

    if requests_potentially_affect_license_limit:
        time.sleep(60)
        double_check = is_license_limit_reached(get_all_fields_from_sf)
        limit = double_check[0]
        licenses = double_check[1]
    if limit is True:    
        on_hold = sf.prep_response("default license limit reached ({})".format(licenses), "default license limit reached ({})".format(licenses), get_all_fields_from_sf["Access_Request__c"])
        
        sf.update_access_request(get_all_fields_from_sf["Id"], on_hold)
        
        email_alert("access requested to an account already at the default license limit", 
        """ access request id {} has been put on hold, please confirm account did not purchase additional licenses. \n
            
            licenses already used = {}
            Name = {}
            Id = {}
            Access_Combo__c = {} 
            \n
            https://darlingconsulting.lightning.force.com/lightning/r/Access_Request__c/{}/view
            \n
            https://darlingconsulting.lightning.force.com/lightning/r/Case/{}/view

        """.format(get_all_fields_from_sf["Id"], licenses, get_all_fields_from_sf["Name"], get_all_fields_from_sf["Id"], get_all_fields_from_sf["Access_Combo__c"], get_all_fields_from_sf["Id"], get_all_fields_from_sf["Case__c"]))
        return


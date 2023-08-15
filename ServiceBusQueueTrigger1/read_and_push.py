import logging
import azure.functions as func
from ServiceBusQueueTrigger1.okta_calls import Okta_API
from ServiceBusQueueTrigger1.dcgcoreapi_calls import DCG_Core_API
from ServiceBusQueueTrigger1.salesforce_calls import Salesforce_Api
from ServiceBusQueueTrigger1.send_email import email_alert
from ServiceBusQueueTrigger1.moveit_calls import moveit_calls
from ServiceBusQueueTrigger1.moveit_api import moveit_api
from ServiceBusQueueTrigger1.constants import moveit_products
from ServiceBusQueueTrigger1.product_license_limit_check import is_license_limit_reached, wait_and_check_license_limit


def read_and_push_accessrequest(get_all_fields_from_sf, access_id):
    sf = Salesforce_Api()
    okta_user_name = get_all_fields_from_sf["Okta_Login__c"]
    bankkey = get_all_fields_from_sf["BankKey__c"]

    if okta_user_name == "Needs Review":
        on_hold = sf.prep_response("login needs review", "login needs review", get_all_fields_from_sf["Access_Request__c"])
        sf.update_access_request(access_id, on_hold)
        return

    elif get_all_fields_from_sf["Product_Module_Request__c"]:        
        dcg = DCG_Core_API()
        modules = get_all_fields_from_sf["User_Module_List__c"]
        if not modules:
            modules = []
        else:
            modules = modules.split(",")
        dcg.user_modules_replace(modules, bankkey, okta_user_name)
        


    # elif get_all_fields_from_sf["Access_Request__c"] == "Remove Access" and okta_user_name is None:
    #     on_hold = sf.prep_response("no login name", "no login name", get_all_fields_from_sf["Access_Request__c"])
    #     sf.update_access_request(access_id, on_hold)
    #     return

    if get_all_fields_from_sf["Product__c"] == "Data Analytics":
        dcg = DCG_Core_API()
        mv = moveit_api(get_all_fields_from_sf)

        if get_all_fields_from_sf["Access_Request__c"] == "Remove Access":
            action = "DELETE"
        elif get_all_fields_from_sf["Access_Request__c"] == "Add Access":
            action = "PUT"
        else:
            mv.status_update_on_hold(get_all_fields_from_sf["Id"], "request needs to be Add or Remove Access")
        
        if okta_user_name is None:
            okta_user_name = get_all_fields_from_sf["Email__c"]
        
        use = dcg.update_user(action, okta_user_name, bankkey)
        ddw = dcg.get_db_name(bankkey)
        if "Successfully" in use and ddw is not None:
            mv.status_update_success(get_all_fields_from_sf["Id"], f'{use, str(ddw)}')
        else:
            if ddw is None and "Successfully" in use:
                mv.status_update_on_hold(get_all_fields_from_sf["Id"], f"no ddw attached to bankkey: {bankkey}. user added to sys admin")
            else: 
                mv.status_update_on_hold(get_all_fields_from_sf["Id"], use)
        logging.info(f'finished executing Data Analytics')
        return


    if get_all_fields_from_sf["Product__c"] in moveit_products:
        mv = moveit_calls(get_all_fields_from_sf)
        if "none" in mv.bank_level_root.split(" - ")[-1]:
            mv.status_update_on_hold(get_all_fields_from_sf["Id"], f"Cert_or_Charter__c is none on access request")
            return
        mv.moveit_process_request()
        logging.info(f'finished executing function moveit_process_request')
        return
    
########################################################################

    # elif get_all_fields_from_sf["Access_Request__c"] == "Add Access" and get_all_fields_from_sf["Email__c"].split("@")[-1].lower() != "darlingconsulting.com": 
    #     license_limit_reached = is_license_limit_reached(get_all_fields_from_sf)
    #     if license_limit_reached[0] is True:
    #         wait_and_check_license_limit(get_all_fields_from_sf, license_limit_reached[1])

####################################################

    ok = Okta_API()
    okta_response = ok.okta_process_request(get_all_fields_from_sf)

    #define dcgapi_response
    is_core_needed = ok.is_core_needed(get_all_fields_from_sf)
    
    if is_core_needed:
        dcg = DCG_Core_API()
        dcgapi_response = dcg.core_api_process_request(get_all_fields_from_sf)
    elif not is_core_needed:
        dcgapi_response = "not called as other apps require its access"           
    else:    
        dcgapi_response = "not called as there was an issue in the okta calls"           

    clean_combined_responses = sf.prep_response(dcgapi_response, okta_response, get_all_fields_from_sf["Access_Request__c"])
    sf.update_access_request(access_id, clean_combined_responses)
    logging.info(f'finished executing function update_access_request')

    return

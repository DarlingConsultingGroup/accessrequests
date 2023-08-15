import requests
import json
import os
import warnings
warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
from ServiceBusQueueTrigger1.get_dcg_api_token import get_access_token
from ServiceBusQueueTrigger1.config import env


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test


class DCG_Core_API():
    @ignore_warnings
    def __init__(self):
        self.baseurl = env()["dcgapi_base_url"]
        self.access_token = get_access_token()
        self.headers = {
                'Authorization': 'Bearer ' + self.access_token,
                'Content-type': 'application/json', 
                'Accept': 'text/plain'}


    #action = PUT, DELETE
    def update_user(self, action, user_name, bank_key):
        url = self.baseurl + "institutions/" + bank_key+"/users?userId="+user_name+""
        response = requests.request(action, url, headers=self.headers, data={})
        if response.status_code == 204:
            if action == "DELETE":
                return 'Successfully removed User: {} from Bank_Key: {}'.format(user_name, bank_key)
            else:
                return 'Successfully added User: {} to Bank_Key: {}'.format(user_name, bank_key)
        else:
            return 'errorCode - Bank_Key {} does not exist'.format(bank_key), response
    

    def core_api_process_request(self, get_all_fields_from_sf):
        product = get_all_fields_from_sf["Product__c"]
        add_or_remove = get_all_fields_from_sf["Access_Request__c"]
        username = get_all_fields_from_sf["Okta_Login__c"]   
        bank_key = get_all_fields_from_sf["BankKey__c"]   
        if not username:
            username = get_all_fields_from_sf["Email__c"]   

        if product == "D360" or product == "L360" or product == "P360" or product == "Loans360 - Credit Simulator" or product == "Loans360":
            if add_or_remove == "Add Access":
                return self.update_user("PUT", username, bank_key)
            elif add_or_remove == "Remove Access":
                return self.update_user("DELETE", username, bank_key)
            else:
                return "expected Add or Remove Access, got {}".format(add_or_remove)
        else:
            return None


    def loans_post_inst_meta_data(self, bank_key, sp_id, institution_type, regulatoryId):
        url = self.baseurl + '/Institutions/metadata'
        bank_name_types = {"012700000001XOeAAM": "Bank",
                            "012700000001XPCAA2": "CreditUnion",
                            "012700000001XP2AAM": "Bank",
                            "012700000001XPIAA2": "Bank",
                            "012700000001XtHAAU": "Bank",
                            "012700000001XP8AAM": "Bank"}
        institution_type = bank_name_types[institution_type]
        req_body = {
                "institutionKey": int(bank_key),
                "snlInstitutionId": int(sp_id),
                "institutionType": institution_type,
                "regulatoryId": regulatoryId}
        response = requests.request("POST", url, headers=self.headers, data=json.dumps(req_body))
        return response


    #summary": "Used to replace all modules for an institute.  Deletes all, then re-adds specified modules."
    def modules_replace(self, modules, institutionKey):
        url = self.baseurl + '/Modules/replace'
        req_body = {
                    "modules": modules,
                    "institutionKey": institutionKey}
        response = requests.request("POST", url, headers=self.headers, data=json.dumps(req_body))
        return response


    def modules_add_insititue(self, modules, institutionKey):
        url = self.baseurl + '/Modules'
        req_body = {
                    "modules": modules,
                    "institutionKey": institutionKey}
        response = requests.request("POST", url, headers=self.headers, data=json.dumps(req_body))
        return response


        # "summary": "Used to replace all modules for an user for an institute.  Deletes all, then re-adds specified modules.",
    def user_modules_replace(self, modules, institutionKey, useremail):
        url = self.baseurl + '/Modules/user/replace'
        req_body = {
                    "modules": modules,
                    "institutionKey": institutionKey,
                    "userEmail": useremail}
        response = requests.request("POST", url, headers=self.headers, data=json.dumps(req_body))
        return response


    def get_db_name(self, bankkey):
        url = self.baseurl + "institutions/" + str(bankkey)+'/database-name'
        # req_body = {"key": bankkey}
        response = requests.request("GET", url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None


    def get_users_by_key(self, bankkey):
        url = f"{self.baseurl}institutions/{bankkey}/users"
        response = requests.request("GET", url, headers=self.headers)
        return response.json()


    #for bankkey create
    def create_bankkey(self, name):
        url = f"{self.baseurl}/Institutions"
        req_body = {
                    "key": 0,
                    "name": name,
                    "displayName": name}
        response = requests.request("POST", url, headers=self.headers, data=json.dumps(req_body))
        return response.json()

    #for bankkey create
    def get_bankkey_by_regid(self, regulatoryId):
        url = f"{self.baseurl}Institutions/regulatory-id/{regulatoryId}"
        response = requests.request("GET", url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None


# Salesforce Bank Test 1; 0000001; 0017000001E1uZuAAJ
# dc = DCG_Core_API()
# creat = dc.create_bankkey("Salesforce Bank Test 1")
# dc.get_bankkey_by_regid("0000001")
# creat == None
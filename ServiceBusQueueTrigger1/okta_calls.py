import requests
import json
import os
import warnings
warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
from . config import env
from . salesforce_calls import Salesforce_Api
from . send_email import email_alert

def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test

class Okta_API():
    @ignore_warnings
    def __init__(self):
        self.base_url = env()["okta_base_url"]
        self.header_info = env()["okta_header"]
        self.app_dict = env()["app_dict"]

    def formatted_response(self, response):
        response_json = json.dumps(response.json())
        response_list = json.loads(response_json)
        return response_list


    def get_user_id_okta(self, email):
        response = requests.request("GET", f'{self.base_url}/api/v1/users/{email}', headers=self.header_info, data={})
        clean_response = self.formatted_response(response)
        return clean_response


    def get_group(self, id):
        response = requests.request("GET", self.base_url + '/api/v1/groups/' + id, headers=self.header_info, data={})
        return response.json()


    def get_users(self, id):
        response = requests.request("GET", f'{self.base_url}/api/v1/users/{id}/appLinks', headers=self.header_info, data={})
        return response.json()


    def list_all_users(self):
        response = requests.request("GET", self.base_url + '/api/v1/users?filter=status+eq+\"PROVISIONED\"', headers=self.header_info, data={})
        return response.json()


    def get_groups_assigned_to_app(self, appid):
        appid = str(self.app_dict[appid])
        response = requests.request("GET", f'{self.base_url}/api/v1/apps/{appid}/groups', headers=self.header_info, data={})
        return response.json()


    def suspend_user(self, user_id):
        response = requests.request("POST", self.base_url + "/api/v1/users/" + user_id + "/lifecycle/suspend", headers=self.header_info, data={})
        if response.status_code == 200:
            return 'Successfully suspended user id {} from okta'.format(user_id)
        else:
            removed_error = self.formatted_response(response)
            if len(removed_error["errorCauses"]) > 0:
                return removed_error["errorCauses"]
            else:
                return removed_error["errorSummary"]


    def unsuspend_user(self, user_id):
        response = requests.request("POST", self.base_url + "/api/v1/users/" + user_id + "/lifecycle/unsuspend", headers=self.header_info, data={})
        if response.status_code == 200:
            return 'Successfully reactivated user id {} to okta'.format(user_id)
        else:
            unsuspend_error = self.formatted_response(response)
            if len(unsuspend_error["errorCauses"]) > 0:
                return unsuspend_error["errorCauses"]
            else:
                return unsuspend_error["errorSummary"]


    def activate_user(self, userId):
        '''Activates a user

        This operation can only be performed on users with a 
        STAGED or DEPROVISIONED status. Activation of a user 
        is an asynchronous operation.
        '''
        response = requests.request("POST", self.base_url + f"/api/v1/users/{userId}/lifecycle/activate", headers=self.header_info)
        return self.formatted_response(response)    


    def create_activated_user_without_credentials(self, firstname, lastname, login):
        payload="{\n\"profile\": {\n\"firstName\": \""+str(firstname)+"\",\n\"lastName\": \""+str(lastname)+"\",\n\"email\": \""+login+"\",\n\"login\": \""+login+"\"\n}\n}"                 
        response = requests.request("POST", self.base_url + "/api/v1/users?activate=true", headers=self.header_info, data=payload)
        return self.formatted_response(response)


    def assign_user_to_app_for_sso(self, userid, product):
        appid = str(self.app_dict[product])
        url = self.base_url + "/api/v1/apps/" + appid + "/users"
        payload = "{\n  \"id\": \"" + userid + "\",\n  \"scope\": \"USER\",\n  \"credentials\": {\n\n  }\n}" 
        response = requests.request("POST", url, headers=self.header_info, data=payload)
        return self.formatted_response(response)


    def remove_user_from_app(self, user_id, product):
        appid = self.app_dict[product]
        url = self.base_url + "/api/v1/apps/" + appid + "/users/" + user_id
        response = requests.request("DELETE", url, headers=self.header_info, data={})
        if response.status_code == 204:
            return 'Successfully removed (okta) user id {} from app {}'.format(user_id, product)
        else:
            removed_error = self.formatted_response(response)
            if len(removed_error["errorCauses"]) > 2:
                return removed_error["errorCauses"]
            else:
                return removed_error["errorSummary"]


    def add_okta(self, get_all_fields_from_sf):
        new_user_id = self.create_activated_user_without_credentials(get_all_fields_from_sf["Firstname__c"], get_all_fields_from_sf["Lastname__c"], get_all_fields_from_sf["Email__c"])

        try:
            user_id = new_user_id["id"]
        except:
            return new_user_id["errorSummary"]

        self.assign_user_to_app_for_sso(user_id, "About D360")
        self.assign_user_to_app_for_sso(user_id, "About L360")
        self.assign_user_to_app_for_sso(user_id, "About P360")

        if get_all_fields_from_sf["is_Advisory__c"]:
            self.add_user_to_group(user_id, "DCGtools")

        sf = Salesforce_Api()
        sf.update_contact(get_all_fields_from_sf["Contact__c"], {"Okta_Login__c": get_all_fields_from_sf["Email__c"]})
        sf.update_access_request(get_all_fields_from_sf["Id"], {"okta_login_email_created__c": user_id})
        return user_id
            

    def okta_process_request(self, get_all_fields_from_sf, update_okta_login=False):
        product = get_all_fields_from_sf["Product__c"]
        add_or_remove = get_all_fields_from_sf["Access_Request__c"]
        okta_user_name = get_all_fields_from_sf["Okta_Login__c"]
        if not okta_user_name:
            okta_user_name = get_all_fields_from_sf["Email__c"]
            update_okta_login = True
            

        user = self.get_user_id_okta(okta_user_name)
        try:
            user_id = user["id"]
            user_status = user["status"]
            
            if update_okta_login:
                sf = Salesforce_Api()
                sf.update_contact(get_all_fields_from_sf["Contact__c"], {"Okta_Login__c": okta_user_name})     
        except KeyError:
            user_id = "not found"
            user_status = "not created"
        
        if add_or_remove == "Remove Access":
            if product == "okta":
                try:
                    return self.suspend_user(user_id)
                except:
                    return user_id
            elif "Loans360" in product:
                sf = Salesforce_Api()
                #check to see if they have more than 1 module, dont remove tile
                contactobject = sf.get_contact(get_all_fields_from_sf['Contact__c'])
                if contactobject["Loans360__c"] and contactobject["Loans360_Credit_Simulator__c"]:
                    return "another module remains; okta tile Successfully not removed"

            if user_status.lower() == 'provisioned':
                try:
                    return self.suspend_user(user_id)
                except:
                    return user_id


            remove_app = self.remove_user_from_app(user_id, product)

            if "Successfully" not in remove_app:
                remove_user_from_group = self.remove_user_from_group(user_id, product + "group")

                if "Successfully" not in remove_user_from_group:
                    return f'app: {remove_app}. group: {remove_user_from_group}'
                else:
                    email_alert("remove user from app fail", f'remove_user_from_app response: {remove_app}\n\n remove_user_from_group response: {remove_user_from_group}\n\n product: {product}\n\n okta_user_name: {okta_user_name}, \n\n     \n   https://darlingconsulting.lightning.force.com/lightning/r/Access_Request__c/{get_all_fields_from_sf["Id"]}/view', pers=True)
  

            return 'Successfully removed (okta) user id {} from {}'.format(user_id, product)


        elif add_or_remove == "Add Access":
            if user_status == "SUSPENDED":
                self.unsuspend_user(user_id)
            
            if user_status.lower() == 'deprovisioned':
                try:
                    add_okta_user_full = self.activate_user(user_id)
                except:
                    return "error in creating okta user please review"  

            if user_id == "not found":  
                try:
                    user_id = self.add_okta(get_all_fields_from_sf)
                except:
                    return "error in finding or creating okta user please review"      

            if product == "okta":
                return 'Successfully created user id {} for {}'.format(user_id, get_all_fields_from_sf["Email__c"])

            elif product == "MoveIt" or product == "okta MoveIT":
                add_to_product = self.assign_user_to_app_for_sso(user_id, product) 
                if "errorSummary" in add_to_product:
                    return add_to_product["errorSummary"]
                else:
                    return 'Successfully assigned {} to {}'.format(product, okta_user_name)

            else:  #(ex. add a 360 tool)          
                if "Loans360" not in product:
                    self.remove_user_from_app(user_id, "About " + product)
                self.add_user_to_group(user_id, "DCGtools")                    
                add_to_product = self.assign_user_to_app_for_sso(user_id, product)
                if "errorSummary" in add_to_product:
                    return add_to_product["errorSummary"]
                else:
                    return 'Successfully assigned {} to {}'.format(product, okta_user_name)
        else:
            #not an add or remove...for ex pw reset for okta 
            return "{} not yet automated".format(add_or_remove)    


    def is_core_needed(self, get_all_fields_from_sf):
        if get_all_fields_from_sf["Access_Request__c"] == "Add Access":
            return True
        okta_user_name = get_all_fields_from_sf["Okta_Login__c"]
        if not okta_user_name:
            okta_user_name = get_all_fields_from_sf["Email__c"]
        user_id = self.get_user_id_okta(okta_user_name)
        try:
            userid = user_id["id"]
        except KeyError:
            return False
        url = self.base_url + '/api/v1/apps/?filter=user.id+eq+\"' + str(userid) + '\"'
        response = requests.request("GET", url, headers=self.header_info, data={})
        clean_response = self.formatted_response(response)
        core_needed_values = ["0oa6w6n95qcxng0mJ0y6", "0oa6vc5xzCA1TdPON0y6", "0oa93x89tAbmeGitk0y6", "00g2wpcl5JLOEGGFUCCX", "00g2vxxgwXWLORIJGTTD", "00gscqjt1sKzlExPO0x7", "00g3aspi8AFILWVUWGXO", "0oar5m3w0xriPR4vJ0x7", "0oar5m3w0xriPR4vJ0x7"]
        try:
            for i in clean_response:
                if i["id"] in core_needed_values:
                    return False
                else:
                    continue
            return True
        except:
            return "cannot confirm"




    def add_user_to_group(self, user_id, group):
        appid = self.app_dict[group]
        url = self.base_url + "/api/v1/groups/" + appid + "/users/" + user_id
        response = requests.request("PUT", url, headers=self.header_info, data={})
        if response.status_code == 204:
            return 'Successfully added (okta) user id {} to {}'.format(user_id, group)
        else:
            add_error = self.formatted_response(response)
            if len(add_error["errorCauses"]) > 2:
                return add_error["errorCauses"]
            else:
                return add_error["errorSummary"]


    def remove_user_from_group(self, user_id, group):
        appid = self.app_dict[group]
        url = f'{self.base_url}/api/v1/groups/{appid}/users/{user_id}'
        response = requests.request("DELETE", url, headers=self.header_info, data={})
        if response.status_code == 204:
            return 'Successfully removed (okta) user id {} from group {}'.format(user_id, group)
        else:
            removed_error = self.formatted_response(response)
            if len(removed_error["errorCauses"]) > 2:
                return removed_error["errorCauses"]
            else:
                return removed_error["errorSummary"]



    def get_user_applinks(self, okta_id):
        response = requests.request("GET", f'{self.base_url}/api/v1/users/{okta_id}/appLinks', headers=self.header_info, data={})
        clean_response = self.formatted_response(response)
        return clean_response
    
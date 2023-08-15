import requests
import json
from . salesforce_calls import Salesforce_Api
import time
import pickle
from . send_email import email_alert
import os

class moveit_api():

    def __init__(self, get_all_fields_from_sf):
        requests.packages.urllib3.disable_warnings()

        self.token_path = '/api/v1/token'
        self.base_uri = 'https://dcgfile.darlingconsulting.com'
        self.token_endpoint = self.base_uri + self.token_path
        self.userName = os.environ['moveitusername']
        self.password = os.environ['moveitpw']
        self.token = self.generateToken()
        self.headers = {
                        'content-type': "application/json;charset=UTF-8",
                        'authorization': "Bearer " + self.token}
        self.sf_request_id = get_all_fields_from_sf["Id"]
        self.sf_add_or_remove = get_all_fields_from_sf["Access_Request__c"]
        self.user = get_all_fields_from_sf["Okta_Login__c"]
        self.email = get_all_fields_from_sf["Email__c"]
        self.user_id = None
        if self.user:
            self.dcg_employee = self.user.split("@")[-1].lower() == "darlingconsulting.com"
        else:
            self.dcg_employee = None
        self.product = get_all_fields_from_sf["Product__c"]
        self.folder_name_requested = get_all_fields_from_sf.get("Folder_Name__c", None)
        self.default_group_name_requested = get_all_fields_from_sf.get("Default_MoveIt_Security_Group__c", None)


        self.bankname = get_all_fields_from_sf["Account_Name__c"]
        self.stateabbreviation = get_all_fields_from_sf["State__c"]
        self.certificate_charter_holdingco = get_all_fields_from_sf["Cert_or_Charter__c"]
        self.bank_level_root_raw = f"{self.bankname} - {self.stateabbreviation} - {self.certificate_charter_holdingco}" 
        self.bank_level_root = self.bank_level_root_raw.lower()

        self.get_all_fields_from_sf = get_all_fields_from_sf



    def generateToken(self):
        payload = {'username': self.userName, 'password': self.password, 'grant_type': 'password'}
        r = requests.post(self.token_endpoint, data=payload)
        my_token = r.json()['access_token']
        return my_token


    def _get_all(self, searchtype):
        results = self._get_pages(searchtype)
        if searchtype == "users":
          name_to_id_dict = {i["email"].lower(): i["id"] for i in results}
        else:
          name_to_id_dict = {i["name"].lower(): i["id"] for i in results}
        with open(f'moveit_ids/{searchtype}.pickle', 'wb') as handle:
            pickle.dump(name_to_id_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return name_to_id_dict


    def _get_pages(self, searchtype, pgnum=1, limit_page_count=100000):
        ''' return list of records 
            applies to groups/users/files/folders. 
        
        '''
        types = ['groups', 'users', 'files', 'folders']
        if searchtype.lower() not in types:
            raise ValueError("Invalid type. Expected one of: %s" % types)

        url =f'{self.base_uri}/api/v1/{searchtype}?page={str(pgnum)}&perPage=3000'
        users_list = requests.get(url, headers=self.headers)

        try:
            results = users_list.json()["items"]
        except KeyError:
            try:
                time.sleep(1)
                headers = self.headers
                users_list = requests.get(url, headers=headers)

                results = users_list.json()["items"]
            except KeyError:
                self.status_update_on_hold(self.sf_request_id, (f'key error with items on {str(type)} search on pgnum = {str(pgnum)}.....\n here is the content: {str(users_list.content)}'))
                return
        
        total_pgs = users_list.json()["paging"]["totalPages"]
        if pgnum < int(total_pgs) and pgnum < int(limit_page_count):
            results.extend(self._get_pages(searchtype, pgnum=pgnum+1))
        return results


    def add_member_to_group(self, groupId):
        payload = {"id": self.user_id,
                    "userIds": [self.user_id]}
        users_list = requests.post(f'{self.base_uri}/api/v1/groups/{groupId}/members', data=json.dumps(payload), headers=self.headers)
        return users_list


    def get_list_of_subfolders(self, parentid):
        url =f'{self.base_uri}/api/v1/folders/{parentid}/subfolders'
        users_list = requests.get(url, headers=self.headers)
        try:
            results = users_list.json()["items"]
        except KeyError:
            results = []
        return results


    def get_folder_details(self, parentid):
        url =f'{self.base_uri}/api/v1/folders/{parentid}/'
        users_list = requests.get(url, headers=self.headers)
        results = users_list.json()
        return results

    def get_folder_details_acls(self, parentid):
        url =f'{self.base_uri}/api/v1/folders/{parentid}/acls'
        users_list = requests.get(url, headers=self.headers)
        results = users_list.json()
        return results


    def folders_user_can_view(self, moveitid):
        url =f'{self.base_uri}/api/v1/folders?user={moveitid}'
        users_list = requests.get(url, headers=self.headers)
        results = users_list.json()
        return results

    def cur_user(self, email):
        url =f'{self.base_uri}/api/v1/users?username={email}&perPage=3000'
        users_list = requests.get(url, headers=self.headers)
        results = users_list.json()
        return results


    def create_user(self, email):
        payload = {"fullName": email,
                    "username": email,
                    "email": email,
                    "permission": "User",
                    "receivesNotification": "ReceivesNoNotifications",
                    "orgID": 6097,
                    "password": "DarlingConsultingGroup43!"}
        users_list = requests.post(f'{self.base_uri}/api/v1/users', data=json.dumps(payload), headers=self.headers)
        return users_list


    def create_subfolder(self, new_folder_name, parent_folder_id='172364921'):
        payload = {
                    "inheritPermissions": "None",
                    "name": f"{new_folder_name}"
                    }
        resposnse = requests.post(f'{self.base_uri}/api/v1/folders/{parent_folder_id}/subfolders', data=json.dumps(payload), headers=self.headers)
        return resposnse.json()


    def _change_maint_settings(self, folderid):
        payload = {
                    "folderCleanup": {
                        "isCleanupEnabled": "true",
                        "deleteOldFilesAfterDays": 180,
                        "deleteEmptySubfoldersAfterDays": 0
                    },
                    "displayNewFilesForDays": 7,
                    "folderQuota": {
                        "quota": 3000,
                        "quotaLevel": "MB",
                        "applyToFilesInSubfolders": "true"
                    },
                    "applyToSubfolders": "true"
                    }
        resposnse = requests.patch(f'{self.base_uri}/api/v1/folders/{folderid}/maintenance', data=json.dumps(payload), headers=self.headers)
        return resposnse.json()

    def _change_misc_settings(self, folderid):
        payload = {
                    "hideHistory": "true",
                    "createThumbnails": "false",
                    "enforceUniqueFilenames": "true",
                    "allowFileOverwrite": "true",
                    "customSortField": "None"
                    }
        resposnse = requests.patch(f'{self.base_uri}/api/v1/folders/{folderid}/miscellaneous', data=json.dumps(payload), headers=self.headers)
        return resposnse.json()


    def create_group(self, group_name):
        payload = {"name": f"{group_name}",
                    "description": "Group"}
        resposnse = requests.post(f'{self.base_uri}/api/v1/groups', data=json.dumps(payload), headers=self.headers)
        return resposnse.json()


    def delete_user(self):
        response = requests.delete(f'{self.base_uri}/api/v1/users/{self.user_id}', headers=self.headers)
        return response


    def add_group_to_folder(self, groupId, folderid, permissions_dict):
        notify = permissions_dict["notify"]
        admin = permissions_dict["admin"]
        write_and_delete = permissions_dict["write_and_delete"]

        payload = {"notificationMessage": "string",
                    "type": "Group",
                    "id": str(groupId),
                    "permissions": {"readFiles": "true",
                                    "writeFiles": f"{write_and_delete}",
                                    "deleteFiles": f"{write_and_delete}",
                                    "listFiles": "true",
                                    "notify": f"{notify}",
                                    "addDeleteSubfolders": "false",
                                    "share": "true",
                                    "sharePermissions": {"readFiles": "true",
                                                        "writeFiles": f"{write_and_delete}",
                                                        "deleteFiles": f"{write_and_delete}",
                                                        "listFiles": "true",
                                                        "notify": f"{notify}",
                                                        "listUsers": "false"},
                                                        "admin": f"{admin}",
                                                        "listUsers": "false"}}
        users_list = requests.post(f'{self.base_uri}/api/v1/folders/{folderid}/acls', data=json.dumps(payload), headers=self.headers)
        return users_list


    def remove_member_from_group(self, Id):
        users_list = requests.delete(f'{self.base_uri}/api/v1/groups/{Id}/members/{self.user_id}', headers=self.headers)
        return users_list


    def get_members_by_groupid(self, Id):
        users_list = requests.get(f'{self.base_uri}/api/v1/groups/{Id}/members/', headers=self.headers)
        return users_list.json()


    def status_update_on_hold(self, access_id, status_message):
        email_alert("moveit request put on hold", f'{status_message}    \n     \n   https://darlingconsulting.lightning.force.com/lightning/r/Access_Request__c/{access_id}/view', pers=True)
        data = {"Access_Status__c": "On Hold",
                "okta_status__c": status_message}
        sf = Salesforce_Api()
        sf.update_access_request(access_id, data)
        return


    def status_update_success(self, access_id, status_message):
        data = {"Access_Status__c": "Completed",
                "Auto_Completed_API__c": True,
                "okta_status__c": status_message}
        sf = Salesforce_Api()
        sf.update_access_request(access_id, data)
        return




    def get_logs(self, startdate, pgnum=1):
        url =f'{self.base_uri}/api/v1/logs?page={str(pgnum)}&perPage=500&action=3&successFailure=Success&startDateTime={startdate}'
        users_list = requests.get(url, headers=self.headers)
        results = users_list.json()["items"]
        total_pgs = users_list.json()["paging"]["totalPages"]
        if pgnum < int(total_pgs):
            results.extend(self.get_logs(startdate=startdate, pgnum=pgnum+1))
        return results
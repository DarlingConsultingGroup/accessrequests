from . salesforce_calls import Salesforce_Api
import requests
import os
import json

class moveitbackfill():
    '''dcgfile goes to old moveit, newfile goes to new'''

    def __init__(self, site):
        self.token_path = '/api/v1/token'
        self.base_uri = f'https://{site}.darlingconsulting.com'
        self.token_endpoint = self.base_uri + self.token_path
        self.userName = os.environ['moveitusername']
        self.password = os.environ['moveitpw']
        self.token = self.generateToken()
        self.headers = {
                        'content-type': "application/json;charset=UTF-8",
                        'authorization': "Bearer " + self.token}

    def generateToken(self):
        payload = {'username': self.userName, 'password': self.password, 'grant_type': 'password'}
        r = requests.post(self.token_endpoint, data=payload)
        my_token = r.json()['access_token']
        return my_token


    def _get_pages(self, searchtype, pgnum=1, limit_page_count=100000):
        ''' return list of records 
            applies to groups/users/files/folders. 
        
        '''
        types = ['groups', 'users', 'files', 'folders']
        if searchtype.lower() not in types:
            raise ValueError("Invalid type. Expected one of: %s" % types)

        url =f'{self.base_uri}/api/v1/{searchtype}?page={str(pgnum)}&perPage=3000'
        users_list = requests.get(url, headers=self.headers)
        results = users_list.json()["items"]        
        total_pgs = users_list.json()["paging"]["totalPages"]
        if pgnum < int(total_pgs) and pgnum < int(limit_page_count):
            results.extend(self._get_pages(searchtype, pgnum=pgnum+1))
        return results



    def create_subfolder(self, new_folder_name, parent_folder_id='172364921'):
        '''parent_folder_id should be dcg server / org level, not the bank level. default corresponds to existing dcgfile server, not new'''
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


    def get_members_by_groupid(self, Id):
        users_list = requests.get(f'{self.base_uri}/api/v1/groups/{Id}/members/', headers=self.headers)
        return users_list.json()


    def folders_user_can_view(self, moveitid):
        url =f'{self.base_uri}/api/v1/folders?user={moveitid}'
        users_list = requests.get(url, headers=self.headers)
        results = users_list.json()
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







    def add_member_to_group(self, userid, groupId):
        payload = {"id": userid,
                    "userIds": [userid]}
        users_list = requests.post(f'{self.base_uri}/api/v1/groups/{groupId}/members', data=json.dumps(payload), headers=self.headers)
        return users_list












        
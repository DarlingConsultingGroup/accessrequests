import requests
import json
from . import constants
from . salesforce_calls import Salesforce_Api
from . okta_calls import Okta_API
from . send_email import email_alert
import copy
import time
import logging
from ServiceBusQueueTrigger1.moveit_api import moveit_api
import pickle
import datetime



class moveit_calls(moveit_api):

    def __init__(self):
        self.result = None #Hold, Success
        self.return_text_for_sf = None




    def moveit_process_request(self):

        if self.sf_add_or_remove != "Add Access" and self.sf_add_or_remove != "Remove Access":
            self.result = "Hold" 
            self.return_text_for_sf = "automation needs Access_Request__c = 'Add Access' or 'Remove Access'"
            return
        
        if self.folder_name_requested is None and self.product not in ["MoveIt", "okta MoveIT"]:
            self.result = "Hold" 
            self.return_text_for_sf = "automation needs folder name"
            return


        self.user_id = self.get_user_id() 
        if not self.user_id and self.sf_add_or_remove == "Add Access":
            self._create_user()



        if self.product in ["MoveIt", "okta MoveIT"]: 
            if self.sf_add_or_remove == "Add Access":
                self.result = "Success" 
                self.return_text_for_sf = f'{self.user} exists in moveit and okta'
            else:
                if self.user_id:
                    response = self.delete_user()
                ok = Okta_API()
                add_moveit_tile = copy.copy(self.get_all_fields_from_sf)
                add_moveit_tile["Product__c"] = "MoveIt"
                okta_response = ok.okta_process_request(add_moveit_tile)
                
                if ("Successfully" in okta_response or "not found" in okta_response) and (self.user_id is None or response.status_code == 204 or str(response.json()["title"]) == 'Resource Not Found'):
                    self.result = "Success" 
                    self.return_text_for_sf = str(response)
                    return
                else:
                    self.result = "Hold"
                    self.return_text_for_sf = str(okta_response)
            return

        self.group_name_requested = self.get_requested_group_name()

        group_id = self.get_group_id(self.group_name_requested)

        folder_id_list = self.get_folder_id()
        requested_folder_id = folder_id_list[0]
        if requested_folder_id is None:
            return 
        user_internal_groups_list = []
        if self.dcg_employee:
            for dcg_group_id in constants.dcg_internal_group.values():
                group_members = self.get_members_by_groupid(dcg_group_id)
                for users in group_members["items"]:
                    if users["email"].lower() == self.user.lower():
                        user_internal_groups_list.append(dcg_group_id)
                        break
            if len(user_internal_groups_list) == 1:
                if self.sf_add_or_remove == "Add Access":
                    internal_group_id = user_internal_groups_list[0]
                    permissions = constants.group_names_permissions(self.bank_level_root)[self.group_name_requested]
                    response = self.add_group_to_folder(internal_group_id, requested_folder_id, permissions)

            elif len(user_internal_groups_list) > 1 and 297601 and 297701 not in user_internal_groups_list:
                self.result = "Hold" 
                self.return_text_for_sf = f'dont know which group to {self.sf_add_or_remove}, user in mulitple dcg groups'
                return



        if self.sf_add_or_remove == "Add Access":
            response = self.add_member_to_group(group_id)
            permissions = constants.group_names_permissions(self.bank_level_root)[self.group_name_requested]
            response = self.add_group_to_folder(group_id, requested_folder_id, permissions)
            if response.status_code == 409:
                self.result = "Success" 
                self.return_text_for_sf = f'{str(response.json()["title"])}: {str(response.json()["detail"])}'
                return
        elif self.sf_add_or_remove == "Remove Access":
            response = self.remove_member_from_group(group_id)
            if str(response.json()["title"]) == 'Resource Not Found':
                self.result = "Success" 
                self.return_text_for_sf = f'{str(response.json()["title"])}: {str(response.json()["detail"])}'
                return
            
        if response.status_code >= 200 and response.status_code < 300:
            self.result = "Success" 
            self.return_text_for_sf = f'completed {self.sf_add_or_remove} for {self.group_name_requested}'
        else:
            self.result = "Hold" 
            self.return_text_for_sf = f'dont know which group to {self.sf_add_or_remove}, user in mulitple dcg groups'
        return




    def check_pickle(self, type, name):
      '''takes name of group/user/folder and returns moveitid
      
      params:
        type: users, groups, folders
        name: username, foldername, or group name as it would appear in moveit
        '''
        
      with open(f'moveit_ids/{type}.pickle', 'rb') as handle:
        try:
            b = pickle.load(handle)
        except EOFError:
            return None
        return b.get(name, None)
        

    def get_group_id(self, name):
        group_id = self.check_pickle("groups", name)
        
        if not group_id:
            group_dict_lower_keys = self._get_all("groups")
            try:
                group_id = group_dict_lower_keys[name.lower()]
            except KeyError:
                try:
                    name_w_leading_0 = name.lower().split("-")
                    name_w_leading_0[-1] = " 0"+name_w_leading_0[-1].replace(" ", "")
                    group_id = group_dict_lower_keys["-".join(name_w_leading_0)]
                except KeyError:
                    id_list = [group_dict_lower_keys[k] for k in group_dict_lower_keys.keys() if name.split(' - ',1)[1].lower() == k.split(' - ',1)[-1]]

                    if len(id_list) == 0 and self.sf_add_or_remove == "Add Access":
                        group_id = self.create_group(name)                    
                    elif len(id_list) == 1:
                        group_id = id_list[0]
                    else:
                        self.result = "Hold" 
                        self.return_text_for_sf = f'couldnt find match for {name.lower()} in groups master_dict'
        return group_id


    def get_folder_id(self):
        ''' returns [desired folder id, parent folder id of bank]'''
        parent_folder_id = self._get_parent_folder_id()
        folder_id = self._get_requested_folder_id(parent_folder_id)
        return [folder_id, parent_folder_id]


    def _get_requested_folder_id(self, parent_folder_id):
        list_of_subfolders = self.get_list_of_subfolders(parent_folder_id)
        folder_id = None

        sub_names = []
        for i in list_of_subfolders:
            if i["name"].lower() == self.folder_name_requested.lower():
                folder_id = i["id"]
            sub_names.append(i["name"])

        if not folder_id:
            if self.sf_add_or_remove == "Add Access":
                folder_response = self.create_subfolder(self.folder_name_requested, parent_folder_id=parent_folder_id)
                try:
                    folder_id = folder_response["id"]
                except KeyError:
                    logging.info(f'folder_response: {str(folder_response)}...parent_folder_id: {str(parent_folder_id)}')
                    self.result = "Hold" 
                    self.return_text_for_sf = f'couldnt find folder id and then tried to create "{self.folder_name_requested}" but that likely already exists. {folder_response}'
                    return
            else:
                logging.info(f'folder not found, nothing to remove')
                return self.status_update_success(self.sf_request_id, f'could not find {self.folder_name_requested}. nothing to remove from')

        try:
            groups_for_folder = constants.get_groups_for_folder_creation(self.bank_level_root)[self.folder_name_requested]
        except KeyError:
            try:
                groups_for_folder = constants.get_groups_for_folder_creation(self.bank_level_root)[self.folder_name_requested.split(" - ")[-1]]
            except KeyError:
                groups_for_folder = []
        
        for group in groups_for_folder:
            if group in constants.dcg_internal_group.keys():
                permissions = constants.group_names_permissions(self.bank_level_root)[group]
                add_internalgrou_to_childfolder = self.add_group_to_folder(constants.dcg_internal_group[group], folder_id, permissions)  

        moveit_group_from_sf_ticket = constants.default_groups_sf_to_moveit.get(self.default_group_name_requested)
        if moveit_group_from_sf_ticket:
            permissions = constants.group_names_permissions(self.bank_level_root)[moveit_group_from_sf_ticket]
            self.add_group_to_folder(constants.dcg_internal_group[moveit_group_from_sf_ticket], folder_id, permissions) 
        return folder_id


    def _search_for_parent_folder_id(self, dict_to_search):
        parent_folder_id = None
        try:
            parent_folder_id = dict_to_search[self.bank_level_root]
        except TypeError:
            return parent_folder_id
        except KeyError:
            try:
                name_w_leading_0 = self.bank_level_root.split("-")
                name_w_leading_0[-1] = " 0"+name_w_leading_0[-1].replace(" ", "")
                parent_folder_id = dict_to_search["-".join(name_w_leading_0)]
            except KeyError:
                id_list = [dict_to_search[k] for k in dict_to_search.keys() if self.bank_level_root.split(' - ',1)[1] == k.split(' - ',1)[-1]]
                if len(id_list) == 1:
                    parent_folder_id = id_list[0]
                elif len(id_list) != 0:
                    self.status_update_on_hold(self.sf_request_id, (f'couldnt find folder match for {self.bank_level_root} in folders master_dict'))
                    return
        return parent_folder_id


    def _get_parent_folder_id(self, retry=True):
        # search for folder with pickled dict

        parent_folder_id = self.check_pickle("folders", self.bank_level_root)

        if not parent_folder_id:
            parent_folder_id = self._search_for_parent_folder_id(self._get_all("folders"))
            
        if not parent_folder_id and self.sf_add_or_remove == "Add Access":
            try:
                parent_folder_repsonse = self.create_subfolder(self.bank_level_root_raw)  
                parent_folder_id = parent_folder_repsonse["id"]  
                self._change_maint_settings(parent_folder_id)
                self._change_misc_settings(parent_folder_id) 
            except KeyError as e:
                if retry:
                    return self._get_parent_folder_id(retry=False)
                else:
                    message = f'couldnt find parent_folder_id, failed creating "{self.bank_level_root_raw}" due to: {str(e)}'
                    self.status_update_on_hold(self.sf_request_id, message)
                    return message
                email_alert("moveit access request error", f"exception: {str(e)} \n expecting parent folder ID to come back but instead got: {str(parent_folder_repsonse)}", pers=True)
                return e  
        return parent_folder_id


        
    def _create_user(self):
        created_user = self.create_user(self.user)
        found_on_retry = False
        try:
            self.user_id = created_user.json()["id"]
        except KeyError:
            time.sleep(10)
            refreshed_users_dict = self._get_all("users")
            self.user_id = refreshed_users_dict.get(self.user.lower(), None)
            found_on_retry = True
            if self.user_id is None:
                self.status_update_on_hold(self.sf_request_id, f'couldnt find moveit userId, failed creating: {str(created_user)}')
                return


        ok = Okta_API()
        add_moveit_tile = copy.copy(self.get_all_fields_from_sf)
        add_moveit_tile["Product__c"] = "MoveIt"
        okta_response = ok.okta_process_request(add_moveit_tile)
        if "Successfully" not in okta_response or created_user.status_code != 201: 
            time.sleep(5)
            okta_response = ok.okta_process_request(add_moveit_tile)

            if "Successfully" not in okta_response: 
                self.status_update_on_hold(self.sf_request_id, f'{okta_response}. Line 274')
                return
            else:
                if self.sf_add_or_remove == "Add Access":
                    if created_user.status_code not in [201, 409]:
                        self.status_update_on_hold(self.sf_request_id, f'{okta_response}. Line 278')
                        return
                else:
                    if created_user.status_code != 201:
                        self.status_update_on_hold(self.sf_request_id, f'{okta_response}. Line 283')
                        return
        return self.user_id


    def get_user_id(self):
        if not self.user:
            self.user = self.email
            self.dcg_employee = self.user.split("@")[-1].lower() == "darlingconsulting.com"

        self.user_id = self.check_pickle("users", self.user)

        if not self.user_id:
            refreshed_users_dict = self._get_all("users")
            self.user_id = refreshed_users_dict.get(self.user.lower(), None)
        return self.user_id



    def get_requested_group_name(self):
        ''' return a list where [bank_level_group_name, group_name]
        '''
        if not self.folder_name_requested:
            self.status_update_on_hold(self.sf_request_id, "Folder_Name__c is blank where there should be a value, as it is a moveit folder request")
            return

        if self.dcg_employee:
            try:
                group_name = self.bank_level_root + constants.dcg_contact_group_suffix[self.folder_name_requested]
            except KeyError:
                group_name = self.bank_level_root + constants.dcg_contact_group_suffix[self.folder_name_requested.split(" - ")[-1]]
        if not self.dcg_employee:
            try:
                group_name = self.bank_level_root + constants.not_dcg_contact_group_suffix[self.folder_name_requested]
            except KeyError:
                group_name = self.bank_level_root + constants.not_dcg_contact_group_suffix[self.folder_name_requested.split(" - ")[-1]]
        return group_name

from . config import env
import warnings
warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test


class Salesforce_Api():
    @ignore_warnings
    def __init__(self):
        self.client = env()["sf_client"]

    def get_access_request(self, sf_recordid):
        pull_list = {}
        for key, value in self.client.sobjects.Access_Request__c.get(sf_recordid).items():
            pull_list.update({key: value})
        return pull_list


    def get_case(self, sf_recordid):
        pull_list = {}
        for key, value in self.client.sobjects.Case.get(sf_recordid).items():
            pull_list.update({key: value})
        return pull_list


    def create_case(self, data):
        return self.client.sobjects.Case.insert(data)


    def get_contact(self, sf_recordid):
        pull_list = {}
        for key, value in self.client.sobjects.Contact.get(sf_recordid).items():
            pull_list.update({key: value})
        return pull_list


    def get_account(self, sf_recordid):
        pull_list = {}
        for key, value in self.client.sobjects.Account.get(sf_recordid).items():
            pull_list.update({key: value})
        return pull_list


    def update_access_request(self, sf_recordid, data):
        return self.client.sobjects.Access_Request__c.update(sf_recordid, data)


    def update_contact(self, sf_recordid, data):
        return self.client.sobjects.Contact.update(sf_recordid, data)


    def update_case(self, sf_recordid, data):
        return self.client.sobjects.Case.update(sf_recordid, data)


    def update_account(self, sf_recordid, data):
        return self.client.sobjects.Account.update(sf_recordid, data)


    def prep_response(self, dcgapiresponse, okta_response, add_or_remove):
        if not dcgapiresponse:
            dcgapiresponse = 'not called'
        if "Successfully" in okta_response and "not called" in dcgapiresponse:
                data = {"Access_Status__c": "Completed",
                        "Auto_Completed_API__c": True,
                        "okta_status__c": str(okta_response),
                        "sysadmin_status__c": str(dcgapiresponse)}

        elif "Successfully" in okta_response and "Successfully" in dcgapiresponse:
            data = {"Access_Status__c": "Completed",
                    "Auto_Completed_API__c": True,
                    "okta_status__c": str(okta_response),
                    "sysadmin_status__c": str(dcgapiresponse)}

        elif ("not found" in okta_response or 'Cannot suspend a user that is not active' in str(okta_response)) and add_or_remove == "Remove Access" and ("not called" in dcgapiresponse or "Successfully" in dcgapiresponse):
            data = {"Access_Status__c": "Completed",
                "Auto_Completed_API__c": True,
                "okta_status__c": str(okta_response),
                "sysadmin_status__c": str(dcgapiresponse)}
        else:
            data = {"Access_Status__c": "On Hold",
                    "okta_status__c": str(okta_response),
                    "sysadmin_status__c": str(dcgapiresponse)}

        return data
        
    def query_salesforce(self, querystring):
        return self.client.sobjects.query(querystring)



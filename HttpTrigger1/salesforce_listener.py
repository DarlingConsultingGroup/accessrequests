import xmltodict


class salesforce_listener():
    
    def __init__(self, obm):
        self.full_message = xmltodict.parse(obm)
        self.notifications = self.full_message['soapenv:Envelope']['soapenv:Body']['notifications']['Notification']
        self.session_id = self.full_message['soapenv:Envelope']['soapenv:Body']['notifications']['SessionId']

    def access_request_ids(self):
        access_request_id_list = []
        if isinstance(self.notifications, list):
            for access_requests in self.notifications:
                access_request_id_list.append(access_requests['sObject']['sf:Id'])
        else:
            access_request_id_list.append(self.notifications['sObject']['sf:Id'])
        return access_request_id_list
    
    def get_accounts_to_send(self):
        account = []
        if isinstance(self.notifications, list):
            for access_requests in self.notifications:
                account.append(access_requests['sObject'])
        else:
            account.append(self.notifications['sObject'])
        return account


    def send_acknowledgment_to_sf(self):
        return '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" ' \
           'xmlns:out="http://soap.sforce.com/2005/09/outbound"><soapenv:Header/><soapenv:Body><out' \
           ':notificationsResponse><out:Ack>true</out:Ack></out:notificationsResponse></soapenv:Body></soapenv' \
           ':Envelope> ' 
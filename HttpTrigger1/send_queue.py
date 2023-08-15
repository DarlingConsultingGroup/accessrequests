
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

connstr = os.environ['AC_SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['AC_SERVICE_BUS_QUEUE_NAME']

def send_que(accessid):
    with ServiceBusClient.from_connection_string(connstr) as client:
        with client.get_queue_sender(queue_name) as sender:
            # Sending a single message
            single_message = ServiceBusMessage(accessid)
            sender.send_messages(single_message)




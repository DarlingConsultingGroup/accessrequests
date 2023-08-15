import pathlib
from context import ServiceBusQueueTrigger1
from context import moveitchecker


from moveitchecker.utlities import currentEasternTimestampString
from moveitchecker.blobUpdater import blobUpdater
from moveitchecker.getDepositClients import moveitSalesforceData


mv = moveitSalesforceData()

bs = mv.getDepositClientList(refresh=True)


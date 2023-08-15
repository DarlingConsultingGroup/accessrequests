import pathlib
from context import ServiceBusQueueTrigger1
from context import moveitchecker


from moveitchecker.utlities import currentEasternTimestampString
from moveitchecker.blobUpdater import blobUpdater



df = pd.read_csv(r"C:/Users/cbarry/python/access-requests/tests/outSalesforce.csv")

self.blob = 'testBlob.csv'

bs._updateBlob()

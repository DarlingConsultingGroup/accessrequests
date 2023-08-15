from azure.storage.blob import BlobServiceClient
import csv
import io
import pandas as pd
import os
import logging
from datetime import datetime, timedelta
from moveitchecker.utlities import currentEasternTimestampString



class blobUpdater:
    def __init__(self):
        container_name = "moveitlogs"
        blob_service_client = BlobServiceClient.from_connection_string(os.environ['moveitlogsConnectionString'])
        self.container_client = blob_service_client.get_container_client(container_name)
        self.blobNameIn = "inSalesforce.csv"
        self.blobNameOut = "outSalesforce.csv"
        self.blobNameTimestamp = "moveitLastPollTimestamp.txt"
        self.blob = ''


    def updateBlobIn(self, data):
        self.blob = self.blobNameIn
        self._updateBlob(data)
        return


    def updateBlobOut(self, data):
        self.blob = self.blobNameOut
        self._updateBlob(data)
        return


    def writeTimestampFile(self, timestamp_str):
        blob_client = self.container_client.get_blob_client(self.blobNameTimestamp)
        response = blob_client.upload_blob(timestamp_str, overwrite=True)
        return response


    def readTimestampFile(self):
        blob_client = self.container_client.get_blob_client(self.blobNameTimestamp)
        timestamp_str = blob_client.download_blob().readall().decode("utf-8")
        return timestamp_str


    def _updateBlob(self, dataForBlob):
        df = pd.DataFrame(dataForBlob).to_csv(index=None, header=None, encoding='utf-8')
        if self.container_client.get_blob_client(self.blob).exists():
            blob_client = self.container_client.get_blob_client(self.blob)
            if not blob_client.exists():
                blob_client.create_append_blob()
            response = blob_client.append_block(data=df, length=len(df))
            logging.info(f"mvy log updated {self.blob} with {len(dataForBlob)} records at {currentEasternTimestampString(lookbackMinutes=0)}")
            return response
        else:
            return False




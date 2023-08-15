import unittest
import pathlib
import pandas as pd
# from ServiceBusQueueTrigger1 import constants
from context import ServiceBusQueueTrigger1
import json
import csv


TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()


extract = pd.read_csv("S:\Security\MOVEit Incident\manualedits_foldersImpacted_to_sfAccount_ID_18__c.csv")

salesforce = pd.read_csv(r"C:/Users/cbarry/Desktop/report1689016159928.csv", encoding='latin1')

list(set(extract["Account_ID_18__c"].unique().tolist()).difference(salesforce["Account ID (18)"].unique().tolist()))



    


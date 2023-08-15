import os
from salesforce_api import Salesforce
import warnings
warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

#set "prod" or "dev" to define environment variables
# okta is to prod regardless. dev is for sandbox, sys admin tables

prod_or_dev = "prod" 

def env():
    if prod_or_dev == "prod":
        environment_variable = {
            "okta_base_url": "https://dcg.okta.com",
            "okta_header": {'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'Authorization': os.environ['okta_header_one_prod']},
            #salesforce : okta app ids
            "app_dict": {"About D360": '0oa68ogj9VBMCu2wp0y6',
                        "About L360": '0oa5b2tuam10CEsCn0y6',
                        "About P360": '0oa6a9nq05k0Csm5k0y6',
                        "D360": '0oa6w6n95qcxng0mJ0y6',
                        "L360": '0oa6vc5xzCA1TdPON0y6',
                        "P360": '0oa93x89tAbmeGitk0y6',
                        "Loans360": '0oar5m3w0xriPR4vJ0x7',
                        "Loans360 - Credit Simulator": '0oar5m3w0xriPR4vJ0x7',
                        "DCGtools": "00g2wpe4lNDIMOQSTDNC",
                        "Data Analytics": "0oa6uwj6ycYOVZfqu0y6",
                        "okta MoveIT": "0oa7i78ecyAO9WVtG0y6", #same as MoveIt
                        "MoveIt": "0oa7i78ecyAO9WVtG0y6",
                        ###########groupIDs#####################
                        "D360group": '00g2wpcl5JLOEGGFUCCX',
                        "L360group": '00g2vxxgwXWLORIJGTTD',
                        "Loans360group": '00gscqjt1sKzlExPO0x7',
                        "Loans360 - Credit Simulatorgroup": '00gscqjt1sKzlExPO0x7', 
                        "P360group": '00g3aspi8AFILWVUWGXO',
                        "okta MoveITgroup": "0oa7i78ecyAO9WVtG0y6", # same as app
                        "MoveItgroup": "0oa7i78ecyAO9WVtG0y6", # same as app
},
            "sf_client": Salesforce(username=os.environ['apiuser'],
                                    password=os.environ['apipw'],
                                    security_token=os.environ['apitoken']),
            "dcgapi_base_url":os.environ['dcgapi_base_url']
        }
        
    elif prod_or_dev == "dev":
        environment_variable = {
            "okta_base_url" : "https://dcg.okta.com",
            "okta_header" : {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'Authorization': os.environ['okta_header_one_prod']},
            "app_dict" :  {"L360": '0oaoqd0rufRDvBdt70x7',
                            "D360": '0oaordme5ahMx2wNV0x7',
                            "P360": '0oaordme5ahMx2wNV0x7',
                            "About D360": '0oa68ogj9VBMCu2wp0y6',
                            "About L360": '0oa5b2tuam10CEsCn0y6',
                            "About P360": '0oa6a9nq05k0Csm5k0y6',
                            "DCGtools": "0oa6w6iyalYfpUpV30y6",
                            "Data Analytics": "0oa6uwj6ycYOVZfqu0y6"},
            "sf_client": Salesforce(username=os.environ['apiuser'],
                                    password=os.environ['apipw'],
                                    security_token=os.environ['apitoken']),
            "dcgapi_base_url" : "https://dcg-core-api-dev.azurewebsites.net/api/"
        }
    else:
        None
    return environment_variable




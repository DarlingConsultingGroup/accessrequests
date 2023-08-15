this repo contains the the code for Function App: accessfunction 
https://portal.azure.com/#@darlingconsulting0.onmicrosoft.com/resource/subscriptions/ced70610-77c5-4a35-ab64-48e92828efd4/resourceGroups/DCG-Software-PROD/providers/Microsoft.Web/sites/accessfunction/appServices

commits to the master branch are auto deployed to the function app. 

there are 6 different functions included:

- HttpTrigger1 - this is the original trigger that fields most of the access requests sent from salesforce. the trigger that sends a message to this endpoint is defined here: https://darlingconsulting.lightning.force.com/lightning/setup/WorkflowOutboundMessaging/page?address=%2F04k4u0000008QYl
- ServiceBusQueueTrigger1 - this is the service bus that takes the id of the message recieved from the HttpTrigger1 and actually processes the request (calls okta's api, moveit's api, salesforce's api)
- acctoktaaudit - this http trigger function recieves requests from salesforce defined by this trigger: https://darlingconsulting.lightning.force.com/lightning/setup/WorkflowOutboundMessaging/page?address=%2F04k4u000000oLyC
- acctoktaauditbus - this bus process the account audit requests. it calls okta, puts the data into a csv and sends an email with attachment to the requestor
- bank_meta_data - this http trigger function is intended to keep .231/DCGLIVE [DIP_Data].[dbo].[BankMetadata] updated. uses dcg core api (https://dcg-core-api-dev.azurewebsites.net/index.html). it recieves requests from salesforce defined by this trigger: https://darlingconsulting.lightning.force.com/lightning/setup/WorkflowOutboundMessaging/page?address=%2F04k4u0000004Egn
- institute_module - this is part of institute level access assignment that has yet to be fully implemented, but should be once prepayments is inclueded in loans360. it recieves requests from salesforce defined by this trigger: https://darlingconsulting.lightning.force.com/lightning/setup/WorkflowOutboundMessaging/page?address=%2F04k4u0000004Egd


the top 2 functions in the list above are the most commonly used (these are access requests submitted in salesforce by dcg employees on behalf of clients). 
if there is a failure on an access request assignment there are 3 retries built in. 

if you want to process a specifc request, run access-requests\tests\servicebus_samples.py with the access request id set as a variable in the file.


to copy app settings from azure to your local: 
 - az webapp config appsettings list --name accessfunction --resource-group DCG-Software-PROD --output json > local.settings.json
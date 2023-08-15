moveit_products = ["ALCO Folder", "Data & Doc Folder", "Project Folder", "Report Folder", "MoveIt", "Moveit", "okta MoveIT"]


default_groups_sf_to_moveit = {"RMAV": "Judis Project Group",
                                  "QRAS":"Drews DCG Group"}

not_dcg_contact_group_suffix = {"DCG ALCO Reports": " - ALCO", 
                                "Reports": " - ALCO",
                                "Data and Documentation": "", 
                                "Data": ""}

dcg_contact_group_suffix = {"DCG ALCO Reports": " - DCG", 
                            "Reports": " - DCG",
                            "Data and Documentation": " - DCG", 
                            "Data": " - DCG",  }


dcg_internal_group = {"DCG - Analyst Managers":226401,
                        "DCG Executive Coordinators":246601,
                        "Drews DCG Group":297601,
                        "ATG Group":49601,
                        "Judis Project Group":297701}

access_request_fields_used = ["Okta_Login__c", "BankKey__c", "Product_Module_Request__c", "User_Module_List__c", "Access_Request__c", "Product__c", "Email__c", "Case__c", "Contact__c", "Access_Combo__c", "Id", "Name"]

case_fields_used = ["Num_D360_Contacts__c", "Num_P360_Contacts__c", "Num_L360_Contacts__c", "Num_Loans360_Contacts__c", "Num_Loans360_Credit_Simulator_Contacts__c"]


def get_groups_for_folder_creation(bank_level_root):
    groups_assigned_to_subfolder = {
        "Data":[f"{bank_level_root}"],
        "Reports":[f"{bank_level_root} - ALCO", "DCG Executive Coordinators"],
        "Data and Documentation": [f"{bank_level_root}", f"{bank_level_root} - DCG", "DCG - Analyst Managers", "ATG Group"], 
        "DCG ALCO Reports": [f"{bank_level_root} - ALCO", f"{bank_level_root} - DCG", "DCG - Analyst Managers", "DCG Executive Coordinators"]}
    return groups_assigned_to_subfolder


# permissions: notify, admin, write/delete
def group_names_permissions(standard):
    group_names_permissions = {
        "Drews DCG Group": 
            {"notify": "true", "admin": "false", "write_and_delete": "true"},
        "Judis Project Group": 
            {"notify": "true", "admin": "false", "write_and_delete": "true"}, 
        "DCG Executive Coordinators": 
            {"notify": "true", "admin": "false", "write_and_delete": "true"},
        f"{standard}": 
            {"notify": "true", "admin": "false", "write_and_delete": "true"},
        f"{standard} - ALCO": 
            {"notify": "true", "admin": "false", "write_and_delete": "false"}, 
        f"{standard} - DCG": 
            {"notify": "true", "admin": "false", "write_and_delete": "true"},
        "DCG - Analyst Managers": 
            {"notify": "false", "admin": "false", "write_and_delete": "true"},
        "ATG Group": 
            {"notify": "true", "admin": "false", "write_and_delete": "true"},
    }
    return group_names_permissions



contact_hasproduct_fields = {
"D360": "Okta_D360__c",
"L360": "Okta_L360__c",
"Loans360": "Loans360__c",
"Loans360 - Credit Simulator": "Loans360_Credit_Simulator__c",
"P360":	"Okta_P360__c"
}

default_license_limits = {
"D360": ["Num_D360_Contacts__c", 500],
"L360": ["Num_L360_Contacts__c", 300],
"Loans360": ["Num_Loans360_Contacts__c", 500],
"Loans360 - Credit Simulator": ["Num_Loans360_Credit_Simulator_Contacts__c", 500],
"P360":	["Num_P360_Contacts__c", 500]
}

# default_license_limits = {
# "D360": ["Num_D360_Contacts__c", 5],
# "L360": ["Num_L360_Contacts__c", 3],
# "Loans360": ["Num_Loans360_Contacts__c", 5],
# "Loans360 - Credit Simulator": ["Num_Loans360_Credit_Simulator_Contacts__c", 5],
# "P360":	["Num_P360_Contacts__c", 5]
# }




import requests
import json
from Utilities import DBProcessor, ConfigReader
from DataProvider import GlobalConstants
import sqlite3
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

dbPath = ConfigReader.read_config_paths("System", "automation_suite_path")+"/Database/ezeauto.db"

def get_api_from_db() -> dict:
    """
    This method is used to get the api details from the api_details table of database.
    :return: dict
    """
    dict_api_details = {}
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute("SELECT * from api_details where ApiName = 'createMerchant';")
    details = cursor.fetchall()
    dict_api_details["ID"] = details[0][0]
    dict_api_details["ApiName"] = details[0][1]
    dict_api_details["Protocol"] = details[0][2]
    dict_api_details["Method"] = details[0][3]
    dict_api_details["EndPoint"] = details[0][4]
    dict_api_details["Header"] = details[0][5]
    dict_api_details["RequestBody"] = details[0][6]
    dict_api_details["ExpectedResult"] = details[0][7]
    dict_api_details["CurlData"] = details[0][8]
    cursor.close()
    conn.close()
    return dict_api_details


def check_if_merchant_exists(merchant_code: str) -> bool:
    """
    This method is used for checking if the merchant is already available in the system.
    org_employee
    :param merchant_code: str
    :return: bool
    """
    df_query_result = DBProcessor.getValueFromDB("select * from org_employee where org_code ='" + merchant_code + "';")
    if df_query_result.empty:
        print("Merchant "+merchant_code+" does not exist in this environment")
        logger.info("Merchant "+merchant_code+" does not exist in this environment")
        return False
    else:
        print("Merchant " + merchant_code + " already exists in this environment")
        logger.info("Merchant " + merchant_code + " already exists in this environment")
        return True

def generate_merchant_creation_api_body() -> list:
    """
    This method is used to generate the request body of the merchant creation API.
    This reads the merchant_creation_details table and gets the list of merchants along with details
    and updates the merchant creation api.
    :return: list
    """
    lst_merchant_creation_api_body = []

    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute("SELECT * from merchant;")
        merchants = cursor.fetchall()
        if merchants:
            for merchant in merchants:
                if not check_if_merchant_exists(merchant[0]) and merchant[0] != "Ezetap":
                    try:
                        merchant_creation_api = json.loads(get_api_from_db()["RequestBody"])
                        merchant_creation_api["username"] = ConfigReader.read_config("SuperUserCredentials", "username")
                        merchant_creation_api["password"] = ConfigReader.read_config("SuperUserCredentials", "password")
                        # for replacing the merchant details in the api
                        merchant_creation_api["merchantCode"] = merchant_creation_api["name"] = merchant_creation_api["reportingOrgCode"] = merchant[0]
                        cursor.execute("SELECT * from user where MerchantCode = '"+merchant[0]+"'")
                        users  = cursor.fetchall()
                        if users:
                            count = 0
                            for user in users:
                                if(count>0):
                                    merchant_creation_api["users"].append(json.loads(get_api_from_db()["RequestBody"])["users"][0])
                                    merchant_creation_api["users"].append(merchant_creation_api["users"][0])
                                merchant_creation_api["users"][count]["name"] = user[0]
                                merchant_creation_api["users"][count]["mobileNumber"] = merchant_creation_api["users"][count]["userToken"] = user[1]
                                if str(user[3]).lower() == "admin":
                                    merchant_creation_api["users"][count]["roles"] = GlobalConstants.ADMIN_USER_ROLES
                                elif str(user[3]).lower() == "agent":
                                    merchant_creation_api["users"][count]["roles"] = GlobalConstants.AGENT_USER_ROLES
                                count +=1
                            lst_merchant_creation_api_body.append(merchant_creation_api)
                    except Exception as e:
                        print("Unable to generate api for merchant "+merchant[0]+"due to error "+str(e))
                        logger.error(("Unable to generate api for merchant "+merchant[0]+"due to error "+str(e)))
                else:
                    cursor.execute("update merchant set CreationStatus = 'Existed' where MerchantCode ='"+merchant[0]+"';")
                    cursor.execute("update user set CreationStatus = 'Existed' where MerchantCode ='"+merchant[0]+"';")
                    conn.commit()
            cursor.close()
            conn.close()
        else:
            print("Merchant creation details db is empty")
            logger.fatal("Merchant creation details db is empty")
            cursor.close()
            conn.close()
    except Exception as e:
        print("Unable to fetch merchant creation details from the ezeauto.db due to error "+str(e))
        logger.fatal("Unable to fetch merchant creation details from the ezeauto.db due to error "+str(e))
    return lst_merchant_creation_api_body


def create_merchants_with_users():
    """
    This method is used to create the merchants along with the users.
    This calls the generate_merchant_creation_api_body method for getting the list of request bodies.
    Each request body represents a merchant.
    :return:
    """
    api_details = get_api_from_db()
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    url = "https://dev11.ezetap.com/api/2.0/merchant/manage"
    # url = ConfigReader.read_config("APIs","baseurl")+api_details["EndPoint"]
    headers = {
        'Content-Type': 'application/json',
        # 'Cookie': 'jsessionid=7b0d0888-f3aa-49bd-8486-2ac217194e88'
    }
    # headers = json.loads(api_details["Header"])
    merchant_code = ""
    lst_merchant_creation_body = generate_merchant_creation_api_body()
    if lst_merchant_creation_body:
        for merchant_creation_api_body in lst_merchant_creation_body:
            merchant_code = merchant_creation_api_body["merchantCode"]
            payload = json.dumps(merchant_creation_api_body)
            print(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            response_string = response.text
            print("-----------------------------------")
            print(response_string)
            if response_string["success"] == True:
                logger.info("Merchant with users created successfully.")
                try:
                    cursor.execute("update merchant set CreationStatus = 'Created' where MerchantCode = '"+merchant_code+"'")
                    cursor.execute("update user set CreationStatus = 'Created' where MerchantCode = '" +merchant_code+"'")
                    cursor.commit()
                    cursor.close()
                    conn.close()
                except:
                    print("Unable to update the ezeauto db on the merchant creation.")
                    logger.warning("Unable to update the ezeauto db on the merchant creation.")
            else:
                logger.warning("Merchant creation failed")

    else:
        print("Merchant creation skipped.")
        logger.info("Merchant creation skipped")


create_merchants_with_users()





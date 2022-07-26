import requests
import json
import pandas
import sqlite3
from Utilities import DBProcessor, ConfigReader, ResourceAssigner
from DataProvider import GlobalConstants
from Utilities.execution_log_processor import EzeAutoLogger


logger = EzeAutoLogger(__name__)
dbPath = ConfigReader.read_config_paths("System", "automation_suite_path")+"/Database/ezeauto.db"
excel_path = ConfigReader.read_config_paths("System", "automation_suite_path")+"/DataProvider/merchant_user_creation.xlsx"



def create_merchants_with_users():
    """
    This method is used to create the merchants along with the users.
    This calls the generate_merchant_creation_api_body method for getting the list of request bodies.
    Each request body represents a merchant.
    """
    api_details = get_api_from_db("createMerchant")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    url = ConfigReader.read_config("APIs", "baseurl")+api_details["EndPoint"]
    headers = json.loads(api_details["Header"])
    global user_name
    lst_merchant_creation_body = generate_merchant_creation_api_body()
    if lst_merchant_creation_body:
        for merchant_creation_api_body in lst_merchant_creation_body:
            user_name = merchant_creation_api_body["merchantCode"]
            payload = json.dumps(merchant_creation_api_body)
            logger.debug(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            logger.debug(response.text)
            result = json.loads(response.text)
            if result["success"]:
                logger.info(f"Merchant {user_name} with users created successfully.")
                try:
                    cursor.execute("update merchants set CreationStatus = 'Created', Availability = 'Available' where MerchantCode = '" + user_name + "'")
                    cursor.execute("update users set CreationStatus = 'Created', Availability = 'Available' where MerchantCode = '" + user_name + "'")
                    conn.commit()
                except Exception as e:
                    print(f"Unable to update the ezeauto db on the merchant {user_name} creation due to error " + str(e))
                    logger.warning(f"Unable to update the ezeauto db on the merchant {user_name} creation due to error " + str(e))
            else:
                logger.warning(f"Merchant {user_name} creation failed")

    else:
        print("Merchant creation skipped.")
        logger.info("Merchant creation skipped")
    cursor.close()
    conn.close()


def create_users_for_merchant(merchant_code):
    """
        This method is used to create the users for the specified merchant
        This calls the generate_user_creation_api_body method for getting the list of request bodies.
        Each request body represents a user.
        """
    api_details = get_api_from_db("createUser")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    url = ConfigReader.read_config("APIs", "baseurl") + api_details["EndPoint"]
    headers = json.loads(api_details["Header"])
    global user_name
    lst_user_creation_body = generate_users_creation_api_body(merchant_code)
    if lst_user_creation_body:
        for user_creation_api_body in lst_user_creation_body:
            user_name = user_creation_api_body["name"]
            payload = json.dumps(user_creation_api_body)
            logger.debug(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            logger.debug(response.text)
            result = json.loads(response.text)
            if result["success"]:
                logger.info(f"User {user_name} with users created successfully.")
                try:
                    cursor.execute(
                        "update users set CreationStatus = 'Created', Availability = 'Available' where Name = '" + user_name + "'")
                    conn.commit()
                except Exception as e:
                    print(
                        f"Unable to update the ezeauto db on the user {user_name} creation due to error " + str(
                            e))
                    logger.warning(
                        f"Unable to update the ezeauto db on the user {user_name} creation due to error " + str(
                            e))
            else:
                logger.warning(f"User {user_name} creation failed")

    else:
        print("User creation skipped.")
        logger.info("User creation skipped")
    cursor.close()
    conn.close()


def get_api_from_db(api_name:str) -> dict:
    """
    This method is used to get the api details from the api_details table of database.

    :param api_name:str
    :return: dict
    """
    dict_api_details = {}
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * from api_details where ApiName = '{api_name}';")
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


def check_if_user_exists(name: str) -> bool:
    """
    This method is used for checking if the user is already available in the system
        :param name: str
        :return: bool
    """

    df_query_result = DBProcessor.getValueFromDB("select * from org_employee where name ='" + name + "';")
    if df_query_result.empty:
        print("User "+name+" does not exist in this environment")
        logger.info("User "+name+" does not exist in this environment")
        return False
    else:
        print("User " + name + " already exists in this environment")
        logger.info("User " + name + " already exists in this environment")
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
        cursor.execute("SELECT * from merchants;")
        merchants = cursor.fetchall()
        if merchants:
            for merchant in merchants:
                # if merchant[0] == "EZETAP":
                #     create_users_for_merchant("EZETAP")
                if not check_if_merchant_exists(merchant[0]):
                    try:
                        merchant_creation_api = json.loads(get_api_from_db("createMerchant")["RequestBody"])
                        merchant_creation_api["username"] = ConfigReader.read_config("SuperUserCredentials", "username")
                        merchant_creation_api["password"] = ConfigReader.read_config("SuperUserCredentials", "password")
                        # for replacing the merchant details in the api
                        merchant_creation_api["merchantCode"] = merchant_creation_api["name"] = merchant_creation_api["reportingOrgCode"] = merchant[0]
                        cursor.execute("SELECT * from users where MerchantCode = '"+merchant[0]+"';")
                        users = cursor.fetchall()
                        if users:
                            count = 0
                            for user in users:
                                if count > 0:
                                    merchant_creation_api["users"].append(json.loads(get_api_from_db("createMerchant")["RequestBody"])["users"][0])
                                    merchant_creation_api["users"].append(merchant_creation_api["users"][0])
                                merchant_creation_api["users"][count]["name"] = user[0]
                                merchant_creation_api["users"][count]["userToken"] = user[2]
                                merchant_creation_api["users"][count]["userPassword"] = user[3]
                                merchant_creation_api["users"][count]["mobileNumber"] = user[4]
                                if str(user[5]).lower() == "admin":
                                    merchant_creation_api["users"][count]["roles"] = GlobalConstants.ADMIN_USER_ROLES
                                elif str(user[5]).lower() == "app":
                                    merchant_creation_api["users"][count]["roles"] = GlobalConstants.APP_USER_ROLES
                                count += 1
                            lst_merchant_creation_api_body.append(merchant_creation_api)
                        else:
                            logger.warning("This merchant does not have any associated user.")
                    except Exception as e:
                        print("Unable to generate api for merchant "+merchant[0]+"due to error "+str(e))
                        logger.error(("Unable to generate api for merchant "+merchant[0]+"due to error "+str(e)))
                else:
                    create_users_for_merchant(merchant[0])
                    cursor.execute("update merchants set CreationStatus = 'Existed', Availability = 'Available' where MerchantCode ='"+merchant[0]+"';")
                    cursor.execute("update users set CreationStatus = 'Existed', Availability = 'Available'  where MerchantCode ='"+merchant[0]+"';")
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


def generate_users_creation_api_body(merchant_code:str) -> list:
    """
    This method is used to generate the request body of the user creation API.
    This reads the users table and gets the list of users for a specific merchant and prepares the API.
        :param merchant_code:str
        :return: list
    """
    lst_user_creation_api_body = []

    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * from users WHERE MerchantCode = '{merchant_code}';")
        users = cursor.fetchall()
        if users:
            for user in users:
                if not check_if_user_exists(user[0]):
                    try:
                        user_creation_api = json.loads(get_api_from_db("createUser")["RequestBody"])
                        user_creation_api["username"] = ConfigReader.read_config("SuperUserCredentials", "username")
                        user_creation_api["password"] = ConfigReader.read_config("SuperUserCredentials", "password")
                        # for replacing the user details in the api
                        user_creation_api["name"] = user[0]
                        if str(user[5]).lower() == "admin":
                            user_creation_api["roles"] = GlobalConstants.ADMIN_USER_ROLES
                        elif str(user[5]).lower() == "app":
                            user_creation_api["roles"] = GlobalConstants.APP_USER_ROLES
                        elif str(user[5]).lower() == "portal":
                            user_creation_api["roles"] = GlobalConstants.PORTAL_USER_ROLES
                        user_creation_api["userToken"] = user[2]
                        user_creation_api["userPassword"] = user[3]
                        user_creation_api["mobileNumber"] = user[4]
                        lst_user_creation_api_body.append(user_creation_api)
                    except Exception as e:
                        print("Unable to generate api for user "+user[0]+"due to error "+str(e))
                        logger.error(("Unable to generate api for user "+user[0]+"due to error "+str(e)))
                else:
                    logger.info(f"User {user[0]} already exists in the system.")
                    print(f"User {user[0]} already exists in the system.")
                    cursor.execute("update users set CreationStatus = 'Existed', Availability = 'Available'  where name ='"+user[0]+"';")
                    conn.commit()
            cursor.close()
            conn.close()
        else:
            print("Merchant does not have any users.")
            logger.error("Merchant does not have any users.")
            cursor.close()
            conn.close()
    except Exception as e:
        print("Unable to fetch user creation details from the ezeauto.db due to error "+str(e))
        logger.fatal("Unable to fetch user creation details from the ezeauto.db due to error "+str(e))
    return lst_user_creation_api_body


def update_merchants_to_db(merchants_list : list):
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        for merchant in merchants_list:
            try:
                cursor.execute(f"insert into merchants(MerchantCode)values('{merchant}');")
                conn.commit()
                logger.info(f"Merchant {merchant} successfully added to the merchants db.")
            except Exception as e:
                logger.error(f"Unable to add the merchant {merchant} into db due to error {e}")
    except Exception as e:
        logger.error(f"Unable to connect to the db due to error {e}")
    cursor.close()
    conn.close()

def update_users_to_db(users_list : list):
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        for user in users_list:
            if(check_merchant_exists_in_automation_db(user["MerchantCode"])):
                try:
                    cursor.execute(f"insert into users(Name, MerchantCode, Username, Password, Mobile, Type)values(\"{user['Name']}\", \"{user['MerchantCode']}\", \"{user['Username']}\", \"{user['Password']}\", \"{user['Mobile']}\", \"{user['Type']}\");")
                    conn.commit()
                    logger.info(f"User {user['Name']} successfully added to the users db.")
                except Exception as e:
                    logger.error(f"Unable to add the user {user['Name']} into db due to error {e}")
            else:
                logger.info(f"User {user['Name']} creation skipped since associated merchant is not available in merchants db.")
    except Exception as e:
        logger.error(f"Unable to connect to the db due to error {e}")
    cursor.close()
    conn.close()


def check_merchant_exists_in_automation_db(merchant):
    conn = ""
    cursor = ""
    exists = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        try:
            cursor.execute(f"select * from merchants where MerchantCode = '{merchant}'")
            merchant_info = cursor.fetchone()
            if merchant_info is None:
                logger.info(f"Merchant {merchant} is not available in the automation db.")
                exists =  False
            else:
                logger.info(f"Merchant {merchant} is available in the automation db.")
                exists =  True
        except Exception as e:
            logger.error(f"Unable to check if {merchant} is available in the automation db.")
    except Exception as e:
        logger.error(f"Unable to connect to the db due to error {e}")
    cursor.close()
    conn.close()
    return exists


def get_merchants_list_from_excel() -> list:
    merchants_list = []
    merchant_creation_excel_data = pandas.read_excel(excel_path, sheet_name="UserDetails")
    if len(merchant_creation_excel_data)>0:
        for i in range(0, len(merchant_creation_excel_data)):
            merchant_name = ""
            if str((merchant_creation_excel_data.loc[i]).to_dict()["Type"]).lower() == "portal":
                merchant_name = "EZETAP"
            elif str((merchant_creation_excel_data.loc[i]).to_dict()["Type"]).lower() in ["admin", "app"]:
                merchant_name = (merchant_creation_excel_data.loc[i]).to_dict()["MerchantCode"]
            else:
                merchant_name = (merchant_creation_excel_data.loc[i]).to_dict()["MerchantCode"]
                logger.error(f"Merchant {merchant_name} is not added to the list since type is specified wrongly.")
                merchant_name = ""
            if not merchant_name in merchants_list and merchant_name != "":
                merchants_list.append(merchant_name)
    else:
        logger.warning("Unable to pull merchants list since no data available in the merchant creation excel file.")
    return merchants_list


def get_users_list_from_excel() -> list:
    users_list = []
    merchant_creation_excel_data = pandas.read_excel(excel_path, sheet_name="UserDetails")
    if len(merchant_creation_excel_data) > 0:
        for i in range(0, len(merchant_creation_excel_data)):
            if str((merchant_creation_excel_data.loc[i]).to_dict()["Type"]).lower() in ["portal", "admin", "app"]:
                user_details = {}
                user_details["Name"] = (merchant_creation_excel_data.loc[i]).to_dict()["Name"]
                if str((merchant_creation_excel_data.loc[i]).to_dict()["Type"]).lower() == "portal":
                    user_details["MerchantCode"] = "EZETAP"
                else:
                    user_details["MerchantCode"] = (merchant_creation_excel_data.loc[i]).to_dict()["MerchantCode"]
                user_details["Username"] = (merchant_creation_excel_data.loc[i]).to_dict()["Username"]
                user_details["Password"] = (merchant_creation_excel_data.loc[i]).to_dict()["Password"]
                user_details["Mobile"] = (merchant_creation_excel_data.loc[i]).to_dict()["Mobile"]
                user_details["Type"] = (merchant_creation_excel_data.loc[i]).to_dict()["Type"]
                users_list.append(user_details)
            else:
                logger.error(f"Type of user {(merchant_creation_excel_data.loc[i]).to_dict()['Name']} is defined wrongly. So its not added to user creation list.")
    else:
        logger.warning("Unable to pull users list since no data available in the merchant creation excel file.")
    return users_list

ResourceAssigner.clearAssignerTables()
update_merchants_to_db(get_merchants_list_from_excel())
update_users_to_db(get_users_list_from_excel())
create_merchants_with_users()
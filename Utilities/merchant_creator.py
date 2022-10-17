import pandas
import requests
import json
import sqlite3
from Utilities import DBProcessor, ConfigReader,sqlite_processor
from DataProvider import GlobalConstants
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)
# dbPath = ConfigReader.read_config_paths("System", "automation_suite_path") + "/Database/ezeauto.db"
excel_path = ConfigReader.read_config_paths("System",
                                            "automation_suite_path") + "/DataProvider/merchant_user_creation.xlsx"
lst_unavailable_tid = []
lst_unavailable_device_serial = []


def create_merchants():
    """
    This method is used to create the merchants for execution.
    """
    create_merchant_required = ConfigReader.read_config("Setup", "create_and_configure_merchants").lower()
    sqlite_processor.update_merchants_to_db(sqlite_processor.get_merchants_list_from_excel())
    sqlite_processor.update_users_to_db(sqlite_processor.get_users_list_from_excel())
    sqlite_processor.update_acquisitions_to_db()
    if create_merchant_required == "true":
        create_merchants_with_users()
    else:
        set_merchants_users_available()
        logger.debug("Merchant creation skipped as per the user configuration.")
    sqlite_processor.update_app_users_to_db()
    sqlite_processor.update_portal_users_to_db()
    sqlite_processor.update_terminal_details_of_all_merchants()


def create_merchants_with_users():
    """
    This method is used to create the merchants along with the users.
    This calls the generate_merchant_creation_api_body method for getting the list of request bodies.
    Each request body represents a merchant.
    """
    api_details = get_api_details_from_db("createMerchant")
    conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
    cursor = conn.cursor()
    url = ConfigReader.read_config("APIs", "baseurl") + api_details["EndPoint"]
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
                    cursor.execute(
                        "update merchants set CreationStatus = 'Created', Availability = 'Available' where MerchantCode = '" + user_name + "'")
                    cursor.execute(
                        "update users set CreationStatus = 'Created', Availability = 'Available' where MerchantCode = '" + user_name + "'")
                    conn.commit()
                except Exception as e:
                    print(
                        f"Unable to update the ezeauto db on the merchant {user_name} creation due to error " + str(e))
                    logger.warning(
                        f"Unable to update the ezeauto db on the merchant {user_name} creation due to error " + str(e))
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
    api_details = get_api_details_from_db("createUser")
    conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
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


def check_if_merchant_exists(merchant_code: str) -> bool:
    """
    This method is used for checking if the merchant is already available in the system.

    :param merchant_code: str
    :return: bool
    """

    df_query_result = DBProcessor.getValueFromDB("select * from org_employee where org_code ='" + merchant_code + "';")
    if df_query_result.empty:
        print("Merchant " + merchant_code + " does not exist in this environment")
        logger.info("Merchant " + merchant_code + " does not exist in this environment")
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
        print("User " + name + " does not exist in this environment")
        logger.info("User " + name + " does not exist in this environment")
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
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * from merchants;")
        merchants = cursor.fetchall()
        if merchants:
            for merchant in merchants:
                # if merchant[0] == "EZETAP":
                #     create_users_for_merchant("EZETAP")
                if not check_if_merchant_exists(merchant[0]):
                    try:
                        merchant_creation_api = json.loads(get_api_details_from_db("createMerchant")["RequestBody"])
                        merchant_creation_api["username"] = ConfigReader.read_config("SuperUserCredentials", "username")
                        merchant_creation_api["password"] = ConfigReader.read_config("SuperUserCredentials", "password")
                        merchant_creation_api["acquisitions"] = generate_acquisitions_for_merchant_creation(merchant[0])
                        # for replacing the merchant details in the api
                        merchant_creation_api["merchantCode"] = merchant_creation_api["name"] = merchant_creation_api[
                            "reportingOrgCode"] = merchant[0]
                        cursor.execute("SELECT * from users where MerchantCode = '" + merchant[0] + "';")
                        users = cursor.fetchall()
                        if users:
                            count = 0
                            for user in users:
                                if count > 0:
                                    merchant_creation_api["users"].append(
                                        json.loads(get_api_details_from_db("createMerchant")["RequestBody"])["users"][0])
                                    merchant_creation_api["users"].append(merchant_creation_api["users"][0])
                                merchant_creation_api["users"][count]["name"] = user[0]
                                merchant_creation_api["users"][count]["userToken"] = user[2]
                                merchant_creation_api["users"][count]["userPassword"] = user[3]
                                merchant_creation_api["users"][count]["mobileNumber"] = str(user[4])
                                if str(user[5]).lower() == "admin":
                                    merchant_creation_api["users"][count]["roles"] = GlobalConstants.ADMIN_USER_ROLES
                                elif str(user[5]).lower() == "app":
                                    merchant_creation_api["users"][count]["roles"] = GlobalConstants.APP_USER_ROLES
                                count += 1
                            lst_merchant_creation_api_body.append(merchant_creation_api)
                        else:
                            logger.warning("This merchant does not have any associated user.")
                    except Exception as e:
                        print("Unable to generate api for merchant " + merchant[0] + "due to error " + str(e))
                        logger.error(("Unable to generate api for merchant " + merchant[0] + "due to error " + str(e)))
                else:
                    create_users_for_merchant(merchant[0])
                    cursor.execute(
                        "update merchants set CreationStatus = 'Existed', Availability = 'Available' where MerchantCode ='" +
                        merchant[0] + "';")
                    conn.commit()
            cursor.close()
            conn.close()
        else:
            print("Merchant creation details db is empty")
            logger.fatal("Merchant creation details db is empty")
            cursor.close()
            conn.close()
    except Exception as e:
        print("Unable to fetch merchant creation details from the ezeauto.db due to error " + str(e))
        logger.fatal("Unable to fetch merchant creation details from the ezeauto.db due to error " + str(e))
    return lst_merchant_creation_api_body


def generate_users_creation_api_body(merchant_code: str) -> list:
    """
    This method is used to generate the request body of the user creation API.
    This reads the users table and gets the list of users for a specific merchant and prepares the API.
        :param merchant_code:str
        :return: list
    """
    lst_user_creation_api_body = []

    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * from users WHERE MerchantCode = '{merchant_code}';")
        users = cursor.fetchall()
        if users:
            for user in users:
                if not check_if_user_exists(user[0]):
                    try:
                        user_creation_api = json.loads(get_api_details_from_db("createUser")["RequestBody"])
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
                        print("Unable to generate api for user " + user[0] + "due to error " + str(e))
                        logger.error(("Unable to generate api for user " + user[0] + "due to error " + str(e)))
                else:
                    logger.info(f"User {user[0]} already exists in the system.")
                    print(f"User {user[0]} already exists in the system.")
                    cursor.execute(
                        "update users set CreationStatus = 'Existed', Availability = 'Available'  where name ='" + user[
                            0] + "';")
                    conn.commit()
            cursor.close()
            conn.close()
        else:
            print("Merchant does not have any users.")
            logger.error("Merchant does not have any users.")
            cursor.close()
            conn.close()
    except Exception as e:
        print("Unable to fetch user creation details from the ezeauto.db due to error " + str(e))
        logger.fatal("Unable to fetch user creation details from the ezeauto.db due to error " + str(e))
    return lst_user_creation_api_body


def generate_acquisitions_for_merchant_creation(merchant_id: str) -> list:
    """
    This method is used to generate the dictionary with acquisitions that can be added to the merchant creation api
    :param merchant_id str
    :return: list
    """
    lst_acquisitions_detail = []
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("select * from api_details where ApiName = 'createMerchant';")
        api_request_body = json.loads(cursor.fetchone()[6])
        try:
            acquisition_details = api_request_body['acquisitions'][0]
        except Exception as e:
            logger.error(f"Create merchant api request body is incorrect.")
            lst_acquisitions_detail = None
            return lst_acquisitions_detail
        try:
            cursor.execute("select * from acquisitions;")
            acquisitions = cursor.fetchall()
            for i in range(0, len(acquisitions)):
                acquisition_details['acquirerCode'] = acquisitions[i][0]
                acquisition_details['paymentGateway'] = acquisitions[i][1]
                acquisition_details['terminals'] = generate_terminal_details_for_merchant_creation(merchant_id,
                                                                                                   acquisitions[i][0],
                                                                                                   acquisitions[i][1])
                lst_acquisitions_detail.append(acquisition_details.copy())
            return lst_acquisitions_detail
        except Exception as e:
            logger.error(f"Unable to get the acquisition details from db due to error {str(e)}")
            lst_acquisitions_detail = None
            return lst_acquisitions_detail
    except Exception as e:
        logger.error(f"Unable to connect to the db due to error {str(e)}")
        lst_acquisitions_detail = None
        return lst_acquisitions_detail


def generate_terminal_details_for_merchant_creation(merchant_id: str, acquirer_code: str, payment_gateway: str) -> list:
    """
    This method is used to generate the dictionary with terminal details that can be added to the merchant creation api
    body. This method also add the new device into the device table.
    :param merchant_id str
    :param acquirer_code str
    :param payment_gateway str
    :return: list
    """
    lst_terminals_detail = []
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("select * from api_details where ApiName = 'createMerchant';")
        api_request_body = json.loads(cursor.fetchone()[6])
        try:
            acquisition_details = api_request_body['acquisitions'][0]
            terminal_details = acquisition_details['terminals'][0]
        except Exception as e:
            logger.error(f"Create merchant api request body is incorrect.")
            lst_terminals_detail = None
            return lst_terminals_detail
        terminal_details_unique_value_fields = generate_terminal_details(merchant_id)
        try:
            cursor.execute(
                f"SELECT * FROM acquisitions where AcquirerCode = '{acquirer_code}' and PaymentGateway = '{payment_gateway}';")
            acquisitions = cursor.fetchall()[0]
            number_of_terminals = int(acquisitions[2])
            tid_number_increment = 0
            device_number_increment = 0
            for i in range(0, number_of_terminals):
                terminal_details['acquirerCode'] = acquirer_code
                terminal_details['paymentGateway'] = payment_gateway
                terminal_details['mid'] = terminal_details_unique_value_fields['mid']
                terminal_details['tid'] = (terminal_details_unique_value_fields['tid'][:-2]) + "a" + str(
                    tid_number_increment)
                while check_if_tid_exists(terminal_details['tid']):
                    tid_number_increment += 1
                    terminal_details['tid'] = (terminal_details_unique_value_fields['tid'][:-2]) + "a" + str(
                        tid_number_increment)
                    terminal_details['tid'] = trim_extra_digits_of_tid(tid=terminal_details['tid'], max_length=8)
                terminal_details['hsmName'] = acquisitions[3]
                # Following logic is to perform the factory device registration
                logger.info("Trying to perform factory device registration...")
                terminal_details['deviceSerial'] = terminal_details_unique_value_fields['device_id'] + str(
                    device_number_increment)
                condition = check_if_device_serial_exists(terminal_details['deviceSerial'])
                if condition:
                    while condition:
                        device_number_increment += 1
                        terminal_details['deviceSerial'] = terminal_details_unique_value_fields['device_id'] + str(
                            device_number_increment)
                        condition = check_if_device_serial_exists(terminal_details['deviceSerial'])
                        if condition == False:
                            try:
                                DBProcessor.setValueToDB(
                                    f"INSERT INTO device(device_id,  device_serial,  batch_no,  firmware_version,  device_version,  created_by,  created_time,  modified_by,  modified_time,  org_code, status) VALUES ('{terminal_details['deviceSerial']}',  '{terminal_details['deviceSerial']}',  '0007',  'PAX A910',  'PAX A910',  'ezetap', now(),  'ezetap',  now(),  '{merchant_id}', 'ACTIVE');")
                                logger.info(f"Device {terminal_details['deviceSerial']} added to environment.")
                            except Exception as e:
                                logger.error(f"Unable to insert device details into db due to error {str(e)}")
                            break
                else:
                    try:
                        DBProcessor.setValueToDB(
                            f"INSERT INTO device(device_id,  device_serial,  batch_no,  firmware_version,  device_version,  created_by,  created_time,  modified_by,  modified_time,  org_code, status) VALUES ('{terminal_details['deviceSerial']}',  '{terminal_details['deviceSerial']}',  '0007',  'PAX A910',  'PAX A910',  'ezetap', now(),  'ezetap',  now(),  '{merchant_id}', 'ACTIVE');")
                        logger.info(f"Device {terminal_details['deviceSerial']} added to environment.")
                    except Exception as e:
                        logger.error(f"Unable to insert device details into db due to error {str(e)}")
                lst_terminals_detail.append(terminal_details.copy())
            return lst_terminals_detail
        except Exception as e:
            logger.error(f"Unable to get the acquisition details from acquisition db due to error {str(e)}")
            lst_terminals_detail = None
            return lst_terminals_detail
    except Exception as e:
        logger.error(f"Unable to connect to sqlite db due to error {str(e)}")
        lst_terminals_detail = None
        return lst_terminals_detail


def generate_terminal_details(merchant_id: str) -> dict:
    """
    This method is used to generate the mid, tid and device id that is unique
    :param merchant_id str
    :returns: dict
    """
    terminal_details = {}
    username = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT Username from users where MerchantCode = '{merchant_id}' limit 1;")
        username = cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Unable to get the merchant details due to error {str(e)}")
    if username:
        terminal_details['mid'] = "MIDIS" + username
        terminal_details['tid'] = username[-8:]
        terminal_details['device_id'] = "D" + username
    else:
        terminal_details = None
    return terminal_details


def check_if_tid_exists(tid: str) -> bool:
    """
    This method is used to check if the tid exists in the environment
    :param tid str
    :return: bool
    """
    try:
        if tid in lst_unavailable_tid:
            logger.debug(f"TID {tid} is already assigned.")
            return True
        else:
            lst_unavailable_tid.append(tid)
            result = DBProcessor.getValueFromDB(f"Select * from terminal_info where tid = '{tid}';")
            if len(result) > 0:
                logger.debug(f"TID {tid} already exists in the environment.")
                return True
            else:
                logger.debug(f"TID {tid} is not available in the environment.")
                return False
    except Exception as e:
        logger.error(f"Unable to check if tid exists in the environment, due to error {str(e)}")
        return None


def check_if_device_serial_exists(device_serial: str) -> bool:
    """
    This method is used to check if the device serial already exists in the environment
    :param device_serial str
    :return: bool
    """
    try:
        if device_serial in lst_unavailable_device_serial:
            logger.debug(f"Device serial {device_serial} is already assigned.")
            return True
        else:
            lst_unavailable_device_serial.append(device_serial)
            result = DBProcessor.getValueFromDB(f"Select * from device where device_serial = '{device_serial}';")
            if len(result) > 0:
                logger.debug(f"Device {device_serial} already exists in the environment.")
                return True
            else:
                logger.debug(f"Device {device_serial} is not available in the environment.")
                return False
    except Exception as e:
        logger.error(f"Unable to check if device serial exists in the environment, due to error {str(e)}")
        return None


def get_device_serial_of_merchant(org_code: str, acquisition: str, payment_gateway: str) -> str:
    """
    This method is used to get the device serial number associated with the acquisition of merchant
    :param org_code str
    :param acquisition str
    :param payment_gateway str
    :return: str
    """
    device_serial = None
    try:
        result = DBProcessor.getValueFromDB(
            f"SELECT device_serial FROM terminal_info WHERE org_code = '{org_code}' and acquirer_code = '{acquisition}' and payment_gateway = '{payment_gateway}';")
        if len(result) > 0:
            device_serial = result['device_serial'][0]
        else:
            logger.warn(
                f"Device serial info not available for the acquisition '{acquisition}' of merchant '{org_code}'.")
    except Exception as e:
        logger.error(f"Unable to get the device serial from db due to error {str(e)}")
    return device_serial


def get_merchant_id_of_user(user_id: str) -> str:
    """
    This method is used to get the merchant id associated with the user id
    :param user_id str
    :return: str
    """
    merchant_id = None
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"select * from users where Name = '{user_id}';")
        merchant_id = cursor.fetchone()[1]
    except Exception as e:
        logger.error(f"Unable to get the merchant id due to error {str(e)}")
    cursor.close()
    conn.close()
    return merchant_id


def trim_extra_digits_of_tid(tid: str, max_length: int) -> str:
    """
    This method is used to trim the tid to the required length
    :param tid str
    :param max_length int
    :return: str
    """
    if len(tid) > max_length:
        length_to_remove = len(tid) - max_length
        trim_position = -abs(length_to_remove + 3)
        while len(tid) > max_length:
            tid = tid[:trim_position] + tid[trim_position + 1:]
        return tid
    else:
        return tid


def get_api_details_from_db(api_name: str) -> dict:
    """
    This method is used to get the api details from the api_details table of database.

    :param api_name:str
    :return: dict
    """
    dict_api_details = {}
    conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
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


def set_merchants_users_available():
    """
    This method is used to set the status of all the merchants and users as "Existed" and "Available"
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE merchants SET CreationStatus = 'Existed', Availability = 'Available';")
        conn.commit()
        cursor.execute("UPDATE users SET CreationStatus = 'Existed', Availability = 'Available';")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Unable to set the status of merchants and users as available, due to error {str(e)}")


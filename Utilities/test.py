import sqlite3
import time

from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)

dbPath = ConfigReader.read_config_paths("System","automation_suite_path")+"/Database/ezeauto.db"

def getAppUserCredentials(testcase_id: str) -> list:
    """
    This method is used to get the app user credentials along with the merchant code of the user.
    :param testcase_id: str
    :return: list
    """
    app_user_details = {}
    proceed = False
    conn = ""
    cursor = ""
    print("Trying to get available app user credentials from DB")
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        timer = 0
        while timer < 10:
            assigned_merchant = get_merchant_assigned_to_testcase(testcase_id)
            available_user = ""
            if assigned_merchant:
                available_user = get_user_details(assigned_merchant,"App")
                if available_user:
                    app_user_details["name"] = available_user[0]
                    app_user_details["merchant_code"] = available_user[1]
                    app_user_details["username"] = available_user[2]
                    app_user_details["password"] = available_user[3]
                    block_user(app_user_details["name"],testcase_id)
                    break
                else:
                    logger.warning("App user is not available under this merchant.")
                    app_user_details = None
            else:
                unassigned_merchant = get_available_merchant()
                if unassigned_merchant:
                    available_user = get_user_details(unassigned_merchant, "App")
                    if available_user:
                        if block_merchant(unassigned_merchant, testcase_id):
                            app_user_details["name"] = available_user[0]
                            app_user_details["merchant_code"] = available_user[1]
                            app_user_details["username"] = available_user[2]
                            app_user_details["password"] = available_user[3]
                            block_user(app_user_details["name"], testcase_id)
                            break
                        else:
                            logger.error("Though user is available, attempt to block merchant failed.")
                            app_user_details = None
                    else:
                        logger.warning("Unable to find any available app user under the merchant.")
                        app_user_details = None
                else:
                    logger.info("Unable to find an available merchant.")
                    app_user_details = None
            time.sleep(1)
            timer = timer+1
    except Exception as e:
        logger.error("Unable get the app user details from db due to error "+str(e))
        app_user_details = None
    cursor.close()
    conn.close()
    return app_user_details


def get_admin_user_details(testcase_id: str) -> list:
    """
    This method is used to get the admin user credentials along with the merchant code of the user.
    :param testcase_id: str
    :return: list
    """
    admin_user_details = {}
    proceed = False
    conn = ""
    cursor = ""
    print("Trying to get available admin user credentials from DB")
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        timer = 0
        while timer < 10:
            assigned_merchant = get_merchant_assigned_to_testcase(testcase_id)
            available_user = ""
            if assigned_merchant:
                available_user = get_user_details(assigned_merchant,"Admin")
                if available_user:
                    admin_user_details["name"] = available_user[0]
                    admin_user_details["merchant_code"] = available_user[1]
                    admin_user_details["username"] = available_user[2]
                    admin_user_details["password"] = available_user[3]
                    block_user(admin_user_details["name"], testcase_id)
                    break
                else:
                    logger.warning("Admin user is not available under this merchant.")
                    admin_user_details = None
            else:
                unassigned_merchant = get_available_merchant()
                if unassigned_merchant:
                    available_user = get_user_details(unassigned_merchant, "Admin")
                    if available_user:
                        if block_merchant(unassigned_merchant, testcase_id):
                            admin_user_details["name"] = available_user[0]
                            admin_user_details["merchant_code"] = available_user[1]
                            admin_user_details["username"] = available_user[2]
                            admin_user_details["password"] = available_user[3]
                            block_user(admin_user_details["name"], testcase_id)
                            break
                        else:
                            logger.error("Though user is available, attempt to block merchant failed.")
                            admin_user_details = None
                    else:
                        logger.warning("Unable to find any available app user under the merchant.")
                        admin_user_details = None
                else:
                    logger.info("Unable to find an available merchant.")
                    admin_user_details = None
            time.sleep(1)
            timer = timer+1
    except Exception as e:
        logger.error("Unable get the app user details from db due to error "+str(e))
        admin_user_details = None
    return admin_user_details


def getPortalUserCredentials(testcase_id: str) -> list:
    """
    This method is used to get the portal user credentials along with the merchant code of the user.
    :param testcase_id: str
    :return: list
    """
    proceed = False
    conn = ""
    cursor = ""
    print("Trying to get available portal user credentials from DB")
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        portal_user_details = {}
        timer = 0
        while timer < 10:
            assigned_merchant = "EZETAP"
            available_user = ""
            available_user = get_user_details(assigned_merchant, "Portal")
            if available_user:
                portal_user_details["name"] = available_user[0]
                portal_user_details["merchant_code"] = available_user[1]
                portal_user_details["username"] = available_user[2]
                portal_user_details["password"] = available_user[3]
                if not block_user(portal_user_details["name"], testcase_id):
                    portal_user_details = None
                break
            else:
                logger.warning("Portal user is not currently available. Retrying..")
                portal_user_details = None
            time.sleep(1)
            timer = timer+1
    except Exception as e:
        logger.error("Unable to connect to the Database for fetching the app user details")
        portal_user_details = None
    cursor.close()
    conn.close()
    return portal_user_details

def releaseAppUser(testcase_id:str) -> bool:
    """
    This method is used to release an app user that is assigned to a test case.
        :param testcase_id
        :return: bool
    """
    release_status = False
    user = get_user_assigned_to_testcase(testcase_id, "App")
    if user:
        if unblock_user(user,testcase_id):
            merchant = get_merchant_of_user(user)
            if check_if_merchant_be_released(merchant):
                if unblock_merchant(merchant, testcase_id):
                    release_status = True
                else:
                    release_status = False
            else:
                release_status = True
        else:
            release_status = False
    else:
        if user == None :
            user = ""
        logger.info(f"User {user} was not blocked. So releasing is skipped.")
    return release_status

def release_admin_user(testcase_id:str) -> bool:
    """
    This method is used to release an admin user that is assigned to a test case.
        :param testcase_id
        :return: bool
    """
    release_status = False
    user = get_user_assigned_to_testcase(testcase_id, "Admin")
    if user:
        if unblock_user(user,testcase_id):
            merchant = get_merchant_of_user(user)
            if check_if_merchant_be_released(merchant):
                if unblock_merchant(merchant, testcase_id):
                    release_status = True
                else:
                    release_status = False
            else:
                release_status = True
        else:
            release_status = False
    else:
        if user == None :
            user = ""
        logger.info(f"User {user} was not blocked. So releasing is skipped.")
    return release_status

def releasePortalUser(testcase_id:str) -> bool:
    """
    This method is used to release an portal user that is assigned to a test case.
        :param testcase_id
        :return: bool
    """
    release_status = False
    user = get_user_assigned_to_testcase(testcase_id, "Portal")
    if user:
        if unblock_user(user, testcase_id):
            release_status = True
    else:
        if user == None :
            user = ""
        logger.info(f"User {user} was not blocked. So releasing is skipped.")
    return release_status


def get_merchant_assigned_to_testcase(testcase_id: str) -> str:
    """
    This method is used to get the merchant assigned to the test case.
    :param testcase_id: str, db cursor
    :return: str
    """
    global merchant
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT * FROM merchants_blocked WHERE TestcaseID = "{testcase_id}"')
        db_values = cursor.fetchone()
        if db_values:
            merchant = db_values[0]
        else:
            merchant =  None
    except Exception as e:
        logger.error("Unable to check if any merchant is assigned to the test case. This is due to error "+str(e))
        merchant =  None
    cursor.close()
    conn.close()
    return merchant

def get_available_merchant() -> str:
    """
    This method is used to get the available merchant
    :param testcase_id: db cursor
    :return: str
    """
    global merchant
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute('SELECT MerchantCode FROM (SELECT * FROM merchants WHERE CreationStatus IN("Created", "Existed")) WHERE  Availability = "Available" AND MerchantCode != "EZETAP";')
        db_values = cursor.fetchone()
        if db_values:
            merchant = db_values[0]
        else:
            merchant = None
    except Exception as e:
        logger.error("Unable to fetch any available merchants due to error "+str(e))
        merchant = None
    cursor.close()
    conn.close()
    return merchant

def get_user_details(merchant_code: str, user_type : str) -> str:
    """
    This method is used for getting the user details from the user table for a specific merchant.
    :param user_type : str
    :return: bool
    """
    global user
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        if merchant_code == "EZETAP":
            cursor.execute(
                f'SELECT Name, MerchantCode, Username, Password FROM users WHERE MerchantCode = "{merchant_code}" AND Type = "{user_type}" AND Availability = "Available";')
        else:
            cursor.execute(f'SELECT Name, MerchantCode, Username, Password FROM users WHERE MerchantCode = "{merchant_code}" AND Type = "{user_type}";')
        db_values = cursor.fetchone()
        if db_values:
            user = db_values
        else:
            user = None
    except Exception as e:
        logger.error("Unable to get the user details of the merchant due to error "+str(e))
        user = None
    cursor.close()
    conn.close()
    return user

def block_merchant_and_users_for_testcase(testcase_id : str, merchant_code : str) -> bool:
    """
    This method is used for blocking the merchant that is going to be assigned to a test case.
    :param testcase_id : str, merchant_code : str, db_connection, db_cursor.
    :return: bool
    """
    block_status = False
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO merchants_blocked(MerchantCode, TestcaseID) Values ("{merchant_code}","{testcase_id}");')
        conn.commit()
        cursor.execute(f'UPDATE merchants SET Availability = "Blocked" where MerchantCode = "{merchant_code}";')
        conn.commit()
        cursor.execute(f'UPDATE users SET Availability = "Blocked" where MerchantCode = "{merchant_code}";')
        conn.commit()
        block_status = True
    except Exception as e:
        logger.error("Unable to block the merchant due to error "+str(e))
        cursor.execute(
            f'DELETE FROM merchants_blocked WHERE MerchantCode = "{merchant_code}";')
        conn.commit()
        cursor.execute(f'UPDATE merchants SET Availability = "Available" where MerchantCode = "{merchant_code}";')
        conn.commit()
    cursor.close()
    conn.close()
    return block_status

def block_user(user_name:str, testcase_id:str) ->bool:
    """
    This method is used to block an user for a particular test case.
    This impacts two tables.
    1. User table where the availability is set to blocked.
    2. users_blocked table where an entry is added for the test case.

    :param user_name:str, testcase_id:str
    :return bool
    """
    blocked_status = False
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO users_blocked(Name, TestcaseID)values('{user_name}','{testcase_id}');")
        conn.commit()
        try:
            cursor.execute(f"UPDATE users SET Availability = 'Blocked' where Name = '{user_name}'")
            conn.commit()
            blocked_status = True
        except Exception as e:
            logger.error("Unable to block the user due to error " + str(e))
            cursor.execute(f"DELETE FROM users_blocked WHERE Name = '{user_name}' AND TestCaseID = '{testcase_id}'")
            conn.commit()
    except Exception as e:
        merchant = get_merchant_of_user(user_name)
        if merchant != "EZETAP":
            if str(e).__contains__("UNIQUE constraint failed"):
                logger.info("This user was already blocked for this test case.")
            else:
                logger.error("Unable block the user due to error " + str(e))
        else:
            logger.error("Unable block the user due to error "+str(e))
    cursor.close()
    conn.close()
    return blocked_status


def unblock_user(user_name:str, testcase_id:str) ->bool:
    """
        This method is used to unblock an user for a particular test case.
        This impacts two tables.
        1. User table where the availability is set to Available.
        2. users_blocked table where an entry is deleted.

            :param user_name:str, testcase_id:str
            :return: bool
        """
    unblocked_status = False
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM users_blocked WHERE Name = '{user_name}' AND TestCaseID = '{testcase_id}'")
        conn.commit()
        try:
            cursor.execute(f"UPDATE users SET Availability = 'Available' where Name = '{user_name}'")
            conn.commit()
            logger.info(f"User {user_name} was unblocked successfully.")
            unblocked_status = True
        except Exception as e:
            logger.error("Unable to unblock the user due to error " + str(e))
            cursor.execute(f"INSERT INTO users_blocked(Name, TestcaseID)values('{user_name}','{testcase_id}');")
            conn.commit()
    except Exception as e:
        logger.error("Unable unblock the user due to error " + str(e))
    cursor.close()
    conn.close()
    return unblocked_status


def block_merchant(merchant_code:str, testcase_id:str) ->bool:
    """
    This method is used to block a merchant for a particular test case.
    This impacts two tables.
    1. merchants table where the availability is set to blocked.
    2. merchants_blocked table where an entry is added for the test case.

    :param merchant_code:str, testcase_id:str
    :return bool
    """
    blocked_status = False
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO merchants_blocked(MerchantCode, TestcaseID)values('{merchant_code}','{testcase_id}');")
        conn.commit()
        try:
            cursor.execute(f"UPDATE merchants SET Availability = 'Blocked' where MerchantCode = '{merchant_code}'")
            conn.commit()
            blocked_status = True
        except Exception as e:
            logger.error("Unable to block the merchant due to error " + str(e))
            cursor.execute(f"DELETE FROM merchants_blocked WHERE MerchantCode = '{merchant_code}' AND TestCaseID = '{testcase_id}'")
            conn.commit()
    except Exception as e:
        logger.error("Unable block the merchant due to error "+str(e))
    cursor.close()
    conn.close()
    return blocked_status


def unblock_merchant(merchant_code:str, testcase_id:str) -> bool:
    """
        This method is used to unblock a merchant.
        This impacts two tables.
        1. merchants table where the availability is set to Available.
        2. merchants_blocked table where an entry is deleted.

            :param merchant_code:str, testcase_id:str
            :return: bool
        """

    unblocked_status = False
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM merchants_blocked WHERE MerchantCode = '{merchant_code}' AND TestCaseID = '{testcase_id}'")
        conn.commit()
        try:
            cursor.execute(f"UPDATE merchants SET Availability = 'Available' where MerchantCode = '{merchant_code}'")
            conn.commit()
            logger.info(f"Merchant {merchant_code} was unblocked successfully.")
            unblocked_status = True
        except Exception as e:
            logger.error("Unable to unblock the merchant due to error " + str(e))
            cursor.execute(f"INSERT INTO merchants_blocked(MerchantCode, TestcaseID)values('{merchant_code}','{testcase_id}');")
            conn.commit()
    except Exception as e:
        logger.error("Unable unblock the merchant due to error " + str(e))
    cursor.close()
    conn.close()
    return unblocked_status

def check_if_merchant_be_released(merchant_code:str) ->bool:
    """
    This method is used to check if a merchant can be released.
    Here the status of all the users under the merchant is check and if none of the users are blocked, merchant is release.

    :param merchant_code:str, testcase_id:str
    :return: bool
    """
    release_status = False
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE MerchantCode = '{merchant_code}' and Availability = 'Blocked';")
        users = cursor.fetchall()
        if users:
            logger.info("Merchant cannot be unblocked. There are user/s which are blocked.")
            release_status = False
        else:
            logger.info("Merchant can be unblocked. There is no user blocked.")
            release_status = True
    except Exception as e:
        logger.error("Unable to check the release status of merchant due to error "+str(e))
    cursor.close()
    conn.close()
    return release_status


def get_user_assigned_to_testcase(testcase_id:str, user_type:str) -> str:
    """
    This method is used to fetch the user assigned to a testcase.
    This also requires the the type of user since a test case can have more than one type of user.
    :param testcase_id:str
    :return: str
    """
    user = ""
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users_blocked where TestcaseID = '{testcase_id}';")
        users = cursor.fetchall()
        for current_user in users:
            user_name = current_user[0]
            cursor.execute(f"SELECT * from users where Name = '{user_name}';")
            user_details = cursor.fetchone()
            if str(user_details[5]).lower() == user_type.lower():
                user = user_details[0]
                break
            else:
                user = None
    except Exception as e:
        if str(e).__contains__("'NoneType' object is not subscriptable"):
            logger.info(f"No user is assigned to the testcase {testcase_id}")
        else:
            logger.error("Unable to get the user associated with the test case due to error "+str(e))
        user = None
    cursor.close()
    conn.close()
    return user

def get_merchant_assigned_to_testcase(testcase_id:str) -> str:
    """
    This method is used to fetch the merchant assigned to a testcase.
    :param testcase_id:str
    :return: str
    """
    merchant = ""
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM merchants_blocked where TestcaseID = '{testcase_id}';")
        db_value = cursor.fetchone()
        merchant = db_value[0]
    except Exception as e:
        logger.error("Unable to get the merchant associated with the test case due to error "+str(e))
        merchant = None
    cursor.close()
    conn.close()
    return merchant

def get_merchant_of_user(user_name:str) -> str:
    """This method is used to fetch the merchant associated with a user.
    :param user_name:str
    :return: str
    """
    merchant = ""
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"SELECT MerchantCode FROM users WHERE Name = '{user_name}';")
        db_value = cursor.fetchone()
        if(db_value):
            merchant = db_value[0]
        else:
            logger.info("User is not available in the users table.")
            merchant = None
    except Exception as e:
        logger.error("Unable to get the merchant associated with user due to error "+str(e))
        merchant = None
    cursor.close()
    conn.close()
    return merchant



# print(getAppUserCredentials("ABC"))
# print(get_admin_user_details("DEF"))
# print(getPortalUserCredentials("GHI"))
# time.sleep(5)
# print(releaseAppUser("ABC"))
# print(release_admin_user("DEF"))
# print(releasePortalUser("GHI"))




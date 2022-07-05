import sqlite3
from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)

dbPath = ConfigReader.read_config_paths("System","automation_suite_path")+"/Database/ezeauto.db"

def get_app_user_details(testcase_id: str) -> list:
    """
    This method is used to get the app user credentials along with the merchant code of the user.
    :param testcase_id: str
    :return: list
    """
    proceed = False
    print("Trying to get available app user credentials from DB")
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        app_user_details = {}
        timer = 0
        while timer < 10:
            assigned_merchant = get_merchant_assigned_to_testcase(testcase_id, cursor)
            available_user = ""
            if assigned_merchant:
                available_user = get_user_details(cursor,assigned_merchant,"App")
                if available_user:
                    app_user_details["name"] = available_user[0]
                    app_user_details["merchant_code"] = available_user[1]
                    app_user_details["username"] = available_user[2]
                    app_user_details["password"] = available_user[3]
                    return app_user_details
                else:
                    logger.warning("App user is not available under this merchant.")
                    return None
            else:
                unassigned_merchant = get_available_merchant(cursor)
                available_user = get_user_details(cursor, unassigned_merchant, "App")
                if available_user:
                    if block_merchant_and_users_for_testcase(conn, cursor, testcase_id, unassigned_merchant):
                        app_user_details["name"] = available_user[0]
                        app_user_details["merchant_code"] = available_user[1]
                        app_user_details["username"] = available_user[2]
                        app_user_details["password"] = available_user[3]
                        return app_user_details
                    else:
                        logger.error("Though user is available, attempt to block merchant failed.")
                        return None
                else:
                    logger.warning("App user is not available under this merchant.")
                    return None
            timer = timer+1
    except Exception as e:
        logger.error("Unable to connect to the Database for fetching the app user details")
        return None


def get_admin_user_details(testcase_id: str) -> list:
    """
    This method is used to get the admin user credentials along with the merchant code of the user.
    :param testcase_id: str
    :return: list
    """
    proceed = False
    print("Trying to get available admin user credentials from DB")
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        admin_user_details = {}
        timer = 0
        while timer < 10:
            assigned_merchant = get_merchant_assigned_to_testcase(testcase_id, cursor)
            available_user = ""
            if assigned_merchant:
                available_user = get_user_details(cursor,assigned_merchant,"Admin")
                if available_user:
                    admin_user_details["name"] = available_user[0]
                    admin_user_details["merchant_code"] = available_user[1]
                    admin_user_details["username"] = available_user[2]
                    admin_user_details["password"] = available_user[3]
                    return admin_user_details
                else:
                    logger.warning("Admin user is not available under this merchant.")
                    return None
            else:
                unassigned_merchant = get_available_merchant(cursor)
                available_user = get_user_details(cursor, unassigned_merchant, "Admin")
                if available_user:
                    if block_merchant_and_users_for_testcase(conn, cursor, testcase_id, unassigned_merchant):
                        admin_user_details["name"] = available_user[0]
                        admin_user_details["merchant_code"] = available_user[1]
                        admin_user_details["username"] = available_user[2]
                        admin_user_details["password"] = available_user[3]
                        return admin_user_details
                    else:
                        logger.error("Though user is available, attempt to block merchant failed.")
                        return None
                else:
                    logger.warning("Admin user is not available under this merchant.")
                    return None
            timer = timer+1
    except Exception as e:
        logger.error("Unable to connect to the Database for fetching the app user details")
        return None

def get_merchant_assigned_to_testcase(testcase_id: str, dbcursor) -> str:
    """
    This method is used to get the merchant assigned to the test case.
    :param testcase_id: str, db cursor
    :return: str
    """
    try:
        dbcursor.execute(f'SELECT * FROM merchants_blocked WHERE TestcaseID = "{testcase_id}"')
        merchant = dbcursor.fetchone()
        if merchant:
            return merchant[0]
        else:
            return None
    except Exception as e:
        logger.error("Unable to check if any merchant is assigned to the test case. This is due to error "+str(e))
        return None

def get_available_merchant(dbcursor) -> str:
    """
    This method is used to get the available merchant
    :param testcase_id: db cursor
    :return: str
    """
    try:
        dbcursor.execute('SELECT MerchantCode FROM (SELECT * FROM merchants WHERE CreationStatus IN("Created", "Existed")) WHERE  Availability = "Available" AND MerchantCode != "EZETAP";')
        merchants = dbcursor.fetchone()
        if merchants:
            return merchants[0]
        else:
            return None
    except Exception as e:
        logger.error("Unable to fetch any available merchants due to error "+str(e))
        return None

def get_user_details(dbcursor, merchant_code: str, user_type : str) -> str:
    """
    This method is used for getting the user details from the user table.
    :param user_type : str
    :return: bool
    """
    try:
        dbcursor.execute(f'SELECT Name, MerchantCode, Username, Password FROM users WHERE MerchantCode = "{merchant_code}" AND Type = "{user_type}";')
        user_details = dbcursor.fetchone()
        if user_details:
            return user_details
        else:
            return None
    except Exception as e:
        logger.error("Unable to get the user details of the merchant due to error "+str(e))
        return None

def block_merchant_and_users_for_testcase(db_connection, db_cursor, testcase_id : str, merchant_code : str) -> bool:
    """
    This method is used for blocking the merchant that is going to be assigned to a test case.
    :param testcase_id : str, merchant_code : str, db_connection, db_cursor.
    :return: bool
    """
    try:
        db_cursor.execute(f'INSERT INTO merchants_blocked(MerchantCode, TestcaseID) Values ("{merchant_code}","{testcase_id}");')
        db_connection.commit()
        db_cursor.execute(f'UPDATE merchants SET Availability = "Blocked" where MerchantCode = "{merchant_code}";')
        db_connection.commit()
        db_cursor.execute(f'UPDATE users SET Availability = "Blocked" where MerchantCode = "{merchant_code}";')
        db_connection.commit()
        return True
    except Exception as e:
        logger.error("Unable to block the merchant due to error "+str(e))
        return False

print(get_admin_user_details("TC_02"))



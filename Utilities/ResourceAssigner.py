import sqlite3
import time
from datetime import datetime
from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)

dbPath = ConfigReader.read_config_paths("System", "automation_suite_path")+"/Database/ezeauto.db"


def getDeviceFromDB(testCaseID):
    proceed = False
    print("Trying to get available device from DB")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    device = {}
    timer = 0
    while timer<10:
        try:
            cursor.execute("SELECT DeviceId,DeviceName FROM devices WHERE Status = 'Available';")
            devices = cursor.fetchall()
            if devices != None and len(devices) > 0:
                for dev in devices:
                    deviceID = str(dev[0])
                    deviceName = dev[1]
                    try:
                        cursor.execute(
                            "INSERT INTO devices_blocked(DeviceId, DeviceName, TestCaseID) VALUES('" + deviceID + "','" + deviceName + "','" + testCaseID + "');")
                        conn.commit()
                        try:
                            cursor.execute("UPDATE devices SET Status = 'Blocked' WHERE DeviceId = '" + deviceID + "';")
                            conn.commit()
                            print("Appium server with device ID " + deviceID + " is available")
                            device['DeviceId'] = deviceID
                            device['DeviceName'] = deviceName
                            proceed = True
                            break
                        except:
                            print("Unable to change the status of device in DB, so deleting the entry in devices_blocked table.")
                            cursor.execute("DELETE FROM devices_blocked WHERE DeviceId = '" + deviceID + "';")
                            conn.commit()
                            proceed == False
                    except Exception as e:
                        proceed = False
                        if str(e).__contains__("UNIQUE constraint failed"):
                            print(
                                "Two processess tried accessing the same device, hence this test case will retry to get another device.")
                        else:
                            print("Unable to add entry into the devices_blocked table due to error : " + str(e))
            else:
                print("Unable to fetch any device. Retrying...")
                proceed = False
        except Exception as e:
            print("Unable to retrieve Device details from devices db due to error : "+str(e))
            proceed = False

        if proceed:
            break
        else:
            time.sleep(1)
            timer += 1
    conn.commit()
    conn.close()

    if len(device)==0:
        return None
    else:
        return device



def releaseDeviceInDBusingTestCaseID(testCaseID):

    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        proceed = True
        cursor.execute("SELECT DeviceId FROM devices_blocked WHERE TestCaseID = '" + testCaseID + "';")
        try:
            DeviceIds = cursor.fetchall()
            try:
                cursor.execute("DELETE FROM devices_blocked WHERE TestCaseID = '" + testCaseID + "';")
                conn.commit()
                for id in DeviceIds:
                    try:
                        cursor.execute("UPDATE devices SET Status='Available' WHERE DeviceId = '" + id[0] + "';")
                        conn.commit()
                        print(id[0] + " is released at " + str(datetime.now().time()))
                    except Exception as e:
                        print("Unable to release the device due to " + str(e))
            except Exception as e:
                print("Unable to delete the device from devices_blocked DB due to "+str(e))
                proceed = False

        except Exception as e:
            print("Unable to get device from devices_blocked table due to error : "+str(e))
            print("Above error is because given test case does not have any devices blocked.")
        conn.commit()
        conn.close()
    except:
        print("Unable to release the device associated with test case " + testCaseID)


def getAppiumServerFromDB(testCaseID):
    proceed = False
    print("Trying to get available appium server from DB")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    appiumServer={}
    timer = 0
    while timer<20:
        try:
            cursor.execute("SELECT PortNumber,ServerName FROM appium_servers WHERE Status = 'Available';")
            availableAppiumServers = cursor.fetchall()
            if availableAppiumServers != None and len(availableAppiumServers) > 0 :
                for server in availableAppiumServers:
                    portNumber = str(server[0])
                    serverName = server[1]
                    try:
                        cursor.execute(
                            "INSERT INTO appium_servers_blocked(PortNumber, ServerName, TestCaseID) VALUES('" + portNumber + "','" + serverName + "','" + testCaseID + "');")
                        conn.commit()
                        try:
                            cursor.execute("UPDATE appium_servers SET Status = 'Blocked' WHERE PortNumber = '"+portNumber+"';")
                            conn.commit()
                            print("Appium server with port number " + portNumber + " is available")
                            appiumServer['PortNumber'] = portNumber
                            appiumServer['ServerName'] = serverName
                            proceed = True
                            break
                        except:
                            print("Unable to change the status of appium server in DB, so deleting the entry in appium_servers_blocked table.")
                            cursor.execute("DELETE FROM appium_servers_blocked WHERE PortNumber = '"+portNumber+"';")
                            conn.commit()
                            proceed == False
                    except Exception as e:
                        proceed = False
                        if str(e).__contains__("UNIQUE constraint failed"):
                            print(
                                "Two processess tried accessing the same server, hence this test case will retry to get another server.")
                        else:
                            print("Unable to add entry into the appium_servers_blocked table due to error : " + str(e))
            else:
                print("Unable to fetch any appium server. Retrying...")
                proceed = False
        except Exception as e:
            print("Unable to retrieve Device details from devices db due to error : "+str(e))
            proceed = False

        if proceed:
            break
        else:
            time.sleep(1)
            timer += 1
    conn.commit()
    conn.close()

    if len(appiumServer)==0:
        return None
    else:
        return appiumServer



def releaseAppiumServerInDBUsingTestCaseID(testCaseID):

    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        proceed = True
        cursor.execute("SELECT PortNumber FROM appium_servers_blocked WHERE TestCaseID = '" + testCaseID + "';")
        try:
            PortNumber = cursor.fetchall()
            try:
                cursor.execute("DELETE FROM appium_servers_blocked WHERE TestCaseID = '" + testCaseID + "';")
                conn.commit()
                print("Deleted the entry in appium_servers_blocked table for the test case "+testCaseID)
                for port in PortNumber:
                    try:
                        cursor.execute("UPDATE appium_servers SET Status='Available' WHERE PortNumber = '" + str(port[0]) + "';")
                        conn.commit()
                        print(str(port[0]) + " is released at " + str(datetime.now().time()))
                    except Exception as e:
                        print("Unable to release the port number due to " + str(e))
            except Exception as e:
                print("Unable to delete the port number from appium_servers_blocked DB due to "+str(e))
                proceed = False

        except Exception as e:
            print("Unable to get appium server from appium_servers table due to error : "+str(e))
            print("Above error is because given test case does not have any appium servers blocked.")
        conn.commit()
        conn.close()
    except:
        print("Unable to release the appium server associated with test case " + testCaseID)



def clearAssignerTables():
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users_blocked;")
        cursor.execute("DELETE FROM users;")
        cursor.execute("DELETE FROM merchants_blocked;")
        cursor.execute("DELETE FROM merchants;")
        cursor.execute("DELETE FROM devices;")
        cursor.execute("DELETE FROM devices_blocked;")
        cursor.execute("DELETE FROM appium_servers;")
        cursor.execute("DELETE FROM appium_servers_blocked;")
        cursor.execute("DELETE FROM api_details;")
        conn.commit()
    except Exception as e:
        print("Unable to clear the user tables due to error : "+str(e))
    cursor.close()
    conn.close()


def updateAppUsersInDB(listOfDictionariesWithAppUserDetails : []):
    """
    This method is used to update the user details into the user_credentials database.
    Make sure the argument passed is a list of dictionaries containing details of the user i.e., username and password.
    Make sure the dictionary for each user contains the below two keys
    1. Username
    2. Password
    """
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        if len(listOfDictionariesWithAppUserDetails)>0:
            for userDetails in listOfDictionariesWithAppUserDetails:
                username = userDetails["Username"]
                password = userDetails["Password"]
                try:
                    cursor.execute("INSERT INTO app_users(Username, Password, Status)values('"+username+"','"+password+"', 'Available');")
                    print("App user "+username+" added successfully to the DB.")
                except Exception as e:
                    print("Unable to add the app user "+username+" to the db due to the error - "+str(e))
            conn.commit()
            conn.close()
        else:
            print("App users list is empty")
    except Exception as e:
        print("Unable to update the app user details to DB")

def updatePortalUsersInDB(listOfDictionariesWithPortalUserDetails : []):
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        if len(listOfDictionariesWithPortalUserDetails)>0:
            for userDetails in listOfDictionariesWithPortalUserDetails:
                username = userDetails["Username"]
                password = userDetails["Password"]
                try:
                    cursor.execute("INSERT INTO portal_users(Username, Password, Status)values('"+username+"','"+password+"', 'Available');")
                    print("Portal user "+username+" added successfully to the DB.")
                except Exception as e:
                    print("Unable to add the portal user "+username+" to the db due to the error - "+str(e))
            conn.commit()
            conn.close()
        else:
            print("Portal users list is empty")
    except Exception as e:
        print("Unable to update the portal user details to DB")

def updateAppiumServersInDB(listOfPorts: []):
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        if len(listOfPorts)>0:
            i=1
            for port in listOfPorts:
                try:
                    cursor.execute("INSERT INTO appium_servers(PortNumber, ServerName, Status)values("+str(port)+", 'Server"+str(i)+"', 'Available');")
                    print("Appium server port "+str(port)+" successfully added to the db.")
                    i +=1
                except Exception as e:
                    print("Unable to add the appium server with port "+port+"to the db due to error - "+str(e))
            conn.commit()
            conn.close()
        else:
            print("Appium servers list is empty")
    except Exception as e:
        print("Unable to update the appium servers to DB")


def updateDevicesInDB(listOfDevices: []):
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        if len(listOfDevices)>0:
            i=1
            for device in listOfDevices:
                try:
                    cursor.execute("INSERT INTO devices(DeviceId, DeviceName, Status)values('"+str(device)+"', 'Device"+str(i)+"', 'Available');")
                    conn.commit()
                    print("Device "+device+" successfully added to the db.")
                    i +=1
                except Exception as e:
                    print("Unable to add the device "+device+" in the db due to error -"+str(e))
            conn.close()

        else:
            print("Devices list is empty")
    except Exception as e:
        print("Unable to update the devices to DB")


def getAppUserCredentials(testcase_id: str) -> dict:
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


def get_admin_user_details(testcase_id: str) -> dict:
    """
    This method is used to get the admin user credentials along with the merchant code of the user.
    :param testcase_id: str
    :return: dict
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


def getPortalUserCredentials(testcase_id: str) -> dict:
    """
    This method is used to get the portal user credentials along with the merchant code of the user.
    :param testcase_id: str
    :return: dict
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

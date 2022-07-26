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
    while timer < 10:
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


def getAppUserCredentials(testCaseID):
    proceed = False
    print("Trying to get available app user credentials from DB")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    appUserCredentials={}
    timer = 0
    while timer<20:
        try:
            cursor.execute("SELECT Username, Password FROM app_users WHERE Status = 'Available';")
            availableAppUsers = cursor.fetchall()
            if availableAppUsers != None and len(availableAppUsers) > 0 :
                for appUser in availableAppUsers:
                    username = str(appUser[0])
                    password = appUser[1]
                    try:
                        cursor.execute("INSERT INTO app_users_blocked(Username, TestCaseID) VALUES('"+username+"','"+testCaseID+"');")
                        conn.commit()
                        try:
                            cursor.execute("UPDATE app_users SET Status = 'Blocked' WHERE Username = '"+username+"';")
                            conn.commit()
                            print("App username " + username + " is available")
                            print("App username " + username + " is assigned at "+str(datetime.now().time()))
                            appUserCredentials['Username'] = username
                            appUserCredentials['Password'] = password
                            proceed = True
                            break
                        except:
                            print("Unable to change the status of app user in DB, so deleting the entry in app_users_blocked table.")
                            cursor.execute("DELETE FROM app_users_blocked WHERE username = '"+username+"';")
                            conn.commit()
                            proceed == False
                    except Exception as e:
                        proceed = False
                        if str(e).__contains__("UNIQUE constraint failed"):
                            print(
                                "Two processess tried accessing the same app user, hence this test case will retry to get another app user.")
                        else:
                            print("Unable to add entry into the app_users_blocked table due to error : " + str(e))
            else:
                print("Unable to fetch any app user. Retrying...")
                proceed = False
        except Exception as e:
            print("Unable to retrieve app user details from app_users db due to error : "+str(e))
            proceed = False

        if proceed:
            break
        else:
            time.sleep(1)
            timer += 1
    conn.commit()
    conn.close()

    if len(appUserCredentials)==0:
        return None
    else:
        return appUserCredentials

def getPortalUserCredentials(testCaseID):
    proceed = False
    print("Trying to get available portal user credentials from DB")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    portalUserCredentials={}
    timer = 0
    while timer<20:
        try:
            cursor.execute("SELECT Username, Password FROM portal_users WHERE Status = 'Available';")
            availablePortalUsers = cursor.fetchall()
            if availablePortalUsers != None and len(availablePortalUsers) > 0 :
                for portalUser in availablePortalUsers:
                    username = str(portalUser[0])
                    password = portalUser[1]
                    try:
                        cursor.execute("INSERT INTO portal_users_blocked(Username, TestCaseID) VALUES('"+username+"','"+testCaseID+"');")
                        conn.commit()
                        try:
                            cursor.execute("UPDATE portal_users SET Status = 'Blocked' WHERE Username = '"+username+"';")
                            conn.commit()
                            print("Portal username " + username + " is available")
                            print("Portal username " + username + " is assigned at "+str(datetime.now().time()))
                            portalUserCredentials['Username'] = username
                            portalUserCredentials['Password'] = password
                            proceed = True
                            break
                        except:
                            print("Unable to change the status of portal user in DB, so deleting the entry in portal_users_blocked table.")
                            cursor.execute("DELETE FROM portal_users_blocked WHERE username = '"+username+"';")
                            conn.commit()
                            proceed = False
                    except Exception as e:
                        proceed = False
                        if str(e).__contains__("UNIQUE constraint failed"):
                            print(
                                "Two processess tried accessing the same portal user, hence this test case will retry to get another portal user.")
                        else:
                            print("Unable to add entry into the portal_users_blocked table due to error : " + str(e))
            else:
                print("Unable to fetch any portal user. Retrying...")
                proceed = False
        except Exception as e:
            print("Unable to retrieve portal user details from portal_users db due to error : "+str(e))
            proceed = False

        if proceed:
            break
        else:
            time.sleep(1)
            timer += 1
    conn.commit()
    conn.close()

    if len(portalUserCredentials)==0:
        return None
    else:
        return portalUserCredentials



def releaseAppUser(testCaseID):

    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        proceed = True
        cursor.execute("SELECT Username FROM app_users_blocked WHERE TestCaseID = '" + testCaseID + "';")
        try:
            username = cursor.fetchall();
            try:
                cursor.execute("DELETE FROM app_users_blocked WHERE TestCaseID = '" + testCaseID + "';")
                conn.commit()
                for user in username:
                    try:
                        cursor.execute("UPDATE app_users SET Status='Available' WHERE Username = '" + user[0] + "';")
                        conn.commit()
                        print("App user "+user[0] + " is released at " + str(datetime.now().time()))
                    except Exception as e:
                        print("Unable to release the app user due to " + e)
            except Exception as e:
                print("Unable to delete the app user from app_users_blocked DB due to "+str(e))
                proceed = False

        except Exception as e:
            print("Unable to get app user from app_users table due to error : "+str(e))
            print("Above error is because given test case does not have any app users blocked.")
        conn.commit()
        conn.close()
    except:
        print("Unable to release the app user associated with test case " + testCaseID)

def releasePortalUser(testCaseID):

    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        proceed = True
        cursor.execute("SELECT Username FROM portal_users_blocked WHERE TestCaseID = '" + testCaseID + "';")
        try:
            username = cursor.fetchall();
            try:
                cursor.execute("DELETE FROM portal_users_blocked WHERE TestCaseID = '" + testCaseID + "';")
                conn.commit()
                for user in username:
                    try:
                        cursor.execute("UPDATE portal_users SET Status='Available' WHERE Username = '" + user[0] + "';")
                        conn.commit()
                        print("Portal user "+user[0] + " is released at " + str(datetime.now().time()))
                    except Exception as e:
                        print("Unable to release the portal user due to " + e)
            except Exception as e:
                print("Unable to delete the portal user from portal_users_blocked DB due to "+str(e))
                proceed = False

        except Exception as e:
            print("Unable to get portal user from portal_users table due to error : "+str(e))
            print("Above error is because given test case does not have any portal users blocked.")
        conn.commit()
        conn.close()
    except:
        print("Unable to release the portal user associated with test case " + testCaseID)

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


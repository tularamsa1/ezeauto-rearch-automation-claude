import sqlite3
import pandas
from DataProvider import GlobalConstants
from Utilities import ConfigReader, DBProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)
merchant_user_creation_excel_path = ConfigReader.read_config_paths("System",
                                                                   "automation_suite_path") + "/DataProvider/merchant_user_creation.xlsx"


def clearAssignerTables():
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users_blocked;")
        cursor.execute("DELETE FROM users;")
        cursor.execute("DELETE FROM merchants_blocked;")
        cursor.execute("DELETE FROM merchants;")
        cursor.execute("DELETE FROM app_users_blocked;")
        cursor.execute("DELETE FROM app_users;")
        cursor.execute("DELETE FROM portal_users_blocked;")
        cursor.execute("DELETE FROM portal_users;")
        cursor.execute("DELETE FROM devices_blocked;")
        cursor.execute("DELETE FROM devices;")
        cursor.execute("DELETE FROM appium_servers_blocked;")
        cursor.execute("DELETE FROM appium_servers;")
        cursor.execute("DELETE FROM api_details;")
        cursor.execute("DELETE FROM acquisitions;")
        cursor.execute("DELETE FROM terminal_details;")
        cursor.execute("DELETE FROM remotepay_settings;")
        conn.commit()
        logger.info("All the assigner tables cleared successfully.")
    except Exception as e:
        print("Unable to clear the user tables due to error : " + str(e))
    cursor.close()
    conn.close()


def update_merchants_to_db(merchants_list: list):
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
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


def update_users_to_db(users_list: list):
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        for user in users_list:
            if check_merchant_exists_in_automation_db(user["MerchantCode"]):
                try:
                    cursor.execute(
                        f"insert into users(Name, MerchantCode, Username, Password, Mobile, Type)values(\"{user['Name']}\", \"{user['MerchantCode']}\", \"{user['Username']}\", \"{user['Password']}\", \"{user['Mobile']}\", \"{user['Type']}\");")
                    conn.commit()
                    logger.info(f"User {user['Name']} successfully added to the users db.")
                except Exception as e:
                    logger.error(f"Unable to add the user {user['Name']} into db due to error {e}")
            else:
                logger.info(
                    f"User {user['Name']} creation skipped since associated merchant is not available in merchants db.")
    except Exception as e:
        logger.error(f"Unable to connect to the db due to error {e}")
    cursor.close()
    conn.close()


def update_app_users_to_db():
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE type = 'App' and CreationStatus IN ('Created','Existed');")
        app_users = cursor.fetchall()
        if app_users:
            for app_user in app_users:
                try:
                    cursor.execute(
                        f"INSERT INTO app_users(Username, Password, Status)VALUES('{app_user[2]}','{app_user[3]}', 'Available')")
                    conn.commit()
                    logger.info(f"App user {app_user[0]} added to the db successfully.")
                except Exception as e:
                    if str(e).__contains__("UNIQUE constraint failed"):
                        logger.info(f"App user {app_user[0]} is already available in the db.")
                    else:
                        logger.error(f"Unable to add entries into app_user table due to error {str(e)}")
        else:
            logger.warning("Users table does not contain any app users that was created or existed in this environment")
    except Exception as e:
        logger.error(f"Unable to connect to automation db due to error {str(e)}")
    cursor.close()
    conn.close()


def update_portal_users_to_db():
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE type = 'Portal' and CreationStatus IN ('Created','Existed');")
        portal_users = cursor.fetchall()
        if portal_users:
            for portal_user in portal_users:
                try:
                    cursor.execute(
                        f"INSERT INTO portal_users(Username, Password, Status)VALUES('{portal_user[2]}','{portal_user[3]}', 'Available')")
                    conn.commit()
                    logger.info(f"Portal user {portal_user[0]} added to the db successfully.")
                except Exception as e:
                    if str(e).__contains__("UNIQUE constraint failed"):
                        logger.info(f"Portal user {portal_user[0]} is already available in the db.")
                    else:
                        logger.error(f"Unable to add entries into portal_user table due to error {str(e)}")
        else:
            logger.warning("Users table does not contain any portal users that was created or existed in this "
                           "environment")
    except Exception as e:
        logger.error(f"Unable to connect to automation db due to error {str(e)}")
    cursor.close()
    conn.close()


def get_merchants_list_from_excel() -> list:
    merchants_list = []
    merchant_creation_excel_data = pandas.read_excel(merchant_user_creation_excel_path, sheet_name="UserDetails")
    if len(merchant_creation_excel_data) > 0:
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
    merchant_creation_excel_data = pandas.read_excel(merchant_user_creation_excel_path, sheet_name="UserDetails")
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
                logger.error(
                    f"Type of user {(merchant_creation_excel_data.loc[i]).to_dict()['Name']} is defined wrongly. So its not added to user creation list.")
    else:
        logger.warning("Unable to pull users list since no data available in the merchant creation excel file.")
    return users_list


def check_merchant_exists_in_automation_db(merchant):
    conn = ""
    cursor = ""
    exists = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(f"select * from merchants where MerchantCode = '{merchant}'")
            merchant_info = cursor.fetchone()
            if merchant_info is None:
                logger.info(f"Merchant {merchant} is not available in the automation db.")
                exists = False
            else:
                logger.info(f"Merchant {merchant} is available in the automation db.")
                exists = True
        except Exception as e:
            logger.error(f"Unable to check if {merchant} is available in the automation db due to error {str(e)}")
    except Exception as e:
        logger.error(f"Unable to connect to the db due to error {e}")
    cursor.close()
    conn.close()
    return exists


def update_acquisitions_to_db():
    """
    This method is used to read the acquisition details from excel and update the db.
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        acquisition_details = pandas.read_excel(merchant_user_creation_excel_path, sheet_name="AcquisitionDetails")
        acquisition_details.fillna('N/A', inplace=True)
        for i in range(0, len(acquisition_details)):
            cursor.execute(f"SELECT * FROM acquisitions WHERE AcquirerCode = '{acquisition_details.iloc[i]['Acquirer Code']}' AND PaymentGateway = '{acquisition_details.iloc[i]['Payment Gateway']}';")
            if not len (cursor.fetchall())>0:
                cursor.execute(
                    f"""INSERT INTO acquisitions(AcquirerCode, PaymentGateway, NumberOfTerminals, HsmName, BankCode, BqrBankCode, UPIBankCode, BqrTerminalDependant, UpiTerminalDependant, KeyForUpi, VirtualMidRequired)values("{acquisition_details.iloc[i]['Acquirer Code']}", "{acquisition_details.iloc[i]['Payment Gateway']}", "{acquisition_details.iloc[i]['Number of Terminals']}", "{acquisition_details.iloc[i]['HSM Name']}", "{acquisition_details.iloc[i]['Bank Code']}", "{acquisition_details.iloc[i]['BQR Bank Code']}", "{acquisition_details.iloc[i]['UPI(psp) Bank Code']}", "{acquisition_details.iloc[i]['BQR Terminal Dependant']}", "{acquisition_details.iloc[i]['UPI Terminal Dependant']}", "{acquisition_details.iloc[i]['Key for UPI']}", "{acquisition_details.iloc[i]['virtual MID Required']}");""")
                conn.commit()
                logger.debug(f"Details of acquisition {acquisition_details.iloc[i]['Acquirer Code']} and payment gateway {acquisition_details.iloc[i]['Payment Gateway']} added to acquisitions table.")
            else:
                logger.debug(f"Entry for acquisition{acquisition_details.iloc[i]['Acquirer Code']} and payment gateway{acquisition_details.iloc[i]['Payment Gateway']} is already available.")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Unable to update the acquisition details to sqlite db due to error {str(e)}")


def update_terminal_details_of_merchant(merchant_code: str):
    """
    This method is used to update the terminal-details table in the db.
    :param merchant_code str
    """
    conn = ""
    cursor = ""
    try:
        result = DBProcessor.getValueFromDB(f"SELECT name from org where org_code = '{merchant_code}';")
        merchant_name = result['name'][0]
        result = DBProcessor.getValueFromDB(f"SELECT tid, device_serial, acquirer_code, payment_gateway, "
                                            f"acq_category_code, mid from terminal_info "
                                            f"where org_code = '{merchant_code}';")
        if len(result) > 0:
            conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
            cursor = conn.cursor()
            for i in range(0, len(result)):
                try:
                    cursor.execute(f"INSERT INTO terminal_details(TID, DeviceSerial, AcquirerCode, PaymentGateway,"
                                   f" CategoryCode, MID, MerchantCode, MerchantName)VALUES('{result['tid'][i]}', "
                                   f"'{result['device_serial'][i]}', '{result['acquirer_code'][i]}', "
                                   f"'{result['payment_gateway'][i]}', '{result['acq_category_code'][i]}', "
                                   f"'{result['mid'][i]}', '{merchant_code}', '{merchant_name}');")
                    logger.debug(f"Details of tid {result['tid'][i]} added to the terminal details table.")
                except sqlite3.IntegrityError as e:
                    logger.error(f"Unable to add tid {result['tid'][i]} entry for {merchant_code} due to error {str(e)}")
            conn.commit()
            cursor.close()
            conn.close()
        else:
            logger.warning("Merchant does not have any terminals configured.")
    except Exception as e:
        logger.error(f"Unable to update the terminal details into the ezeauto db due to error {str(e)}")


def update_terminal_details_of_all_merchants():
    """
    This method is used to update the terminal details of all merchants into the db.
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"Select MerchantCode from merchants where CreationStatus in ('Created','Existed') and "
                       "Availability = 'Available';")
        merchants = cursor.fetchall()
        for merchant in merchants:
            update_terminal_details_of_merchant(merchant[0])
    except Exception as e:
        logger.error(f"Unable to connect to db due to error {str(e)}")


def update_remotepay_settings():
    """
    This method is used to update the remotepay_settings table with the values defined in excel.
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        remotepay_setting_details = pandas.read_excel(merchant_user_creation_excel_path, sheet_name="RemotepaySettings")
        for i in range(0, len(remotepay_setting_details)):
            cursor.execute(f"Select * from remotepay_settings where Name = '{remotepay_setting_details['Name'][i]}';")
            result = cursor.fetchall()
            try:
                if len(result) > 0:
                    cursor.execute(f"update remotepay_settings set Value = '{remotepay_setting_details['Value'][i]}',"
                                   f"Component = '{remotepay_setting_details['Component'][i]}',"
                                   f"LockId = '{remotepay_setting_details['LockId'][i]}',"
                                   f"Entity = '{remotepay_setting_details['Entity'][i]}', "
                                   f"EntityId = '{remotepay_setting_details['EntityId'][i]}',"
                                   f"Inheritable = '{remotepay_setting_details['Inheritable'][i]}' where "
                                   f"Name = '{remotepay_setting_details['Name'][i]}';")
                else:
                    cursor.execute(f"insert into remotepay_settings(Name, Value, Component, LockId, Entity, EntityId, "
                                   f"Inheritable)values('{remotepay_setting_details['Name'][i]}',"
                                   f"'{remotepay_setting_details['Value'][i]}',"
                                   f"'{remotepay_setting_details['Component'][i]}',"
                                   f"'{remotepay_setting_details['LockId'][i]}',"
                                   f"'{remotepay_setting_details['Entity'][i]}',"
                                   f"'{remotepay_setting_details['EntityId'][i]}',"
                                   f"'{remotepay_setting_details['Inheritable'][i]}');")
                conn.commit()
                logger.debug(f"Details of {remotepay_setting_details['Name'][i]} remote pay settings updated to db.")
            except Exception as e:
                logger.debug(f"Details of {remotepay_setting_details['Name'][i]} remote pay settings not updated to db.")
    except Exception as e:
        logger.error(f"Unable to update the remote pay settings due to error {str(e)}")
    cursor.close()
    conn.close()
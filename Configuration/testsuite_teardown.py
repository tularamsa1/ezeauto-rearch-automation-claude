import sqlite3
import string
import requests
import json
import random
from Configuration.TestSuiteSetup import logger
from DataProvider import GlobalConstants
from Utilities import DBProcessor, APIProcessor, ConfigReader


def revert_payment_settings_default(org_code, bank_code, portal_un, portal_pw, payment_mode=None, bank_code_bqr=None):
    if payment_mode == "CNP":
        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='" + bank_code + "'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                              "password": portal_pw})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

    if payment_mode == "UPI":
        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='" + bank_code + "'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                              "password": portal_pw})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

    if payment_mode == "BQRV4":
        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating bharatqr_merchant_config table inactive: {result}")
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='" + bank_code + "'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)

        if bank_code in ["ICICI_DIRECT", "AXIS_DIRECT"]: bank_code = bank_code_bqr
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='" + bank_code + "'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                              "password": portal_pw})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

    api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_un,
                                                                           "password": portal_pw,
                                                                           "settingForOrgCode": org_code})
    api_details["RequestBody"]["settings"]["upiEnabled"] = "true"
    logger.debug(f"API details  : {api_details} ")
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for setting preconditions is : {response}")

    api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_un,
                                                                            "password": portal_pw,
                                                                            "settingForOrgCode": org_code})
    api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
    api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 6
    logger.debug(f"API details  : {api_details} ")
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for setting preconditions is : {response}")

    api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_un,
                                                                                "password": portal_pw,
                                                                                "settingForOrgCode": org_code})
    api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "false"
    api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
    logger.debug(f"API details  : {api_details}")
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

    api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_un,
                                                                          "password": portal_pw,
                                                                          "settingForOrgCode": org_code})
    api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
    logger.debug(f"API details  : {api_details}")
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

    query = "update terminal_dependency_config set terminal_dependent_enabled=0 where org_code ='" + org_code + "';"
    result = DBProcessor.setValueToDB(query)
    logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                          "password": portal_pw})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for setting precondition DB refresh is : {response}")

    query = "update remotepay_setting set setting_value=2 where setting_name='cnpTxnTimeoutDuration' and  org_code='" + org_code + "';"
    result = DBProcessor.setValueToDB(query)
    logger.info(f"RESULT of updating remotepay_setting table: {result}")


def revert_cnp_payment_settings_default(org_code, bank_code, portal_un, portal_pw, payment_gateway=None):
    if payment_gateway == "CYBERSOURCE":
        query = "update merchant_pg_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating merchant_pg_config table inactive: {result}")
        query = "update merchant_pg_config set status = 'ACTIVE' where org_code='" + org_code + "' and payment_gateway='" + bank_code + "'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                              "password": portal_pw})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

    if payment_gateway == "TPSL":
        query = "update merchant_pg_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")
        query = "update merchant_pg_config set status = 'ACTIVE' where org_code='" + org_code + "' and payment_gateway='" + bank_code + "';"
        logger.info(f"Query is: {query}")
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                              "password": portal_pw})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

    if payment_gateway == "UPI":
        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='" + bank_code + "'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                              "password": portal_pw})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

    query = "update remotepay_setting set setting_value=2 where setting_name='cnpTxnTimeoutDuration' and  org_code='" + org_code + "';"
    result = DBProcessor.setValueToDB(query)
    logger.info(f"RESULT of updating remotepay_setting table: {result}")

    api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_un,
                                                                          "password": portal_pw,
                                                                          "settingForOrgCode": org_code})
    api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
    logger.debug(f"API details  : {api_details}")
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

    query = "update terminal_dependency_config set terminal_dependent_enabled=0 where org_code ='" + org_code + "';"
    result = DBProcessor.setValueToDB(query)
    logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                          "password": portal_pw})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for setting precondition DB refresh is : {response}")


def revert_card_payment_settings_default(org_code: str, portal_un: str, portal_pw: str):
    """
    This method is used to revert the card related settings.
    param: org_code str
    param: portal_un str
    param: portal_pw str
    """
    logger.info(f"Inside the function revert_card_payment_settings_default in testsuite_teardown")

    api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_un,
                                                                                   "password": portal_pw,
                                                                                   "settingForOrgCode": org_code})
    api_details["RequestBody"]["settings"]["cardPaymentEnabled"] = "true"
    api_details["RequestBody"]["settings"]["tipEnabled"] = "false"
    api_details["RequestBody"]["settings"]["tipPercentage"] = "15"
    api_details["RequestBody"]["settings"]["cashBackOption"] = 0
    api_details["RequestBody"]["settings"]["minCashBackAmount"] = "100"
    api_details["RequestBody"]["settings"]["maxCashBackAmount"] = "2000"
    api_details["RequestBody"]["settings"]["preAuthOption"] = "0"
    api_details["RequestBody"]["settings"]["twoStepConfirmPreAuthEnabled"] = "false"
    api_details["RequestBody"]["settings"]["mqttEnabled"] = "false"
    api_details["RequestBody"]["settings"]["mqttRetryPeriod"] = "30"
    api_details["RequestBody"]["settings"]["refundEnabled"] = "true"

    logger.debug(f"API details  : {api_details} ")
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for setting preconditions is : {response}")


def revert_org_settings_default(org_code, portal_un, portal_pw):
    orgsettings_apidetails = DBProcessor.get_api_details('org_settings_update', request_body={
        "username": portal_un,
        "password": portal_pw,
        "settingForOrgCode": org_code
    })
    # Set session expiry as default (86400 sec)
    orgsettings_apidetails["RequestBody"]["settings"]["sessionTimeOut"] = "86400"
    # Set autologin as default (false)
    orgsettings_apidetails["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "false"
    # disabling khaata
    orgsettings_apidetails["RequestBody"]["settings"]["enableKhataForMerchants"] = "false"
    # disabling emi
    orgsettings_apidetails["RequestBody"]["settings"]["emiEnabled"] = "false"
    orgsettings_apidetails["RequestBody"]["settings"]["brandEmiEnabled"] = "true"
    # disabling paylater
    orgsettings_apidetails["RequestBody"]["settings"]["paylaterEnabled"] = "false"
    # disabling collectMobileEmailUpfront
    orgsettings_apidetails["RequestBody"]["settings"]["collectMobileEmailUpfront"] = "false"
    #disabling MultilingualForApp
    orgsettings_apidetails["RequestBody"]["settings"]["enableMultilingualForApp"] = "false"

    logger.debug(f"API details  : {orgsettings_apidetails} ")
    response = APIProcessor.send_request(orgsettings_apidetails)
    logger.debug(f"Response received for setting sessionExpiry as default is : {response}")


def revert_config_FC(portal_username, portal_password):
    """
    This method is to delete the static_qr data from staticqr_intent table and upi_merchant_config data which is having
    following pg_merchant_ids: 'V0$E_ID$MNTR$3gv6aUTnwrN742','V0$E_ID$MNTR$agO6RXqbLMNUMV','V0$E_ID$MNTR$hnea1t9qrvjGUV'
    FC: FREE_CHARGE(Payment Gateway)
    """
    config_ids = []
    conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * from merchants;")
    merchants = cursor.fetchall()
    automation_merchants = []
    for merchant in merchants:
        automation_merchants.append(merchant[0])
    automation_merchants = str(tuple(automation_merchants))
    logger.debug(f"automation merchants are : {automation_merchants}")
    query = "select id from upi_merchant_config where pgMerchantId in ('V0$E_ID$MNTR$3gv6aUTnwrN742', " \
            "'V0$E_ID$MNTR$agO6RXqbLMNUMV', 'V0$E_ID$MNTR$hnea1t9qrvjGUV');"
    logger.debug(f"Query to fetch id from the upi_merchant_config for which upi_bank_code is "
                 f"AXIS_FC : {query}")
    result = DBProcessor.getValueFromDB(query)
    logger.debug(f"Result for the query '{query}' is : {result} ")
    for i in range(int(len(result))):
        config_ids.append(result['id'].values[i])
    config_ids = str(tuple(config_ids))

    query = "delete from staticqr_intent where config_id in " + config_ids + ";"
    result = DBProcessor.delete_value_from_db(query)
    logger.debug(f"Result for the query '{query}' is : {result} ")

    query = "delete from upi_merchant_config where pgMerchantId in ('V0$E_ID$MNTR$3gv6aUTnwrN742', " \
            "'V0$E_ID$MNTR$agO6RXqbLMNUMV', 'V0$E_ID$MNTR$hnea1t9qrvjGUV') and org_code not in " + \
            automation_merchants + "; "
    result = DBProcessor.delete_value_from_db(query)
    logger.debug(f"Result for the query '{query}' is : {result} ")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                          "password": portal_password})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for setting precondition DB refresh is : {response}")


def delete_staticqr_intent_table_entry(portal_username, portal_password, config_id):
    """
    This method is to delete the static_qr data from staticqr_intent table based on config id
    """

    query = "delete from staticqr_intent where config_id ='" + str(config_id) + "';"
    result = DBProcessor.delete_value_from_db(query)
    logger.debug(f"Result for the query '{query}' is : {result} ")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                          "password": portal_password})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for DB refresh is : {response}")


def delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa):
    """
    This method is to delete the static_qr data from staticqr_intent table based on vpa
    """

    query = "delete from staticqr_intent where vpa ='" + str(vpa) + "';"
    result = DBProcessor.delete_value_from_db(query)
    logger.debug(f"Result for the query '{query}' is : {result} ")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                          "password": portal_password})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for DB refresh is : {response}")


def delete_qrcode_audit_table_entry(portal_username, portal_password, org_code):
    """
    This method is to delete all the entries from qrcode_audit table based on org code
    """

    query = "delete from qrcode_audit where org_code ='" + str(org_code) + "';"
    result = DBProcessor.delete_value_from_db(query)
    logger.debug(f"Result for the query '{query}' is : {result} ")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                          "password": portal_password})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for DB refresh is : {response}")


def delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code):
    """
    This method is to delete the static_qr data from staticqr_intent table based on org code
    """

    query = "delete from staticqr_intent where org_code ='" + str(org_code) + "';"
    result = DBProcessor.delete_value_from_db(query)
    logger.debug(f"Result for the query '{query}' is : {result} ")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                          "password": portal_password})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for DB refresh is : {response}")


def get_account_labels_and_set_default_account(org_code: str, portal_un: str, portal_pw: str) -> dict:
    """
    This method is used to do the setup for default account parameter in the org setting for the current org_code and
    return the account_labels dictionary.
    :param org_code str
    :param portal_un str
    :param portal_pw str
    :return: dict
    """
    account_labels = {}
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT AccountLabel1, AccountLabel2 from acquisitions limit 1;")
        _account_labels = cursor.fetchone()
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_un, "password": portal_pw, "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"] = {"defaultAccount": f"{_account_labels[0]}"}
        logger.debug(f"API details  : {api_details} ")
        account_labels['name1'] = _account_labels[0]
        account_labels['name2'] = _account_labels[1]
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting defaultAccount is : {response}")
        return account_labels
    except Exception as e:
        logger.debug(f"Unable to get the entity id of merchant due to error {str(e)}")


def revert_p2p_settings(portal_un, portal_pw, app_username, app_password, org_code):
    # Enable P2P, Autologin, and disable AutologinForLogout
    api_details = DBProcessor.get_api_details('org_settings_update', request_body={
        "username": portal_un,
        "password": portal_pw,
        "settingForOrgCode": org_code
    })

    api_details["RequestBody"]["settings"]["p2pEnabled"] = "true"
    api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
    api_details["RequestBody"]["settings"]["autoLoginByTokenLogOutEnabled"] = "false"
    logger.debug(f"API details  : {api_details}")
    response = APIProcessor.send_request(api_details)
    logger.debug(
        f"Response received for setting preconditions for p2p, autoLoginByTokenEnabled and autoLoginByTokenLogOutEnabled is : {response}")

    # Enable queue functionality
    query = "update p2p_setting set disable_queue=0 where org_code='" + str(org_code) + "';"
    logger.debug(f"Query to update queue as enabled in DB : {query}")
    result = DBProcessor.setValueToDB(query)
    logger.debug(f"Query result : {result}")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                          "password": portal_pw})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for DB refresh is : {response}")


def get_normal_p2p_user(portal_un, portal_pw, app_un, app_pw, org_code):
    """
    This method is used to select/ create new user which allowed to do normal txns along with P2P txns
    :param portal_un str
    :param portal_pw str
    :param app_un str
    :param org_code str
    :return: string
    """
    query_all_users = "select username from org_employee where org_code ='" + str(
        org_code) + "' and roles = 'ROLE_CLAGENT' and username!='" + str(app_un) + "';"
    result_all_users = DBProcessor.getValueFromDB(query_all_users)
    logger.info(
        f"Query to select all users under the org {org_code} with only Agent role except the current user {app_un}")
    logger.debug(f"Result of fetching all users with agent role except the current user: {result_all_users}")
    logger.debug(f"Count of users selected except the current user {app_un} : {len(result_all_users)}")
    if len(result_all_users) >= 1:
        logger.info(f"There are other active users under the org {org_code}")
        for i in range(len(result_all_users)):
            user = result_all_users['username'].values[i]
            logger.debug(f"Selected existing user is {user}")
            query_sett = "select sett.setting_value from org_employee empl LEFT JOIN setting sett on sett.entity_id =empl.id where empl.username='" + str(
                user) + "' and sett.setting_name='onlyP2PUser';"
            result_sett_val = DBProcessor.getValueFromDB(query_sett)

            logger.info(
                f"Query to get the setting_value of 'OnlyP2PUser' from setting table for the user {user} : {query_sett}")
            logger.debug(
                f"Result of setting_value of 'OnlyP2PUser' from setting table for the user {user} : {result_sett_val}")

            if len(result_sett_val) >= 1:
                logger.info(
                    f"Value of setting_value for 'OnlyP2PUser' for {user} is : {result_sett_val['setting_value'].values[0]}")
                # If the selected user is OnlyP2P allowed user
                if result_sett_val['setting_value'].values[0] == "true":
                    logger.info(f"Selected user {user} is allowed to do only P2P txns")
                    logger.info(f"Fetching next user...")
                    continue;
                else:
                    # Change password of the newly selected existing user by calling create_user API
                    logger.info(
                        f"Selected user {user} has an entry in setting table and can do normal transactions as well")
                    app_user, app_password = p2p_change_password(portal_un, portal_pw, user, org_code)
                    return app_user, app_password
                    break
            else:
                # Change password of the newly selected existing user by calling create_user API
                logger.info(
                    f"Selected user {user} can do normal transactions as well and has no entry in setting table")
                app_user, app_password = p2p_change_password(portal_un, portal_pw, user, org_code)
                return app_user, app_password
                break

        # Create new user with agent role since there are no other normal users
        logger.info(f"All active users under {org_code} are allowed to do only P2P txns. So creating new user.")
        app_user, app_password = p2p_create_user(portal_un, portal_pw, app_pw, org_code)
        return app_user, app_password

    else:
        # Create new user with agent role
        logger.info(f"No existing active users under the org {org_code}. So creating new user.")
        app_user, app_password = p2p_create_user(portal_un, portal_pw, app_pw, org_code)
        return app_user, app_password


def p2p_create_user(portal_un, portal_pw, app_pw, org_code):
    app_user = str(random.randint(1000000000, 9999999999))
    app_password = app_pw
    logger.info(f"Creating new user in agent role with username {app_user} and password {app_password}")
    name = "EzeAutoUser"
    api_details = DBProcessor.get_api_details('createUser', request_body={
        "mobileNumber": app_user,
        "name": name,
        "roles": ["ROLE_CLAGENT"],
        "userPassword": app_password,
        "userToken": app_user,
        "username": portal_un,
        "password": portal_pw
    })
    payload = api_details['RequestBody']
    endPoint = api_details['EndPoint']
    method = api_details['Method']
    headers = api_details['Header']
    url = ConfigReader.read_config("APIs", "baseUrl") + endPoint
    url = url.replace('EZETAP', org_code)
    resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
    APIProcessor.update_api_details_to_report_variables(resp)
    response_new_user_creation = json.loads(resp.text)
    logger.debug(f"response received for createUser api for {app_user} is : {response_new_user_creation}")
    if response_new_user_creation["success"]:
        logger.debug(f"Created new user {app_user} with agent role with password {app_password}")
        return app_user, app_password
    else:
        logger.error(f"User creation failed for {app_user} : {response_new_user_creation}")
        raise Exception(f"Could not create new user {app_user}")


def p2p_change_password(portal_un, portal_pw, app_user, org_code):
    app_password = "P2P" + ''.join(random.choice(string.digits) for _ in range(7))
    name = "EzeAutoUser"
    logger.info(f"Changing password of new selected user {app_user}")
    logger.info(f"New password {app_password}")
    logger.info(f"New mobile number {app_user}")
    logger.info(f"New name {name}")

    api_details = DBProcessor.get_api_details('createUser', request_body={
        "mobileNumber": app_user,
        "name": name,
        "roles": ["ROLE_CLAGENT"],
        "userPassword": app_password,
        "userToken": app_user,
        "username": portal_un,
        "password": portal_pw
    })
    payload = api_details['RequestBody']
    endPoint = api_details['EndPoint']
    method = api_details['Method']
    headers = api_details['Header']
    url = ConfigReader.read_config("APIs", "baseUrl") + endPoint
    url = url.replace('EZETAP', org_code)
    resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
    APIProcessor.update_api_details_to_report_variables(resp)
    response_change_pwd = json.loads(resp.text)
    logger.debug(
        f"response received for changing the password for {app_user} using createUser api is : {response_change_pwd}")
    if response_change_pwd["success"]:
        logger.debug(f"Changed the current password of existing user to {app_password}")
        return app_user, app_password
    else:
        logger.error(f"Change password for {app_user} using create_user API failed : {response_change_pwd}")
        raise Exception(f"Could not change password of the existing user {app_user}")

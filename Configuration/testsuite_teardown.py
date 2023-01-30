import sqlite3
import string

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


def revert_org_settings_default(org_code, portal_un, portal_pw):
    # Set session expiry as default (86400 sec)
    orgsettings_apidetails_setExpiry = DBProcessor.get_api_details('org_settings_update',
                                                                   request_body={"username": portal_un,
                                                                                 "password": portal_pw,
                                                                                 "settingForOrgCode": org_code})
    orgsettings_apidetails_setExpiry["RequestBody"]["settings"]["sessionTimeOut"] = "86400"
    logger.debug(f"API details  : {orgsettings_apidetails_setExpiry} ")
    response = APIProcessor.send_request(orgsettings_apidetails_setExpiry)
    logger.debug(f"Response received for setting sessionExpiry as default is : {response}")

    # Set autologin as default (false)
    orgsettings_apidetails_autoLoginEnable = DBProcessor.get_api_details('org_settings_update',
                                                                         request_body={"username": portal_un,
                                                                                       "password": portal_pw,
                                                                                       "settingForOrgCode": org_code})
    orgsettings_apidetails_autoLoginEnable["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "false"
    logger.debug(f"API details  : {orgsettings_apidetails_autoLoginEnable} ")
    response = APIProcessor.send_request(orgsettings_apidetails_autoLoginEnable)
    logger.debug(f"Response received for setting autoLoginByTokenEnabled as False is : {response}")


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

    query = "delete from staticqr_intent where config_id ='"+str(config_id)+"';"
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

    query = "delete from staticqr_intent where vpa ='"+str(vpa)+"';"
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

    query = "delete from staticqr_intent where org_code ='"+str(org_code)+"';"
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


def revert_p2p_settings(portal_un, portal_pw, app_un, app_pw, org_code):
    # query = "select id from org_employee where username ='" + str(app_un) + "'"
    # logger.debug(f"Query to fetch user id from the DB : {query}")
    # result = DBProcessor.getValueFromDB(query)
    # user_id = result['id'].values[0]
    # logger.debug(f"Query result, user id : {user_id}")

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

    # # Enable 'Only P2P allowed User'
    # query = "update setting set setting_value ='true' where setting_name='onlyP2PUser' and entity_id ='" + str(
    #     user_id) + "';"
    # logger.debug(f"Query to update user as 'allow only P2P' as enabled in DB : {query}")
    # result = DBProcessor.setValueToDB(query)
    # logger.debug(f"Query result : {result}")

    # Enable queue functionality
    query = "update p2p_setting set disable_queue=0 where org_code='" + str(org_code) + "';"
    logger.debug(f"Query to update queue as enabled in DB : {query}")
    result = DBProcessor.setValueToDB(query)
    logger.debug(f"Query result : {result}")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_un,
                                                                          "password": portal_pw})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for DB refresh is : {response}")



def get_normal_p2p_allowed_user(portal_un, portal_pw, app_un, app_pw, org_code):
    """
    This method is used to create an user which allowed to do normal txns and P2P txns
    :param portal_un str
    :param portal_pw str
    :param app_un str
    :param org_code str
    :return: string
    """
    import requests
    import json
    import random

    query = "select * from org_employee where org_code ='"+str(org_code)+"' and roles = 'ROLE_CLAGENT' and username!='"+str(app_un)+"';"
    result_users = DBProcessor.getValueFromDB(query)
    if len(result_users) >=1:
        app_username = result_users['username'][0]
    else:

    # Fetching users other than current user
    logger.info(f"Fetching all users from the org other than current user")
    query = "select empl.username,sett.setting_value from org_employee empl LEFT JOIN setting sett on empl.org_code = sett.org_code and sett.entity_id =empl.id and empl.username!='" + str(
        app_un) + "' and empl.roles = 'ROLE_CLAGENT' where sett.org_code='" + str(org_code) + "' and sett.setting_name='onlyP2PUser';"
    result_all_users = DBProcessor.getValueFromDB(query)
    is_user_required = True
    logger.debug(f"Other users under the org {org_code} is {str(result_all_users)}")
    logger.debug(f"Number of users selected from DB under the org_code is : {len(result_all_users)}")

    for i in range(len(result_all_users)):
        if result_all_users['setting_value'][i] == "true":
            logger.info(f"setting_value of the user selected is True")
            is_user_required = True
            logger.debug(f"user creation is required")
            continue
        else:
            is_user_required = False
            app_username = result_all_users['username'][i]
            logger.debug(f"user creation is not required")
            logger.info(f"New user selected is {app_username}")
            break
    if is_user_required:  # Create a new user via API
        app_username = str(random.randint(1000000000, 9999999999))
        logger.info(f"Creating new user in agent role with username {app_username}")
        name = "EzeAuto" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        api_details = DBProcessor.get_api_details('createUser', request_body={
            "mobileNumber": app_username,
            "name": name,
            "roles": ["ROLE_CLAGENT"],
            "userPassword": app_pw,
            "userToken": app_username,
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
        response = json.loads(resp.text)
        logger.debug(f"response received for createUser api is : {response}")
        if response["success"]:
            logger.debug(f"Created new user with agent role")
            return app_username
        else:
            logger.error(f"User creation failed : {response}")
            # add exception
    else:  # If user creation is not required
        return app_username


#
# def get_only_p2p_allowed_user():

import sqlite3

from Configuration.TestSuiteSetup import logger
from DataProvider import GlobalConstants
from Utilities import DBProcessor, APIProcessor


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

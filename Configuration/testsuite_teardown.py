from Configuration.TestSuiteSetup import logger
from Utilities import DBProcessor, APIProcessor


def revert_payment_settings_default(org_code, bank_code, portal_un, portal_pw, payment_mode=None):
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


def revert_cnp_payment_settings_default(org_code, bank_code, portal_un, portal_pw, payment_gateway=None):
    if payment_gateway == "Cybersource":
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

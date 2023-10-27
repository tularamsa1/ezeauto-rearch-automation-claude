import pytest
import random
import sys
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner, \
    merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities import card_processor

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_100_104_151():
    """
        Sub Feature Code: NonUI_Common_FDC_Card_Offline_Refund_EMVCTLS_DEBIT_VISA
        Sub Feature Description: API that performs EMVCTLS offline refund txn using DEBIT VISA card via FDC
        TC naming code description:
        100: Payment Method
        104: CARD
        151: TC0151
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")
        device_serial =  merchant_creator.get_device_serial_of_merchant(org_code=org_code,acquisition="ICICI",payment_gateway="FDC")

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = True, config_log= False,closedloop_log=False,q2_log=True)

        
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10,1000)
            card_details = card_processor.get_card_details_from_excel("EMVCTLS_DEBIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={"deviceSerial": device_serial,
                                                                    "username": app_username,
                                                                    "password": app_password,
                                                                    "amount": str(original_amount),
                                                                    "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                                    "nonce": card_details['Nonce'],
                                                                    "externalRefNumber": str(card_details['External Ref']) + str(random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                query = "select id from terminal_info where device_serial = '" + device_serial + "' and payment_gateway = 'FDC' and acquirer_code = 'ICICI';"
                result = DBProcessor.getValueFromDB(query)
                terminal_info_id = result['id'].iloc[0]
                logger.debug(f"Query result: fetching terminal_info_id of FDC PG: {terminal_info_id}")
                api_details = DBProcessor.get_api_details('Settlement', request_body={"username": portal_username,
                                                                            "password": portal_password})
                api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
                settle_response = APIProcessor.send_request(api_details)
                settle_success = settle_response['success']
                if settle_success == True:
                    api_details = DBProcessor.get_api_details('Offline_Refund',
                                                              request_body={"username": app_username,
                                                                            "password": app_password,
                                                                            "ezetapDeviceData": card_details[
                                                                                "Ezetap Device Data"],
                                                                            "originalTransactionId": txn_id,
                                                                            "amount": original_amount,
                                                                            "deviceSerial": device_serial})
                    refund_response = APIProcessor.send_request(api_details)
                    refund_success = refund_response['success']
                else:
                    logger.error("Settlement failed")

            else:
                logger.error("card Payment failed")



            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
         # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            bin_no = card_processor.get_device_data_details(card_details['Ezetap Device Data'])['CLEAR_PAN'][0:6]
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if refund_success == True:
                    expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode":"CARD",
                                         "pmt_status":"REFUNDED",
                                        "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                         "pmt_card_bin":bin_no,
                                         "pmt_card_brand":"VISA", "pmt_card_type":"DEBIT", "card_txn_type":"CTLS",
                                         "txn_type":"REFUND", "acq_code":"ICICI"}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    amount = float(refund_response['amount'])
                    txnid = refund_response['txnId']
                    orgtxnid = refund_response['origTxnId']
                    payment_mode = refund_response['paymentMode']
                    payment_status = refund_response['status']
                    payment_state = refund_response['states'][0]
                    settlement_status = refund_response['settlementStatus']
                    payment_card_bin = refund_response['paymentCardBin']
                    payment_card_brand = refund_response['paymentCardBrand']
                    payment_card_type = refund_response['paymentCardType']
                    card_txn_type = refund_response['cardTxnTypeDesc']
                    txn_type = refund_response['txnType']
                    acq_code = refund_response['acquirerCode']
                    logger.info(f"API Result: Fetch Response of refund payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                    actualAPIValues = {"success": refund_success,"txn_amt": amount, "pmt_mode":payment_mode,
                                       "pmt_status":payment_status,
                                        "pmt_state":payment_state, "settle_status":settlement_status,
                                       "pmt_card_bin":payment_card_bin,
                                         "pmt_card_brand":payment_card_brand, "pmt_card_type":payment_card_type,
                                       "card_txn_type":card_txn_type, "txn_type":txn_type, "acq_code":acq_code}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    logger.error("Offline Refund is not successfull")

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")


        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:

                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode":"CARD",
                                    "pmt_status":"REFUNDED",
                                    "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "pmt_state_1": "REFUNDED", "settle_status_1": "SETTLED",
                                    "pmt_card_bin":bin_no,
                                    "pmt_card_brand":"VISA", "pmt_card_type":"DEBIT",
                                    "txn_type":"REFUND", "acq_code":"ICICI", "pmt_gateway":"FDC",
                                    "mware_txn_amt": float(original_amount), "mware_pmt_mode": "CARD",
                                    "mware_pmt_status": "REFUNDED",
                                    "mware_pmt_state": "AUTHORIZED", "mware_settle_status": "PENDING",
                                    "mware_pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "mware_pmt_state_1": "REFUNDED", "mware_settle_status_1": "SETTLED",
                                    "mware_pmt_card_bin": bin_no,
                                    "mware_pmt_card_brand": "VISA", "mware_pmt_card_type": "DEBIT",
                                    "mware_txn_type": "REFUND", "mware_acq_code": "ICICI", "mware_pmt_gateway": "FDC",
                                    "txn_amt_req": float(original_amount), "pmt_status_req":"SUCCESS",
                                    "pmt_status_req_1":"SUCCESS"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '"+txnid+"';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]
                pmt_state = result_txn["state"].iloc[0]
                pmt_card_bin = result_txn["payment_card_bin"].iloc[0]
                pmt_card_brand = result_txn["payment_card_brand"].iloc[0]
                pmt_card_type = result_txn["payment_card_type"].iloc[0]
                txn_type = result_txn["txn_type"].iloc[0]
                acq_code = result_txn["acquirer_code"].iloc[0]
                pmt_gateway = result_txn["payment_gateway"].iloc[0]

                query_txn = "select settlement_status, status, state from txn where id = '" + orgtxnid + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                settle_status_1 = result_txn["settlement_status"].iloc[0]
                pmt_status_1 = result_txn["status"].iloc[0]
                pmt_state_1 = result_txn["state"].iloc[0]

                query_txn_mware = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where ref_txn_id = '" + txnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware,"mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_txn_amt = float(result_txn_mware["amount"].iloc[0])
                mware_pmt_mode = result_txn_mware["payment_mode"].iloc[0]
                mware_settle_status = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status = result_txn_mware["status"].iloc[0]
                mware_pmt_state = result_txn_mware["state"].iloc[0]
                mware_pmt_card_bin = result_txn_mware["payment_card_bin"].iloc[0]
                mware_pmt_card_brand = result_txn_mware["payment_card_brand"].iloc[0]
                mware_pmt_card_type = result_txn_mware["payment_card_type"].iloc[0]
                mware_txn_type = result_txn_mware["txn_type"].iloc[0]
                mware_acq_code = result_txn_mware["acquirer_code"].iloc[0]
                mware_pmt_gateway = result_txn_mware["payment_gateway"].iloc[0]

                query_txn_mware = "select settlement_status, status, state from txn where ref_txn_id = '" + orgtxnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware, "mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_settle_status_1 = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status_1 = result_txn_mware["status"].iloc[0]
                mware_pmt_state_1 = result_txn_mware["state"].iloc[0]

                query_txn_req = "select amount, status from txn_request where id = '" + txnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                txn_amt_req = float(result_txn_req["amount"].iloc[0])
                pmt_status_req = result_txn_req["status"].iloc[0]

                query_txn_req = "select status from txn_request where id = '" + orgtxnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                pmt_status_req_1 = result_txn_req["status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode":pmt_mode,
                                    "pmt_status":pmt_status,
                                    "pmt_state":pmt_state, "settle_status": settle_status,
                                    "pmt_status_1": pmt_status_1,
                                    "pmt_state_1": pmt_state_1, "settle_status_1": settle_status_1,
                                    "pmt_card_bin":pmt_card_bin,
                                    "pmt_card_brand":pmt_card_brand, "pmt_card_type":pmt_card_type,
                                    "txn_type":txn_type, "acq_code":acq_code, "pmt_gateway":pmt_gateway,
                                    "mware_txn_amt": mware_txn_amt, "mware_pmt_mode":mware_pmt_mode,
                                    "mware_pmt_status": mware_pmt_status,
                                    "mware_pmt_state": mware_pmt_state, "mware_settle_status": mware_settle_status,
                                    "mware_pmt_status_1": mware_pmt_status_1,
                                    "mware_pmt_state_1": mware_pmt_state_1, "mware_settle_status_1": mware_settle_status_1,
                                    "mware_pmt_card_bin": mware_pmt_card_bin,
                                    "mware_pmt_card_brand": mware_pmt_card_brand, "mware_pmt_card_type":mware_pmt_card_type,
                                    "mware_txn_type": mware_txn_type, "mware_acq_code": mware_acq_code,
                                    "mware_pmt_gateway": mware_pmt_gateway,"txn_amt_req":txn_amt_req,
                                    "pmt_status_req":pmt_status_req,"pmt_status_req_1":pmt_status_req_1}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
                logger.info(f"Completed DB validation for the test case : {testcase_id}")

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    finally:
        Configuration.executeFinallyBlock(testcase_id)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_100_104_152():
    """
        Sub Feature Code: NonUI_Common_FDC_Card_Offline_Refund_EMVCTLS_DEBIT_MASTER
        Sub Feature Description: API that performs EMVCTLS Offline refund txn using DEBIT MASTER card via FDC
        TC naming code description:
        100: Payment Method
        104: CARD
        152: TC152
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")
        device_serial =  merchant_creator.get_device_serial_of_merchant(org_code=org_code,acquisition="ICICI",payment_gateway="FDC")

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = True, config_log= False,closedloop_log=False,q2_log=True)

        
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10,1000)
            card_details = card_processor.get_card_details_from_excel("EMVCTLS_DEBIT_MASTER")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={"deviceSerial": device_serial,
                                                                    "username": app_username,
                                                                    "password": app_password,
                                                                    "amount": str(original_amount),
                                                                    "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                                    "nonce": card_details['Nonce'],
                                                                    "externalRefNumber": str(card_details['External Ref']) + str(random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                query = "select id from terminal_info where device_serial = '" + device_serial + "' and payment_gateway = 'FDC' and acquirer_code = 'ICICI';"
                result = DBProcessor.getValueFromDB(query)
                terminal_info_id = result['id'].iloc[0]
                logger.debug(f"Query result: fetching terminal_info_id of FDC PG: {terminal_info_id}")
                api_details = DBProcessor.get_api_details('Settlement', request_body={"username": portal_username,
                                                                            "password": portal_password})
                api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
                settle_response = APIProcessor.send_request(api_details)
                settle_success = settle_response['success']
                if settle_success == True:
                    api_details = DBProcessor.get_api_details('Offline_Refund',
                                                              request_body={"username": app_username,
                                                                            "password": app_password,
                                                                            "ezetapDeviceData": card_details[
                                                                                "Ezetap Device Data"],
                                                                            "originalTransactionId": txn_id,
                                                                            "amount": original_amount,
                                                                            "deviceSerial": device_serial})
                    refund_response = APIProcessor.send_request(api_details)
                    refund_success = refund_response['success']
                else:
                    logger.error("Settlement failed")

            else:
                logger.error("card Payment failed")



            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
         # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            bin_no = card_processor.get_device_data_details(card_details['Ezetap Device Data'])['CLEAR_PAN'][0:6]
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if refund_success == True:
                    expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode":"CARD",
                                         "pmt_status":"REFUNDED",
                                        "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                         "pmt_card_bin":bin_no,
                                         "pmt_card_brand":"MASTER_CARD", "pmt_card_type":"DEBIT", "card_txn_type":"CTLS",
                                         "txn_type":"REFUND", "acq_code":"ICICI"}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    amount = float(refund_response['amount'])
                    txnid = refund_response['txnId']
                    orgtxnid = refund_response['origTxnId']
                    payment_mode = refund_response['paymentMode']
                    payment_status = refund_response['status']
                    payment_state = refund_response['states'][0]
                    settlement_status = refund_response['settlementStatus']
                    payment_card_bin = refund_response['paymentCardBin']
                    payment_card_brand = refund_response['paymentCardBrand']
                    payment_card_type = refund_response['paymentCardType']
                    card_txn_type = refund_response['cardTxnTypeDesc']
                    txn_type = refund_response['txnType']
                    acq_code = refund_response['acquirerCode']
                    logger.info(f"API Result: Fetch Response of refund payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                    actualAPIValues = {"success": refund_success,"txn_amt": amount, "pmt_mode":payment_mode,
                                       "pmt_status":payment_status,
                                        "pmt_state":payment_state, "settle_status":settlement_status,
                                       "pmt_card_bin":payment_card_bin,
                                         "pmt_card_brand":payment_card_brand, "pmt_card_type":payment_card_type,
                                       "card_txn_type":card_txn_type, "txn_type":txn_type, "acq_code":acq_code}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    logger.error("Offline Refund is not successfull")

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")


        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:

                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode":"CARD",
                                    "pmt_status":"REFUNDED",
                                    "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "pmt_state_1": "REFUNDED", "settle_status_1": "SETTLED",
                                    "pmt_card_bin":bin_no,
                                    "pmt_card_brand":"MASTER_CARD", "pmt_card_type":"DEBIT",
                                    "txn_type":"REFUND", "acq_code":"ICICI", "pmt_gateway":"FDC",
                                    "mware_txn_amt": float(original_amount), "mware_pmt_mode": "CARD",
                                    "mware_pmt_status": "REFUNDED",
                                    "mware_pmt_state": "AUTHORIZED", "mware_settle_status": "PENDING",
                                    "mware_pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "mware_pmt_state_1": "REFUNDED", "mware_settle_status_1": "SETTLED",
                                    "mware_pmt_card_bin": bin_no,
                                    "mware_pmt_card_brand": "MASTER_CARD", "mware_pmt_card_type": "DEBIT",
                                    "mware_txn_type": "REFUND", "mware_acq_code": "ICICI", "mware_pmt_gateway": "FDC",
                                    "txn_amt_req": float(original_amount), "pmt_status_req":"SUCCESS",
                                    "pmt_status_req_1":"SUCCESS"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '"+txnid+"';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]
                pmt_state = result_txn["state"].iloc[0]
                pmt_card_bin = result_txn["payment_card_bin"].iloc[0]
                pmt_card_brand = result_txn["payment_card_brand"].iloc[0]
                pmt_card_type = result_txn["payment_card_type"].iloc[0]
                txn_type = result_txn["txn_type"].iloc[0]
                acq_code = result_txn["acquirer_code"].iloc[0]
                pmt_gateway = result_txn["payment_gateway"].iloc[0]

                query_txn = "select settlement_status, status, state from txn where id = '" + orgtxnid + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                settle_status_1 = result_txn["settlement_status"].iloc[0]
                pmt_status_1 = result_txn["status"].iloc[0]
                pmt_state_1 = result_txn["state"].iloc[0]

                query_txn_mware = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where ref_txn_id = '" + txnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware,"mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_txn_amt = float(result_txn_mware["amount"].iloc[0])
                mware_pmt_mode = result_txn_mware["payment_mode"].iloc[0]
                mware_settle_status = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status = result_txn_mware["status"].iloc[0]
                mware_pmt_state = result_txn_mware["state"].iloc[0]
                mware_pmt_card_bin = result_txn_mware["payment_card_bin"].iloc[0]
                mware_pmt_card_brand = result_txn_mware["payment_card_brand"].iloc[0]
                mware_pmt_card_type = result_txn_mware["payment_card_type"].iloc[0]
                mware_txn_type = result_txn_mware["txn_type"].iloc[0]
                mware_acq_code = result_txn_mware["acquirer_code"].iloc[0]
                mware_pmt_gateway = result_txn_mware["payment_gateway"].iloc[0]

                query_txn_mware = "select settlement_status, status, state from txn where ref_txn_id = '" + orgtxnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware, "mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_settle_status_1 = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status_1 = result_txn_mware["status"].iloc[0]
                mware_pmt_state_1 = result_txn_mware["state"].iloc[0]

                query_txn_req = "select amount, status from txn_request where id = '" + txnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                txn_amt_req = float(result_txn_req["amount"].iloc[0])
                pmt_status_req = result_txn_req["status"].iloc[0]

                query_txn_req = "select status from txn_request where id = '" + orgtxnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                pmt_status_req_1 = result_txn_req["status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode":pmt_mode,
                                    "pmt_status":pmt_status,
                                    "pmt_state":pmt_state, "settle_status": settle_status,
                                    "pmt_status_1": pmt_status_1,
                                    "pmt_state_1": pmt_state_1, "settle_status_1": settle_status_1,
                                    "pmt_card_bin":pmt_card_bin,
                                    "pmt_card_brand":pmt_card_brand, "pmt_card_type":pmt_card_type,
                                    "txn_type":txn_type, "acq_code":acq_code, "pmt_gateway":pmt_gateway,
                                    "mware_txn_amt": mware_txn_amt, "mware_pmt_mode":mware_pmt_mode,
                                    "mware_pmt_status": mware_pmt_status,
                                    "mware_pmt_state": mware_pmt_state, "mware_settle_status": mware_settle_status,
                                    "mware_pmt_status_1": mware_pmt_status_1,
                                    "mware_pmt_state_1": mware_pmt_state_1, "mware_settle_status_1": mware_settle_status_1,
                                    "mware_pmt_card_bin": mware_pmt_card_bin,
                                    "mware_pmt_card_brand": mware_pmt_card_brand, "mware_pmt_card_type":mware_pmt_card_type,
                                    "mware_txn_type": mware_txn_type, "mware_acq_code": mware_acq_code,
                                    "mware_pmt_gateway": mware_pmt_gateway,"txn_amt_req":txn_amt_req,
                                    "pmt_status_req":pmt_status_req,"pmt_status_req_1":pmt_status_req_1}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
                logger.info(f"Completed DB validation for the test case : {testcase_id}")

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    finally:
        Configuration.executeFinallyBlock(testcase_id)





@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_100_104_153():
    """
        Sub Feature Code: NonUI_Common_FDC_Card_Offline_Refund_EMVCTLS_DEBIT_RUPAY
        Sub Feature Description: API that performs EMVCTLS Offline refund txn using DEBIT RUPAY card via FDC
        TC naming code description:
        100: Payment Method
        104: CARD
        153: TC153
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")
        device_serial =  merchant_creator.get_device_serial_of_merchant(org_code=org_code,acquisition="ICICI",payment_gateway="FDC")

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = True, config_log= False,closedloop_log=False,q2_log=True)

        
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10,1000)
            card_details = card_processor.get_card_details_from_excel("EMVCTLS_DEBIT_RUPAY")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={"deviceSerial": device_serial,
                                                                    "username": app_username,
                                                                    "password": app_password,
                                                                    "amount": str(original_amount),
                                                                    "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                                    "nonce": card_details['Nonce'],
                                                                    "externalRefNumber": str(card_details['External Ref']) + str(random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                query = "select id from terminal_info where device_serial = '" + device_serial + "' and payment_gateway = 'FDC' and acquirer_code = 'ICICI';"
                result = DBProcessor.getValueFromDB(query)
                terminal_info_id = result['id'].iloc[0]
                logger.debug(f"Query result: fetching terminal_info_id of FDC PG: {terminal_info_id}")
                api_details = DBProcessor.get_api_details('Settlement', request_body={"username": portal_username,
                                                                            "password": portal_password})
                api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
                settle_response = APIProcessor.send_request(api_details)
                settle_success = settle_response['success']
                if settle_success == True:
                    api_details = DBProcessor.get_api_details('Offline_Refund',
                                                              request_body={"username": app_username,
                                                                            "password": app_password,
                                                                            "ezetapDeviceData": card_details[
                                                                                "Ezetap Device Data"],
                                                                            "originalTransactionId": txn_id,
                                                                            "amount": original_amount,
                                                                            "deviceSerial": device_serial})
                    refund_response = APIProcessor.send_request(api_details)
                    refund_success = refund_response['success']
                else:
                    logger.error("Settlement failed")

            else:
                logger.error("card Payment failed")



            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
         # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            bin_no = card_processor.get_device_data_details(card_details['Ezetap Device Data'])['CLEAR_PAN'][0:6]
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if refund_success == True:
                    expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode":"CARD",
                                         "pmt_status":"REFUNDED",
                                        "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                         "pmt_card_bin":bin_no,
                                         "pmt_card_brand":"RUPAY", "pmt_card_type":"DEBIT", "card_txn_type":"CTLS",
                                         "txn_type":"REFUND", "acq_code":"ICICI"}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    amount = float(refund_response['amount'])
                    txnid = refund_response['txnId']
                    orgtxnid = refund_response['origTxnId']
                    payment_mode = refund_response['paymentMode']
                    payment_status = refund_response['status']
                    payment_state = refund_response['states'][0]
                    settlement_status = refund_response['settlementStatus']
                    payment_card_bin = refund_response['paymentCardBin']
                    payment_card_brand = refund_response['paymentCardBrand']
                    payment_card_type = refund_response['paymentCardType']
                    card_txn_type = refund_response['cardTxnTypeDesc']
                    txn_type = refund_response['txnType']
                    acq_code = refund_response['acquirerCode']
                    logger.info(f"API Result: Fetch Response of refund payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                    actualAPIValues = {"success": refund_success,"txn_amt": amount, "pmt_mode":payment_mode,
                                       "pmt_status":payment_status,
                                        "pmt_state":payment_state, "settle_status":settlement_status,
                                       "pmt_card_bin":payment_card_bin,
                                         "pmt_card_brand":payment_card_brand, "pmt_card_type":payment_card_type,
                                       "card_txn_type":card_txn_type, "txn_type":txn_type, "acq_code":acq_code}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    logger.error("Offline Refund is not successfull")

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")


        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:

                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode":"CARD",
                                    "pmt_status":"REFUNDED",
                                    "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "pmt_state_1": "REFUNDED", "settle_status_1": "SETTLED",
                                    "pmt_card_bin":bin_no,
                                    "pmt_card_brand":"RUPAY", "pmt_card_type":"DEBIT",
                                    "txn_type":"REFUND", "acq_code":"ICICI", "pmt_gateway":"FDC",
                                    "mware_txn_amt": float(original_amount), "mware_pmt_mode": "CARD",
                                    "mware_pmt_status": "REFUNDED",
                                    "mware_pmt_state": "AUTHORIZED", "mware_settle_status": "PENDING",
                                    "mware_pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "mware_pmt_state_1": "REFUNDED", "mware_settle_status_1": "SETTLED",
                                    "mware_pmt_card_bin": bin_no,
                                    "mware_pmt_card_brand": "RUPAY", "mware_pmt_card_type": "DEBIT",
                                    "mware_txn_type": "REFUND", "mware_acq_code": "ICICI", "mware_pmt_gateway": "FDC",
                                    "txn_amt_req": float(original_amount), "pmt_status_req":"SUCCESS",
                                    "pmt_status_req_1":"SUCCESS"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '"+txnid+"';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]
                pmt_state = result_txn["state"].iloc[0]
                pmt_card_bin = result_txn["payment_card_bin"].iloc[0]
                pmt_card_brand = result_txn["payment_card_brand"].iloc[0]
                pmt_card_type = result_txn["payment_card_type"].iloc[0]
                txn_type = result_txn["txn_type"].iloc[0]
                acq_code = result_txn["acquirer_code"].iloc[0]
                pmt_gateway = result_txn["payment_gateway"].iloc[0]

                query_txn = "select settlement_status, status, state from txn where id = '" + orgtxnid + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                settle_status_1 = result_txn["settlement_status"].iloc[0]
                pmt_status_1 = result_txn["status"].iloc[0]
                pmt_state_1 = result_txn["state"].iloc[0]

                query_txn_mware = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where ref_txn_id = '" + txnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware,"mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_txn_amt = float(result_txn_mware["amount"].iloc[0])
                mware_pmt_mode = result_txn_mware["payment_mode"].iloc[0]
                mware_settle_status = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status = result_txn_mware["status"].iloc[0]
                mware_pmt_state = result_txn_mware["state"].iloc[0]
                mware_pmt_card_bin = result_txn_mware["payment_card_bin"].iloc[0]
                mware_pmt_card_brand = result_txn_mware["payment_card_brand"].iloc[0]
                mware_pmt_card_type = result_txn_mware["payment_card_type"].iloc[0]
                mware_txn_type = result_txn_mware["txn_type"].iloc[0]
                mware_acq_code = result_txn_mware["acquirer_code"].iloc[0]
                mware_pmt_gateway = result_txn_mware["payment_gateway"].iloc[0]

                query_txn_mware = "select settlement_status, status, state from txn where ref_txn_id = '" + orgtxnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware, "mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_settle_status_1 = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status_1 = result_txn_mware["status"].iloc[0]
                mware_pmt_state_1 = result_txn_mware["state"].iloc[0]

                query_txn_req = "select amount, status from txn_request where id = '" + txnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                txn_amt_req = float(result_txn_req["amount"].iloc[0])
                pmt_status_req = result_txn_req["status"].iloc[0]

                query_txn_req = "select status from txn_request where id = '" + orgtxnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                pmt_status_req_1 = result_txn_req["status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode":pmt_mode,
                                    "pmt_status":pmt_status,
                                    "pmt_state":pmt_state, "settle_status": settle_status,
                                    "pmt_status_1": pmt_status_1,
                                    "pmt_state_1": pmt_state_1, "settle_status_1": settle_status_1,
                                    "pmt_card_bin":pmt_card_bin,
                                    "pmt_card_brand":pmt_card_brand, "pmt_card_type":pmt_card_type,
                                    "txn_type":txn_type, "acq_code":acq_code, "pmt_gateway":pmt_gateway,
                                    "mware_txn_amt": mware_txn_amt, "mware_pmt_mode":mware_pmt_mode,
                                    "mware_pmt_status": mware_pmt_status,
                                    "mware_pmt_state": mware_pmt_state, "mware_settle_status": mware_settle_status,
                                    "mware_pmt_status_1": mware_pmt_status_1,
                                    "mware_pmt_state_1": mware_pmt_state_1, "mware_settle_status_1": mware_settle_status_1,
                                    "mware_pmt_card_bin": mware_pmt_card_bin,
                                    "mware_pmt_card_brand": mware_pmt_card_brand, "mware_pmt_card_type":mware_pmt_card_type,
                                    "mware_txn_type": mware_txn_type, "mware_acq_code": mware_acq_code,
                                    "mware_pmt_gateway": mware_pmt_gateway,"txn_amt_req":txn_amt_req,
                                    "pmt_status_req":pmt_status_req,"pmt_status_req_1":pmt_status_req_1}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
                logger.info(f"Completed DB validation for the test case : {testcase_id}")

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    finally:
        Configuration.executeFinallyBlock(testcase_id)




@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_100_104_154():
    """
        Sub Feature Code: NonUI_Common_FDC_Card_Offline_Refund_EMVCTLS_CREDIT_VISA
        Sub Feature Description: API that performs EMVCTLS Offline refund txn using CREDIT VISA card via FDC
        TC naming code description:
        100: Payment Method
        104: CARD
        154: TC0154
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")
        device_serial =  merchant_creator.get_device_serial_of_merchant(org_code=org_code,acquisition="ICICI",payment_gateway="FDC")

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = True, config_log= False,closedloop_log=False,q2_log=True)

        
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10,1000)
            card_details = card_processor.get_card_details_from_excel("EMVCTLS_CREDIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={"deviceSerial": device_serial,
                                                                    "username": app_username,
                                                                    "password": app_password,
                                                                    "amount": str(original_amount),
                                                                    "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                                    "nonce": card_details['Nonce'],
                                                                    "externalRefNumber": str(card_details['External Ref']) + str(random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                query = "select id from terminal_info where device_serial = '" + device_serial + "' and payment_gateway = 'FDC' and acquirer_code = 'ICICI';"
                result = DBProcessor.getValueFromDB(query)
                terminal_info_id = result['id'].iloc[0]
                logger.debug(f"Query result: fetching terminal_info_id of FDC PG: {terminal_info_id}")
                api_details = DBProcessor.get_api_details('Settlement', request_body={"username": portal_username,
                                                                            "password": portal_password})
                api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
                settle_response = APIProcessor.send_request(api_details)
                settle_success = settle_response['success']
                if settle_success == True:
                    api_details = DBProcessor.get_api_details('Offline_Refund',
                                                              request_body={"username": app_username,
                                                                            "password": app_password,
                                                                            "ezetapDeviceData": card_details[
                                                                                "Ezetap Device Data"],
                                                                            "originalTransactionId": txn_id,
                                                                            "amount": original_amount,
                                                                            "deviceSerial": device_serial})
                    refund_response = APIProcessor.send_request(api_details)
                    refund_success = refund_response['success']
                else:
                    logger.error("Settlement failed")

            else:
                logger.error("card Payment failed")



            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
         # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            bin_no = card_processor.get_device_data_details(card_details['Ezetap Device Data'])['CLEAR_PAN'][0:6]
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if refund_success == True:
                    expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode":"CARD",
                                         "pmt_status":"REFUNDED",
                                        "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                         "pmt_card_bin":bin_no,
                                         "pmt_card_brand":"VISA", "pmt_card_type":"CREDIT", "card_txn_type":"CTLS",
                                         "txn_type":"REFUND", "acq_code":"ICICI"}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    amount = float(refund_response['amount'])
                    txnid = refund_response['txnId']
                    orgtxnid = refund_response['origTxnId']
                    payment_mode = refund_response['paymentMode']
                    payment_status = refund_response['status']
                    payment_state = refund_response['states'][0]
                    settlement_status = refund_response['settlementStatus']
                    payment_card_bin = refund_response['paymentCardBin']
                    payment_card_brand = refund_response['paymentCardBrand']
                    payment_card_type = refund_response['paymentCardType']
                    card_txn_type = refund_response['cardTxnTypeDesc']
                    txn_type = refund_response['txnType']
                    acq_code = refund_response['acquirerCode']
                    logger.info(f"API Result: Fetch Response of refund payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                    actualAPIValues = {"success": refund_success,"txn_amt": amount, "pmt_mode":payment_mode,
                                       "pmt_status":payment_status,
                                        "pmt_state":payment_state, "settle_status":settlement_status,
                                       "pmt_card_bin":payment_card_bin,
                                         "pmt_card_brand":payment_card_brand, "pmt_card_type":payment_card_type,
                                       "card_txn_type":card_txn_type, "txn_type":txn_type, "acq_code":acq_code}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    logger.error("Offline Refund is not successfull")

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")


        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:

                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode":"CARD",
                                    "pmt_status":"REFUNDED",
                                    "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "pmt_state_1": "REFUNDED", "settle_status_1": "SETTLED",
                                    "pmt_card_bin":bin_no,
                                    "pmt_card_brand":"VISA", "pmt_card_type":"CREDIT",
                                    "txn_type":"REFUND", "acq_code":"ICICI", "pmt_gateway":"FDC",
                                    "mware_txn_amt": float(original_amount), "mware_pmt_mode": "CARD",
                                    "mware_pmt_status": "REFUNDED",
                                    "mware_pmt_state": "AUTHORIZED", "mware_settle_status": "PENDING",
                                    "mware_pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "mware_pmt_state_1": "REFUNDED", "mware_settle_status_1": "SETTLED",
                                    "mware_pmt_card_bin": bin_no,
                                    "mware_pmt_card_brand": "VISA", "mware_pmt_card_type": "CREDIT",
                                    "mware_txn_type": "REFUND", "mware_acq_code": "ICICI", "mware_pmt_gateway": "FDC",
                                    "txn_amt_req": float(original_amount), "pmt_status_req":"SUCCESS",
                                    "pmt_status_req_1":"SUCCESS"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '"+txnid+"';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]
                pmt_state = result_txn["state"].iloc[0]
                pmt_card_bin = result_txn["payment_card_bin"].iloc[0]
                pmt_card_brand = result_txn["payment_card_brand"].iloc[0]
                pmt_card_type = result_txn["payment_card_type"].iloc[0]
                txn_type = result_txn["txn_type"].iloc[0]
                acq_code = result_txn["acquirer_code"].iloc[0]
                pmt_gateway = result_txn["payment_gateway"].iloc[0]

                query_txn = "select settlement_status, status, state from txn where id = '" + orgtxnid + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                settle_status_1 = result_txn["settlement_status"].iloc[0]
                pmt_status_1 = result_txn["status"].iloc[0]
                pmt_state_1 = result_txn["state"].iloc[0]

                query_txn_mware = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where ref_txn_id = '" + txnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware,"mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_txn_amt = float(result_txn_mware["amount"].iloc[0])
                mware_pmt_mode = result_txn_mware["payment_mode"].iloc[0]
                mware_settle_status = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status = result_txn_mware["status"].iloc[0]
                mware_pmt_state = result_txn_mware["state"].iloc[0]
                mware_pmt_card_bin = result_txn_mware["payment_card_bin"].iloc[0]
                mware_pmt_card_brand = result_txn_mware["payment_card_brand"].iloc[0]
                mware_pmt_card_type = result_txn_mware["payment_card_type"].iloc[0]
                mware_txn_type = result_txn_mware["txn_type"].iloc[0]
                mware_acq_code = result_txn_mware["acquirer_code"].iloc[0]
                mware_pmt_gateway = result_txn_mware["payment_gateway"].iloc[0]

                query_txn_mware = "select settlement_status, status, state from txn where ref_txn_id = '" + orgtxnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware, "mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_settle_status_1 = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status_1 = result_txn_mware["status"].iloc[0]
                mware_pmt_state_1 = result_txn_mware["state"].iloc[0]

                query_txn_req = "select amount, status from txn_request where id = '" + txnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                txn_amt_req = float(result_txn_req["amount"].iloc[0])
                pmt_status_req = result_txn_req["status"].iloc[0]

                query_txn_req = "select status from txn_request where id = '" + orgtxnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                pmt_status_req_1 = result_txn_req["status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode":pmt_mode,
                                    "pmt_status":pmt_status,
                                    "pmt_state":pmt_state, "settle_status": settle_status,
                                    "pmt_status_1": pmt_status_1,
                                    "pmt_state_1": pmt_state_1, "settle_status_1": settle_status_1,
                                    "pmt_card_bin":pmt_card_bin,
                                    "pmt_card_brand":pmt_card_brand, "pmt_card_type":pmt_card_type,
                                    "txn_type":txn_type, "acq_code":acq_code, "pmt_gateway":pmt_gateway,
                                    "mware_txn_amt": mware_txn_amt, "mware_pmt_mode":mware_pmt_mode,
                                    "mware_pmt_status": mware_pmt_status,
                                    "mware_pmt_state": mware_pmt_state, "mware_settle_status": mware_settle_status,
                                    "mware_pmt_status_1": mware_pmt_status_1,
                                    "mware_pmt_state_1": mware_pmt_state_1, "mware_settle_status_1": mware_settle_status_1,
                                    "mware_pmt_card_bin": mware_pmt_card_bin,
                                    "mware_pmt_card_brand": mware_pmt_card_brand, "mware_pmt_card_type":mware_pmt_card_type,
                                    "mware_txn_type": mware_txn_type, "mware_acq_code": mware_acq_code,
                                    "mware_pmt_gateway": mware_pmt_gateway,"txn_amt_req":txn_amt_req,
                                    "pmt_status_req":pmt_status_req,"pmt_status_req_1":pmt_status_req_1}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
                logger.info(f"Completed DB validation for the test case : {testcase_id}")

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    finally:
        Configuration.executeFinallyBlock(testcase_id)




@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_100_104_155():
    """
        Sub Feature Code: NonUI_Common_FDC_Card_Offline_Refund_EMVCTLS_CREDIT_MASTER
        Sub Feature Description: API that performs EMVCTLS Offline refund txn using CREDIT MASTER card via FDC
        TC naming code description:
        100: Payment Method
        104: CARD
        155: TC155
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")
        device_serial =  merchant_creator.get_device_serial_of_merchant(org_code=org_code,acquisition="ICICI",payment_gateway="FDC")

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = True, config_log= False,closedloop_log=False,q2_log=True)

        
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10,1000)
            card_details = card_processor.get_card_details_from_excel("EMVCTLS_CREDIT_MASTER")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={"deviceSerial": device_serial,
                                                                    "username": app_username,
                                                                    "password": app_password,
                                                                    "amount": str(original_amount),
                                                                    "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                                    "nonce": card_details['Nonce'],
                                                                    "externalRefNumber": str(card_details['External Ref']) + str(random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                query = "select id from terminal_info where device_serial = '" + device_serial + "' and payment_gateway = 'FDC' and acquirer_code = 'ICICI';"
                result = DBProcessor.getValueFromDB(query)
                terminal_info_id = result['id'].iloc[0]
                logger.debug(f"Query result: fetching terminal_info_id of FDC PG: {terminal_info_id}")
                api_details = DBProcessor.get_api_details('Settlement', request_body={"username": portal_username,
                                                                            "password": portal_password})
                api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
                settle_response = APIProcessor.send_request(api_details)
                settle_success = settle_response['success']
                if settle_success == True:
                    api_details = DBProcessor.get_api_details('Offline_Refund',
                                                              request_body={"username": app_username,
                                                                            "password": app_password,
                                                                            "ezetapDeviceData": card_details[
                                                                                "Ezetap Device Data"],
                                                                            "originalTransactionId": txn_id,
                                                                            "amount": original_amount,
                                                                            "deviceSerial": device_serial})
                    refund_response = APIProcessor.send_request(api_details)
                    refund_success = refund_response['success']
                else:
                    logger.error("Settlement failed")

            else:
                logger.error("card Payment failed")



            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
         # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            bin_no = card_processor.get_device_data_details(card_details['Ezetap Device Data'])['CLEAR_PAN'][0:6]
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if refund_success == True:
                    expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode":"CARD",
                                         "pmt_status":"REFUNDED",
                                        "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                         "pmt_card_bin":bin_no,
                                         "pmt_card_brand":"MASTER_CARD", "pmt_card_type":"CREDIT", "card_txn_type":"CTLS",
                                         "txn_type":"REFUND", "acq_code":"ICICI"}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    amount = float(refund_response['amount'])
                    txnid = refund_response['txnId']
                    orgtxnid = refund_response['origTxnId']
                    payment_mode = refund_response['paymentMode']
                    payment_status = refund_response['status']
                    payment_state = refund_response['states'][0]
                    settlement_status = refund_response['settlementStatus']
                    payment_card_bin = refund_response['paymentCardBin']
                    payment_card_brand = refund_response['paymentCardBrand']
                    payment_card_type = refund_response['paymentCardType']
                    card_txn_type = refund_response['cardTxnTypeDesc']
                    txn_type = refund_response['txnType']
                    acq_code = refund_response['acquirerCode']
                    logger.info(f"API Result: Fetch Response of refund payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                    actualAPIValues = {"success": refund_success,"txn_amt": amount, "pmt_mode":payment_mode,
                                       "pmt_status":payment_status,
                                        "pmt_state":payment_state, "settle_status":settlement_status,
                                       "pmt_card_bin":payment_card_bin,
                                         "pmt_card_brand":payment_card_brand, "pmt_card_type":payment_card_type,
                                       "card_txn_type":card_txn_type, "txn_type":txn_type, "acq_code":acq_code}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    logger.error("Offline Refund is not successfull")

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")


        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:

                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode":"CARD",
                                    "pmt_status":"REFUNDED",
                                    "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "pmt_state_1": "REFUNDED", "settle_status_1": "SETTLED",
                                    "pmt_card_bin":bin_no,
                                    "pmt_card_brand":"MASTER_CARD", "pmt_card_type":"CREDIT",
                                    "txn_type":"REFUND", "acq_code":"ICICI", "pmt_gateway":"FDC",
                                    "mware_txn_amt": float(original_amount), "mware_pmt_mode": "CARD",
                                    "mware_pmt_status": "REFUNDED",
                                    "mware_pmt_state": "AUTHORIZED", "mware_settle_status": "PENDING",
                                    "mware_pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "mware_pmt_state_1": "REFUNDED", "mware_settle_status_1": "SETTLED",
                                    "mware_pmt_card_bin": bin_no,
                                    "mware_pmt_card_brand": "MASTER_CARD", "mware_pmt_card_type": "CREDIT",
                                    "mware_txn_type": "REFUND", "mware_acq_code": "ICICI", "mware_pmt_gateway": "FDC",
                                    "txn_amt_req": float(original_amount), "pmt_status_req":"SUCCESS",
                                    "pmt_status_req_1":"SUCCESS"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '"+txnid+"';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]
                pmt_state = result_txn["state"].iloc[0]
                pmt_card_bin = result_txn["payment_card_bin"].iloc[0]
                pmt_card_brand = result_txn["payment_card_brand"].iloc[0]
                pmt_card_type = result_txn["payment_card_type"].iloc[0]
                txn_type = result_txn["txn_type"].iloc[0]
                acq_code = result_txn["acquirer_code"].iloc[0]
                pmt_gateway = result_txn["payment_gateway"].iloc[0]

                query_txn = "select settlement_status, status, state from txn where id = '" + orgtxnid + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                settle_status_1 = result_txn["settlement_status"].iloc[0]
                pmt_status_1 = result_txn["status"].iloc[0]
                pmt_state_1 = result_txn["state"].iloc[0]

                query_txn_mware = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where ref_txn_id = '" + txnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware,"mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_txn_amt = float(result_txn_mware["amount"].iloc[0])
                mware_pmt_mode = result_txn_mware["payment_mode"].iloc[0]
                mware_settle_status = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status = result_txn_mware["status"].iloc[0]
                mware_pmt_state = result_txn_mware["state"].iloc[0]
                mware_pmt_card_bin = result_txn_mware["payment_card_bin"].iloc[0]
                mware_pmt_card_brand = result_txn_mware["payment_card_brand"].iloc[0]
                mware_pmt_card_type = result_txn_mware["payment_card_type"].iloc[0]
                mware_txn_type = result_txn_mware["txn_type"].iloc[0]
                mware_acq_code = result_txn_mware["acquirer_code"].iloc[0]
                mware_pmt_gateway = result_txn_mware["payment_gateway"].iloc[0]

                query_txn_mware = "select settlement_status, status, state from txn where ref_txn_id = '" + orgtxnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware, "mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_settle_status_1 = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status_1 = result_txn_mware["status"].iloc[0]
                mware_pmt_state_1 = result_txn_mware["state"].iloc[0]

                query_txn_req = "select amount, status from txn_request where id = '" + txnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                txn_amt_req = float(result_txn_req["amount"].iloc[0])
                pmt_status_req = result_txn_req["status"].iloc[0]

                query_txn_req = "select status from txn_request where id = '" + orgtxnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                pmt_status_req_1 = result_txn_req["status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode":pmt_mode,
                                    "pmt_status":pmt_status,
                                    "pmt_state":pmt_state, "settle_status": settle_status,
                                    "pmt_status_1": pmt_status_1,
                                    "pmt_state_1": pmt_state_1, "settle_status_1": settle_status_1,
                                    "pmt_card_bin":pmt_card_bin,
                                    "pmt_card_brand":pmt_card_brand, "pmt_card_type":pmt_card_type,
                                    "txn_type":txn_type, "acq_code":acq_code, "pmt_gateway":pmt_gateway,
                                    "mware_txn_amt": mware_txn_amt, "mware_pmt_mode":mware_pmt_mode,
                                    "mware_pmt_status": mware_pmt_status,
                                    "mware_pmt_state": mware_pmt_state, "mware_settle_status": mware_settle_status,
                                    "mware_pmt_status_1": mware_pmt_status_1,
                                    "mware_pmt_state_1": mware_pmt_state_1, "mware_settle_status_1": mware_settle_status_1,
                                    "mware_pmt_card_bin": mware_pmt_card_bin,
                                    "mware_pmt_card_brand": mware_pmt_card_brand, "mware_pmt_card_type":mware_pmt_card_type,
                                    "mware_txn_type": mware_txn_type, "mware_acq_code": mware_acq_code,
                                    "mware_pmt_gateway": mware_pmt_gateway,"txn_amt_req":txn_amt_req,
                                    "pmt_status_req":pmt_status_req,"pmt_status_req_1":pmt_status_req_1}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
                logger.info(f"Completed DB validation for the test case : {testcase_id}")

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    finally:
        Configuration.executeFinallyBlock(testcase_id)





@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_100_104_156():
    """
        Sub Feature Code: NonUI_Common_FDC_Card_Offline_Refund_EMVCTLS_CREDIT_RUPAY
        Sub Feature Description: API that performs EMVCTLS Offline refund txn using CREDIT RUPAY card via FDC
        TC naming code description:
        100: Payment Method
        104: CARD
        156: TC156
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")
        device_serial =  merchant_creator.get_device_serial_of_merchant(org_code=org_code,acquisition="ICICI",payment_gateway="FDC")

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = True, config_log= False,closedloop_log=False,q2_log=True)

        
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10,1000)
            card_details = card_processor.get_card_details_from_excel("EMVCTLS_CREDIT_RUPAY")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={"deviceSerial": device_serial,
                                                                    "username": app_username,
                                                                    "password": app_password,
                                                                    "amount": str(original_amount),
                                                                    "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                                    "nonce": card_details['Nonce'],
                                                                    "externalRefNumber": str(card_details['External Ref']) + str(random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                query = "select id from terminal_info where device_serial = '" + device_serial + "' and payment_gateway = 'FDC' and acquirer_code = 'ICICI';"
                result = DBProcessor.getValueFromDB(query)
                terminal_info_id = result['id'].iloc[0]
                logger.debug(f"Query result: fetching terminal_info_id of FDC PG: {terminal_info_id}")
                api_details = DBProcessor.get_api_details('Settlement', request_body={"username": portal_username,
                                                                            "password": portal_password})
                api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
                settle_response = APIProcessor.send_request(api_details)
                settle_success = settle_response['success']
                if settle_success == True:
                    api_details = DBProcessor.get_api_details('Offline_Refund',
                                                              request_body={"username": app_username,
                                                                            "password": app_password,
                                                                            "ezetapDeviceData": card_details[
                                                                                "Ezetap Device Data"],
                                                                            "originalTransactionId": txn_id,
                                                                            "amount": original_amount,
                                                                            "deviceSerial": device_serial})
                    refund_response = APIProcessor.send_request(api_details)
                    refund_success = refund_response['success']
                else:
                    logger.error("Settlement failed")

            else:
                logger.error("card Payment failed")



            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
         # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            bin_no = card_processor.get_device_data_details(card_details['Ezetap Device Data'])['CLEAR_PAN'][0:6]
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if refund_success == True:
                    expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode":"CARD",
                                         "pmt_status":"REFUNDED",
                                        "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                         "pmt_card_bin":bin_no,
                                         "pmt_card_brand":"RUPAY", "pmt_card_type":"CREDIT", "card_txn_type":"CTLS",
                                         "txn_type":"REFUND", "acq_code":"ICICI"}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    amount = float(refund_response['amount'])
                    txnid = refund_response['txnId']
                    orgtxnid = refund_response['origTxnId']
                    payment_mode = refund_response['paymentMode']
                    payment_status = refund_response['status']
                    payment_state = refund_response['states'][0]
                    settlement_status = refund_response['settlementStatus']
                    payment_card_bin = refund_response['paymentCardBin']
                    payment_card_brand = refund_response['paymentCardBrand']
                    payment_card_type = refund_response['paymentCardType']
                    card_txn_type = refund_response['cardTxnTypeDesc']
                    txn_type = refund_response['txnType']
                    acq_code = refund_response['acquirerCode']
                    logger.info(f"API Result: Fetch Response of refund payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                    actualAPIValues = {"success": refund_success,"txn_amt": amount, "pmt_mode":payment_mode,
                                       "pmt_status":payment_status,
                                        "pmt_state":payment_state, "settle_status":settlement_status,
                                       "pmt_card_bin":payment_card_bin,
                                         "pmt_card_brand":payment_card_brand, "pmt_card_type":payment_card_type,
                                       "card_txn_type":card_txn_type, "txn_type":txn_type, "acq_code":acq_code}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    logger.error("Offline Refund is not successfull")

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")


        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:

                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode":"CARD",
                                    "pmt_status":"REFUNDED",
                                    "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "pmt_state_1": "REFUNDED", "settle_status_1": "SETTLED",
                                    "pmt_card_bin":bin_no,
                                    "pmt_card_brand":"RUPAY", "pmt_card_type":"CREDIT",
                                    "txn_type":"REFUND", "acq_code":"ICICI", "pmt_gateway":"FDC",
                                    "mware_txn_amt": float(original_amount), "mware_pmt_mode": "CARD",
                                    "mware_pmt_status": "REFUNDED",
                                    "mware_pmt_state": "AUTHORIZED", "mware_settle_status": "PENDING",
                                    "mware_pmt_status_1": "AUTHORIZED_REFUNDED",
                                    "mware_pmt_state_1": "REFUNDED", "mware_settle_status_1": "SETTLED",
                                    "mware_pmt_card_bin": bin_no,
                                    "mware_pmt_card_brand": "RUPAY", "mware_pmt_card_type": "CREDIT",
                                    "mware_txn_type": "REFUND", "mware_acq_code": "ICICI", "mware_pmt_gateway": "FDC",
                                    "txn_amt_req": float(original_amount), "pmt_status_req":"SUCCESS",
                                    "pmt_status_req_1":"SUCCESS"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '"+txnid+"';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]
                pmt_state = result_txn["state"].iloc[0]
                pmt_card_bin = result_txn["payment_card_bin"].iloc[0]
                pmt_card_brand = result_txn["payment_card_brand"].iloc[0]
                pmt_card_type = result_txn["payment_card_type"].iloc[0]
                txn_type = result_txn["txn_type"].iloc[0]
                acq_code = result_txn["acquirer_code"].iloc[0]
                pmt_gateway = result_txn["payment_gateway"].iloc[0]

                query_txn = "select settlement_status, status, state from txn where id = '" + orgtxnid + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                settle_status_1 = result_txn["settlement_status"].iloc[0]
                pmt_status_1 = result_txn["status"].iloc[0]
                pmt_state_1 = result_txn["state"].iloc[0]

                query_txn_mware = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where ref_txn_id = '" + txnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware,"mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_txn_amt = float(result_txn_mware["amount"].iloc[0])
                mware_pmt_mode = result_txn_mware["payment_mode"].iloc[0]
                mware_settle_status = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status = result_txn_mware["status"].iloc[0]
                mware_pmt_state = result_txn_mware["state"].iloc[0]
                mware_pmt_card_bin = result_txn_mware["payment_card_bin"].iloc[0]
                mware_pmt_card_brand = result_txn_mware["payment_card_brand"].iloc[0]
                mware_pmt_card_type = result_txn_mware["payment_card_type"].iloc[0]
                mware_txn_type = result_txn_mware["txn_type"].iloc[0]
                mware_acq_code = result_txn_mware["acquirer_code"].iloc[0]
                mware_pmt_gateway = result_txn_mware["payment_gateway"].iloc[0]

                query_txn_mware = "select settlement_status, status, state from txn where ref_txn_id = '" + orgtxnid + "';"
                result_txn_mware = DBProcessor.getValueFromDB(query_txn_mware, "mware")
                logger.debug(f"Query result: {result_txn_mware}")

                mware_settle_status_1 = result_txn_mware["settlement_status"].iloc[0]
                mware_pmt_status_1 = result_txn_mware["status"].iloc[0]
                mware_pmt_state_1 = result_txn_mware["state"].iloc[0]

                query_txn_req = "select amount, status from txn_request where id = '" + txnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                txn_amt_req = float(result_txn_req["amount"].iloc[0])
                pmt_status_req = result_txn_req["status"].iloc[0]

                query_txn_req = "select status from txn_request where id = '" + orgtxnid + "';"
                result_txn_req = DBProcessor.getValueFromDB(query_txn_req)
                logger.debug(f"Query result: {result_txn_req}")

                pmt_status_req_1 = result_txn_req["status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode":pmt_mode,
                                    "pmt_status":pmt_status,
                                    "pmt_state":pmt_state, "settle_status": settle_status,
                                    "pmt_status_1": pmt_status_1,
                                    "pmt_state_1": pmt_state_1, "settle_status_1": settle_status_1,
                                    "pmt_card_bin":pmt_card_bin,
                                    "pmt_card_brand":pmt_card_brand, "pmt_card_type":pmt_card_type,
                                    "txn_type":txn_type, "acq_code":acq_code, "pmt_gateway":pmt_gateway,
                                    "mware_txn_amt": mware_txn_amt, "mware_pmt_mode":mware_pmt_mode,
                                    "mware_pmt_status": mware_pmt_status,
                                    "mware_pmt_state": mware_pmt_state, "mware_settle_status": mware_settle_status,
                                    "mware_pmt_status_1": mware_pmt_status_1,
                                    "mware_pmt_state_1": mware_pmt_state_1, "mware_settle_status_1": mware_settle_status_1,
                                    "mware_pmt_card_bin": mware_pmt_card_bin,
                                    "mware_pmt_card_brand": mware_pmt_card_brand, "mware_pmt_card_type":mware_pmt_card_type,
                                    "mware_txn_type": mware_txn_type, "mware_acq_code": mware_acq_code,
                                    "mware_pmt_gateway": mware_pmt_gateway,"txn_amt_req":txn_amt_req,
                                    "pmt_status_req":pmt_status_req,"pmt_status_req_1":pmt_status_req_1}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
                logger.info(f"Completed DB validation for the test case : {testcase_id}")

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    finally:
        Configuration.executeFinallyBlock(testcase_id)





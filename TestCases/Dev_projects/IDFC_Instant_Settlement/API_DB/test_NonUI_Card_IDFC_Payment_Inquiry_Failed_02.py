import time
import pytest
import random
import sys
from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner, \
    merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities import card_processor
import numpy as np

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d100_d101_062():
    """
        Sub Feature Code: NonUI_Common_IDFC_Card_failed_Inquiry_Instant_Settlement_EMVCTLS_DEBIT_VISA
        Sub Feature Description: API that performs failed inquiry on IS settlement when IS call is Timeout for CTLS DEBIT VISA card via IDFC_FDC
        TC naming code description:
        d100: Dev Projects
        d101: IDFC Instant Settlement
        062: TC062
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {portal_cred}")
        super_username = portal_cred['Username']
        super_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code=org_code, portal_un=super_username,
                                                       portal_pw=super_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        card_processor.update_invalid_merchant_account_details(org_code=org_code)
        card_processor.update_idfc_timeout_properties('10000')
        card_processor.update_idfc_paymentApi_read_timeout('1')
        card_processor.update_idfc_paymentApi_write_timeout('1')

        query_url = "select prop_value from ezetap_properties where prop_key = 'instantSettlementInquiryApiUrl';"
        logger.debug(f"Query to fetch payment inquiry url from the DB : {query}")
        result = DBProcessor.getValueFromDB(query_url)
        url = str(result['prop_value'].values[0])
        logger.debug(f"Query result, url : {url}")
        if url.__contains__('castlemock'):
            card_processor.update_instant_settle_clientcode('EZETAP1')
        else:
            card_processor.update_instant_settle_clientcode('EZETAP')
        api_details = DBProcessor.get_api_details('DB Refresh',
                                                  request_body={
                                                      "username": super_username,
                                                      "password": super_password,
                                                  })

        response = APIProcessor.send_request(api_details)
        logger.info(f"response of DB refresh: {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=True,
                                                   config_log=False, closedloop_log=False, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10,1000)
            card_details = card_processor.get_card_details_from_excel("IDFC_EMVCTLS_DEBIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="IDFC",
                                                              payment_gateway="IDFC_FDC"),
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response received from card payment is {response}")
            card_payment_success = response['success']
            time.sleep(10)
            if card_payment_success == True:
                txn_id = response['txnId']
                api_details = DBProcessor.get_api_details('paymentInquiry',
                                                          request_body={"username": super_username,
                                                                        "password": super_password,
                                                                        "txnId": txn_id,
                                                                        })
                paymentinquiry_response = APIProcessor.send_request(api_details)
                logger.info(f"Response received from payment Inquiry for {txn_id} is {paymentinquiry_response}")
            else:
                logger.error("Card payment Failed")

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
                    expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode":"CARD",
                                         "pmt_status":"AUTHORIZED",
                                        "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                         "pmt_card_bin":bin_no,
                                         "pmt_card_brand":"VISA", "pmt_card_type":"DEBIT", "card_txn_type":"CTLS",
                                         "txn_type":"CHARGE", "acq_code":"IDFC", "voidable":False, "refundable":False}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    amount = float(response['amount'])
                    txnid = response['txnId']
                    payment_mode = response['paymentMode']
                    payment_status = response['status']
                    payment_state = response['states'][0]
                    settlement_status = response['settlementStatus']
                    payment_card_bin = response['paymentCardBin']
                    payment_card_brand = response['paymentCardBrand']
                    payment_card_type = response['paymentCardType']
                    card_txn_type = response['cardTxnTypeDesc']
                    txn_type = response['txnType']
                    acq_code = response['acquirerCode']
                    voidable = response['voidable']
                    refundable = response['refundable']

                    logger.info(f"API Result: Fetch Response of Card Payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                    actualAPIValues = {"success": card_payment_success,"txn_amt": amount, "pmt_mode":payment_mode,
                                       "pmt_status":payment_status,
                                        "pmt_state":payment_state, "settle_status":settlement_status,
                                       "pmt_card_bin":payment_card_bin,
                                         "pmt_card_brand":payment_card_brand, "pmt_card_type":payment_card_type,
                                       "card_txn_type":card_txn_type, "txn_type":txn_type, "acq_code":acq_code,
                                       "voidable":voidable, "refundable":refundable}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")


        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                result = DBProcessor.getValueFromDB("select * from ezetap_properties where type = 'INSTANT_SETTLEMENT' and prop_key = 'msfRateForInstantSettlement';")
                msf_per = float(result["prop_value"].iloc[0])
                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode":"CARD",
                                    "pmt_status":"AUTHORIZED",
                                    "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_card_bin":bin_no,
                                    "pmt_card_brand":"VISA", "pmt_card_type":"DEBIT",
                                    "txn_type":"CHARGE", "acq_code":"IDFC", "pmt_gateway":"IDFC_FDC",
                                    "is_txn_amt":float(original_amount), "is_msf_percentage":msf_per,"is_settle_amt":(float(original_amount)-(float(original_amount) * ((msf_per)/100))),
                                    "is_org_code":org_code,"is_acq_code":"IDFC","is_resp_code":"NULL",
                                    "is_resp_desc":"TIMEOUT","is_error_code":"NULL",
                                    "is_error_desc":"NULL","is_inquiry_resp_code":"200", "is_inquiry_resp_desc":"FAILED",
                                    "is_inquiry_error_code":"ENQ007",
                                    "is_inquiry_error_rsn":"Sorry!! No Matching Information found for the given input values","is_settle_status":"IS_FAILED"}
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

                query_is_txn_details = "select  * from instant_settlement_details where id = '" + txnid + "';"
                result_is_txn_details = DBProcessor.getValueFromDB(query_is_txn_details)
                result_is_txn_details = result_is_txn_details.replace(np.nan,'NULL',regex=True)
                logger.debug(f"Query result: {result_is_txn_details}")

                is_txn_amt = float(result_is_txn_details["transaction_amount"].iloc[0])
                is_msf_percentage = result_is_txn_details["msf_percentage"].iloc[0]
                is_settle_amt = result_is_txn_details["settlement_amount"].iloc[0]
                is_org_code = result_is_txn_details["org_code"].iloc[0]
                is_acq_code = result_is_txn_details["acquirer_code"].iloc[0]
                is_resp_code = result_is_txn_details["response_code"].iloc[0]
                is_resp_desc = result_is_txn_details["response_description"].iloc[0]
                is_error_code = result_is_txn_details["error_code"].iloc[0]
                is_error_desc = result_is_txn_details["error_description"].iloc[0]
                is_inquiry_resp_code = result_is_txn_details["inquiry_resp_code"].iloc[0]
                is_inquiry_resp_desc = result_is_txn_details["inquiry_resp_description"].iloc[0]
                is_inquiry_error_code = result_is_txn_details["inquiry_error_cd"].iloc[0]
                is_inquiry_error_rsn = result_is_txn_details["inquiry_error_rsn"].iloc[0]
                is_settle_status = result_is_txn_details["settlement_status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode":pmt_mode,
                                    "pmt_status":pmt_status,
                                    "pmt_state":pmt_state, "settle_status": settle_status,
                                    "pmt_card_bin":pmt_card_bin,
                                    "pmt_card_brand":pmt_card_brand, "pmt_card_type":pmt_card_type,
                                    "txn_type":txn_type, "acq_code":acq_code, "pmt_gateway":pmt_gateway,
                                    "is_txn_amt":is_txn_amt, "is_msf_percentage":is_msf_percentage,"is_settle_amt":is_settle_amt,
                                    "is_org_code":is_org_code,"is_acq_code":is_acq_code,"is_resp_code":is_resp_code,
                                    "is_resp_desc":is_resp_desc,"is_error_code":is_error_code,
                                    "is_error_desc":is_error_desc,"is_inquiry_resp_code":is_inquiry_resp_code, "is_inquiry_resp_desc":is_inquiry_resp_desc,
                                    "is_inquiry_error_code":is_inquiry_error_code,
                                    "is_inquiry_error_rsn":is_inquiry_error_rsn,"is_settle_status":is_settle_status
                                    }
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
def test_d100_d101_063():
    """
        Sub Feature Code: NonUI_Common_IDFC_Card_Failed_Inquiry_Instant_Settlement_EMVCTLS_DEBIT_MASTER
        Sub Feature Description: API that performs failed inquiry on IS settlement when IS call is Timeout for CTLS MASTER_CARD VISA card via IDFC_FDC
        TC naming code description:
        d100: Dev Projects
        d101: IDFC Instant Settlement
        063: TC063
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {portal_cred}")
        super_username = portal_cred['Username']
        super_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code=org_code, portal_un=super_username,
                                                       portal_pw=super_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        card_processor.update_invalid_merchant_account_details(org_code=org_code)
        card_processor.update_idfc_timeout_properties('10000')
        card_processor.update_idfc_paymentApi_read_timeout('1')
        card_processor.update_idfc_paymentApi_write_timeout('1')

        query_url = "select prop_value from ezetap_properties where prop_key = 'instantSettlementInquiryApiUrl';"
        logger.debug(f"Query to fetch payment inquiry url from the DB : {query}")
        result = DBProcessor.getValueFromDB(query_url)
        url = str(result['prop_value'].values[0])
        logger.debug(f"Query result, url : {url}")
        if url.__contains__('castlemock'):
            card_processor.update_instant_settle_clientcode('EZETAP1')
        else:
            card_processor.update_instant_settle_clientcode('EZETAP')
        api_details = DBProcessor.get_api_details('DB Refresh',
                                                  request_body={
                                                      "username": super_username,
                                                      "password": super_password,
                                                  })

        response = APIProcessor.send_request(api_details)
        logger.info(f"response of DB refresh: {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=True,
                                                   config_log=False, closedloop_log=False, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("IDFC_EMVCTLS_DEBIT_MASTER")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="IDFC",
                                                              payment_gateway="IDFC_FDC"),
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response received from card payment is {response}")
            card_payment_success = response['success']
            time.sleep(10)
            if card_payment_success == True:
                txn_id = response['txnId']
                api_details = DBProcessor.get_api_details('paymentInquiry',
                                                          request_body={"username": super_username,
                                                                        "password": super_password,
                                                                        "txnId": txn_id,
                                                                        })
                paymentinquiry_response = APIProcessor.send_request(api_details)
                logger.info(f"Response received from payment Inquiry for {txn_id} is {paymentinquiry_response}")
            else:
                logger.error("Card payment Failed")

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
                expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode": "CARD",
                                     "pmt_status": "AUTHORIZED",
                                     "pmt_state": "AUTHORIZED", "settle_status": "PENDING",
                                     "pmt_card_bin": bin_no,
                                     "pmt_card_brand": "MASTER_CARD", "pmt_card_type": "DEBIT", "card_txn_type": "CTLS",
                                     "txn_type": "CHARGE", "acq_code": "IDFC", "voidable": False, "refundable": False}

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                amount = float(response['amount'])
                txnid = response['txnId']
                payment_mode = response['paymentMode']
                payment_status = response['status']
                payment_state = response['states'][0]
                settlement_status = response['settlementStatus']
                payment_card_bin = response['paymentCardBin']
                payment_card_brand = response['paymentCardBrand']
                payment_card_type = response['paymentCardType']
                card_txn_type = response['cardTxnTypeDesc']
                txn_type = response['txnType']
                acq_code = response['acquirerCode']
                voidable = response['voidable']
                refundable = response['refundable']

                logger.info(
                    f"API Result: Fetch Response of Card Payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                actualAPIValues = {"success": card_payment_success, "txn_amt": amount, "pmt_mode": payment_mode,
                                   "pmt_status": payment_status,
                                   "pmt_state": payment_state, "settle_status": settlement_status,
                                   "pmt_card_bin": payment_card_bin,
                                   "pmt_card_brand": payment_card_brand, "pmt_card_type": payment_card_type,
                                   "card_txn_type": card_txn_type, "txn_type": txn_type, "acq_code": acq_code,
                                   "voidable": voidable, "refundable": refundable}
                logger.debug(f"actualAPIValues: {actualAPIValues}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")

        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                result = DBProcessor.getValueFromDB(
                    "select * from ezetap_properties where type = 'INSTANT_SETTLEMENT' and prop_key = 'msfRateForInstantSettlement';")
                msf_per = float(result["prop_value"].iloc[0])
                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode": "CARD",
                                    "pmt_status": "AUTHORIZED",
                                    "pmt_state": "AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_card_bin": bin_no,
                                    "pmt_card_brand": "MASTER_CARD", "pmt_card_type": "DEBIT",
                                    "txn_type": "CHARGE", "acq_code": "IDFC", "pmt_gateway": "IDFC_FDC",
                                    "is_txn_amt": float(original_amount), "is_msf_percentage": msf_per,
                                    "is_settle_amt": (
                                                float(original_amount) - (float(original_amount) * ((msf_per) / 100))),
                                    "is_org_code": org_code, "is_acq_code": "IDFC", "is_resp_code": "NULL",
                                    "is_resp_desc": "TIMEOUT", "is_error_code": "NULL",
                                    "is_error_desc": "NULL", "is_inquiry_resp_code": "200",
                                    "is_inquiry_resp_desc": "FAILED",
                                    "is_inquiry_error_code": "ENQ007",
                                    "is_inquiry_error_rsn": "Sorry!! No Matching Information found for the given input values", "is_settle_status": "IS_FAILED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '" + txnid + "';"
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

                query_is_txn_details = "select  * from instant_settlement_details where id = '" + txnid + "';"
                result_is_txn_details = DBProcessor.getValueFromDB(query_is_txn_details)
                result_is_txn_details = result_is_txn_details.replace(np.nan, 'NULL', regex=True)
                logger.debug(f"Query result: {result_is_txn_details}")

                is_txn_amt = float(result_is_txn_details["transaction_amount"].iloc[0])
                is_msf_percentage = result_is_txn_details["msf_percentage"].iloc[0]
                is_settle_amt = result_is_txn_details["settlement_amount"].iloc[0]
                is_org_code = result_is_txn_details["org_code"].iloc[0]
                is_acq_code = result_is_txn_details["acquirer_code"].iloc[0]
                is_resp_code = result_is_txn_details["response_code"].iloc[0]
                is_resp_desc = result_is_txn_details["response_description"].iloc[0]
                is_error_code = result_is_txn_details["error_code"].iloc[0]
                is_error_desc = result_is_txn_details["error_description"].iloc[0]
                is_inquiry_resp_code = result_is_txn_details["inquiry_resp_code"].iloc[0]
                is_inquiry_resp_desc = result_is_txn_details["inquiry_resp_description"].iloc[0]
                is_inquiry_error_code = result_is_txn_details["inquiry_error_cd"].iloc[0]
                is_inquiry_error_rsn = result_is_txn_details["inquiry_error_rsn"].iloc[0]
                is_settle_status = result_is_txn_details["settlement_status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode": pmt_mode,
                                  "pmt_status": pmt_status,
                                  "pmt_state": pmt_state, "settle_status": settle_status,
                                  "pmt_card_bin": pmt_card_bin,
                                  "pmt_card_brand": pmt_card_brand, "pmt_card_type": pmt_card_type,
                                  "txn_type": txn_type, "acq_code": acq_code, "pmt_gateway": pmt_gateway,
                                  "is_txn_amt": is_txn_amt, "is_msf_percentage": is_msf_percentage,
                                  "is_settle_amt": is_settle_amt,
                                  "is_org_code": is_org_code, "is_acq_code": is_acq_code, "is_resp_code": is_resp_code,
                                  "is_resp_desc": is_resp_desc, "is_error_code": is_error_code,
                                  "is_error_desc": is_error_desc, "is_inquiry_resp_code": is_inquiry_resp_code,
                                  "is_inquiry_resp_desc": is_inquiry_resp_desc,
                                  "is_inquiry_error_code": is_inquiry_error_code,
                                  "is_inquiry_error_rsn": is_inquiry_error_rsn, "is_settle_status": is_settle_status
                                  }
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
def test_d100_d101_064():
    """
        Sub Feature Code: NonUI_Common_IDFC_Card_Failed_Inquiry_Instant_Settlement_EMVCTLS_DEBIT_RUPAY
        Sub Feature Description: API that performs failed inquiry on IS settlement when IS call is Timeout for CTLS RUPAY VISA card via IDFC_FDC
        TC naming code description:
        d100: Dev Projects
        d101: IDFC Instant Settlement
        064: TC064
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {portal_cred}")
        super_username = portal_cred['Username']
        super_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code=org_code, portal_un=super_username,
                                                       portal_pw=super_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        card_processor.update_invalid_merchant_account_details(org_code=org_code)
        card_processor.update_idfc_timeout_properties('10000')
        card_processor.update_idfc_paymentApi_read_timeout('1')
        card_processor.update_idfc_paymentApi_write_timeout('1')

        query_url = "select prop_value from ezetap_properties where prop_key = 'instantSettlementInquiryApiUrl';"
        logger.debug(f"Query to fetch payment inquiry url from the DB : {query}")
        result = DBProcessor.getValueFromDB(query_url)
        url = str(result['prop_value'].values[0])
        logger.debug(f"Query result, url : {url}")
        if url.__contains__('castlemock'):
            card_processor.update_instant_settle_clientcode('EZETAP1')
        else:
            card_processor.update_instant_settle_clientcode('EZETAP')
        api_details = DBProcessor.get_api_details('DB Refresh',
                                                  request_body={
                                                      "username": super_username,
                                                      "password": super_password,
                                                  })

        response = APIProcessor.send_request(api_details)
        logger.info(f"response of DB refresh: {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=True,
                                                   config_log=False, closedloop_log=False, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("IDFC_EMVCTLS_DEBIT_RUPAY")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="IDFC",
                                                              payment_gateway="IDFC_FDC"),
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response received from card payment is {response}")
            card_payment_success = response['success']
            time.sleep(10)
            if card_payment_success == True:
                txn_id = response['txnId']
                api_details = DBProcessor.get_api_details('paymentInquiry',
                                                          request_body={"username": super_username,
                                                                        "password": super_password,
                                                                        "txnId": txn_id,
                                                                        })
                paymentinquiry_response = APIProcessor.send_request(api_details)
                logger.info(f"Response received from payment Inquiry for {txn_id} is {paymentinquiry_response}")
            else:
                logger.error("Card payment Failed")

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
                expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode": "CARD",
                                     "pmt_status": "AUTHORIZED",
                                     "pmt_state": "AUTHORIZED", "settle_status": "PENDING",
                                     "pmt_card_bin": bin_no,
                                     "pmt_card_brand": "RUPAY", "pmt_card_type": "DEBIT", "card_txn_type": "CTLS",
                                     "txn_type": "CHARGE", "acq_code": "IDFC", "voidable": False, "refundable": False}

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                amount = float(response['amount'])
                txnid = response['txnId']
                payment_mode = response['paymentMode']
                payment_status = response['status']
                payment_state = response['states'][0]
                settlement_status = response['settlementStatus']
                payment_card_bin = response['paymentCardBin']
                payment_card_brand = response['paymentCardBrand']
                payment_card_type = response['paymentCardType']
                card_txn_type = response['cardTxnTypeDesc']
                txn_type = response['txnType']
                acq_code = response['acquirerCode']
                voidable = response['voidable']
                refundable = response['refundable']

                logger.info(
                    f"API Result: Fetch Response of Card Payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                actualAPIValues = {"success": card_payment_success, "txn_amt": amount, "pmt_mode": payment_mode,
                                   "pmt_status": payment_status,
                                   "pmt_state": payment_state, "settle_status": settlement_status,
                                   "pmt_card_bin": payment_card_bin,
                                   "pmt_card_brand": payment_card_brand, "pmt_card_type": payment_card_type,
                                   "card_txn_type": card_txn_type, "txn_type": txn_type, "acq_code": acq_code,
                                   "voidable": voidable, "refundable": refundable}
                logger.debug(f"actualAPIValues: {actualAPIValues}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")

        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                result = DBProcessor.getValueFromDB(
                    "select * from ezetap_properties where type = 'INSTANT_SETTLEMENT' and prop_key = 'msfRateForInstantSettlement';")
                msf_per = float(result["prop_value"].iloc[0])
                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode": "CARD",
                                    "pmt_status": "AUTHORIZED",
                                    "pmt_state": "AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_card_bin": bin_no,
                                    "pmt_card_brand": "RUPAY", "pmt_card_type": "DEBIT",
                                    "txn_type": "CHARGE", "acq_code": "IDFC", "pmt_gateway": "IDFC_FDC",
                                    "is_txn_amt": float(original_amount), "is_msf_percentage": msf_per,
                                    "is_settle_amt": (
                                                float(original_amount) - (float(original_amount) * ((msf_per) / 100))),
                                    "is_org_code": org_code, "is_acq_code": "IDFC", "is_resp_code": "NULL",
                                    "is_resp_desc": "TIMEOUT", "is_error_code": "NULL",
                                    "is_error_desc": "NULL", "is_inquiry_resp_code": "200",
                                    "is_inquiry_resp_desc": "FAILED",
                                    "is_inquiry_error_code": "ENQ007",
                                    "is_inquiry_error_rsn": "Sorry!! No Matching Information found for the given input values", "is_settle_status": "IS_FAILED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '" + txnid + "';"
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

                query_is_txn_details = "select  * from instant_settlement_details where id = '" + txnid + "';"
                result_is_txn_details = DBProcessor.getValueFromDB(query_is_txn_details)
                result_is_txn_details = result_is_txn_details.replace(np.nan, 'NULL', regex=True)
                logger.debug(f"Query result: {result_is_txn_details}")

                is_txn_amt = float(result_is_txn_details["transaction_amount"].iloc[0])
                is_msf_percentage = result_is_txn_details["msf_percentage"].iloc[0]
                is_settle_amt = result_is_txn_details["settlement_amount"].iloc[0]
                is_org_code = result_is_txn_details["org_code"].iloc[0]
                is_acq_code = result_is_txn_details["acquirer_code"].iloc[0]
                is_resp_code = result_is_txn_details["response_code"].iloc[0]
                is_resp_desc = result_is_txn_details["response_description"].iloc[0]
                is_error_code = result_is_txn_details["error_code"].iloc[0]
                is_error_desc = result_is_txn_details["error_description"].iloc[0]
                is_inquiry_resp_code = result_is_txn_details["inquiry_resp_code"].iloc[0]
                is_inquiry_resp_desc = result_is_txn_details["inquiry_resp_description"].iloc[0]
                is_inquiry_error_code = result_is_txn_details["inquiry_error_cd"].iloc[0]
                is_inquiry_error_rsn = result_is_txn_details["inquiry_error_rsn"].iloc[0]
                is_settle_status = result_is_txn_details["settlement_status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode": pmt_mode,
                                  "pmt_status": pmt_status,
                                  "pmt_state": pmt_state, "settle_status": settle_status,
                                  "pmt_card_bin": pmt_card_bin,
                                  "pmt_card_brand": pmt_card_brand, "pmt_card_type": pmt_card_type,
                                  "txn_type": txn_type, "acq_code": acq_code, "pmt_gateway": pmt_gateway,
                                  "is_txn_amt": is_txn_amt, "is_msf_percentage": is_msf_percentage,
                                  "is_settle_amt": is_settle_amt,
                                  "is_org_code": is_org_code, "is_acq_code": is_acq_code, "is_resp_code": is_resp_code,
                                  "is_resp_desc": is_resp_desc, "is_error_code": is_error_code,
                                  "is_error_desc": is_error_desc, "is_inquiry_resp_code": is_inquiry_resp_code,
                                  "is_inquiry_resp_desc": is_inquiry_resp_desc,
                                  "is_inquiry_error_code": is_inquiry_error_code,
                                  "is_inquiry_error_rsn": is_inquiry_error_rsn, "is_settle_status": is_settle_status
                                  }
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
def test_d100_d101_065():
    """
        Sub Feature Code: NonUI_Common_IDFC_Card_Failed_Inquiry_Instant_Settlement_EMVCTLS_CREDIT_VISA
        Sub Feature Description: API that performs failed inquiry on IS settlement when IS call is Timeout for CTLS VISA CREDIT card via IDFC_FDC
        TC naming code description:
        d100: Dev Projects
        d101: IDFC Instant Settlement
        065: TC065
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {portal_cred}")
        super_username = portal_cred['Username']
        super_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code=org_code, portal_un=super_username,
                                                       portal_pw=super_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        card_processor.update_invalid_merchant_account_details(org_code=org_code)
        card_processor.update_idfc_timeout_properties('10000')
        card_processor.update_idfc_paymentApi_read_timeout('1')
        card_processor.update_idfc_paymentApi_write_timeout('1')

        query_url = "select prop_value from ezetap_properties where prop_key = 'instantSettlementInquiryApiUrl';"
        logger.debug(f"Query to fetch payment inquiry url from the DB : {query}")
        result = DBProcessor.getValueFromDB(query_url)
        url = str(result['prop_value'].values[0])
        logger.debug(f"Query result, url : {url}")
        if url.__contains__('castlemock'):
            card_processor.update_instant_settle_clientcode('EZETAP1')
        else:
            card_processor.update_instant_settle_clientcode('EZETAP')
        api_details = DBProcessor.get_api_details('DB Refresh',
                                                  request_body={
                                                      "username": super_username,
                                                      "password": super_password,
                                                  })

        response = APIProcessor.send_request(api_details)
        logger.info(f"response of DB refresh: {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=True,
                                                   config_log=False, closedloop_log=False, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10,1000)
            card_details = card_processor.get_card_details_from_excel("IDFC_EMVCTLS_CREDIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="IDFC",
                                                              payment_gateway="IDFC_FDC"),
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response received from card payment is {response}")
            card_payment_success = response['success']
            time.sleep(10)
            if card_payment_success == True:
                txn_id = response['txnId']
                api_details = DBProcessor.get_api_details('paymentInquiry',
                                                          request_body={"username": super_username,
                                                                        "password": super_password,
                                                                        "txnId": txn_id,
                                                                        })
                paymentinquiry_response = APIProcessor.send_request(api_details)
                logger.info(f"Response received from payment Inquiry for {txn_id} is {paymentinquiry_response}")
            else:
                logger.error("Card payment Failed")

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
                    expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode":"CARD",
                                         "pmt_status":"AUTHORIZED",
                                        "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                         "pmt_card_bin":bin_no,
                                         "pmt_card_brand":"VISA", "pmt_card_type":"CREDIT", "card_txn_type":"CTLS",
                                         "txn_type":"CHARGE", "acq_code":"IDFC", "voidable":False, "refundable":False}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    amount = float(response['amount'])
                    txnid = response['txnId']
                    payment_mode = response['paymentMode']
                    payment_status = response['status']
                    payment_state = response['states'][0]
                    settlement_status = response['settlementStatus']
                    payment_card_bin = response['paymentCardBin']
                    payment_card_brand = response['paymentCardBrand']
                    payment_card_type = response['paymentCardType']
                    card_txn_type = response['cardTxnTypeDesc']
                    txn_type = response['txnType']
                    acq_code = response['acquirerCode']
                    voidable = response['voidable']
                    refundable = response['refundable']

                    logger.info(f"API Result: Fetch Response of Card Payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                    actualAPIValues = {"success": card_payment_success,"txn_amt": amount, "pmt_mode":payment_mode,
                                       "pmt_status":payment_status,
                                        "pmt_state":payment_state, "settle_status":settlement_status,
                                       "pmt_card_bin":payment_card_bin,
                                         "pmt_card_brand":payment_card_brand, "pmt_card_type":payment_card_type,
                                       "card_txn_type":card_txn_type, "txn_type":txn_type, "acq_code":acq_code,
                                       "voidable":voidable, "refundable":refundable}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")


        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                result = DBProcessor.getValueFromDB("select * from ezetap_properties where type = 'INSTANT_SETTLEMENT' and prop_key = 'msfRateForInstantSettlement';")
                msf_per = float(result["prop_value"].iloc[0])
                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode":"CARD",
                                    "pmt_status":"AUTHORIZED",
                                    "pmt_state":"AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_card_bin":bin_no,
                                    "pmt_card_brand":"VISA", "pmt_card_type":"CREDIT",
                                    "txn_type":"CHARGE", "acq_code":"IDFC", "pmt_gateway":"IDFC_FDC",
                                    "is_txn_amt":float(original_amount), "is_msf_percentage":msf_per,"is_settle_amt":(float(original_amount)-(float(original_amount) * ((msf_per)/100))),
                                    "is_org_code":org_code,"is_acq_code":"IDFC","is_resp_code":"NULL",
                                    "is_resp_desc":"TIMEOUT","is_error_code":"NULL",
                                    "is_error_desc":"NULL","is_inquiry_resp_code":"200", "is_inquiry_resp_desc":"FAILED",
                                    "is_inquiry_error_code":"ENQ007",
                                    "is_inquiry_error_rsn":"Sorry!! No Matching Information found for the given input values","is_settle_status":"IS_FAILED"}
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

                query_is_txn_details = "select  * from instant_settlement_details where id = '" + txnid + "';"
                result_is_txn_details = DBProcessor.getValueFromDB(query_is_txn_details)
                result_is_txn_details = result_is_txn_details.replace(np.nan,'NULL',regex=True)
                logger.debug(f"Query result: {result_is_txn_details}")

                is_txn_amt = float(result_is_txn_details["transaction_amount"].iloc[0])
                is_msf_percentage = result_is_txn_details["msf_percentage"].iloc[0]
                is_settle_amt = result_is_txn_details["settlement_amount"].iloc[0]
                is_org_code = result_is_txn_details["org_code"].iloc[0]
                is_acq_code = result_is_txn_details["acquirer_code"].iloc[0]
                is_resp_code = result_is_txn_details["response_code"].iloc[0]
                is_resp_desc = result_is_txn_details["response_description"].iloc[0]
                is_error_code = result_is_txn_details["error_code"].iloc[0]
                is_error_desc = result_is_txn_details["error_description"].iloc[0]
                is_inquiry_resp_code = result_is_txn_details["inquiry_resp_code"].iloc[0]
                is_inquiry_resp_desc = result_is_txn_details["inquiry_resp_description"].iloc[0]
                is_inquiry_error_code = result_is_txn_details["inquiry_error_cd"].iloc[0]
                is_inquiry_error_rsn = result_is_txn_details["inquiry_error_rsn"].iloc[0]
                is_settle_status = result_is_txn_details["settlement_status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode":pmt_mode,
                                    "pmt_status":pmt_status,
                                    "pmt_state":pmt_state, "settle_status": settle_status,
                                    "pmt_card_bin":pmt_card_bin,
                                    "pmt_card_brand":pmt_card_brand, "pmt_card_type":pmt_card_type,
                                    "txn_type":txn_type, "acq_code":acq_code, "pmt_gateway":pmt_gateway,
                                    "is_txn_amt":is_txn_amt, "is_msf_percentage":is_msf_percentage,"is_settle_amt":is_settle_amt,
                                    "is_org_code":is_org_code,"is_acq_code":is_acq_code,"is_resp_code":is_resp_code,
                                    "is_resp_desc":is_resp_desc,"is_error_code":is_error_code,
                                    "is_error_desc":is_error_desc,"is_inquiry_resp_code":is_inquiry_resp_code, "is_inquiry_resp_desc":is_inquiry_resp_desc,
                                    "is_inquiry_error_code":is_inquiry_error_code,
                                    "is_inquiry_error_rsn":is_inquiry_error_rsn,"is_settle_status":is_settle_status
                                    }
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
def test_d100_d101_066():
    """
        Sub Feature Code: NonUI_Common_IDFC_Card_Failed_Inquiry_Instant_Settlement_EMVCTLS_CREDIT_MASTER
        Sub Feature Description: API that performs failed inquiry on IS settlement when IS call is Timeout for CTLS MASTER_CARD CREDIT card via IDFC_FDC
        TC naming code description:
        d100: Dev Projects
        d101: IDFC Instant Settlement
        066: TC066
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {portal_cred}")
        super_username = portal_cred['Username']
        super_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code=org_code, portal_un=super_username,
                                                       portal_pw=super_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        card_processor.update_invalid_merchant_account_details(org_code=org_code)
        card_processor.update_idfc_timeout_properties('10000')
        card_processor.update_idfc_paymentApi_read_timeout('1')
        card_processor.update_idfc_paymentApi_write_timeout('1')

        query_url = "select prop_value from ezetap_properties where prop_key = 'instantSettlementInquiryApiUrl';"
        logger.debug(f"Query to fetch payment inquiry url from the DB : {query}")
        result = DBProcessor.getValueFromDB(query_url)
        url = str(result['prop_value'].values[0])
        logger.debug(f"Query result, url : {url}")
        if url.__contains__('castlemock'):
            card_processor.update_instant_settle_clientcode('EZETAP1')
        else:
            card_processor.update_instant_settle_clientcode('EZETAP')
        api_details = DBProcessor.get_api_details('DB Refresh',
                                                  request_body={
                                                      "username": super_username,
                                                      "password": super_password,
                                                  })

        response = APIProcessor.send_request(api_details)
        logger.info(f"response of DB refresh: {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=True,
                                                   config_log=False, closedloop_log=False, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("IDFC_EMVCTLS_CREDIT_MASTER")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="IDFC",
                                                              payment_gateway="IDFC_FDC"),
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response received from card payment is {response}")
            card_payment_success = response['success']
            time.sleep(10)
            if card_payment_success == True:
                txn_id = response['txnId']
                api_details = DBProcessor.get_api_details('paymentInquiry',
                                                          request_body={"username": super_username,
                                                                        "password": super_password,
                                                                        "txnId": txn_id,
                                                                        })
                paymentinquiry_response = APIProcessor.send_request(api_details)
                logger.info(f"Response received from payment Inquiry for {txn_id} is {paymentinquiry_response}")
            else:
                logger.error("Card payment Failed")

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
                expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode": "CARD",
                                     "pmt_status": "AUTHORIZED",
                                     "pmt_state": "AUTHORIZED", "settle_status": "PENDING",
                                     "pmt_card_bin": bin_no,
                                     "pmt_card_brand": "MASTER_CARD", "pmt_card_type": "CREDIT", "card_txn_type": "CTLS",
                                     "txn_type": "CHARGE", "acq_code": "IDFC", "voidable": False, "refundable": False}

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                amount = float(response['amount'])
                txnid = response['txnId']
                payment_mode = response['paymentMode']
                payment_status = response['status']
                payment_state = response['states'][0]
                settlement_status = response['settlementStatus']
                payment_card_bin = response['paymentCardBin']
                payment_card_brand = response['paymentCardBrand']
                payment_card_type = response['paymentCardType']
                card_txn_type = response['cardTxnTypeDesc']
                txn_type = response['txnType']
                acq_code = response['acquirerCode']
                voidable = response['voidable']
                refundable = response['refundable']

                logger.info(
                    f"API Result: Fetch Response of Card Payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                actualAPIValues = {"success": card_payment_success, "txn_amt": amount, "pmt_mode": payment_mode,
                                   "pmt_status": payment_status,
                                   "pmt_state": payment_state, "settle_status": settlement_status,
                                   "pmt_card_bin": payment_card_bin,
                                   "pmt_card_brand": payment_card_brand, "pmt_card_type": payment_card_type,
                                   "card_txn_type": card_txn_type, "txn_type": txn_type, "acq_code": acq_code,
                                   "voidable": voidable, "refundable": refundable}
                logger.debug(f"actualAPIValues: {actualAPIValues}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")

        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                result = DBProcessor.getValueFromDB(
                    "select * from ezetap_properties where type = 'INSTANT_SETTLEMENT' and prop_key = 'msfRateForInstantSettlement';")
                msf_per = float(result["prop_value"].iloc[0])
                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode": "CARD",
                                    "pmt_status": "AUTHORIZED",
                                    "pmt_state": "AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_card_bin": bin_no,
                                    "pmt_card_brand": "MASTER_CARD", "pmt_card_type": "CREDIT",
                                    "txn_type": "CHARGE", "acq_code": "IDFC", "pmt_gateway": "IDFC_FDC",
                                    "is_txn_amt": float(original_amount), "is_msf_percentage": msf_per,
                                    "is_settle_amt": (
                                                float(original_amount) - (float(original_amount) * ((msf_per) / 100))),
                                    "is_org_code": org_code, "is_acq_code": "IDFC", "is_resp_code": "NULL",
                                    "is_resp_desc": "TIMEOUT", "is_error_code": "NULL",
                                    "is_error_desc": "NULL", "is_inquiry_resp_code": "200",
                                    "is_inquiry_resp_desc": "FAILED",
                                    "is_inquiry_error_code": "ENQ007",
                                    "is_inquiry_error_rsn": "Sorry!! No Matching Information found for the given input values", "is_settle_status": "IS_FAILED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '" + txnid + "';"
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

                query_is_txn_details = "select  * from instant_settlement_details where id = '" + txnid + "';"
                result_is_txn_details = DBProcessor.getValueFromDB(query_is_txn_details)
                result_is_txn_details = result_is_txn_details.replace(np.nan, 'NULL', regex=True)
                logger.debug(f"Query result: {result_is_txn_details}")

                is_txn_amt = float(result_is_txn_details["transaction_amount"].iloc[0])
                is_msf_percentage = result_is_txn_details["msf_percentage"].iloc[0]
                is_settle_amt = result_is_txn_details["settlement_amount"].iloc[0]
                is_org_code = result_is_txn_details["org_code"].iloc[0]
                is_acq_code = result_is_txn_details["acquirer_code"].iloc[0]
                is_resp_code = result_is_txn_details["response_code"].iloc[0]
                is_resp_desc = result_is_txn_details["response_description"].iloc[0]
                is_error_code = result_is_txn_details["error_code"].iloc[0]
                is_error_desc = result_is_txn_details["error_description"].iloc[0]
                is_inquiry_resp_code = result_is_txn_details["inquiry_resp_code"].iloc[0]
                is_inquiry_resp_desc = result_is_txn_details["inquiry_resp_description"].iloc[0]
                is_inquiry_error_code = result_is_txn_details["inquiry_error_cd"].iloc[0]
                is_inquiry_error_rsn = result_is_txn_details["inquiry_error_rsn"].iloc[0]
                is_settle_status = result_is_txn_details["settlement_status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode": pmt_mode,
                                  "pmt_status": pmt_status,
                                  "pmt_state": pmt_state, "settle_status": settle_status,
                                  "pmt_card_bin": pmt_card_bin,
                                  "pmt_card_brand": pmt_card_brand, "pmt_card_type": pmt_card_type,
                                  "txn_type": txn_type, "acq_code": acq_code, "pmt_gateway": pmt_gateway,
                                  "is_txn_amt": is_txn_amt, "is_msf_percentage": is_msf_percentage,
                                  "is_settle_amt": is_settle_amt,
                                  "is_org_code": is_org_code, "is_acq_code": is_acq_code, "is_resp_code": is_resp_code,
                                  "is_resp_desc": is_resp_desc, "is_error_code": is_error_code,
                                  "is_error_desc": is_error_desc, "is_inquiry_resp_code": is_inquiry_resp_code,
                                  "is_inquiry_resp_desc": is_inquiry_resp_desc,
                                  "is_inquiry_error_code": is_inquiry_error_code,
                                  "is_inquiry_error_rsn": is_inquiry_error_rsn, "is_settle_status": is_settle_status
                                  }
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
def test_d100_d101_067():
    """
        Sub Feature Code: NonUI_Common_IDFC_Card_Failed_Inquiry_Instant_Settlement_EMVCTLS_CREDIT_RUPAY
        Sub Feature Description: API that performs failed inquiry on IS settlement when IS call is Timeout for CTLS RUPAY CREDIT card via IDFC_FDC
        TC naming code description:
        d100: Dev Projects
        d101: IDFC Instant Settlement
        067: TC067
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {portal_cred}")
        super_username = portal_cred['Username']
        super_password = portal_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_org_settings_default(org_code=org_code, portal_un=super_username,
                                                       portal_pw=super_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        card_processor.update_invalid_merchant_account_details(org_code=org_code)
        card_processor.update_idfc_timeout_properties('10000')
        card_processor.update_idfc_paymentApi_read_timeout('1')
        card_processor.update_idfc_paymentApi_write_timeout('1')

        query_url = "select prop_value from ezetap_properties where prop_key = 'instantSettlementInquiryApiUrl';"
        logger.debug(f"Query to fetch payment inquiry url from the DB : {query}")
        result = DBProcessor.getValueFromDB(query_url)
        url = str(result['prop_value'].values[0])
        logger.debug(f"Query result, url : {url}")
        if url.__contains__('castlemock'):
            card_processor.update_instant_settle_clientcode('EZETAP1')
        else:
            card_processor.update_instant_settle_clientcode('EZETAP')
        api_details = DBProcessor.get_api_details('DB Refresh',
                                                  request_body={
                                                      "username": super_username,
                                                      "password": super_password,
                                                  })

        response = APIProcessor.send_request(api_details)
        logger.info(f"response of DB refresh: {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=True,
                                                   config_log=False, closedloop_log=False, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("IDFC_EMVCTLS_CREDIT_RUPAY")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="IDFC",
                                                              payment_gateway="IDFC_FDC"),
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            #
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response received from card payment is {response}")
            card_payment_success = response['success']
            time.sleep(10)
            if card_payment_success == True:
                txn_id = response['txnId']
                api_details = DBProcessor.get_api_details('paymentInquiry',
                                                          request_body={"username": super_username,
                                                                        "password": super_password,
                                                                        "txnId": txn_id,
                                                                        })
                paymentinquiry_response = APIProcessor.send_request(api_details)
                logger.info(f"Response received from payment Inquiry for {txn_id} is {paymentinquiry_response}")
            else:
                logger.error("Card payment Failed")

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
                expectedAPIValues = {"success": True, "txn_amt": float(original_amount), "pmt_mode": "CARD",
                                     "pmt_status": "AUTHORIZED",
                                     "pmt_state": "AUTHORIZED", "settle_status": "PENDING",
                                     "pmt_card_bin": bin_no,
                                     "pmt_card_brand": "RUPAY", "pmt_card_type": "CREDIT", "card_txn_type": "CTLS",
                                     "txn_type": "CHARGE", "acq_code": "IDFC", "voidable": False, "refundable": False}

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                amount = float(response['amount'])
                txnid = response['txnId']
                payment_mode = response['paymentMode']
                payment_status = response['status']
                payment_state = response['states'][0]
                settlement_status = response['settlementStatus']
                payment_card_bin = response['paymentCardBin']
                payment_card_brand = response['paymentCardBrand']
                payment_card_type = response['paymentCardType']
                card_txn_type = response['cardTxnTypeDesc']
                txn_type = response['txnType']
                acq_code = response['acquirerCode']
                voidable = response['voidable']
                refundable = response['refundable']

                logger.info(
                    f"API Result: Fetch Response of Card Payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                actualAPIValues = {"success": card_payment_success, "txn_amt": amount, "pmt_mode": payment_mode,
                                   "pmt_status": payment_status,
                                   "pmt_state": payment_state, "settle_status": settlement_status,
                                   "pmt_card_bin": payment_card_bin,
                                   "pmt_card_brand": payment_card_brand, "pmt_card_type": payment_card_type,
                                   "card_txn_type": card_txn_type, "txn_type": txn_type, "acq_code": acq_code,
                                   "voidable": voidable, "refundable": refundable}
                logger.debug(f"actualAPIValues: {actualAPIValues}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
                logger.info(f"Completed API validation for the test case : {testcase_id}")

        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                result = DBProcessor.getValueFromDB(
                    "select * from ezetap_properties where type = 'INSTANT_SETTLEMENT' and prop_key = 'msfRateForInstantSettlement';")
                msf_per = float(result["prop_value"].iloc[0])
                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode": "CARD",
                                    "pmt_status": "AUTHORIZED",
                                    "pmt_state": "AUTHORIZED", "settle_status": "PENDING",
                                    "pmt_card_bin": bin_no,
                                    "pmt_card_brand": "RUPAY", "pmt_card_type": "CREDIT",
                                    "txn_type": "CHARGE", "acq_code": "IDFC", "pmt_gateway": "IDFC_FDC",
                                    "is_txn_amt": float(original_amount), "is_msf_percentage": msf_per,
                                    "is_settle_amt": (
                                                float(original_amount) - (float(original_amount) * ((msf_per) / 100))),
                                    "is_org_code": org_code, "is_acq_code": "IDFC", "is_resp_code": "NULL",
                                    "is_resp_desc": "TIMEOUT", "is_error_code": "NULL",
                                    "is_error_desc": "NULL", "is_inquiry_resp_code": "200",
                                    "is_inquiry_resp_desc": "FAILED",
                                    "is_inquiry_error_code": "ENQ007",
                                    "is_inquiry_error_rsn": "Sorry!! No Matching Information found for the given input values", "is_settle_status": "IS_FAILED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select amount, payment_mode, settlement_status, status, state, payment_card_bin, payment_card_brand, payment_card_type, payment_gateway, txn_type, acquirer_code from txn where id = '" + txnid + "';"
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

                query_is_txn_details = "select  * from instant_settlement_details where id = '" + txnid + "';"
                result_is_txn_details = DBProcessor.getValueFromDB(query_is_txn_details)
                result_is_txn_details = result_is_txn_details.replace(np.nan, 'NULL', regex=True)
                logger.debug(f"Query result: {result_is_txn_details}")

                is_txn_amt = float(result_is_txn_details["transaction_amount"].iloc[0])
                is_msf_percentage = result_is_txn_details["msf_percentage"].iloc[0]
                is_settle_amt = result_is_txn_details["settlement_amount"].iloc[0]
                is_org_code = result_is_txn_details["org_code"].iloc[0]
                is_acq_code = result_is_txn_details["acquirer_code"].iloc[0]
                is_resp_code = result_is_txn_details["response_code"].iloc[0]
                is_resp_desc = result_is_txn_details["response_description"].iloc[0]
                is_error_code = result_is_txn_details["error_code"].iloc[0]
                is_error_desc = result_is_txn_details["error_description"].iloc[0]
                is_inquiry_resp_code = result_is_txn_details["inquiry_resp_code"].iloc[0]
                is_inquiry_resp_desc = result_is_txn_details["inquiry_resp_description"].iloc[0]
                is_inquiry_error_code = result_is_txn_details["inquiry_error_cd"].iloc[0]
                is_inquiry_error_rsn = result_is_txn_details["inquiry_error_rsn"].iloc[0]
                is_settle_status = result_is_txn_details["settlement_status"].iloc[0]

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode": pmt_mode,
                                  "pmt_status": pmt_status,
                                  "pmt_state": pmt_state, "settle_status": settle_status,
                                  "pmt_card_bin": pmt_card_bin,
                                  "pmt_card_brand": pmt_card_brand, "pmt_card_type": pmt_card_type,
                                  "txn_type": txn_type, "acq_code": acq_code, "pmt_gateway": pmt_gateway,
                                  "is_txn_amt": is_txn_amt, "is_msf_percentage": is_msf_percentage,
                                  "is_settle_amt": is_settle_amt,
                                  "is_org_code": is_org_code, "is_acq_code": is_acq_code, "is_resp_code": is_resp_code,
                                  "is_resp_desc": is_resp_desc, "is_error_code": is_error_code,
                                  "is_error_desc": is_error_desc, "is_inquiry_resp_code": is_inquiry_resp_code,
                                  "is_inquiry_resp_desc": is_inquiry_resp_desc,
                                  "is_inquiry_error_code": is_inquiry_error_code,
                                  "is_inquiry_error_rsn": is_inquiry_error_rsn, "is_settle_status": is_settle_status
                                  }
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
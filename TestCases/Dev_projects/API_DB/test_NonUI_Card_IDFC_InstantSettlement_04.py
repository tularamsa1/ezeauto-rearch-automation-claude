import time

import pytest
import random
import sys
from Configuration import Configuration
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
def test_idfc_settlement_19():
    """
        Sub Feature Code: NonUI_Common_IDFC_Card_InstantSettlement_for_failed_txn
        Sub Feature Description: API that should not perform IDFC instant settlement for failed txn via IDFC_FDC
        TC naming code description:
        100: Payment Method
        104: CARD
        091: TC091
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        card_processor.update_valid_merchant_account_details(org_code=org_code)

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = True, config_log= False,closedloop_log=False,q2_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            original_amount = random.randint(609,699)
            card_details = card_processor.get_card_details_from_excel("IDFC_EMVCTLS_DEBIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={"deviceSerial": merchant_creator.get_device_serial_of_merchant(org_code=org_code,acquisition="IDFC",payment_gateway="IDFC_FDC"),
                                                                    "username":app_username,
                                                                    "password":app_password,
                                                                    "amount": str(original_amount),
                                                                    "ezetapDeviceData":card_details['Ezetap Device Data'],
                                                                    "nonce":card_details['Nonce'],
                                                                    "externalRefNumber" : str(card_details['External Ref']) + str(random.randint(0,9))})

            #
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']

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

                    expectedAPIValues = {"success": False, "error_code": "EZETAP_1000002",
                                         "error_msg":"[IDFC_96] Payment Failed. Please try again. If the problem persists, please contact Ezetap Support.",
                                         "api_msg_title":"DECLINED","api_msg_txt":"IDFC_96: {4}. Payment Failed. Please try again. If the problem persists, please contact Ezetap Support. EZETAP_1000002",
                                         "pmt_status":"FAILED",
                                         "settle_status": "FAILED",
                                         "acq_code":"IDFC", "voidable":False, "refundable":False}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    error_code = response['errorCode']
                    error_msg = response['errorMessage']
                    api_msg_title = response['apiMessageTitle']
                    api_msg_txt = response['apiMessageText']
                    payment_status = response['status']
                    settlement_status = response['settlementStatus']
                    acq_code = response['acquirerCode']
                    voidable = response['voidable']
                    refundable = response['refundable']

                    logger.info(f"API Result: Fetch Response of Card Payment: {card_payment_success}, {error_code}, {error_msg}, {api_msg_title},{api_msg_txt},{payment_status},{settlement_status}")

                    actualAPIValues = {"success": card_payment_success, "error_code": error_code,
                                         "error_msg":error_msg,
                                         "api_msg_title":api_msg_title,"api_msg_txt":api_msg_txt,
                                         "pmt_status":payment_status,
                                         "settle_status": settlement_status,
                                         "acq_code":acq_code, "voidable":voidable, "refundable":refundable}
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
                # result = DBProcessor.getValueFromDB("select * from ezetap_properties where type = 'INSTANT_SETTLEMENT' and prop_key = 'msfRateForInstantSettlement';")
                # msf_per = float(result["prop_value"].iloc[0])
                expectedDBValues = {"txn_amt": float(original_amount), "pmt_mode":"CARD",
                                    "pmt_status":"FAILED",
                                    "pmt_state":"FAILED", "settle_status": "FAILED",
                                    "pmt_card_bin":bin_no,
                                    "pmt_card_brand":"VISA", "pmt_card_type":"DEBIT",
                                    "txn_type":"CHARGE", "acq_code":"IDFC", "pmt_gateway":"IDFC_FDC",
                                   }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select * from txn order by id desc limit 1;"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result: {result_txn}")

                txnid = result_txn["id"].iloc[0]
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

                if result_is_txn_details.empty:
                    logger.info("Card transaction has failed and hence IDFC instant settlement has not been called for this transaction")
                else:
                    logger.info(f"record in instant_settlement_details table", {result_is_txn_details})


                actualDBValues = {"txn_amt": txn_amt, "pmt_mode":pmt_mode,
                                    "pmt_status":pmt_status,
                                    "pmt_state":pmt_state, "settle_status": settle_status,
                                    "pmt_card_bin":pmt_card_bin,
                                    "pmt_card_brand":pmt_card_brand, "pmt_card_type":pmt_card_type,
                                    "txn_type":txn_type, "acq_code":acq_code, "pmt_gateway":pmt_gateway,
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




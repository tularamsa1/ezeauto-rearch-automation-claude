import json
import string
import sys
import random
import pytest
import requests
from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_d102_108_019():
    """
    Sub Feature Code: NonUI_Common_StaticQR_BQRV4_UPI_QR_Generation_Failed_With_VPA_Used_Before_ICICI_DIRECT
    Sub Feature Description: Performing failed UPI static QR generation after generating SQR for BQRV4 with same VPA via ICICI DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 108: UPI STATIC QR, 019: TC019
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
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI',bank_code_bqr='HDFC')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        tid = result['tid'].values[0]
        mid = result['mid'].values[0]

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username,portal_password,vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_hdfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrCodeType": "BHARAT",
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for first static_qrcode_generate_icici_direct for BQRV4 api is : {response}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_hdfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrCodeType": "UPI",
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for second static_qrcode_generate_icici_direct for UPI with same VPA is : {response}")

            api_success = response["success"]
            api_error_code = response["errorCode"]
            api_error_message = response["errorMessage"]
            api_real_code = response["realCode"]

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
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {"success": False,
                                       "error_code": "EZETAP_6100004",
                                       "error_message": "Static QR of a different type already exists for vpa : "+vpa,
                                       "realcode": "STATIC_QR_INTENT_EXISTS_WITH_DIFFERENT_TYPE"
                                       }

                actual_api_values = {"success": api_success,
                                     "error_code" : api_error_code,
                                     "error_message" : api_error_message,
                                     "realcode": api_real_code
                                    }
                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)

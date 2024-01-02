import json
import random
import string
import sys
import pytest
import requests
from Configuration import Configuration, testsuite_teardown, TestSuiteSetup
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_107_038():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_QR_Generation_Success_Via_Razorpay
    Sub Feature Description: Performing static QR generation success via Razorpay
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 038: TC038
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

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

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "publish_id": publish_id,
                    "org_code": org_code,
                    "config_id": upi_mc_id,
                    "vpa": vpa_new,
                    "user_mobile": mobile_number,
                    "user_name": app_username,
                    "mid": mid,
                    "tid": tid,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from staticqr_intent where config_id='{upi_mc_id}'"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                publish_id_db = result["publish_id"].values[0]
                org_code_db = result["org_code"].values[0]
                config_id_db = result["config_id"].values[0]
                vpa_db = result["vpa"].values[0]
                user_mobile_db = result["user_mobile"].values[0]
                username_db = result["user_name"].values[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                qr_type_db = result['qr_type'].values[0]
                intent_type_db = result['intent_type'].values[0]

                actual_db_values = {
                    "publish_id": publish_id_db,
                    "org_code": org_code_db,
                    "config_id": config_id_db,
                    "vpa": vpa_db,
                    "user_mobile": user_mobile_db,
                    "user_name": username_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "qr_type": qr_type_db,
                    "intent_type": intent_type_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_107_039():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_QR_Re_Generation_Via_Razorpay
    Sub Feature Description: Re-generate the static QR and verify the tables getting updated.
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 039: TC039
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

            api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                  "password": portal_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting precondition DB refresh is : {response}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa_new,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for regeneration of static_qrcode_generate_razorpay api is : {response}")
            regeneration_publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from regeneration is : {regeneration_publish_id}")

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

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "publish_id": publish_id,
                    "org_code": org_code,
                    "config_id": upi_mc_id,
                    "vpa": vpa_new,
                    "user_mobile": mobile_number,
                    "user_name": app_username,
                    "mid": mid,
                    "tid": tid,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR",
                    # "audit_publish_id": publish_id,
                    # "audit_org_code": org_code,
                    # "audit_qr_type": "UPI",
                    # "audit_intent_type": "STATIC_QR",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                # query = "select * from qrcode_audit where org_code='" + org_code + "'"
                # logger.debug(f"Query to fetch data from qrcode_audit table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # audit_publish_id_db = result["publish_id"].values[0]
                # audit_org_code_db = result["org_code"].values[0]
                # audit_qr_type_db = result['qr_type'].values[0]
                # audit_intent_type_db = result['intent_type'].values[0]

                # query = "select * from staticqr_intent where org_code='" + org_code + "'"
                query = f"select * from staticqr_intent where publish_id='{regeneration_publish_id}';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                publish_id_db = result["publish_id"].values[0]
                org_code_db = result["org_code"].values[0]
                config_id_db = result["config_id"].values[0]
                vpa_db = result["vpa"].values[0]
                user_mobile_db = result["user_mobile"].values[0]
                username_db = result["user_name"].values[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                qr_type_db = result['qr_type'].values[0]
                intent_type_db = result['intent_type'].values[0]

                actual_db_values = {
                    "publish_id": publish_id_db,
                    "org_code": org_code_db,
                    "config_id": config_id_db,
                    "vpa": vpa_db,
                    "user_mobile": user_mobile_db,
                    "user_name": username_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "qr_type": qr_type_db,
                    "intent_type": intent_type_db,
                    # "audit_publish_id": audit_publish_id_db,
                    # "audit_org_code": audit_org_code_db,
                    # "audit_qr_type": audit_qr_type_db,
                    # "audit_intent_type": audit_intent_type_db,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_107_040():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_QR_Generation_With_AppUser_Via_Razorpay
    Sub Feature Description: Performing static QR generation with app user instead of portal user via Razorpay
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 040: TC040
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": app_username,
                "password": app_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for static_qrcode_generate_razorpay api is : {response}")

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

        # -----------------------------------------Start of API Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "success": False,
                    "message": "You do not have permission to perform this operation.",
                    "realCode": "UNAUTHORIZED_OPERATION"
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                success_api = response['success']
                message_api = response['message']
                real_code_api = response['realCode']

                actual_api_values = {
                    "success": success_api,
                    "message": message_api,
                    "realCode": real_code_api
                }

                logger.debug(f"actual_api_values : {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_107_041():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_QR_Generation_Success_2_times_with_Diff_AppUsers_Via_Razorpay
    Sub Feature Description: Performing static QR generation 2 times with different app users of a merchant via Razorpay
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 041: TC041
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

            logger.debug(f"deleting data from qrcode_audit table for org_code : {org_code}")
            query = "delete from qrcode_audit where org_code ='" + str(org_code) + "'"
            result = DBProcessor.delete_value_from_db(query)
            logger.debug(f"Query result : {result}")

            api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                                  "password": portal_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for DB refresh is : {response}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for static_qrcode_generate_razorpay api is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"Value of publishId obtained from static qr generation for first user is :"
                         f" {generateqr_publish_id}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            query = f"select username from org_employee where org_code='{org_code}';"
            logger.debug(f"Query to fetch all user under the {org_code} org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            is_user_required = False
            user_token = ''
            for i in range(len(result)):
                if result['username'][i] == app_username:
                    is_user_required = True
                    logger.debug(f"user creation is required")
                    continue
                else:
                    is_user_required = False
                    user_token = result['username'][i]
                    logger.debug(f"user creation is not required")
                    break
            if is_user_required:
                user_token = str(random.randint(1000000000, 9999999999))
                name = "EzeAuto" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
                api_details = DBProcessor.get_api_details('createUser', request_body={
                    "mobileNumber": user_token,
                    "name": name,
                    "roles": [
                        "ROLE_CLADMIN", "ROLE_CLAGENTPORTAL", "ROLE_CLAGENTVOID",
                        "ROLE_CLAGENT", "ROLE_CLAGENT_REFUND", "ROLE_CLREFUND"
                    ],
                    "userPassword": "A123456",
                    "userToken": user_token,
                    "username": portal_username,
                    "password": portal_password
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
                    api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                        "username": portal_username,
                        "password": portal_password,
                        "qrUserMobileNo": user_token,
                        "qrUserName": user_token,
                        "merchantVpa": vpa_new,
                    })
                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")
                    regenerated_publish_id = response["publishId"]
                    logger.debug(f"fetching regenerated publish_id from api response is : {regenerated_publish_id}")

            else:
                api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                    "username": portal_username,
                    "password": portal_password,
                    "qrUserMobileNo": user_token,
                    "qrUserName": user_token,
                    "merchantVpa": vpa_new,
                })
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")
                regenerated_publish_id = response["publishId"]
                logger.debug(f"fetching regenerated publish_id from api response is : {regenerated_publish_id}")

                query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID';"
                logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
                result = DBProcessor.getValueFromDB(query)
                vpa_new_2 = result['vpa'].values[0]
                logger.info(f"fetched vpa_new_2 is : {vpa_new_2}")

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

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "publish_id": generateqr_publish_id,
                    "org_code": org_code,
                    "config_id": upi_mc_id,
                    "vpa": vpa_new,
                    "user_mobile": str(app_username),
                    "user_name": str(app_username),
                    "mid": mid,
                    "tid": tid,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR",
                    "publish_id_2": regenerated_publish_id,
                    "org_code_2": org_code,
                    "config_id_2": upi_mc_id,
                    "vpa_2": vpa_new_2,
                    "user_mobile_2": str(user_token),
                    "user_name_2": str(user_token),
                    "mid_2": mid,
                    "tid_2": tid,
                    "qr_type_2": "UPI",
                    "intent_type_2": "STATIC_QR",
                    # "audit_publish_id": publish_id,
                    # "audit_org_code": org_code,
                    # "audit_qr_type": "UPI",
                    # "audit_intent_type": "STATIC_QR",
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                # query = "select * from qrcode_audit where org_code='" + org_code + "'"
                # logger.debug(f"Query to fetch data from qrcode_audit table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # audit_publish_id_db = result["publish_id"].values[0]
                # audit_org_code_db = result["org_code"].values[0]
                # audit_qr_type_db = result['qr_type'].values[0]
                # audit_intent_type_db = result['intent_type'].values[0]

                query = "select * from staticqr_intent where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                publish_id_db = result["publish_id"].values[0]
                org_code_db = result["org_code"].values[0]
                config_id_db = result["config_id"].values[0]
                vpa_db = result["vpa"].values[0]
                user_mobile_db = result["user_mobile"].values[0]
                username_db = result["user_name"].values[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                qr_type_db = result['qr_type'].values[0]
                intent_type_db = result['intent_type'].values[0]

                query = "select * from staticqr_intent where publish_id='" + str(regenerated_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table for regeneration: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of staticqr_intent table : {result}")
                staticqr_intent_publish_id_2 = result["publish_id"].values[0]
                logger.debug(
                    f"Fetching publish_id from staticqr_intent table for regeneration: {staticqr_intent_publish_id_2}")
                staticqr_intent_org_code_2 = result["org_code"].values[0]
                logger.debug(
                    f"Fetching org_code from staticqr_intent table for regeneration: {staticqr_intent_org_code_2}")
                staticqr_intent_vpa_2 = result["vpa"].values[0]
                logger.debug(f"Fetching vpa from staticqr_intent table for regeneration: {staticqr_intent_vpa_2}")
                staticqr_intent_user_mobile_2 = result["user_mobile"].values[0]
                logger.debug(
                    f"Fetching user_mobile from staticqr_intent table for regeneration: {staticqr_intent_user_mobile_2}")
                staticqr_intent_user_name_2 = result["user_name"].values[0]
                logger.debug(
                    f"Fetching user_name from staticqr_intent table for regeneration: {staticqr_intent_user_name_2}")
                staticqr_intent_mid_2 = result["mid"].values[0]
                logger.debug(f"Fetching mid from staticqr_intent table for regeneration: {staticqr_intent_mid_2}")
                staticqr_intent_tid_2 = result["tid"].values[0]
                logger.debug(f"Fetching tid from staticqr_intent table for regeneration: {staticqr_intent_tid_2}")
                staticqr_intent_qrtype_2 = result["qr_type"].values[0]
                logger.debug(
                    f"Fetching qr_type from staticqr_intent table for regeneration: {staticqr_intent_qrtype_2}")
                staticqr_intent_intent_type_2 = result["intent_type"].values[0]
                logger.debug(
                    f"Fetching intent_type from staticqr_intent table for regeneration: {staticqr_intent_intent_type_2}")
                config_id_db_2 = result["config_id"].values[0]
                logger.info(f"regenerated config id : {config_id_db_2}")

                actual_db_values = {
                    "publish_id": publish_id_db,
                    "org_code": org_code_db,
                    "config_id": config_id_db,
                    "vpa": vpa_db,
                    "user_mobile": user_mobile_db,
                    "user_name": username_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "qr_type": qr_type_db,
                    "intent_type": intent_type_db,
                    "publish_id_2": staticqr_intent_publish_id_2,
                    "org_code_2": staticqr_intent_org_code_2,
                    "config_id_2": config_id_db_2,
                    "vpa_2": staticqr_intent_vpa_2,
                    "mid_2": staticqr_intent_mid_2,
                    "tid_2": staticqr_intent_tid_2,
                    "user_mobile_2": staticqr_intent_user_mobile_2,
                    "user_name_2": staticqr_intent_user_name_2,
                    "qr_type_2": staticqr_intent_qrtype_2,
                    "intent_type_2": staticqr_intent_intent_type_2,
                    # "audit_publish_id": audit_publish_id_db,
                    # "audit_org_code": audit_org_code_db,
                    # "audit_qr_type": audit_qr_type_db,
                    # "audit_intent_type": audit_intent_type_db,
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_107_045():
    """
    Sub Feature Code: UI_Common_PM_UPI_StaticQR_Generation_Failure_With_Invalid_VPA_Via_Razorpay
    Sub Feature Description: Verification of UPI Static qr generation failure for invalid VPA via Razorpay
    TC naming code description: 100: Payment method, 107: UPI Static QR, 045: TC045
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

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username, portal_password, vpa)
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # generating random vpa
            dummy_vpa = str(random.randint(11111111, 99999999)) + "@upi"
            logger.debug(f"generated random vpa is : {dummy_vpa}")
            logger.info("generating upi static qr via RAZORPAY_PSP")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": dummy_vpa,
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the static_qrcode_generate_razorpay api is : {response}")
            is_response = response['success']
            logger.debug(f"is_response is : {is_response}")
            error_message = response['errorMessage']
            logger.debug(f"error_message is : {error_message}")

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

        # -----------------------------------------Start of API Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")

            expected_error_message = "UPI_MERCHANT_CONFIG_NOT_FOUND"
            expected_success = False

            try:
                expected_api_values = {
                    "success": expected_success,
                    "errorMessage": expected_error_message
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": is_response,
                    "errorMessage": error_message
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


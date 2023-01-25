import random
import string
import sys
from datetime import datetime

import pytest

from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_109_008():
    """
    Sub Feature Code: UI_Common_PM_Initiate_UPI_QR_via_API_with_Inactive_Label_MultiAcc
    Sub Feature Description: Multi Account - Make label as Inactive then try to initiate QR
    TC naming code description: 100->Payment Method, 110-> MultiAcc_UPI, 008-> TC08
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}') "
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")
        acc_label_id = str(result['acc_label_id'].values[0])
        logger.debug(f"fetched acc_label_id : {acc_label_id}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = f"update label set status='INACTIVE' where id='{acc_label_id}';"
        DBProcessor.setValueToDB(query)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username, "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('upiqrGenerate_multiAcc', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id),
                "accountLabel": str(account_label_name)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upiqrGenerate_multiAcc : {response}")

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
                expected_api_values = {
                    "message": f"Inactive Account Label: {account_label_name}",
                    "errorMessage": f"Inactive Account Label: {account_label_name}",
                    "realCode": "ACCOUNT_LABEL_INACTIVE",
                    "apiMessage": f"Inactive Account Label: {account_label_name}",
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                message = response["message"]
                error_message = response["errorMessage"]
                real_code = response["realCode"]
                api_message = response["apiMessage"]

                actual_api_values = {
                    "message": message,
                    "errorMessage": error_message,
                    "realCode": real_code,
                    "apiMessage": api_message,
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
        query = f"update label set status='ACTIVE' where id='{acc_label_id}';"
        DBProcessor.setValueToDB(query)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username, "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_109_009():
    """
    Sub Feature Code: UI_Common_PM_Initiate_UPI_QR_via_API_with_Invalid_Label_MultiAcc
    Sub Feature Description: Multi Account - Initiate QR with invalid label
    TC naming code description: 100->Payment Method, 110-> MultiAcc_UPI, 009-> TC09
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        logger.debug(f"fetched account_label_name : {account_label_name}")
        invalid_account_label_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")
        acc_label_id = str(result['acc_label_id'].values[0])
        logger.debug(f"fetched acc_label_id : {acc_label_id}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('upiqrGenerate_multiAcc', request_body={
                "username": app_username, "password": app_password, "amount": str(amount), "orderNumber": str(order_id),
                "accountLabel": str(invalid_account_label_name)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for the upiqrGenerate_multiAcc : {response}")

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
                expected_api_values = {
                    "message": f"Invalid Account Label: {invalid_account_label_name}",
                    "errorMessage": f"Invalid Account Label: {invalid_account_label_name}",
                    "realCode": "ACCOUNT_LABEL_INVALID",
                    "apiMessage": f"Invalid Account Label: {invalid_account_label_name}",
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                message = response["message"]
                error_message = response["errorMessage"]
                real_code = response["realCode"]
                api_message = response["apiMessage"]

                actual_api_values = {
                    "message": message,
                    "errorMessage": error_message,
                    "realCode": real_code,
                    "apiMessage": api_message,
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

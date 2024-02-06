import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_314():
    """
     Sub Feature Code: UI_Common_PM_RP_Settings_Enable_Link_Shortening
     Sub Feature Description: Enable CNP Link Shortening from the remote pay settings
     TC naming code description: 100: Payment Method, 103: RemotePay, 314: TC314
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='enableCNPLinkShortening'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, " \
                    f"entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', " \
                    f"now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', " \
                    f"'enableCNPLinkShortening', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name" \
                    f"='enableCNPLinkShortening';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")

            payment_link = response.get('paymentLink')
            logger.debug(f"From response fetch paymentLink : {payment_link}")
            short_payment_link = response.get('shortPaymentLink')
            logger.debug(f"From response fetch shortPaymentLink : {short_payment_link}")

            if len(payment_link) > 0:
                payment_link_generate = True
            else:
                payment_link_generate = False

            if len(short_payment_link) > 0:
                short_payment_link_generate = True
            else:
                short_payment_link_generate = False
            # ------------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "payment_link_generate": True,
                    "short_payment_link_generate": True
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "payment_link_generate": payment_link_generate,
                    "short_payment_link_generate": short_payment_link_generate
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_315():
    """
     Sub Feature Code: UI_Common_PM_RP_Settings_Disable_Link_Shortening
     Sub Feature Description: Disable CNP Link Shortening from the remote pay settings
     TC naming code description: 100: Payment Method, 103: RemotePay, 315: TC315
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='enableCNPLinkShortening'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'enableCNPLinkShortening', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='enableCNPLinkShortening';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")

            payment_link = response.get('paymentLink')
            logger.debug(f"From response fetch paymentLink : {payment_link}")
            short_payment_link = response.get('shortPaymentLink')
            logger.debug(f"From response fetch shortPaymentLink : {short_payment_link}")

            if len(payment_link) > 0:
                payment_link_generate = True
            else:
                payment_link_generate = False

            try:
                if len(short_payment_link) > 0:
                    short_payment_link_generate = True
            except Exception as e:
                logger.exception(f"payment link generation failed due to exception : {e}")
                short_payment_link_generate = False
                # ------------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "payment_link_generate": True,
                    "short_payment_link_generate": False
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "payment_link_generate": payment_link_generate,
                    "short_payment_link_generate": short_payment_link_generate
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
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
        try:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='enableCNPLinkShortening';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
            refresh_db()
            logger.debug(f"Database refreshed")
        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)
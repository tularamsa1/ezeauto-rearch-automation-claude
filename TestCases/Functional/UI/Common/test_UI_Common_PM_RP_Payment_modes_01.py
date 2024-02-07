import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_301():
    """
    Sub Feature Code: UI_Common_PM_RP_Payment_modes_Enabled_Org_and_PG_level
    Sub Feature Description: All payment modes (CC, DC, Net Banking) should be visible on the browser when enabled at org settings and PG settings.
    TC naming code description: 100: Payment Method, 103: RemotePay, 301: TC301
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update merchant_pg_config set status='ACTIVE' where org_code='{org_code}';"
        logger.debug(f"Query to update merchant_pg_config table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"Query result from merchant_pg_config table : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name" \
                    f"='nbEnabledInCnp'; "
            logger.debug(f"Query to update remotepay_setting table for net banking: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the net banking details : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for credit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for credit card : {result}")
        logger.debug(f"result length of credit card: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the credit card details : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for debit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for debit card : {result}")
        logger.debug(f"result length of debit card : {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the debit card  details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the debit card details : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False)

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
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"Initiating the remote pay link : {response}")
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)
            try:
                creditcard = remote_pay_txn.fetch_credit_card_payment_mode_text()
                logger.info(f"Fetching credit card value : {creditcard}")
                debitcard = remote_pay_txn.fetch_debit_card_payment_mode_text()
                logger.info(f"Fetching credit card value : {debitcard}")
                netbanking = remote_pay_txn.fetch_net_banking_payment_mode_text()
                logger.info(f"Fetching netbanking value : {netbanking}")

                if creditcard == "Credit Card" and debitcard == "Debit Card" and netbanking == "Net Banking":
                    logger.info(f"Credit, Debit and Netbanking payment modes are enabled ")

            except Exception as e:
                logger.exception(f"Credit, Debit and Netbanking payment modes are not enabled due to exception : {e}")
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_302():
    """
    Sub Feature Code: UI_Common_PM_RP_Payment_modes_Enabled_Org_level
    Sub Feature Description: No Payment modes are visible when payment modes are enabled at org Settings and disabled at PG settings
    TC naming code description: 100: Payment Method, 103: RemotePay, 302: TC302
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update merchant_pg_config set status='INACTIVE' where org_code='{org_code}';"
        logger.debug(f"Query to update merchant_pg_config table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result from merchant_pg_config table : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for net banking: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the net banking details : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for credit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for credit card : {result}")
        logger.debug(f"result length of credit card: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"

            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the credit card details : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for debit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for debit card : {result}")
        logger.debug(f"result length of debit card : {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the debit card  details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the debit card details : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"Initiating the remote pay link : {response}")

            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)
            payment_modes = ['Credit Card', 'Debit Card', 'Net Banking']
            try:
                list_of_payment_mode = [f"{mode} Element not visible" for mode in payment_modes if
                                        remote_pay_txn.is_credit_debit_netbanking_and_upi_visible(mode) == None]
                logger.debug(f" list of payment mode {list_of_payment_mode}")
                assert list_of_payment_mode[0] == "Credit Card Element not visible", "Credit Card Element is visible"
                logger.info(f"Credit Card payment mode is not enabled")
                assert list_of_payment_mode[1] == "Debit Card Element not visible", "Debit Card Element is visible"
                logger.info(f"Debit Card payment mode is not enabled")
                assert list_of_payment_mode[2] == "Net Banking Element not visible", "Net banking Element is visible"
                logger.info(f"Net banking payment modes is not enabled")

            except Exception as e:
                logger.exception(f"Credit, Debit and Netbanking payment modes are enabled due to exception: {e}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
    finally:
        try:
            query = f"update merchant_pg_config set status='ACTIVE' where org_code='{org_code}';"
            logger.debug(f"Query to update merchant_pg_config table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Reverting back credit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back credit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Reverting back debit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back debit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Reverting back netbanking details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back netbanking details in remotepay_setting table : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_303():
    """
     Sub Feature Code: UI_Common_PM_RP_Payment_mode_Cards_Enabled_PG_and_Org_level
     Sub Feature Description: All payment modes (CC, DC, Net Banking) are enabled at org settings and only cards payment mode enabled at PG settings level
     TC naming code description: 100: Payment Method, 103: 103: RemotePay, 303: TC303
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

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='upiEnabledInCNP';"
        logger.debug(f"Query to update remotepay_setting table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")

        query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='upiCollectEnableOnAndroidDevice';"
        logger.debug(f"Query to update remotepay_setting table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")

        query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='upiCollectEnableOnNonAndroidDevices';"
        logger.debug(f"Query to update remotepay_setting table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")

        query = f"update merchant_pg_config set status='INACTIVE' where org_code='{org_code}' and payment_gateway='TPSL';"
        logger.debug(f"Query to update merchant_pg_config table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True)
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
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response for Remotepay_Initiate api is: {response}")
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)

            check_credit_card_visible_txt = str(remote_pay_txn.fetch_credit_card_payment_mode_text())
            logger.info(f"Your expected credit card message is:  {check_credit_card_visible_txt}")
            check_debit_card_visible_txt = str(remote_pay_txn.fetch_debit_card_payment_mode_text())
            logger.info(f"Your expected debit card message is:  {check_credit_card_visible_txt}")

            if check_credit_card_visible_txt == "Credit Card":
                pass
            else:
                raise Exception("Credit Card payment mode is not visible")

            if check_debit_card_visible_txt == "Debit Card":
                pass
            else:
                raise Exception("Debit Card payment mode is not visible")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
    finally:
        try:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiEnabledInCNP';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiCollectEnableOnAndroidDevice';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiCollectEnableOnNonAndroidDevices';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update merchant_pg_config set status='ACTIVE' where org_code='{org_code}' and payment_gateway='TPSL';"
            logger.debug(f"Query to update merchant_pg_config table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_304():
    """
    Sub Feature Code: UI_Common_PM_RP_Payment_mode_Cards_Enabled_Link_Generation_success
    Sub Feature Description: Card Payment mode is enabled to validate the generation of the payment link
    TC naming code description: 100: Payment Method, 103: RemotePay, 304: TC304
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbaking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbaking : {result}")
        logger.debug(f"result length of netbanking : {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), " \
                    f"'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for net banking: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the net banking details : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for credit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"Query result from remotepay_setting table for credit card : {query}")
        logger.debug(f"result length of credit card: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"

            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the credit card details : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for debit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for debit card : {result}")
        logger.debug(f"result length of debit card : {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'false');"

            logger.debug(f"Query to insert data into remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the debit card  details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the debit card details : {result}")

        query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='upiCollectEnableOnAndroidDevice';"
        logger.debug(f"Query to update remotepay_setting table for upi enabled in cnp : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result after updating the upi enabled in cnp : {result}")

        query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='upiCollectEnableOnNonAndroidDevices';"
        logger.debug(f"Query to update remotepay_setting table for upi collect enable on nonandroid device : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result after updating the upi collect enable on nonandroid device  : {result}")

        query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='upiEnabledInCNP';"
        logger.debug(f"Query to update remotepay_setting table for upi enable in cnp : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result after updating the upi enable in cnp : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Reverting back credit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back credit card details in remotepay_setting table : {result}")
            refresh_db()
            logger.debug(f"DB refresh after reverting back credit card details in remotepay_setting table")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"Initiating the remote pay link : {response}")

            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)
            try:
                creditcard = remote_pay_txn.fetch_credit_card_payment_mode_text()
                logger.info(f"Fetching credit card value : {creditcard}")
                if creditcard == "Credit Card":
                    logger.info(f"Credit payment modes are enabled ")
            except Exception as e:
                logger.exception(f"Credit card payment mode is not enabled due to exception : {e}")
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
    finally:
        try:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Reverting back netbanking details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back netbanking details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Reverting back debit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back debit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiCollectEnableOnAndroidDevice';"
            logger.debug(f"Reverting back upi collect enable on android device details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back upi collect enable on android device details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiCollectEnableOnNonAndroidDevices';"
            logger.debug(f"Reverting back upi collect enable on nonandroid device details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back upi collect enable on nonandroid device details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiEnabledInCNP';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_305():
    """
    Sub Feature Code: UI_Common_PM_RP_Payment_modes_Disabled_Validate_Error_Message
    Sub Feature Description: None of the payment modes are enabled for remote pay, error message should be displayed on Browser flow
    TC naming code description: 100: Payment Method, 103: RemotePay, 305: TC305
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching orgcode value from the org_employee table {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for netbanking : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for netbanking : {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for net banking: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the net banking details : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for credit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for credit card : {query}")
        logger.debug(f"result length of credit card: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, " \
                    f"entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"

            logger.debug(f"Query to insert data into remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the credit card details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for credit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the credit card details : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table for debit card : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from remotepay_setting table for debit card ")
        logger.debug(f"result length of debit card : {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component," \
                    f" entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now()," \
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the debit card  details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the debit card details : {result}")

        query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='upiEnabledInCNP';"
        logger.debug(f"Query to update remotepay_setting table for upi enabled in cnp : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result after updating the upi enabled in cnp : {result}")

        query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='upiCollectEnableOnAndroidDevice';"
        logger.debug(f"Query to update remotepay_setting table for upi collect enable on android device : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result after updating the upi collect enable on android device  : {result}")

        query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='upiCollectEnableOnNonAndroidDevices';"
        logger.debug(f"Query to update remotepay_setting table for upi collect enable on nonandroid device : {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result after updating the upi collect enable on nonandroid device  : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False)

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
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response of remote_pay_initiate api : {response}")
            success_api = response['success']
            logger.info(f"Value of success obtained from remotepay initiate api : {success_api}")
            message_api = response['message']
            logger.info(f"Value of message obtained from remotepay initiate api : {message_api}")
            error_code_api = response['errorCode']
            logger.info(f"Value of errorCode obtained from remotepay initiate api : {error_code_api}")
            error_message_api = response['errorMessage']
            logger.info(f"Value of errorMessage obtained from remotepay initiate api : {error_message_api}")
            real_code_api = response['realCode']
            logger.info(f"Value of realCode obtained from remotepay initiate api : {real_code_api}")
            username_api = response['username']
            logger.info(f"Value of username obtained from remotepay initiate api : {username_api}")
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "success": False,
                    "message": "No active payment method found for null.Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications.",
                    "error_code": "EZETAP_4500014",
                    "error_message": "No active payment method found for null.Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications.",
                    "real_code": "BROWSERPAY_PAYMENT_OPTIONS_NOT_ENABLED",
                    "username": app_username
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": success_api,
                    "message": message_api,
                    "error_code": error_code_api,
                    "error_message": error_message_api,
                    "real_code": real_code_api,
                    "username": username_api
                }
                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
    finally:
        try:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Reverting back netbanking details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back netbanking details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Reverting back credit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back credit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Reverting back debit card details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back debit card details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiEnabledInCNP';"
            logger.debug(f"Reverting back upi enabled in cnp details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back upi enabled in cnp details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiCollectEnableOnAndroidDevice';"
            logger.debug(f"Reverting back upi collect enable on android device details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back upi collect enable on android device details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiCollectEnableOnNonAndroidDevices';"
            logger.debug(f"Reverting back upi collect enable on nonandroid device details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back upi collect enable on nonandroid device details in remotepay_setting table : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)

import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import ResourceAssigner, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_306():
    """
     Sub Feature Code: UI_Common_PM_RP_Payment_modes_Disabled_Validate_Error_Message
     Sub Feature Description: Disable the payment modes after the remote pay link is generated and validate the error message
     TC naming code description: 100: Payment Method, 103: CNP, 306: TC306
    """
    expected_message = "No active payment method found for {0}.Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications."
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']

            query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='nbEnabledInCnp'"
            logger.debug(f"Query to fetch data from remotepay_setting table for net banking : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from remotepay_setting table for net banking : {result}")
            logger.debug(f"result length of net banking :  {len(result)}")

            if (len(result)) < 1:
                query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, " \
                        f"entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', " \
                        f"'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
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
                query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, " \
                        f"component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap'," \
                        f" now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"
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
                query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, " \
                        f"entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), " \
                        f"'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'false');"
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
            logger.debug(f"Database refreshed")

            try:
                ui_browser.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(ui_browser)
                warning_msg = str(remote_pay_txn.fetch_warning_msg_txt())
                logger.info(f"Your expected message is:  {expected_message}")
                logger.info(f"warning message is:  {warning_msg}")
                if warning_msg == expected_message:
                    pass
                else:
                    raise Exception("Failed Message is not matching.")
            except Exception as e:
                logger.exception(f" {e}")
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

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiEnabledInCNP';"
            logger.debug(f"Reverting back upi enabled in cnp details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back upi enabled in cnp details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='upiCollectEnableOnAndroidDevice';"
            logger.debug(f"Reverting back upi collect enable on android device details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back upi collect enable on android device details in remotepay_setting table : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name" \
                    f"='upiCollectEnableOnNonAndroidDevices'; "
            logger.debug(f"Reverting back upi collect enable on nonandroid device details in remotepay_setting table : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"Query result after reverting back upi collect enable on nonandroid device details in remotepay_setting table : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_307():
    """
     Sub Feature Code: UI_Common_PM_RP_Payment_Mode_UPI_Enabled_Cancel_Payment_Navigation
     Sub Feature Description: UPI is enabled, user clicks on CANCEL PAYMENT button then screen should navigate back to UPI option remote payment page
     TC naming code description: 100: Payment Method, 103: RemotePay, 522: TC307
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
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

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
            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)
            remote_pay_txn.clickOnRemotePayUPI()
            remote_pay_txn.clickOnRemotePayLaunchUPI()
            remote_pay_txn.clickOnRemotePayCancelUPI()
            remote_pay_txn.clickOnRemotePayProceed()

            check_upi_visible_txt = str(remote_pay_txn.fetch_upi_payment_mode_text())
            logger.info(f"Your expected upi message is:  {check_upi_visible_txt}")
            if check_upi_visible_txt == "UPI":
                pass
            else:
                raise Exception("UPI payment mode is not visible")
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
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
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
def test_common_100_103_308():
    """
     Sub Feature Code: UI_Common_PM_RP_Payment_Modes_Enabled_After_Link_Generation
     Sub Feature Description: Enable all the payment modes after link creation, when user clicks on link, only the payment mode which was enabled before link creation should be viewed
     TC naming code description: 100: Payment Method, 103: RemotePay, 308: TC308
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
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
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
            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            payment_link_url = response['paymentLink']

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

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

            refresh_db()
            logger.debug(f"Database refreshed")

            ui_browser = TestSuiteSetup.initialize_ui_browser()
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)

            check_upi_visible_txt = str(remote_pay_txn.fetch_upi_payment_mode_text())
            logger.info(f"Your expected upi message is:  {check_upi_visible_txt}")
            check_credit_card_visible_txt = str(remote_pay_txn.fetch_credit_card_payment_mode_text())
            logger.info(f"Your expected credit card message is:  {check_credit_card_visible_txt}")
            check_debit_card_visible_txt = str(remote_pay_txn.fetch_debit_card_payment_mode_text())
            logger.info(f"Your expected debit card message is:  {check_debit_card_visible_txt}")
            check_net_banking_visible_txt = str(remote_pay_txn.fetch_net_banking_payment_mode_text())
            logger.info(f"Your expected net banking message is:  {check_net_banking_visible_txt}")

            assert check_upi_visible_txt == "UPI", "UPI payment mode is not visible"
            assert check_credit_card_visible_txt == "Credit Card", "Credit Card payment mode is not visible"
            assert check_debit_card_visible_txt == "Debit Card", "Debit Card payment mode is not visible"
            assert check_net_banking_visible_txt == "Net Banking", "Net Banking payment mode is not visible"
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
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

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

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_309():
    """
     Sub Feature Code: UI_Common_PM_RP_Payment_Modes_UPI_Enabled_Max_Attempts_Error_Validation
     Sub Feature Description: UPI is enabled, when user reaches max attempts of UPI payment, validate the error message
     TC naming code description: 100: Payment Method, 103: RemotePay, 309: TC309
    """
    expected_message = "Maximum number of attempts for this url exceeded. Please request for a new remote pay url."
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
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='ccEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'ccEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

        query = f"select * from remotepay_setting where org_code='{org_code}' and setting_name='dcEnabledInCnp'"
        logger.debug(f"Query to fetch data from remotepay_setting table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"fetch result: {result}")
        logger.debug(f"result length: {len(result)}")

        if (len(result)) < 1:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

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

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        query = f"select setting_value from remotepay_setting where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed'"
        logger.debug(f"Query to fetch data from the remotepay_setting table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from remotepay_setting table :{result}")
        max_pay_attempt = int(result['setting_value'].values[0])
        logger.debug(f"Fetching max pay attempt from the remotepay_setting table : {max_pay_attempt}")

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
            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)

            while max_pay_attempt >= 0:
                if max_pay_attempt == 0:
                    remote_pay_txn.clickOnRemotePayUPI()
                    remote_pay_txn.clickOnRemotePayLaunchUPI()
                    break
                remote_pay_txn.clickOnRemotePayUPI()
                remote_pay_txn.clickOnRemotePayLaunchUPI()
                remote_pay_txn.clickOnRemotePayCancelUPI()
                remote_pay_txn.clickOnRemotePayProceed()
                max_pay_attempt -= 1

            max_attempt_message = str(remote_pay_txn.maxAttemptsMessage())
            logger.info(f"Your expected max_attempt message is:  {max_attempt_message}")
            logger.info(f"Your expected message is:  {expected_message}")
            if max_attempt_message == expected_message:
                pass
            else:
                raise Exception("Message is not matching.")

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
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='ccEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
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
def test_common_100_103_310():
    """
     Sub Feature Code: UI_Common_PM_RP_Payment_Modes_UPI_Cards_Enabled_UPI_Max_Attempts_Error_Validation
     Sub Feature Description: Card and UPI is enabled, when user reaches max attempts of UPI payment, validate the error message
     TC naming code description: 100: Payment Method, 103: RemotePay, 310: TC310
    """
    expected_message = "Maximum number of attempts for this url exceeded. Please request for a new remote pay url."
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
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, component, entity, entity_id, org_code, setting_name, setting_value) VALUES ('ezetap', now(), 'ezetap', now(), 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
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

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        query = f"select setting_value from remotepay_setting where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed'"
        logger.debug(f"Query to fetch data from the remotepay_setting table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from remotepay_setting table :{result}")
        max_pay_attempt = int(result['setting_value'].values[0])
        logger.debug(f"Fetching max pay attempt from the remotepay_setting table : {max_pay_attempt}")

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
            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)

            while max_pay_attempt >= 0:
                if max_pay_attempt == 0:
                    ui_browser.goto(payment_link_url)
                    remote_pay_txn = RemotePayTxnPage(ui_browser)
                    break
                remote_pay_txn.clickOnRemotePayUPI()
                remote_pay_txn.clickOnRemotePayLaunchUPI()
                remote_pay_txn.clickOnRemotePayCancelUPI()
                remote_pay_txn.clickOnRemotePayProceed()
                max_pay_attempt -= 1

            max_attempt_message = str(remote_pay_txn.maxAttemptsMessage())
            logger.info(f"Your expected max_attempt message is:  {max_attempt_message}")
            logger.info(f"Your expected message is:  {expected_message}")
            if max_attempt_message == expected_message:
                pass
            else:
                raise Exception("Message is not matching.")

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
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)

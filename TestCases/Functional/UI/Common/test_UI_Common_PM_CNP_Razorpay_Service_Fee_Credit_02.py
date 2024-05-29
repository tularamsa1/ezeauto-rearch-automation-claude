import random
import sys
import pytest
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_504():
    """
    Sub Feature Code:UI_Common_PM_CNP_Razorpay_Service_Fee_Credit_Only_Enabled_JSON_Debit_With_FIXED_PERCENT_ANY_Debit_Credit_Scheme_Debit_Card_Details
    Sub Feature Description:Verify Service fee calculated when credit only enabled and JSON is debit with FIXED_PERCENT and ANY(Debit and Credit) scheme  with Debit Card details
    TC naming code description: 100: Payment Method, 103: RemotePay, 504: TC_504
    """
    expected_error_message = f"Please use a valid CREDIT card"
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
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'dcEnabledInCnp', 'false');"
            logger.debug(f"Query to insert data into remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the debit card  details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='false' where org_code='{org_code}' and setting_name='dcEnabledInCnp';"
            logger.debug(f"Query to update remotepay_setting table for debit card : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after updating the debit card details : {result}")

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "ANY"
        payment_by = "DEBIT"
        json_id = "service_fee_json_TC_100_103_504"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "FIXED"
        bank = 'NULL'
        flat_fee, percent = testsuite_teardown.create_service_fee_config_data(portal_username=portal_username,
                                                                              org_code=org_code,
                                                                              derivation_type=derivation_type,
                                                                              scheme=scheme, payment_by=payment_by,
                                                                              config_data_json_id=json_id,
                                                                              payment_mode=payment_mode,
                                                                              account_label=acc_label,
                                                                              bank=bank)

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(45, 50)
            flat_fee = float(flat_fee) if flat_fee is not 'NULL' else 0.00
            percent = float(percent) if percent is not 'NULL' else 0.00
            logger.debug(f"Flat Fee : {flat_fee},Percentage : {percent}")
            service_fee = round((amount * percent / 100) + flat_fee, 2)
            total_amount = amount + service_fee
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Amount used:{amount} and Order ID used :{order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("4111 1111 1111 1111")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                actual_service_fee = remote_pay_txn.fetch_service_fee()
                logger.debug(f"actual service_fee = {actual_service_fee}")
                actual_order_amount = remote_pay_txn.fetch_order_amount()
                logger.debug(f"actual order_amount = {actual_order_amount}")
                actual_total_amount = remote_pay_txn.fetch_total_amount()
                logger.debug(f"actual total_amount = {actual_total_amount}")

                actual_service_fee = float(actual_service_fee.replace("₹", ""))
                actual_order_amount = float(actual_order_amount.replace("₹", ""))
                actual_total_amount = float(actual_total_amount.replace("₹", ""))

                assert service_fee == actual_service_fee, "Service Fee is not matching."
                assert amount == actual_order_amount, "Amount is not matching."
                assert total_amount == actual_total_amount, "Total amount is not matching."

                remote_pay_txn.clickOnProceedToPay()

                error_message = str(remote_pay_txn.invalid_credit_card_error_message())
                logger.debug(f"error message : {error_message}")
                assert error_message == expected_error_message, "Error message is not matching"

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
            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result : {result}")

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
def test_common_100_103_506():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Credit_Only_Enabled_Amt_Out_Of_Range_Credit_Card_Details
    Sub Feature Description: Verify Error Message when Credit only enabled and amount out of range is passed  with Credit Card details
    TC naming code description: 100: Payment Method, 103: RemotePay, 493: TC_506
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
        logger.debug(f"Query to fetch org_code from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-----------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

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
        logger.info(f"Performing DB refresh")

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "MASTER_CARD"
        payment_by = "CREDIT"
        json_id = "service_fee_json_TC_100_103_506"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "FIXED_PERCENT"
        bank = "NULL"
        flat_fee, percent = testsuite_teardown.create_service_fee_config_data(portal_username=portal_username,
                                                                              org_code=org_code,
                                                                              derivation_type=derivation_type,
                                                                              scheme=scheme, payment_by=payment_by,
                                                                              config_data_json_id=json_id,
                                                                              payment_mode=payment_mode,
                                                                              account_label=acc_label, bank=bank)
        logger.info(f"flat_fee is: {flat_fee}")
        logger.info(f"fee percentage is: {percent}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)---------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1001, 1100)
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                logger.info(f"payment intent id is: {payment_intent_id}")
                page = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"clicking on payment link")
                page.goto(payment_link_url)
                logger.info(f"Initiating a card txn")
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                config_error_message = str(remote_pay_txn.serviceFeeConfigErrorMessage())
                logger.info(f"config_error_message: {config_error_message}")
                expected_message = f"An error occured. Please try another payment method or contact {org_code} support."
                assert expected_message == config_error_message, "Expected and actual error message is not matching."

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

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to disable Service Fee for the current merchant : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where setting_name='dcEnabledInCnp' and " \
                    f"org_code='{org_code}';"
            logger.debug(f"Query to update remote pay settings is : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Result for remote pay setting is: {result}")

            query = f"update remotepay_setting set setting_value='true' where setting_name='ccEnabledInCnp' and " \
                    f"org_code='{org_code}';"
            logger.debug(f"Query to update remote pay settings is : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Result for remote pay setting is: {result}")

            query = f"update remotepay_setting set setting_value='true' where setting_name='nbEnabledInCnp' and " \
                    f"org_code='{org_code}';"
            logger.debug(f"Query to update remote pay settings is : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Result for remote pay setting is: {result}")

            refresh_db()
            logger.info(f"Performing DB refresh")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_508():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Credit_Only_Enabled_No_JSON_Credit_Card_Details
    Sub Feature Description: Verify Error Message when credit only enabled and no JSON configured  with Credit Card details
    TC naming code description: 100: Payment Method, 103: RemotePay, 508: TC_508
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
        logger.debug(f"Query to fetch org_code from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-----------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

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
        logger.info(f"Performing DB refresh")

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)---------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1001, 1100)
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                logger.info(f"payment intent id is: {payment_intent_id}")
                page = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"clicking on payment link")
                page.goto(payment_link_url)
                logger.info(f"Initiating a card txn")
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                config_error_message = str(remote_pay_txn.serviceFeeConfigErrorMessage())
                logger.info(f"config_error_message: {config_error_message}")
                expected_message = f"An error occured. Please try another payment method or contact {org_code} support."
                assert expected_message == config_error_message, "Expected and actual error message is not matching."

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

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to disable Service Fee for the current merchant : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result : {result}")

            query = f"update remotepay_setting set setting_value='true' where setting_name='dcEnabledInCnp' and " \
                    f"org_code='{org_code}';"
            logger.debug(f"Query to update remote pay settings is : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Result for remote pay setting is: {result}")

            query = f"update remotepay_setting set setting_value='true' where setting_name='ccEnabledInCnp' and " \
                    f"org_code='{org_code}';"
            logger.debug(f"Query to update remote pay settings is : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Result for remote pay setting is: {result}")

            query = f"update remotepay_setting set setting_value='true' where setting_name='nbEnabledInCnp' and " \
                    f"org_code='{org_code}';"
            logger.debug(f"Query to update remote pay settings is : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Result for remote pay setting is: {result}")

            refresh_db()
            logger.info(f"Performing DB refresh")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)

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
def test_common_100_103_550():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_JSON_Amt_Range_Missed
    Sub Feature Description: Verify Error Message where Amt Range are missed in json
    TC naming code description: 100: Payment Method, 103: RemotePay, 550: TC_550
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table: {org_code}")

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
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
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
        logger.info(f"Performing DB refresh")

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "VISA"
        payment_by = "CREDIT"
        json_id = "service_fee_json_TC_100_103_550"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "FIXED"
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

            amount = random.randint(1, 200)
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
                page = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"clicking on payment link")
                page.goto(payment_link_url)
                logger.info(f"Initiating a card txn")
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                logger.info(f"Entering card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("4012 8888 8888 1881")
                remote_pay_txn.enterCreditCardExpiryMonth("5")
                remote_pay_txn.enterCreditCardExpiryYear("2045")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                logger.info(f"click on proceed button")
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
            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the org settings")
        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_554():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Txn_Amt_Same_As_Max_JSON_Amt
    Sub Feature Description: Verify Service Fee with max amount of JSON passed as txn amount.
    TC naming code description: 100: Payment Method, 103: RemotePay, 554: TC_554
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table: {org_code}")

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
                    f" 'SERVER', 'org', (SELECT id FROM org WHERE org_code ='{org_code}') , '{org_code}', 'nbEnabledInCnp', 'true');"
            logger.debug(f"Query to insert data into remotepay_setting table for net banking : {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result after inserting the net banking details : {result}")
        else:
            query = f"update remotepay_setting set setting_value='true' where org_code='{org_code}' and setting_name='nbEnabledInCnp';"
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
        logger.info(f"Performing DB refresh")

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "MASTER_CARD"
        payment_by = "DEBIT"
        json_id = "service_fee_json_TC_100_103_554"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "FIXED"
        bank = "NULL"
        flat_fee_1, percent_1 = testsuite_teardown.create_service_fee_config_data(portal_username=portal_username,
                                                                                  org_code=org_code,
                                                                                  derivation_type=derivation_type,
                                                                                  scheme=scheme, payment_by=payment_by,
                                                                                  config_data_json_id=json_id,
                                                                                  payment_mode=payment_mode,
                                                                                  account_label=acc_label, bank=bank)
        logger.info(f"flat_fee is: {flat_fee_1}")
        logger.info(f"fee percentage is: {percent_1}")

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

            # Fetching service fee for second txn.
            query = f"select * from service_fee_config where org_code='{org_code}' and payment_by='DEBIT' and " \
                    f"derivation_type='PERCENT' and scheme='MASTER_CARD';"
            logger.debug(f"Query to fetch service fee from the service_fee_config table : {query}")
            result = DBProcessor.getValueFromDB(query)
            flat_fee_2 = result['flat_fee'].values[0]
            logger.info(f"flat_fee is: {flat_fee_2}")
            percent_2 = result['percent'].values[0]
            logger.info(f"service fee percentage is: {percent_2}")

            amount_1 = 1000
            logger.info(f"amount is: {amount_1}")
            flat_fee_1 = float(flat_fee_1) if flat_fee_1 is not 'NULL' else 0.0
            percent_1 = float(percent_1) if percent_1 is not 'NULL' else 0.0
            logger.debug(f"Flat Fee : {flat_fee_1},Percentage : {percent_1}")
            service_fee_1 = round((amount_1 * percent_1 / 100) + flat_fee_1, 2)
            logger.info(f"calculated service is : {service_fee_1}")
            total_amount_1 = amount_1 + service_fee_1
            logger.info(f"total amount is : {total_amount_1}")
            order_id_1 = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order id is: {order_id_1}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "amount": amount_1,
                "externalRefNumber": order_id_1,
                "username": app_username,
                "password": app_password,
                "paymentFlow": "REMOTEPAY"
            })
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id_1 = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"clicking on payment link")
                page.goto(payment_link_url)
                logger.info(f"Initiating a card txn")
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnDebitCardToExpand()
                logger.info(f"Entering card details")
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enterDebitCardExpiryMonth("5")
                remote_pay_txn.enterDebitCardExpiryYear("2045")
                remote_pay_txn.enter_debit_card_cvv("111")
                actual_service_fee = remote_pay_txn.fetch_service_fee()
                logger.debug(f"fetching actual service_fee = {actual_service_fee}")
                actual_order_amount = remote_pay_txn.fetch_order_amount()
                logger.debug(f"fetching actual order_amount = {actual_order_amount}")
                actual_total_amount = remote_pay_txn.fetch_total_amount()
                logger.debug(f"fetching actual total_amount = {actual_total_amount}")

                remote_pay_txn.clickOnProceedToPay()
                logger.info(f"click on proceed button")
                remote_pay_txn.clickOnSuccessBtn()
                logger.info(f"click on success button")
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your actual success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."

                actual_service_fee = float(actual_service_fee.replace("₹", ""))
                logger.info(f"actual service fee is:  {actual_service_fee}")
                logger.info(f"expected service fee is:  {service_fee_1}")
                actual_order_amount = int(float(actual_order_amount.replace("₹", "")))
                logger.info(f"actual order amount is:  {actual_order_amount}")
                logger.info(f"expected order amount is:  {amount_1}")
                actual_total_amount = float(actual_total_amount.replace("₹", ""))
                logger.info(f"actual total amount is:  {actual_total_amount}")
                logger.info(f"expected total mount is:  {total_amount_1}")
                assert service_fee_1 == actual_service_fee, "Service Fee is not matching."
                assert amount_1 == actual_order_amount, "Amount is not matching."
                assert total_amount_1 == actual_total_amount, "Total amount is not matching."

                amount_2 = 5000
                logger.info(f"amount is: {amount_2}")
                flat_fee_2 = float(flat_fee_2) if flat_fee_2 is not None else 0.0 # was failing here before
                percent_2 = float(percent_2) if percent_2 is not 'NULL' else 0.0
                logger.debug(f"Flat Fee : {flat_fee_2},Percentage : {percent_2}")
                service_fee_2 = round((amount_2 * percent_2 / 100) + flat_fee_2, 2)
                logger.info(f"calculated service is : {service_fee_2}")
                total_amount_2 = amount_2 + service_fee_2
                logger.info(f"total amount is : {total_amount_2}")
                order_id_2 = datetime.now().strftime('%m%d%H%M%S')
                logger.info(f"order id is: {order_id_2}")

                api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                    "amount": amount_2,
                    "externalRefNumber": order_id_2,
                    "username": app_username,
                    "password": app_password,
                    "paymentFlow": "REMOTEPAY"
                })
                response = APIProcessor.send_request(api_details)
                if not response['success']:
                    raise Exception("Api could not initiate a cnp txn.")
                else:
                    payment_link_url = response.get('paymentLink')
                    payment_intent_id_2 = response.get('paymentIntentId')
                    page = TestSuiteSetup.initialize_ui_browser()
                    logger.info(f"clicking on payment link")
                    page.goto(payment_link_url)
                    logger.info(f"Initiating a card txn")
                    remote_pay_txn = RemotePayTxnPage(page)
                    remote_pay_txn.clickOnDebitCardToExpand()
                    logger.info(f"Entering card details")
                    remote_pay_txn.enterNameOnTheCard("Sandeep")
                    remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                    remote_pay_txn.enterDebitCardExpiryMonth("5")
                    remote_pay_txn.enterDebitCardExpiryYear("2045")
                    remote_pay_txn.enter_debit_card_cvv("111")
                    actual_service_fee = remote_pay_txn.fetch_service_fee()
                    logger.debug(f"fetching actual service_fee = {actual_service_fee}")
                    actual_order_amount = remote_pay_txn.fetch_order_amount()
                    logger.debug(f"fetching actual order_amount = {actual_order_amount}")
                    actual_total_amount = remote_pay_txn.fetch_total_amount()
                    logger.debug(f"fetching actual total_amount = {actual_total_amount}")

                    remote_pay_txn.clickOnProceedToPay()
                    logger.info(f"click on proceed button")
                    remote_pay_txn.clickOnSuccessBtn()
                    logger.info(f"click on success button")
                    success_message = str(remote_pay_txn.succcessScreenMessage())
                    logger.info(f"Your actual success message is:  {success_message}")
                    logger.info(f"Your expected Message is:  {expected_message}")
                    assert success_message == expected_message, "Success Message is not matching."

                    actual_service_fee = float(actual_service_fee.replace("₹", ""))
                    logger.info(f"actual service fee is:  {actual_service_fee}")
                    logger.info(f"expected service fee is:  {service_fee_2}")
                    actual_order_amount = int(float(actual_order_amount.replace("₹", "")))
                    logger.info(f"actual order amount is:  {actual_order_amount}")
                    logger.info(f"expected order amount is:  {amount_2}")
                    actual_total_amount = float(actual_total_amount.replace("₹", ""))
                    logger.info(f"actual total amount is:  {actual_total_amount}")
                    logger.info(f"expected total mount is:  {total_amount_2}")
                    assert service_fee_2 == actual_service_fee, "Service Fee is not matching."
                    assert amount_2 == actual_order_amount, "Amount is not matching."
                    assert total_amount_2 == actual_total_amount, "Total amount is not matching."

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id_1)}';"
            logger.debug(f"Query to fetch details for first txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_1 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id_1}")
            customer_name_1 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from the txn table : {customer_name_1}")
            payer_name_1 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer name from the txn table: {payer_name_1}")
            posting_date_1 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting date from the txn table: {posting_date_1}")
            created_time_1 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is : {created_time_1}")
            auth_code_1 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table: {auth_code_1}")
            status_1_db = result["status"].iloc[0]
            logger.debug(f"Fetching status from the txn table: {status_1_db}")
            settlement_status_1_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table: {settlement_status_1_db}")
            pmt_mode_1_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from the txn table: {pmt_mode_1_db}")
            amount_1_db = float(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from the txn table: {amount_1_db}")
            state_1_db = result["state"].iloc[0]
            logger.debug(f"Fetching state from the txn table: {state_1_db}")
            payment_gateway_1_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from the txn table {payment_gateway_1_db}")
            txn_type_1_db = result['txn_type'].values[0]
            logger.debug(f"Fetching txn type from the txn table {txn_type_1_db}")
            acquirer_code_1_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table {acquirer_code_1_db}")
            mid_1_db = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table: {mid_1_db}")
            tid_1_db = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table: {tid_1_db}")
            bank_name_1_db = result["bank_name"].values[0]
            logger.debug(f"Fetching bank name from the txn table {bank_name_1_db}")

            query = f"select * from cnp_txn where txn_id='{txn_id_1}';"
            logger.debug(f"Query to fetch details from the cnp_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state_1 = result['state'].values[0]
            logger.debug(f"Fetching cnp_txn_state from cnp_txn table: {cnp_txn_state_1}")
            cnp_txn_auth_code_1 = result['auth_code'].values[0]
            logger.debug(f"Fetching cnp_txn_auth_code from cnp_txn table : {cnp_txn_auth_code_1}")
            cnp_payment_gateway_1 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching cnp_payment_gateway from cnp_txn table : {cnp_payment_gateway_1}")
            cnp_payment_flow_1 = result['payment_flow'].values[0]
            logger.debug(f"Fetching cnp_payment_flow from cnp_txn table : {cnp_payment_flow_1}")
            cnp_txn_card_type_1 = result['payment_option'].values[0]
            logger.debug(f"Fetching card type from cnp_txn table: {cnp_txn_card_type_1}")
            cnp_pmt_card_brand_1 = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment card brand name from cnp_txn table: {cnp_pmt_card_brand_1}")

            query = f"select * from cnpware_txn where txn_id='{txn_id_1}';"
            logger.debug(f"Query to fetch details from the cnpware_txn table : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_payment_gateway_1 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching cnpware_payment_gateway from cnpware_txn table: {cnpware_payment_gateway_1}")
            cnpware_payment_flow_1 = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnpware_txn table: {cnpware_payment_flow_1}")

            query = f"select * from txn where org_code = '{str(org_code)}' and external_ref = '{str(order_id_2)}';"
            logger.debug(f"Query to fetch details for second txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from the txn table : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer name from the txn table: {payer_name_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting date from the txn table: {posting_date_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table is : {created_time_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table: {auth_code_2}")
            status_2_db = result["status"].iloc[0]
            logger.debug(f"Fetching status from the txn table: {status_2_db}")
            settlement_status_2_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table: {settlement_status_2_db}")
            pmt_mode_2_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from the txn table: {pmt_mode_2_db}")
            amount_2_db = float(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from the txn table: {amount_2_db}")
            state_2_db = result["state"].iloc[0]
            logger.debug(f"Fetching state from the txn table: {state_2_db}")
            payment_gateway_2_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from the txn table {payment_gateway_2_db}")
            txn_type_2_db = result['txn_type'].values[0]
            logger.debug(f"Fetching txn type from the txn table {txn_type_2_db}")
            acquirer_code_2_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table {acquirer_code_2_db}")
            mid_2_db = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table: {mid_2_db}")
            tid_2_db = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table: {tid_2_db}")
            bank_name_2_db = result["bank_name"].values[0]
            logger.debug(f"Fetching bank name from the txn table {bank_name_2_db}")

            query = f"select * from cnp_txn where txn_id='{txn_id_2}';"
            logger.debug(f"Query to fetch details from the cnp_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state_2 = result['state'].values[0]
            logger.debug(f"Fetching cnp_txn_state from cnp_txn table: {cnp_txn_state_2}")
            cnp_txn_auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching cnp_txn_auth_code from cnp_txn table : {cnp_txn_auth_code_2}")
            cnp_payment_gateway_2 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching cnp_payment_gateway from cnp_txn table : {cnp_payment_gateway_2}")
            cnp_payment_flow_2 = result['payment_flow'].values[0]
            logger.debug(f"Fetching cnp_payment_flow from cnp_txn table : {cnp_payment_flow_2}")
            cnp_txn_card_type_2 = result['payment_option'].values[0]
            logger.debug(f"Fetching card type from cnp_txn table: {cnp_txn_card_type_2}")
            cnp_pmt_card_brand_2 = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment card brand name from cnp_txn table: {cnp_pmt_card_brand_2}")

            query = f"select * from cnpware_txn where txn_id='{txn_id_2}';"
            logger.debug(f"Query to fetch details from the cnpware_txn table : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_payment_gateway_2 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching cnpware_payment_gateway from cnpware_txn table: {cnpware_payment_gateway_2}")
            cnpware_payment_flow_2 = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnpware_txn table: {cnpware_payment_flow_2}")

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
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time_1 = date_time_converter.to_app_format(posting_date_1)
                date_and_time_2 = date_time_converter.to_app_format(posting_date_2)
                expected_app_values = {
                    "pmt_mode_1": "PAY LINK",
                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": "{:,.2f}".format(total_amount_1),
                    "txn_id_1": txn_id_1,
                    "order_id_1": order_id_1,
                    "pmt_msg_1": "PAYMENT SUCCESSFUL",
                    "customer_name_1": customer_name_1,
                    "settle_status_1": "SETTLED",
                    "auth_code_1": auth_code_1,
                    "date_1": date_and_time_1,
                    "pmt_mode_2": "PAY LINK",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:,.2f}".format(total_amount_2),
                    "txn_id_2": txn_id_2,
                    "order_id_2": order_id_2,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "customer_name_2": customer_name_2,
                    "settle_status_2": "SETTLED",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.debug("Logging into the app.")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Clicking on History")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                logger.debug("Clicking on txn by txn id.")
                txn_history_page.click_on_transaction_by_txn_id(txn_id_1)

                app_payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {app_payment_status_1}")
                app_payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {app_payment_mode_1}")
                app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {app_txn_id_1}")
                app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount_1}")
                app_payment_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id from txn history for the txn : {app_payment_order_id_1}")
                app_payment_status_msg_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {app_payment_status_msg_1}")
                app_payment_customer_name_1 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer name from txn history for the txn : {app_payment_customer_name_1}")
                app_payment_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status from txn history for the txn : {app_payment_settlement_status_1}")
                app_payment_auth_code_1 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn :{app_payment_auth_code_1}")
                app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time_1}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)

                app_payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {app_payment_status_2}")
                app_payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {app_payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount_2}")
                app_payment_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id from txn history for the txn : {app_payment_order_id_2}")
                app_payment_status_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {app_payment_status_msg_2}")
                app_payment_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer name from txn history for the txn : {app_payment_customer_name_2}")
                app_payment_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement status from txn history for the txn : {app_payment_settlement_status_2}")
                app_payment_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn :{app_payment_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time_2}")

                actual_app_values = {
                    "pmt_mode_1": app_payment_mode_1,
                    "pmt_status_1": app_payment_status_1.split(':')[1],
                    "txn_amt_1": app_amount_1.split(' ')[1],
                    "txn_id_1": app_txn_id_1,
                    "order_id_1": app_payment_order_id_1,
                    "pmt_msg_1": app_payment_status_msg_1,
                    "customer_name_1": app_payment_customer_name_1,
                    "settle_status_1": app_payment_settlement_status_1,
                    "auth_code_1": app_payment_auth_code_1,
                    "date_1": app_date_and_time_1,
                    "pmt_mode_2": app_payment_mode_2,
                    "pmt_status_2": app_payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "order_id_2": app_payment_order_id_2,
                    "pmt_msg_2": app_payment_status_msg_2,
                    "customer_name_2": app_payment_customer_name_2,
                    "settle_status_2": app_payment_settlement_status_2,
                    "auth_code_2": app_payment_auth_code_2,
                    "date_2": app_date_and_time_2
                }

                logger.debug(f"actualAppValues: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_1 = date_time_converter.db_datetime(posting_date_1)
                date_2 = date_time_converter.db_datetime(posting_date_2)
                expected_api_values = {
                    "pmt_status_1": "AUTHORIZED",
                    "txn_amt_1": total_amount_1,
                    "pmt_mode_1": "CNP",
                    "pmt_state_1": "SETTLED",
                    "acquirer_code_1": "HDFC",
                    "settle_status_1": "SETTLED",
                    "issuer_code_1": "HDFC",
                    "txn_type_1": "REMOTE_PAY",
                    "org_code_1": org_code,
                    "date_1": date_1,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": total_amount_2,
                    "pmt_mode_2": "CNP",
                    "pmt_state_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "settle_status_2": "SETTLED",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": "REMOTE_PAY",
                    "org_code_2": org_code,
                    "date_2": date_2
                }
                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_1][0]
                logger.debug(f"Response after filtering data of first txn is : {response}")
                status_1_api = response["status"]
                logger.debug(f"Fetching status from api response : {status_1_api}")
                amount_1_api = float(response["amount"])
                logger.debug(f"Fetching amount from api response: {amount_1_api}")
                state_1_api = response["states"][0]
                logger.debug(f"Fetching state from api response : {state_1_api}")
                acquirer_code_1_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer_code from api response: {acquirer_code_1_api}")
                settlement_status_1_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement_status from api response: {settlement_status_1_api}")
                issuer_code_1_api = response["issuerCode"]
                logger.debug(f"Fetching issuer_code from api response: {issuer_code_1_api}")
                txn_type_1_api = response["txnType"]
                logger.debug(f"Fetching txn_type from api response: {txn_type_1_api}")
                org_code_1_api = response["orgCode"]
                logger.debug(f"Fetching org_code from api response: {org_code_1_api}")
                payment_mode_1_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response: {payment_mode_1_api}")
                date_1_api = response["postingDate"]
                logger.debug(f"Fetching date from api response: {date_1_api}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of second txn is : {response}")
                status_2_api = response["status"]
                logger.debug(f"Fetching status from api response : {status_2_api}")
                amount_2_api = float(response["amount"])
                logger.debug(f"Fetching amount from api response: {amount_2_api}")
                state_2_api = response["states"][0]
                logger.debug(f"Fetching state from api response : {state_2_api}")
                acquirer_code_2_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer_code from api response: {acquirer_code_2_api}")
                settlement_status_2_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement_status from api response: {settlement_status_2_api}")
                issuer_code_2_api = response["issuerCode"]
                logger.debug(f"Fetching issuer_code from api response: {issuer_code_2_api}")
                txn_type_2_api = response["txnType"]
                logger.debug(f"Fetching txn_type from api response: {txn_type_2_api}")
                org_code_2_api = response["orgCode"]
                logger.debug(f"Fetching org_code from api response: {org_code_2_api}")
                payment_mode_2_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from api response: {payment_mode_2_api}")
                date_2_api = response["postingDate"]
                logger.debug(f"Fetching date from api response: {date_2_api}")

                actual_api_values = {
                    "pmt_status_1": status_1_api,
                    "txn_amt_1": amount_1_api,
                    "pmt_mode_1": payment_mode_1_api,
                    "pmt_state_1": state_1_api,
                    "acquirer_code_1": acquirer_code_1_api,
                    "settle_status_1": settlement_status_1_api,
                    "issuer_code_1": issuer_code_1_api,
                    "txn_type_1": txn_type_1_api,
                    "org_code_1": org_code_1_api,
                    "date_1": date_time_converter.from_api_to_datetime_format(date_1_api),
                    "pmt_status_2": status_2_api,
                    "txn_amt_2": amount_2_api,
                    "pmt_mode_2": payment_mode_2_api,
                    "pmt_state_2": state_2_api,
                    "acquirer_code_2": acquirer_code_2_api,
                    "settle_status_2": settlement_status_2_api,
                    "issuer_code_2": issuer_code_2_api,
                    "txn_type_2": txn_type_2_api,
                    "org_code_2": org_code_2_api,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_2_api)
                }
                logger.debug(f"actualAPIValues: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status_1": "AUTHORIZED",
                    "pmt_state_1": "SETTLED",
                    "pmt_mode_1": "CNP",
                    "txn_amt_1": total_amount_1,
                    "settle_status_1": "SETTLED",
                    "acquirer_code_1": "HDFC",
                    "pmt_gateway_1": "RAZORPAY",
                    "txn_type_1": "REMOTE_PAY",
                    "pmt_intent_status_1": "COMPLETED",
                    "card_type_1": "CNP_DC",
                    "cnp_pmt_card_brand_1": "MASTER_CARD",
                    "cnp_pmt_gateway_1": "RAZORPAY",
                    "cnp_txn_state_1": "SETTLED",
                    "cnp_pmt_flow_1": "REMOTEPAY",
                    "cnp_auth_code_1": auth_code_1,
                    "cnpware_pmt_gateway_1": "RAZORPAY",
                    "cnpware_pmt_flow_1": "REMOTEPAY",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "CNP",
                    "txn_amt_2": total_amount_2,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "pmt_gateway_2": "RAZORPAY",
                    "txn_type_2": "REMOTE_PAY",
                    "pmt_intent_status_2": "COMPLETED",
                    "card_type_2": "CNP_DC",
                    "cnp_pmt_card_brand_2": "MASTER_CARD",
                    "cnp_pmt_gateway_2": "RAZORPAY",
                    "cnp_txn_state_2": "SETTLED",
                    "cnp_pmt_flow_2": "REMOTEPAY",
                    "cnp_auth_code_2": auth_code_2,
                    "cnpware_pmt_gateway_2": "RAZORPAY",
                    "cnpware_pmt_flow_2": "REMOTEPAY"
                }

                query = f"select * from payment_intent where id='{payment_intent_id_1}'"
                logger.debug(f"Query to fetch payment intent status for first txn from payment_intent table is: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status_1 = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table: {payment_intent_status_1}")

                query = f"select * from payment_intent where id='{payment_intent_id_2}'"
                logger.debug(f"Query to fetch payment intent status for second txn from payment_intent table is: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status_2 = result["status"].iloc[0]
                logger.debug(f"Fetching payment_intent_status from payment_intent table: {payment_intent_status_2}")

                actual_db_values = {
                    "pmt_status_1": status_1_db,
                    "pmt_state_1": state_1_db,
                    "pmt_mode_1": pmt_mode_1_db,
                    "txn_amt_1": amount_1_db,
                    "settle_status_1": settlement_status_1_db,
                    "acquirer_code_1": acquirer_code_1_db,
                    "pmt_gateway_1": payment_gateway_1_db,
                    "txn_type_1": txn_type_1_db,
                    "pmt_intent_status_1": payment_intent_status_1,
                    "card_type_1": cnp_txn_card_type_1,
                    "cnp_pmt_card_brand_1": cnp_pmt_card_brand_1,
                    "cnp_pmt_gateway_1": cnp_payment_gateway_1,
                    "cnp_txn_state_1": cnp_txn_state_1,
                    "cnp_pmt_flow_1": cnp_payment_flow_1,
                    "cnp_auth_code_1": cnp_txn_auth_code_1,
                    "cnpware_pmt_gateway_1": cnpware_payment_gateway_1,
                    "cnpware_pmt_flow_1": cnpware_payment_flow_1,
                    "pmt_status_2": status_2_db,
                    "pmt_state_2": state_2_db,
                    "pmt_mode_2": pmt_mode_2_db,
                    "txn_amt_2": amount_2_db,
                    "settle_status_2": settlement_status_2_db,
                    "acquirer_code_2": acquirer_code_2_db,
                    "pmt_gateway_2": payment_gateway_2_db,
                    "txn_type_2": txn_type_2_db,
                    "pmt_intent_status_2": payment_intent_status_2,
                    "card_type_2": cnp_txn_card_type_2,
                    "cnp_pmt_card_brand_2": cnp_pmt_card_brand_2,
                    "cnp_pmt_gateway_2": cnp_payment_gateway_2,
                    "cnp_txn_state_2": cnp_txn_state_2,
                    "cnp_pmt_flow_2": cnp_payment_flow_2,
                    "cnp_auth_code_2": cnp_txn_auth_code_2,
                    "cnpware_pmt_gateway_2": cnpware_payment_gateway_2,
                    "cnpware_pmt_flow_2": cnpware_payment_flow_2
                }

                logger.debug(f"actualDBValues : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal_1 = date_time_converter.to_portal_format(posting_date_1)
                date_and_time_portal_2 = date_time_converter.to_portal_format(posting_date_2)
                expected_portal_values = {
                    "date_time_1": date_and_time_portal_1,
                    "txn_id_1": txn_id_1,
                    "pmt_state_1": "AUTHORIZED",
                    "pmt_type_1": "CNP",
                    "txn_amt_1": "{:,.2f}".format(total_amount_1),
                    "username_1": app_username,
                    "auth_code_1": '-' if auth_code_1 is None else auth_code_1,
                    "date_time_2": date_and_time_portal_2,
                    "txn_id_2": txn_id_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "CNP",
                    "txn_amt_2": "{:,.2f}".format(total_amount_2),
                    "username_2": app_username,
                    "auth_code_2": '-' if auth_code_2 is None else auth_code_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id_1)
                logger.info(f"Fetching portal txn details : {transaction_details}")
                date_time_1 = transaction_details[0]['Date & Time']
                logger.debug(f"Fetching date_time from portal: {date_time_1}")
                txn_id_1_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"Fetching txn_id from portal: {txn_id_1_portal}")
                total_amt_1_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total_amt from portal: {total_amt_1_portal}")
                auth_code_1_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal: {auth_code_1_portal}")
                txn_type_1_portal = transaction_details[0]['Type']
                logger.debug(f"Fetching txn_type from portal: {txn_type_1_portal}")
                status_1_portal = transaction_details[0]['Status']
                logger.debug(f"Fetching status from portal: {status_1_portal}")
                username_1 = transaction_details[0]['Username']
                logger.debug(f"Fetching username from portal: {username_1}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id_2)
                logger.info(f"Fetching portal txn details : {transaction_details}")
                date_time_2 = transaction_details[0]['Date & Time']
                logger.debug(f"Fetching date_time from portal: {date_time_2}")
                txn_id_2_portal = transaction_details[0]['Transaction ID']
                logger.debug(f"Fetching txn_id from portal: {txn_id_2_portal}")
                total_amt_2_portal = transaction_details[0]['Total Amount'].split()
                logger.debug(f"Fetching total_amt from portal: {total_amt_2_portal}")
                auth_code_2_portal = transaction_details[0]['Auth Code']
                logger.debug(f"Fetching auth_code from portal: {auth_code_2_portal}")
                txn_type_2_portal = transaction_details[0]['Type']
                logger.debug(f"Fetching txn_type from portal: {txn_type_2_portal}")
                status_2_portal = transaction_details[0]['Status']
                logger.debug(f"Fetching status from portal: {status_2_portal}")
                username_2 = transaction_details[0]['Username']
                logger.debug(f"Fetching username from portal: {username_2}")

                actual_portal_values = {
                    "date_time_1": date_time_1,
                    "txn_id_1": txn_id_1_portal,
                    "pmt_state_1": str(status_1_portal),
                    "pmt_type_1": txn_type_1_portal,
                    "txn_amt_1": total_amt_1_portal[1],
                    "username_1": username_1,
                    "auth_code_1": auth_code_1_portal,
                    "date_time_2": date_time_2,
                    "txn_id_2": txn_id_2_portal,
                    "pmt_state_2": str(status_2_portal),
                    "pmt_type_2": txn_type_2_portal,
                    "txn_amt_2": total_amt_2_portal[1],
                    "username_2": username_2,
                    "auth_code_2": auth_code_2_portal
                }
                logger.debug(f"expected_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation----------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date_1, txn_time_1 = date_time_converter.to_chargeslip_format(posting_date_1)
                logger.info(f"date and time is: {txn_date_1},{txn_time_1}")
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(posting_date_2)
                logger.info(f"date and time is: {txn_date_2},{txn_time_2}")

                expected_charge_slip_values_1 = {
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount_1),
                    'SERVICE FEE:': "Rs." + "{:,.2f}".format(service_fee_1),
                    'TOTAL AMOUNT:': "Rs." + "{:,.2f}".format(total_amount_1),
                    'date': txn_date_1,
                    'time': txn_time_1,
                    'AUTH CODE': '' if auth_code_1 is None else auth_code_1
                }

                receipt_validator.perform_charge_slip_validations(txn_id_1, {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values_1)

                expected_charge_slip_values_2 = {
                    'CARD TYPE': 'MasterCard',
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount_2),
                    'SERVICE FEE:': "Rs." + "{:,.2f}".format(service_fee_2),
                    'TOTAL AMOUNT:': "Rs." + "{:,.2f}".format(total_amount_2),
                    'date': txn_date_2,
                    'time': txn_time_2,
                    'AUTH CODE': '' if auth_code_2 is None else auth_code_2
                }

                receipt_validator.perform_charge_slip_validations(txn_id_2, {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values_2)

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
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

            refresh_db()
            logger.debug(f"Refreshing the db after disabling service fee")
        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_551():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Amt_Not_In_Range_Of_JSON
    Sub Feature Description: Verify Error Message when amount not in range of JSON
    TC naming code description: 100: Payment Method, 103: RemotePay, 551: TC551
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

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "MASTER_CARD"
        payment_by = "CREDIT"
        json_id = "service_fee_json_TC_100_103_551"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "FIXED"
        bank = "NULL"
        flat_fee, percent = testsuite_teardown.create_service_fee_config_data(portal_username=portal_username,
                                                                              org_code=org_code,
                                                                              derivation_type=derivation_type,
                                                                              scheme=scheme, payment_by=payment_by,
                                                                              config_data_json_id=json_id,
                                                                              payment_mode=payment_mode,
                                                                              account_label=acc_label, bank=bank)
        logger.info(f"flat_fee: {flat_fee}")
        logger.info(f"percent: {percent}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(301, 399)
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
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
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

            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_553():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Service_Fee_Min_Amt_Greater_Than_Max_Amount_JSON
    Sub Feature Description: Verify Error Message when min amount is greater than max amount in JSON
    TC naming code description: 100: Payment Method, 103: RemotePay, 553: TC553
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

        query = f"update setting set setting_value='true' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
        logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Query result : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after setting the precondition")

        testsuite_teardown.delete_service_fee_config_data(org_code=org_code)
        scheme = "MASTER_CARD"
        payment_by = "CREDIT"
        json_id = "service_fee_json_TC_100_103_553"
        payment_mode = "CNP"
        acc_label = ""
        derivation_type = "FIXED"
        bank = "NULL"
        flat_fee, percent = testsuite_teardown.create_service_fee_config_data(portal_username=portal_username,
                                                                              org_code=org_code,
                                                                              derivation_type=derivation_type,
                                                                              scheme=scheme, payment_by=payment_by,
                                                                              config_data_json_id=json_id,
                                                                              payment_mode=payment_mode,
                                                                              account_label=acc_label, bank=bank)
        logger.info(f"flat_fee: {flat_fee}")
        logger.info(f"percent: {percent}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(301, 399)
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
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
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

            query = f"update setting set setting_value='false' where setting_name='serviceFeeEnabled' and org_code='{org_code}';"
            logger.debug(f"Query to enable Service Fee for the current merchant : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)
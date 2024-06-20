import random
import sys
import time
from datetime import datetime
import pytest

from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal, \
    get_txn_details_for_diff_order_id
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter, card_processor, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_565():
    """
    Sub Feature Code: UI_Common_PM_CNP_Remotepay_Razorpay_CNP_Success_After_Duplicate_Check_Interval_Time_First_Txn_CNP_Success
    Sub Feature Description: Verify CNP Success after duplicate check interval time when first CNP Success is performed
    TC naming code description: 100: Payment Method, 103: RemotePay, 565: TC565
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        api_details["RequestBody"]["settings"]["duplicatePaymentFields"] = "null"
        api_details["RequestBody"]["settings"]["duplicateIntervalForOnlinePayment"] = "1"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for duplicate payment setup to be enabled:  {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
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
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_success_pmt_btn()

                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1"
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table for first txn: {txn_id}")

            time.sleep(60)

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id_2 = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_success_pmt_btn()

                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1"
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table for second txn: {txn_id_2}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch txn details from the txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for first txn: {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for first txn: {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for first txn: {auth_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for first txn: {customer_name_txn}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for first txn: {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for first txn: {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for first txn: {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for first txn: {pmt_status}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for first txn: {payment_mode}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for first txn: {issuer_code_txn}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for first txn: {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for first txn: {amount_txn}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for first txn: {merchant_name}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for first txn: {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for first txn: {org_code_txn}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for first txn: {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for first txn: {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for first txn: {tid_txn}")
            payment_gateway = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for first txn: {payment_gateway}")

            query = f"select * from payment_intent where id = '{payment_intent_id}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

            query = f"select * from cnp_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnp_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for cnp_txn table for first txn: {result} ")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from cnp_txn table for first txn: {cnp_txn_rrn}")
            cnp_txn_payment_option = result['payment_option'].values[0]
            logger.debug(f"Fetching payment_option from cnp_txn table for first txn: {cnp_txn_payment_option}")
            cnp_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnp_txn table for first txn: {cnp_txn_payment_flow}")
            cnp_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnp_txn table for first txn: {cnp_txn_payment_status}")
            cnp_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnp_txn table for first txn: {cnp_txn_type}")
            cnp_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnp_txn table for first txn: {cnp_txn_payment_mode}")
            cnp_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnp_txn table for first txn: {cnp_txn_payment_state}")
            cnp_txn_payment_card_bin = result['payment_card_bin'].values[0]
            logger.debug(
                f"Fetching payment_card_bin from cnp_txn table for first txn: {cnp_txn_payment_card_bin}")
            cnp_txn_payment_card_brand = result['payment_card_brand'].values[0]
            logger.debug(
                f"Fetching payment_card_brand from cnp_txn table for first txn: {cnp_txn_payment_card_brand}")
            cnp_txn_payment_card_type = result['payment_card_type'].values[0]
            logger.debug(
                f"Fetching payment_card_type from cnp_txn table for first txn: {cnp_txn_payment_card_type}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from cnp_txn table for first txn: {cnp_txn_acquirer_code}")
            cnp_txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from cnp_txn table for first txn: {cnp_txn_issuer_code}")
            cnp_txn_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(
                f"Fetching card_last_four_digit from cnp_txn table for first txn: {cnp_txn_card_last_four_digit}")
            cnp_txn_org_code = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from cnp_txn table for first txn: {cnp_txn_org_code}")
            cnp_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnp_txn table for first txn: {cnp_txn_payment_gateway}")

            query = f"select * from cnpware_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnpware_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Fetching result for cnpware_txn table for first txn: {result} ")
            cnpware_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(
                f"Fetching payment_flow from cnpware_txn table for first txn: {cnpware_txn_payment_flow}")
            cnpware_txn_payment_status = result['payment_status'].values[0]
            logger.debug(
                f"Fetching payment_status from cnpware_txn table for first txn: {cnpware_txn_payment_status}")
            cnpware_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnpware_txn table for first txn: {cnpware_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnpware_txn table for first txn: {cnpware_txn_payment_mode}")
            cnpware_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnpware_txn table for first txn: {cnpware_txn_payment_state}")
            cnpware_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnpware_txn table for first txn: {cnpware_txn_payment_gateway}")

            query = f"select * from txn where id='{txn_id_2}'"
            logger.debug(f"Query to fetch txn details from the txn table for second txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for second txn: {created_time_2}")
            acquirer_code_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for second txn: {acquirer_code_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for second txn: {auth_code_2}")
            customer_name_txn_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for second txn: {customer_name_txn_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for second txn: {payer_name_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for second txn: {rrn_2}")
            settle_status_2 = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for second txn: {settle_status_2}")
            pmt_status_2 = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for second txn: {pmt_status_2}")
            payment_mode_2 = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for second txn: {payment_mode_2}")
            issuer_code_txn_2 = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for second txn: {issuer_code_txn_2}")
            pmt_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for second txn: {pmt_state_2}")
            amount_txn_2 = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for second txn: {amount_txn_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for second txn: {merchant_name_2}")
            order_id_txn_2 = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for second txn: {order_id_txn_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for second txn: {org_code_txn_2}")
            customer_mobile_txn_2 = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for second txn: {customer_mobile_txn_2}")
            mid_txn_2 = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for second txn: {mid_txn_2}")
            tid_txn_2 = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for second txn: {tid_txn_2}")
            payment_gateway_2 = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for second txn: {payment_gateway_2}")

            query = f"select * from payment_intent where id = '{payment_intent_id_2}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status_2 = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status_2}")

            query = f"select * from cnp_txn where txn_id = '{txn_id_2}'"
            logger.debug(f"Query to fetch data from the cnp_txn table for second txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for cnp_txn table for second txn: {result} ")
            cnp_txn_rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from cnp_txn table for second txn: {cnp_txn_rrn_2}")
            cnp_txn_payment_option_2 = result['payment_option'].values[0]
            logger.debug(
                f"Fetching payment_option from cnp_txn table for second txn: {cnp_txn_payment_option_2}")
            cnp_txn_payment_flow_2 = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnp_txn table for second txn: {cnp_txn_payment_flow_2}")
            cnp_txn_payment_status_2 = result['payment_status'].values[0]
            logger.debug(
                f"Fetching payment_status from cnp_txn table for second txn: {cnp_txn_payment_status_2}")
            cnp_txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnp_txn table for second txn: {cnp_txn_type_2}")
            cnp_txn_payment_mode_2 = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnp_txn table for second txn: {cnp_txn_payment_mode_2}")
            cnp_txn_payment_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state from cnp_txn table for second txn: {cnp_txn_payment_state_2}")
            cnp_txn_payment_card_bin_2 = result['payment_card_bin'].values[0]
            logger.debug(
                f"Fetching payment_card_bin from cnp_txn table for second txn: {cnp_txn_payment_card_bin_2}")
            cnp_txn_payment_card_brand_2 = result['payment_card_brand'].values[0]
            logger.debug(
                f"Fetching payment_card_brand from cnp_txn table for second txn: {cnp_txn_payment_card_brand_2}")
            cnp_txn_payment_card_type_2 = result['payment_card_type'].values[0]
            logger.debug(
                f"Fetching payment_card_type from cnp_txn table for second txn: {cnp_txn_payment_card_type_2}")
            cnp_txn_acquirer_code_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from cnp_txn table for second txn: {cnp_txn_acquirer_code_2}")
            cnp_txn_issuer_code_2 = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from cnp_txn table for second txn: {cnp_txn_issuer_code_2}")
            cnp_txn_card_last_four_digit_2 = result['card_last_four_digit'].values[0]
            logger.debug(
                f"Fetching card_last_four_digit from cnp_txn table for second txn: {cnp_txn_card_last_four_digit_2}")
            cnp_txn_org_code_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from cnp_txn table for second txn: {cnp_txn_org_code_2}")
            cnp_txn_payment_gateway_2 = result['payment_gateway'].values[0]
            logger.debug(
                f"Fetching payment_gateway from cnp_txn table for second txn: {cnp_txn_payment_gateway_2}")

            query = f"select * from cnpware_txn where txn_id = '{txn_id_2}'"
            logger.debug(f"Query to fetch data from the cnpware_txn table for second txn: {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Fetching result for cnpware_txn table for second txn: {result} ")
            cnpware_txn_payment_flow_2 = result['payment_flow'].values[0]
            logger.debug(
                f"Fetching payment_flow from cnpware_txn table for second txn: {cnpware_txn_payment_flow_2}")
            cnpware_txn_payment_status_2 = result['payment_status'].values[0]
            logger.debug(
                f"Fetching payment_status from cnpware_txn table for second txn: {cnpware_txn_payment_status_2}")
            cnpware_txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnpware_txn table for second txn: {cnpware_txn_type_2}")
            cnpware_txn_payment_mode_2 = result['payment_mode'].values[0]
            logger.debug(
                f"Fetching payment_mode from cnpware_txn table for second txn: {cnpware_txn_payment_mode_2}")
            cnpware_txn_payment_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state from cnpware_txn table for second txn: {cnpware_txn_payment_state_2}")
            cnpware_txn_payment_gateway_2 = result['payment_gateway'].values[0]
            logger.debug(
                f"Fetching payment_gateway from cnpware_txn table for second txn: {cnpware_txn_payment_gateway_2}")

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
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    # "rrn": str(cnp_txn_rrn),
                    "customer_name": customer_name_txn,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile_txn,
                    "card": "*5449",
                    "auth_code": auth_code,

                    "pmt_mode_2": "PAY LINK",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    # "rrn": str(cnp_txn_rrn),
                    "customer_name_2": customer_name_txn_2,
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    "customer_mobile_2": customer_mobile_txn_2,
                    "card_2": "*5449",
                    "auth_code_2": auth_code_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
                login_page = LoginPage(driver=app_driver)
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page = HomePage(driver=app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the first txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the first txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the first txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the first txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the first txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the first txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the first txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the first txn : {txn_id}, {app_settle_status}")
                # app_rrn = txn_history_page.fetch_RRN_text()
                # logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the first txn : {txn_id}, {app_customer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(
                    f"Fetching customer_mobile from txn history for the first txn : {txn_id}, {app_customer_mobile}")
                app_card = txn_history_page.fetch_card_text()
                logger.info(f"Fetching card from txn history for the first txn: {txn_id}, {app_card}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the first txn : {txn_id}, {app_auth_code}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the second txn : {txn_id_2}, {app_amount_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the second txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching payment_msg from txn history for the second txn : {txn_id_2}, {app_payment_msg_2}")
                app_payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment_mode from txn history for the second txn : {txn_id_2}, {app_payment_mode_2}")
                app_payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching payment_status from txn history for the second txn : {txn_id_2}, {app_payment_status_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the second txn : {txn_id_2}, {app_txn_id_2}")
                app_date_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the second txn : {txn_id_2}, {app_date_time_2}")
                app_settle_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching settlement_status from txn history for the second txn : {txn_id_2}, {app_settle_status_2}")
                # app_rrn = txn_history_page.fetch_RRN_text()
                # logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching customer_name from txn history for the second txn : {txn_id_2}, {app_customer_name_2}")
                app_customer_mobile_2 = txn_history_page.fetch_customer_mobile_text()
                logger.info(
                    f"Fetching customer_mobile from txn history for the second txn : {txn_id_2}, {app_customer_mobile_2}")
                app_card_2 = txn_history_page.fetch_card_text()
                logger.info(f"Fetching card from txn history for the second txn: {txn_id_2}, {app_card_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the second txn : {txn_id_2}, {app_auth_code_2}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settle_status,
                    "txn_id": app_txn_id,
                    # "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_time,
                    "customer_mobile": app_customer_mobile,
                    "card": app_card,
                    "auth_code": app_auth_code,

                    "pmt_mode_2": app_payment_mode_2,
                    "pmt_status_2": app_payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "settle_status_2": app_settle_status_2,
                    "txn_id_2": app_txn_id_2,
                    # "rrn": str(cnp_txn_rrn),
                    "customer_name_2": app_customer_name_2,
                    "order_id_2": app_order_id_2,
                    "payment_msg_2": app_payment_msg_2,
                    "date_2": app_date_time_2,
                    "customer_mobile_2": app_customer_mobile_2,
                    "card_2": app_card_2,
                    "auth_code_2": app_auth_code_2
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    # "rrn": str(cnp_txn_rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "name_on_card": payer_name,
                    "customer_mobile": customer_mobile_txn,
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": auth_code,

                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CNP",
                    "pmt_state_2": "SETTLED",
                    # "rrn": str(cnp_txn_rrn),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": "REMOTE_PAY",
                    "mid_2": mid_txn_2,
                    "tid_2": tid_txn_2,
                    "org_code_2": org_code,
                    "date_2": date_2,
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "customer_name_2": customer_name_txn_2,
                    "payer_name_2": payer_name_2,
                    "name_on_card_2": payer_name_2,
                    "customer_mobile_2": customer_mobile_txn_2,
                    "pmt_gateway_2": "RAZORPAY",
                    "auth_code_2": auth_code_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response}")
                api_amount = response_1.get('amount')
                logger.debug(f"From response fetch amount for first txn: {api_amount}")
                api_payment_mode = response_1.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for first txn: {api_payment_mode}")
                api_payment_status = response_1.get('status')
                logger.debug(f"From response fetch payment_status for first txn: {api_payment_status}")
                api_payment_state = response_1.get('states')[0]
                logger.debug(f"From response fetch payment_state for first txn: {api_payment_state}")
                api_mid = response_1.get('mid')
                logger.debug(f"From response fetch mid for first txn: {api_mid}")
                api_tid = response_1.get('tid')
                logger.debug(f"From response fetch tid for first txn: {api_tid}")
                api_acquirer_code = response_1.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for first txn: {api_acquirer_code}")
                api_settle_status = response_1.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for first txn: {api_settle_status}")
                # api_rrn = response.get('rrNumber')
                # logger.debug(f"From response fetch rrn : {api_rrn}")
                api_issuer_code = response_1.get('issuerCode')
                logger.debug(f"From response fetch issuer_code for first txn: {api_issuer_code}")
                api_txn_type = response_1.get('txnType')
                logger.debug(f"From response fetch txn_type for first txn: {api_txn_type}")
                api_org_code = response_1.get('orgCode')
                logger.debug(f"From response fetch org_code for first txn: {api_org_code}")
                api_date_time = response_1.get('createdTime')
                logger.debug(f"From response fetch date_time for first txn: {api_date_time}")
                api_merchant_name = response_1.get('merchantName')
                logger.debug(f"From response fetch merchant_name for first txn: {api_merchant_name}")
                api_ext_ref_number = response_1.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for first txn: {api_ext_ref_number}")
                api_customer_name = response_1.get('customerName')
                logger.debug(f"From response fetch customer_name for first txn: {api_customer_name}")
                api_payer_name = response_1.get('payerName')
                logger.debug(f"From response fetch payer_name for first txn: {api_payer_name}")
                api_name_on_card = response_1.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card for first txn: {api_name_on_card}")
                api_customer_mobile = response_1.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for first txn: {api_customer_mobile}")
                api_payment_gateway = response_1.get('paymentGateway')
                logger.debug(f"From response fetch paymentGateway for first txn: {api_payment_gateway}")
                api_auth_code = response_1.get('authCode')
                logger.debug(f"From response fetch authCode for first txn: {api_auth_code}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of second txn is : {response}")
                api_amount_2 = response_2.get('amount')
                logger.debug(f"From response fetch amount for second txn : {api_amount_2}")
                api_payment_mode_2 = response_2.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for second txn : {api_payment_mode_2}")
                api_payment_status_2 = response_2.get('status')
                logger.debug(f"From response fetch payment_status for second txn : {api_payment_status_2}")
                api_payment_state_2 = response_2.get('states')[0]
                logger.debug(f"From response fetch payment_state for second txn : {api_payment_state_2}")
                api_mid_2 = response_2.get('mid')
                logger.debug(f"From response fetch mid for second txn : {api_mid_2}")
                api_tid_2 = response_2.get('tid')
                logger.debug(f"From response fetch tid for second txn : {api_tid_2}")
                api_acquirer_code_2 = response_2.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for second txn : {api_acquirer_code_2}")
                api_settle_status_2 = response_2.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for second txn : {api_settle_status_2}")
                # api_rrn_2 = response_2.get('rrNumber')
                # logger.debug(f"From response fetch rrn for success txn : {api_rrn_2}")
                api_issuer_code_2 = response_2.get('issuerCode')
                logger.debug(f"From response fetch issuer_code for second txn : {api_issuer_code_2}")
                api_txn_type_2 = response_2.get('txnType')
                logger.debug(f"From response fetch txn_type for second txn : {api_txn_type_2}")
                api_org_code_2 = response_2.get('orgCode')
                logger.debug(f"From response fetch org_code for second txn : {api_org_code_2}")
                api_date_time_2 = response_2.get('createdTime')
                logger.debug(f"From response fetch date_time for second txn : {api_date_time_2}")
                api_merchant_name_2 = response_2.get('merchantName')
                logger.debug(f"From response fetch merchant_name for second txn : {api_merchant_name_2}")
                api_ext_ref_number_2 = response_2.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for second txn : {api_ext_ref_number_2}")
                api_customer_name_2 = response_2.get('customerName')
                logger.debug(f"From response fetch customer_name for second txn : {api_customer_name_2}")
                api_payer_name_2 = response_2.get('payerName')
                logger.debug(f"From response fetch payer_name for second txn : {api_payer_name_2}")
                api_name_on_card_2 = response_2.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card for second txn : {api_name_on_card_2}")
                api_customer_mobile_2 = response_2.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for second txn : {api_customer_mobile_2}")
                api_payment_gateway_2 = response_2.get('paymentGateway')
                logger.debug(f"From response fetch paymentGateway for second txn : {api_payment_gateway_2}")
                api_auth_code_2 = response_2.get('authCode')
                logger.debug(f"From response fetch authCode for second txn : {api_auth_code_2}")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    # "rrn": str(api_rrn),
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "customer_mobile": api_customer_mobile,
                    "pmt_gateway": api_payment_gateway,
                    "auth_code": api_auth_code,

                    "pmt_status_2": api_payment_status_2,
                    "txn_amt_2": api_amount_2,
                    "pmt_mode_2": api_payment_mode_2,
                    "pmt_state_2": api_payment_state_2,
                    # "rrn": str(api_rrn),
                    "settle_status_2": api_settle_status_2,
                    "acquirer_code_2": api_acquirer_code_2,
                    "issuer_code_2": api_issuer_code_2,
                    "txn_type_2": api_txn_type_2,
                    "mid_2": api_mid_2,
                    "tid_2": api_tid_2,
                    "org_code_2": api_org_code_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_2),
                    "ext_ref_number_2": api_ext_ref_number_2,
                    "merchant_name_2": api_merchant_name_2,
                    "customer_name_2": api_customer_name_2,
                    "payer_name_2": api_payer_name_2,
                    "name_on_card_2": api_name_on_card_2,
                    "customer_mobile_2": api_customer_mobile_2,
                    "pmt_gateway_2": api_payment_gateway_2,
                    "auth_code_2": api_auth_code_2
                }
                logger.debug(f"actual_api_values: {actual_api_values}")

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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_intent_status": "COMPLETED",

                    "cnp_pmt_option": "CNP_CC",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "cnp_pmt_state": "SETTLED",
                    "cnp_pmt_card_bin": "526731",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnp_pmt_card_type": "CREDIT",
                    "cnp_acquirer_code": "HDFC",
                    "cnp_issuer_code": "HDFC",
                    "cnp_card_last_four_digit": "5449",
                    "cnp_org_code": org_code,
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "cnpware_pmt_status": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state": "SETTLED",
                    "cnpware_pmt_mode": "CNP",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY",

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "CNP",
                    "txn_amt_2": float(amount),
                    "order_id_2": order_id,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "pmt_gateway_2": "RAZORPAY",
                    "pmt_intent_status_2": "COMPLETED",

                    "cnp_pmt_option_2": "CNP_CC",
                    "cnp_pmt_flow_2": "REMOTEPAY",
                    "cnp_pmt_status_2": "PAYMENT_COMPLETED",
                    "cnp_pmt_state_2": "SETTLED",
                    "cnp_pmt_card_bin_2": "526731",
                    "cnp_pmt_card_brand_2": "MASTER_CARD",
                    "cnp_pmt_card_type_2": "CREDIT",
                    "cnp_acquirer_code_2": "HDFC",
                    "cnp_issuer_code_2": "HDFC",
                    "cnp_card_last_four_digit_2": "5449",
                    "cnp_org_code_2": org_code,
                    "cnp_txn_type_2": "REMOTE_PAY",
                    "cnp_pmt_mode_2": "CNP",
                    "cnp_pmt_gateway_2": "RAZORPAY",

                    "cnpware_pmt_status_2": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state_2": "SETTLED",
                    "cnpware_pmt_mode_2": "CNP",
                    "cnpware_pmt_flow_2": "REMOTEPAY",
                    "cnpware_pmt_gateway_2": "RAZORPAY",
                    "cnpware_txn_type_2": "REMOTE_PAY"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "settle_status": settle_status,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "pmt_gateway": payment_gateway,
                    "pmt_intent_status": payment_intent_status,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_pmt_card_bin": cnp_txn_payment_card_bin,
                    "cnp_pmt_card_brand": cnp_txn_payment_card_brand,
                    "cnp_pmt_card_type": cnp_txn_payment_card_type,
                    "cnp_acquirer_code": cnp_txn_acquirer_code,
                    "cnp_issuer_code": cnp_txn_issuer_code,
                    "cnp_card_last_four_digit": cnp_txn_card_last_four_digit,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "cnpware_pmt_status": cnpware_txn_payment_status,
                    "cnpware_pmt_state": cnpware_txn_payment_state,
                    "cnpware_pmt_mode": cnpware_txn_payment_mode,
                    "cnpware_pmt_flow": cnpware_txn_payment_flow,
                    "cnpware_pmt_gateway": cnpware_txn_payment_gateway,
                    "cnpware_txn_type": cnpware_txn_type,

                    "pmt_status_2": pmt_status_2,
                    "pmt_state_2": pmt_state_2,
                    "pmt_mode_2": payment_mode_2,
                    "txn_amt_2": amount_txn_2,
                    "order_id_2": order_id_txn_2,
                    "settle_status_2": settle_status_2,
                    "acquirer_code_2": acquirer_code_2,
                    "issuer_code_2": issuer_code_txn_2,
                    "pmt_gateway_2": payment_gateway_2,
                    "pmt_intent_status_2": payment_intent_status_2,

                    "cnp_pmt_option_2": cnp_txn_payment_option_2,
                    "cnp_pmt_flow_2": cnp_txn_payment_flow_2,
                    "cnp_pmt_status_2": cnp_txn_payment_status_2,
                    "cnp_pmt_state_2": cnp_txn_payment_state_2,
                    "cnp_pmt_card_bin_2": cnp_txn_payment_card_bin_2,
                    "cnp_pmt_card_brand_2": cnp_txn_payment_card_brand_2,
                    "cnp_pmt_card_type_2": cnp_txn_payment_card_type_2,
                    "cnp_acquirer_code_2": cnp_txn_acquirer_code_2,
                    "cnp_issuer_code_2": cnp_txn_issuer_code_2,
                    "cnp_card_last_four_digit_2": cnp_txn_card_last_four_digit_2,
                    "cnp_org_code_2": cnp_txn_org_code_2,
                    "cnp_txn_type_2": cnp_txn_type_2,
                    "cnp_pmt_mode_2": cnp_txn_payment_mode_2,
                    "cnp_pmt_gateway_2": cnp_txn_payment_gateway_2,

                    "cnpware_pmt_status_2": cnpware_txn_payment_status_2,
                    "cnpware_pmt_state_2": cnpware_txn_payment_state_2,
                    "cnpware_pmt_mode_2": cnpware_txn_payment_mode_2,
                    "cnpware_pmt_flow_2": cnpware_txn_payment_flow_2,
                    "cnpware_pmt_gateway_2": cnpware_txn_payment_gateway_2,
                    "cnpware_txn_type_2": cnpware_txn_type_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_type_2": "CNP",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "rrn_2": "-" if rrn_2 is None else rrn_2,
                    "auth_code_2": "-" if auth_code_2 is None else auth_code_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[1]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[1]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_rrn = transaction_details[1]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[1]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[1]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[1]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")
                portal_auth_code = transaction_details[1]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")

                portal_date_time_2 = transaction_details[0]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time_2}")
                portal_txn_id_2 = transaction_details[0]['Transaction ID']
                logger.info(
                    f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id_2}")
                portal_total_amount_2 = transaction_details[0]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount_2}")
                portal_rrn_2 = transaction_details[0]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn_2}")
                portal_txn_type_2 = transaction_details[0]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type_2}")
                portal_txn_status_2 = transaction_details[0]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status_2}")
                portal_user_2 = transaction_details[0]['Username']
                logger.info(
                    f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user_2}")
                portal_auth_code_2 = transaction_details[0]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code_2}")

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "rrn": portal_rrn,
                    "auth_code": portal_auth_code,

                    "date_time_2": portal_date_time_2,
                    "pmt_status_2": portal_txn_status_2,
                    "pmt_type_2": portal_txn_type_2,
                    "txn_amt_2": portal_total_amount_2.split(' ')[1],
                    "username_2": portal_user_2,
                    "txn_id_2": portal_txn_id_2,
                    "rrn_2": portal_rrn_2,
                    "auth_code_2": portal_auth_code_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)
                expected_charge_slip_values = {
                    "payment_option": "SALE",
                    "merchant_ref_no": 'Ref # ' + str(order_id),
                    "RRN": "" if rrn is None else rrn,
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "MID": mid_txn,
                    "TID": tid_txn,
                    "time": txn_time,
                    "CARD": f"XXXX-XXXX-XXXX-5449",
                    "CARD TYPE": "MasterCard",
                    "AUTH CODE": str(auth_code).strip(),
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                charge_slip_val_result = receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)

                expected_charge_slip_values_2 = {
                    "payment_option": "SALE",
                    "merchant_ref_no": 'Ref # ' + str(order_id),
                    "RRN": "" if rrn_2 is None else rrn_2,
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date_2,
                    "MID": mid_txn_2,
                    "TID": tid_txn_2,
                    "time": txn_time_2,
                    "CARD": f"XXXX-XXXX-XXXX-5449",
                    "CARD TYPE": "MasterCard",
                    "AUTH CODE": str(auth_code_2).strip(),
                }
                logger.debug(f"expected_charge_slip_values_2: {expected_charge_slip_values_2}")
                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2,
                                                                                             credentials={
                                                                                                 "username": app_username,
                                                                                                 "password": app_password
                                                                                             },
                                                                                             expected_details=expected_charge_slip_values_2)

                if charge_slip_val_result and charge_slip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'
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
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "false"
            api_details["RequestBody"]["settings"][
                "duplicatePaymentFields"] = "paymentMode,username,processCode,txnType,amount"
            api_details["RequestBody"]["settings"]["duplicateIntervalForOnlinePayment"] = ""
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for duplicate payment setup to be disabled:  {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_566():
    """
    Sub Feature Code: UI_Common_PM_CNP_Remotepay_Razorpay_Card_Success_After_Duplicate_Check_Interval_Time_First_Txn_CNP_Success
    Sub Feature Description: Verify Card Success after duplicate check interval time when first CNP Success is performed
    TC naming code description: 100: Payment Method, 103: RemotePay, 566: TC566
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
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='HDFC'"
        logger.debug(f"Query to fetch data from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].values[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result['id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')

        testsuite_teardown.revert_card_payment_settings_default(org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "true"
        api_details["RequestBody"]["settings"]["duplicatePaymentFields"] = "null"
        api_details["RequestBody"]["settings"]["duplicateIntervalForOnlinePayment"] = "1"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for duplicate payment setup to be enabled:  {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
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
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_success_pmt_btn()

                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1"
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table for first txn: {txn_id}")

            time.sleep(60)

            card_details = card_processor.get_card_details_from_excel("EMV_DEBIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api_with_original_amount',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="HDFC",
                                                              payment_gateway="HDFC"),
                                                          "username": app_username,
                                                          "password": app_password,
                                                          "amount": str(amount),
                                                          "originalAmount": str(amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(order_id)})

            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            logger.debug(f"card_payment_success : {card_payment_success}")
            if card_payment_success == True:
                txn_id_2 = response['txnId']
                logger.debug(f"From response fetch txn_id : {txn_id_2}")
                confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "ezetapDeviceData": confirm_data[
                                                                            "Ezetap Device Data"],
                                                                        "txnId": txn_id_2
                                                                        })
                confirm_response = APIProcessor.send_request(api_details)
                confirm_success = confirm_response['success']
                logger.debug(f"From response fetch status : {confirm_success}")
            else:
                logger.error("Card payment Failed")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch txn details from the txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for first txn: {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for first txn: {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for first txn: {auth_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for first txn: {customer_name_txn}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for first txn: {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for first txn: {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for first txn: {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for first txn: {pmt_status}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for first txn: {payment_mode}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for first txn: {issuer_code_txn}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for first txn: {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for first txn: {amount_txn}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for first txn: {merchant_name}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for first txn: {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for first txn: {org_code_txn}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for first txn: {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for first txn: {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for first txn: {tid_txn}")
            payment_gateway = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for first txn: {payment_gateway}")

            query = f"select * from payment_intent where id = '{payment_intent_id}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

            query = f"select * from cnp_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnp_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for cnp_txn table for first txn: {result} ")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from cnp_txn table for first txn: {cnp_txn_rrn}")
            cnp_txn_payment_option = result['payment_option'].values[0]
            logger.debug(f"Fetching payment_option from cnp_txn table for first txn: {cnp_txn_payment_option}")
            cnp_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnp_txn table for first txn: {cnp_txn_payment_flow}")
            cnp_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnp_txn table for first txn: {cnp_txn_payment_status}")
            cnp_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnp_txn table for first txn: {cnp_txn_type}")
            cnp_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnp_txn table for first txn: {cnp_txn_payment_mode}")
            cnp_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnp_txn table for first txn: {cnp_txn_payment_state}")
            cnp_txn_payment_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from cnp_txn table for first txn: {cnp_txn_payment_card_bin}")
            cnp_txn_payment_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from cnp_txn table for first txn: {cnp_txn_payment_card_brand}")
            cnp_txn_payment_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from cnp_txn table for first txn: {cnp_txn_payment_card_type}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from cnp_txn table for first txn: {cnp_txn_acquirer_code}")
            cnp_txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from cnp_txn table for first txn: {cnp_txn_issuer_code}")
            cnp_txn_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from cnp_txn table for first txn: {cnp_txn_card_last_four_digit}")
            cnp_txn_org_code = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from cnp_txn table for first txn: {cnp_txn_org_code}")
            cnp_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnp_txn table for first txn: {cnp_txn_payment_gateway}")

            query = f"select * from cnpware_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from the cnpware_txn table for first txn: {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Fetching result for cnpware_txn table for first txn: {result} ")
            cnpware_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnpware_txn table for first txn: {cnpware_txn_payment_flow}")
            cnpware_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnpware_txn table for first txn: {cnpware_txn_payment_status}")
            cnpware_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnpware_txn table for first txn: {cnpware_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnpware_txn table for first txn: {cnpware_txn_payment_mode}")
            cnpware_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnpware_txn table for first txn: {cnpware_txn_payment_state}")
            cnpware_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnpware_txn table for first txn: {cnpware_txn_payment_gateway}")

            query = f"select * from txn where id='{txn_id_2}'"
            logger.debug(f"Query to fetch txn details from the txn table for second txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for second txn: {created_time_2}")
            acquirer_code_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for second txn: {acquirer_code_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for second txn: {auth_code_2}")
            customer_name_txn_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for second txn: {customer_name_txn_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for second txn: {payer_name_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for second txn: {rrn_2}")
            settle_status_2 = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for second txn: {settle_status_2}")
            pmt_status_2 = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for second txn: {pmt_status_2}")
            payment_mode_2 = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for second txn: {payment_mode_2}")
            issuer_code_txn_2 = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for second txn: {issuer_code_txn_2}")
            pmt_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for second txn: {pmt_state_2}")
            amount_txn_2 = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for second txn: {amount_txn_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for second txn: {merchant_name_2}")
            order_id_txn_2 = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for second txn: {order_id_txn_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for second txn: {org_code_txn_2}")
            mid_txn_2 = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for second txn: {mid_txn_2}")
            tid_txn_2 = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for first txn: {tid_txn_2}")
            payment_gateway_2 = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for second txn: {payment_gateway_2}")
            device_serial_txn_2 = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from the txn table for second txn: {device_serial_txn_2}")
            batch_number_2 = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table for second txn: {batch_number_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for second txn: {txn_type_2}")
            pmt_card_brand_2 = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table for second txn: {pmt_card_brand_2}")
            pmt_card_type_2 = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table for second txn: {pmt_card_type_2}")
            card_last_four_digit_2 = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table for second txn: {card_last_four_digit_2}")
            pmt_card_bin_2 = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table for second txn: {pmt_card_bin_2}")
            terminal_info_id_txn_2 = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table for second txn: {terminal_info_id_txn_2}")
            card_txn_type_2 = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table for second txn: {card_txn_type_2}")

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
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                expected_app_values = {
                    "pmt_mode": "PAY LINK",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "customer_name": customer_name_txn,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile_txn,
                    "card": "*5449",
                    "auth_code": auth_code,

                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "AUTHORIZED",
                    "rr_number_2": rrn_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2,
                    "batch_number_2": batch_number_2,
                    "card_type_desc_2": "*0250 EMV",
                    "mid_2": mid,
                    "tid_2": tid,
                    "customer_name_2": "L3TEST"
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
                login_page = LoginPage(driver=app_driver)
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page = HomePage(driver=app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the first txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the first txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the first txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the first txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the first txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the first txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the first txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the first txn : {txn_id}, {app_settle_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the first txn : {txn_id}, {app_customer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the first txn : {txn_id}, {app_customer_mobile}")
                app_card = txn_history_page.fetch_card_text()
                logger.info(f"Fetching card from txn history for the first txn: {txn_id}, {app_card}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the first txn : {txn_id}, {app_auth_code}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the second txn : {txn_id_2}, {app_amount_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the second txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the second txn : {txn_id_2}, {app_payment_msg_2}")
                app_payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the second txn : {txn_id_2}, {app_payment_mode_2}")
                app_payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the second txn : {txn_id_2}, {app_payment_status_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the second txn : {txn_id_2}, {app_txn_id_2}")
                app_date_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the second txn : {txn_id_2}, {app_date_time_2}")
                app_settle_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the second txn : {txn_id_2}, {app_settle_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the second txn : {txn_id_2}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the second txn : {txn_id_2}, {app_auth_code_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the second txn : {txn_id_2}, {app_batch_number_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the second txn : {txn_id_2}, {app_card_type_desc_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the second txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the second txn : {txn_id_2}, {app_tid_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the second txn : {txn_id_2}, {app_customer_name_2}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settle_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_time,
                    "customer_mobile": app_customer_mobile,
                    "card": app_card,
                    "auth_code": app_auth_code,

                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": app_payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": app_payment_status_2.split(':')[1],
                    "rr_number_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settle_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_time_2,
                    "batch_number_2": app_batch_number_2,
                    "card_type_desc_2": app_card_type_desc_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "customer_name_2": app_customer_name_2
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CNP",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "name_on_card": payer_name,
                    "customer_mobile": customer_mobile_txn,
                    "pmt_gateway": "RAZORPAY",
                    "auth_code": auth_code,

                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "AUTHORIZED",
                    "mid_2": mid,
                    "tid_2": tid,
                    "acquirer_code_2": "HDFC",
                    "settle_status_2": "PENDING",
                    "rrn_2": rrn_2,
                    "issuer_code_2": issuer_code_txn_2,
                    "txn_type_2": "CHARGE",
                    "org_code_2": org_code,
                    "batch_number_2": batch_number_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "date_2": date_2,
                    "device_serial_2": device_serial,
                    "card_txn_type_desc_2": "EMV",
                    "auth_code_2": auth_code_2,
                    "card_last_four_digit_2": "0250",
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "pmt_card_bin_2": "476173",
                    "card_type_2": "VISA",
                    "display_pan_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025",
                    "payer_name_2": "L3TEST/CARD0025",
                    "name_on_card_2": "L3TEST/CARD0025",
                    "pmt_gateway_2": "HDFC"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response}")
                api_amount = response_1.get('amount')
                logger.debug(f"From response fetch amount for first txn: {api_amount}")
                api_payment_mode = response_1.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for first txn: {api_payment_mode}")
                api_payment_status = response_1.get('status')
                logger.debug(f"From response fetch payment_status for first txn: {api_payment_status}")
                api_payment_state = response_1.get('states')[0]
                logger.debug(f"From response fetch payment_state for first txn: {api_payment_state}")
                api_mid = response_1.get('mid')
                logger.debug(f"From response fetch mid for first txn: {api_mid}")
                api_tid = response_1.get('tid')
                logger.debug(f"From response fetch tid for first txn: {api_tid}")
                api_acquirer_code = response_1.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for first txn: {api_acquirer_code}")
                api_settle_status = response_1.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for first txn: {api_settle_status}")
                api_issuer_code = response_1.get('issuerCode')
                logger.debug(f"From response fetch issuer_code for first txn: {api_issuer_code}")
                api_txn_type = response_1.get('txnType')
                logger.debug(f"From response fetch txn_type for first txn: {api_txn_type}")
                api_org_code = response_1.get('orgCode')
                logger.debug(f"From response fetch org_code for first txn: {api_org_code}")
                api_date_time = response_1.get('createdTime')
                logger.debug(f"From response fetch date_time for first txn: {api_date_time}")
                api_merchant_name = response_1.get('merchantName')
                logger.debug(f"From response fetch merchant_name for first txn: {api_merchant_name}")
                api_ext_ref_number = response_1.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for first txn: {api_ext_ref_number}")
                api_customer_name = response_1.get('customerName')
                logger.debug(f"From response fetch customer_name for first txn: {api_customer_name}")
                api_payer_name = response_1.get('payerName')
                logger.debug(f"From response fetch payer_name for first txn: {api_payer_name}")
                api_name_on_card = response_1.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card for first txn: {api_name_on_card}")
                api_customer_mobile = response_1.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for first txn: {api_customer_mobile}")
                api_payment_gateway = response_1.get('paymentGateway')
                logger.debug(f"From response fetch paymentGateway for first txn: {api_payment_gateway}")
                api_auth_code = response_1.get('authCode')
                logger.debug(f"From response fetch authCode for first txn: {api_auth_code}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of second txn is : {response}")
                api_amount_2 = response_2.get('amount')
                logger.debug(f"From response fetch amount for second  txn: {api_amount_2}")
                api_payment_mode_2 = response_2.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for second  txn: {api_payment_mode_2}")
                api_payment_status_2 = response_2.get('status')
                logger.debug(f"From response fetch payment_status for second  txn: {api_payment_status_2}")
                api_payment_state_2 = response_2.get('states')[0]
                logger.debug(f"From response fetch payment_state for second  txn: {api_payment_state_2}")
                api_mid_2 = response_2.get('mid')
                logger.debug(f"From response fetch mid for second  txn: {api_mid_2}")
                api_tid_2 = response_2.get('tid')
                logger.debug(f"From response fetch tid for second  txn: {api_tid_2}")
                api_acquirer_code_2 = response_2.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for second  txn: {api_acquirer_code_2}")
                api_settle_status_2 = response_2.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for second  txn: {api_settle_status_2}")
                api_rrn_2 = response_2.get('rrNumber')
                logger.debug(f"From response fetch rrn for second  txn: {api_rrn_2}")
                api_issuer_code_2 = response_2.get('issuerCode')
                logger.debug(f"From response fetch issuer_code for second  txn: {api_issuer_code_2}")
                api_txn_type_2 = response_2.get('txnType')
                logger.debug(f"From response fetch txn_type for second  txn: {api_txn_type_2}")
                api_org_code_2 = response_2.get('orgCode')
                logger.debug(f"From response fetch org_code for second  txn: {api_org_code_2}")
                api_batch_number_2 = response_2.get('batchNumber')
                logger.debug(f"From response fetch batch_number for second  txn: {api_batch_number_2}")
                api_pmt_card_brand_2 = response_2.get('paymentCardBrand')
                logger.debug(f"From response fetch payment_card_brand for second  txn: {api_pmt_card_brand_2}")
                api_pmt_card_type_2 = response_2.get('paymentCardType')
                logger.debug(f"From response fetch payment_card_type for second  txn: {api_pmt_card_type_2}")
                api_date_time_2 = response_2.get('createdTime')
                logger.debug(f"From response fetch date_time for second  txn: {api_date_time_2}")
                api_device_serial_2 = response_2.get('deviceSerial')
                logger.debug(f"From response fetch device_serial for second  txn: {api_device_serial_2}")
                api_card_txn_type_desc_2 = response_2.get('cardTxnTypeDesc')
                logger.debug(f"From response fetch card_txn_type_desc for second  txn: {api_card_txn_type_desc_2}")
                api_merchant_name_2 = response_2.get('merchantName')
                logger.debug(f"From response fetch merchant_name for second  txn: {api_merchant_name_2}")
                api_card_last_four_digit_2 = response_2.get('cardLastFourDigit')
                logger.debug(f"From response fetch card_last_four_digit for second  txn: {api_card_last_four_digit_2}")
                api_ext_ref_number_2 = response_2.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for second  txn: {api_ext_ref_number_2}")
                api_pmt_card_bin_2 = response_2.get('paymentCardBin')
                logger.debug(f"From response fetch payment_card_bin for second  txn: {api_pmt_card_bin_2}")
                api_display_pan_2 = response_2.get('displayPAN')
                logger.debug(f"From response fetch display_pan for second  txn: {api_display_pan_2}")
                api_auth_code_2 = response_2.get('authCode')
                logger.debug(f"From response fetch auth_code for second  txn: {api_auth_code_2}")
                api_card_type_2 = response_2.get('cardType')
                logger.debug(f"From response fetch card_type for second  txn: {api_card_type_2}")
                api_customer_name_2 = response_2.get('customerName')
                logger.debug(f"From response fetch customer_name for second  txn: {api_customer_name_2}")
                api_payer_name_2 = response_2.get('payerName')
                logger.debug(f"From response fetch payer_name for second  txn: {api_payer_name_2}")
                api_name_on_card_2 = response_2.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card for second  txn: {api_name_on_card_2}")
                api_payment_gateway_2 = response_2.get('paymentGateway')
                logger.debug(f"From response fetch paymentGateway for second  txn : {api_payment_gateway_2}")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "customer_mobile": api_customer_mobile,
                    "pmt_gateway": api_payment_gateway,
                    "auth_code": api_auth_code,

                    "txn_amt_2": api_amount_2,
                    "pmt_mode_2": api_payment_mode_2,
                    "pmt_status_2": api_payment_status_2,
                    "pmt_state_2": api_payment_state_2,
                    "mid_2": api_mid_2,
                    "tid_2": api_tid_2,
                    "acquirer_code_2": api_acquirer_code_2,
                    "settle_status_2": api_settle_status_2,
                    "rrn_2": api_rrn_2,
                    "issuer_code_2": api_issuer_code_2,
                    "txn_type_2": api_txn_type_2,
                    "org_code_2": api_org_code_2,
                    "batch_number_2": api_batch_number_2,
                    "pmt_card_brand_2": api_pmt_card_brand_2,
                    "pmt_card_type_2": api_pmt_card_type_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_2),
                    "device_serial_2": api_device_serial_2,
                    "card_txn_type_desc_2": api_card_txn_type_desc_2,
                    "auth_code_2": api_auth_code_2,
                    "card_last_four_digit_2": api_card_last_four_digit_2,
                    "ext_ref_number_2": api_ext_ref_number_2,
                    "merchant_name_2": api_merchant_name_2,
                    "pmt_card_bin_2": api_pmt_card_bin_2,
                    "card_type_2": api_card_type_2,
                    "display_pan_2": api_display_pan_2,
                    "customer_name_2": api_customer_name_2,
                    "payer_name_2": api_payer_name_2,
                    "name_on_card_2": api_name_on_card_2,
                    "pmt_gateway_2": api_payment_gateway_2
                }
                logger.debug(f"actual_api_values: {actual_api_values}")

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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "pmt_gateway": "RAZORPAY",
                    "pmt_intent_status": "COMPLETED",

                    "cnp_pmt_option": "CNP_CC",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "cnp_pmt_state": "SETTLED",
                    "cnp_pmt_card_bin": "526731",
                    "cnp_pmt_card_brand": "MASTER_CARD",
                    "cnp_pmt_card_type": "CREDIT",
                    "cnp_acquirer_code": "HDFC",
                    "cnp_issuer_code": "HDFC",
                    "cnp_card_last_four_digit": "5449",
                    "cnp_org_code": org_code,
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "cnpware_pmt_status": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state": "SETTLED",
                    "cnpware_pmt_mode": "CNP",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_gateway": "RAZORPAY",
                    "cnpware_txn_type": "REMOTE_PAY",

                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "payer_name_2": "L3TEST/CARD0025",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "HDFC",
                    "txn_type_2": "CHARGE",
                    "settle_status_2": "PENDING",
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "device_serial_2": device_serial,
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "476173",
                    "terminal_info_id_2": terminal_info_id,
                    "card_txn_type_2": "02",
                    "card_last_four_digit_2": "0250",
                    "customer_name_2": "L3TEST/CARD0025"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "settle_status": settle_status,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "pmt_gateway": payment_gateway,
                    "pmt_intent_status": payment_intent_status,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_pmt_card_bin": cnp_txn_payment_card_bin,
                    "cnp_pmt_card_brand": cnp_txn_payment_card_brand,
                    "cnp_pmt_card_type": cnp_txn_payment_card_type,
                    "cnp_acquirer_code": cnp_txn_acquirer_code,
                    "cnp_issuer_code": cnp_txn_issuer_code,
                    "cnp_card_last_four_digit": cnp_txn_card_last_four_digit,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "cnpware_pmt_status": cnpware_txn_payment_status,
                    "cnpware_pmt_state": cnpware_txn_payment_state,
                    "cnpware_pmt_mode": cnpware_txn_payment_mode,
                    "cnpware_pmt_flow": cnpware_txn_payment_flow,
                    "cnpware_pmt_gateway": cnpware_txn_payment_gateway,
                    "cnpware_txn_type": cnpware_txn_type,

                    "txn_amt_2": amount_txn_2,
                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": pmt_status_2,
                    "pmt_state_2": pmt_state_2,
                    "acquirer_code_2": acquirer_code_2,
                    "issuer_code_2": issuer_code_txn_2,
                    "payer_name_2": payer_name_2,
                    "mid_2": mid_txn_2,
                    "tid_2": tid_txn_2,
                    "pmt_gateway_2": payment_gateway_2,
                    "txn_type_2": txn_type_2,
                    "settle_status_2": settle_status_2,
                    "pmt_card_brand_2": pmt_card_brand_2,
                    "pmt_card_type_2": pmt_card_type_2,
                    "device_serial_2": device_serial_txn_2,
                    "order_id_2": order_id_txn_2,
                    "org_code_2": org_code_txn_2,
                    "pmt_card_bin_2": pmt_card_bin_2,
                    "terminal_info_id_2": terminal_info_id_txn_2,
                    "card_txn_type_2": card_txn_type_2,
                    "card_last_four_digit_2": card_last_four_digit_2,
                    "customer_name_2": customer_name_txn_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "rrn_2": rrn_2,
                    "auth_code_2": auth_code_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                logger.info(f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[1]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[1]['Total Amount']
                logger.info(f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_rrn = transaction_details[1]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[1]['Type']
                logger.info(f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[1]['Status']
                logger.info(f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[1]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")
                portal_auth_code = transaction_details[1]['Auth Code']
                logger.info(f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")

                portal_date_time_2 = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time_2}")
                portal_txn_id_2 = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id_2}")
                portal_total_amount_2 = transaction_details[0]['Total Amount']
                logger.info(f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount_2}")
                portal_rrn_2 = transaction_details[0]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn_2}")
                portal_txn_type_2 = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type_2}")
                portal_txn_status_2 = transaction_details[0]['Status']
                logger.info(f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status_2}")
                portal_user_2 = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user_2}")
                portal_auth_code_2 = transaction_details[0]['Auth Code']
                logger.info(f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code_2}")

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "rrn": portal_rrn,
                    "auth_code": portal_auth_code,

                    "date_time_2": portal_date_time_2,
                    "pmt_status_2": portal_txn_status_2,
                    "pmt_type_2": portal_txn_type_2,
                    "txn_amt_2": portal_total_amount_2.split(' ')[1],
                    "username_2": portal_user_2,
                    "txn_id_2": portal_txn_id_2,
                    "rrn_2": portal_rrn_2,
                    "auth_code_2": portal_auth_code_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)
                expected_charge_slip_values = {
                    "payment_option": "SALE",
                    "merchant_ref_no": 'Ref # ' + str(order_id),
                    "RRN": "" if rrn is None else rrn,
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "MID": mid_txn,
                    "TID": tid_txn,
                    "time": txn_time,
                    "CARD": f"XXXX-XXXX-XXXX-5449",
                    "CARD TYPE": "MasterCard",
                    "AUTH CODE": str(auth_code).strip(),
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                charge_slip_val_result = receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)

                expected_charge_slip_values_2 = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date_2,
                    "time": txn_time_2,
                    "RRN": rrn_2,
                    "AUTH CODE": str(auth_code_2).strip(),
                    "CARD TYPE": "VISA",
                    "BATCH NO": batch_number_2,
                    "TID": tid,
                    "payment_option": "DEBIT SALE",
                    "CARD": f"XXXX-XXXX-XXXX-0250 EMV"
                }
                logger.debug(f"expected_charge_slip_values_2: {expected_charge_slip_values_2}")
                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2,
                                                                                             credentials={
                                                                                                 "username": app_username,
                                                                                                 "password": app_password
                                                                                             },
                                                                                             expected_details=expected_charge_slip_values_2)

                if charge_slip_val_result and charge_slip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'
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
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["duplicatePaymentCheckEnabledAcrossPaymentModes"] = "false"
            api_details["RequestBody"]["settings"][
                "duplicatePaymentFields"] = "paymentMode,username,processCode,txnType,amount"
            api_details["RequestBody"]["settings"]["duplicateIntervalForOnlinePayment"] = ""
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for duplicate payment setup to be disabled:  {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_100_103_419():
    """
    Sub Feature Code: UI_Common_PM_CNP_Remotepay_Razorpay_Max_Pay_Attempts_Two_First_Txn_Netbanking_Failed_Second_Txn_Netbanking_Success
    Sub Feature Description: Verify 2nd transaction is successful with Net Banking when first Net Banking txn is cancelled
    TC naming code description: 100: Payment Method, 103: RemotePay, 419: TC_419
    """
    expected_success_message = "Your payment is successfully completed! You may close the browser now."
    expected_failed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications."
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
        query = f"update remotepay_setting set setting_value= '2' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
        logger.debug(f"Query to update remotepay_setting table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")
        refresh_db()
        logger.debug(f"Refreshing the db after updating the remotepay setting")
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
            amount = random.randint(900, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                logger.info(f"Response from initiate api is: {response}")
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn_1 = RemotePayTxnPage(page)
                remote_pay_txn_1.remote_pay_netbanking()
                remote_pay_txn_1.remote_pay_click_and_expand_netbanking()
                remote_pay_txn_1.remote_pay_select_netbanking_Rzp()
                remote_pay_txn_1.remote_pay_proceed_netbanking()
                remote_pay_txn_1.click_failure_pmt_btn()
                failed_message = str(remote_pay_txn_1.failureScreenMessage())
                logger.info(f"Failed message is:  {failed_message}")
                logger.info(f"Expected success message is:  {expected_success_message}")
                assert failed_message == expected_failed_message, "Failed Message is not matching."

                query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                        f"desc limit 1 "
                logger.debug(f"Query to fetch txn details from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                txn_id = result['id'].values[0]
                logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn_2 = RemotePayTxnPage(page)
                remote_pay_txn_2.remote_pay_netbanking()
                remote_pay_txn_2.remote_pay_click_and_expand_netbanking()
                remote_pay_txn_2.remote_pay_select_netbanking_Rzp()
                remote_pay_txn_2.remote_pay_proceed_netbanking()
                remote_pay_txn_2.click_success_pmt_btn()
                success_message = str(remote_pay_txn_2.succcessScreenMessage())
                logger.info(f"Your success message is:  {success_message}")
                logger.info(f"Your expected success message is:  {expected_success_message}")
                assert success_message == expected_success_message, "Success Message is not matching."

                query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                        f"desc limit 1 "
                logger.debug(f"Query to fetch txn details from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                txn_id_2 = result['id'].values[0]
                logger.debug(f"Fetching txn_id from the txn table : {txn_id_2}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch txn details from the txn table for failed txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                settle_status = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status from the txn table for failed txn: {settle_status}")
                pmt_status = result['status'].values[0]
                logger.debug(f"Fetching status from the txn table for failed txn: {pmt_status}")
                payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from the txn table for failed txn: {payment_mode}")
                pmt_state = result['state'].values[0]
                logger.debug(f"Fetching state from the txn table for failed txn: {pmt_state}")
                amount_txn = result['amount'].values[0]
                logger.debug(f"Fetching amount from the txn table for failed txn: {amount_txn}")
                order_id_txn = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from the txn table for failed txn: {order_id_txn}")
                payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from the txn table for failed txn: {payment_gateway}")

                query = f"select * from txn where id='{txn_id_2}'"
                logger.debug(f"Query to fetch txn details from the txn table for success txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                settle_status_2 = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status from the txn table for success txn: {settle_status_2}")
                pmt_status_2 = result['status'].values[0]
                logger.debug(f"Fetching status from the txn table for success txn: {pmt_status_2}")
                payment_mode_2 = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from the txn table for success txn: {payment_mode_2}")
                pmt_state_2 = result['state'].values[0]
                logger.debug(f"Fetching state from the txn table for success txn: {pmt_state_2}")
                amount_txn_2 = result['amount'].values[0]
                logger.debug(f"Fetching amount from the txn table for success txn: {amount_txn_2}")
                order_id_txn_2 = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from the txn table for success txn: {order_id_txn_2}")
                payment_gateway_2 = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from the txn table for success txn: {payment_gateway_2}")

                query = f"select * from cnp_txn where txn_id = '{txn_id}'"
                logger.debug(f"Query to fetch data from the cnp_txn table for failed txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result for cnp_txn table : {result} ")
                cnp_txn_payment_option = result['payment_option'].values[0]
                logger.debug(f"Fetching payment_option from cnp_txn table for failed txn: {cnp_txn_payment_option}")
                cnp_txn_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnp_txn table for failed txn: {cnp_txn_payment_flow}")
                cnp_txn_payment_status = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnp_txn table for failed txn: {cnp_txn_payment_status}")
                cnp_txn_type = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnp_txn table for failed txn: {cnp_txn_type}")
                cnp_txn_payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnp_txn table for failed txn: {cnp_txn_payment_mode}")
                cnp_txn_payment_state = result['state'].values[0]
                logger.debug(f"Fetching state from cnp_txn table for failed txn: {cnp_txn_payment_state}")
                cnp_txn_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from cnp_txn table for failed txn: {cnp_txn_payment_gateway}")

                query = f"select * from cnp_txn where txn_id = '{txn_id_2}'"
                logger.debug(f"Query to fetch data from the cnp_txn table for success txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result for cnp_txn table : {result} ")
                cnp_txn_payment_option_2 = result['payment_option'].values[0]
                logger.debug(f"Fetching payment_option from cnp_txn table for success txn: {cnp_txn_payment_option_2}")
                cnp_txn_payment_flow_2 = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnp_txn table for success txn: {cnp_txn_payment_flow_2}")
                cnp_txn_payment_status_2 = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnp_txn table for success txn: {cnp_txn_payment_status_2}")
                cnp_txn_type_2 = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnp_txn table for success txn: {cnp_txn_type_2}")
                cnp_txn_payment_mode_2 = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnp_txn table for success txn: {cnp_txn_payment_mode_2}")
                cnp_txn_payment_state_2 = result['state'].values[0]
                logger.debug(f"Fetching state from cnp_txn table for success txn: {cnp_txn_payment_state_2}")
                cnp_txn_payment_gateway_2 = result['payment_gateway'].values[0]
                logger.debug(
                    f"Fetching payment_gateway from cnp_txn table for success txn: {cnp_txn_payment_gateway_2}")

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
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "CNP",
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "FAILED",
                    "pmt_gateway": "RAZORPAY",
                    "cnp_pmt_option": "CNP_NB",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_FAILED",
                    "cnp_pmt_state": "FAILED",
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "CNP",
                    "txn_amt_2": float(amount),
                    "order_id_2": order_id,
                    "settle_status_2": "SETTLED",
                    "pmt_gateway_2": "RAZORPAY",
                    "cnp_pmt_option_2": "CNP_NB",
                    "cnp_pmt_flow_2": "REMOTEPAY",
                    "cnp_pmt_status_2": "PAYMENT_COMPLETED",
                    "cnp_pmt_state_2": "SETTLED",
                    "cnp_txn_type_2": "REMOTE_PAY",
                    "cnp_pmt_mode_2": "CNP",
                    "cnp_pmt_gateway_2": "RAZORPAY",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "settle_status": settle_status,
                    "pmt_gateway": payment_gateway,
                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "pmt_status_2": pmt_status_2,
                    "pmt_state_2": pmt_state_2,
                    "pmt_mode_2": payment_mode_2,
                    "txn_amt_2": amount_txn_2,
                    "order_id_2": order_id_txn_2,
                    "settle_status_2": settle_status_2,
                    "pmt_gateway_2": payment_gateway_2,
                    "cnp_pmt_option_2": cnp_txn_payment_option_2,
                    "cnp_pmt_flow_2": cnp_txn_payment_flow_2,
                    "cnp_pmt_status_2": cnp_txn_payment_status_2,
                    "cnp_pmt_state_2": cnp_txn_payment_state_2,
                    "cnp_txn_type_2": cnp_txn_type_2,
                    "cnp_pmt_mode_2": cnp_txn_payment_mode_2,
                    "cnp_pmt_gateway_2": cnp_txn_payment_gateway_2,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


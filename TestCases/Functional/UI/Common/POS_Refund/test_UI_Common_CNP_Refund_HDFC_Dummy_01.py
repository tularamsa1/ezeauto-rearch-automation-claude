import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_LoginPage import LoginPage
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.portal_remotePayPage import RemotePayTxnPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_320():
    """
        Sub Feature Code: UI_Common_Mpos_Refund_From_POS_Validate_Full_Refund_CNP
        Sub Feature Description: Verify the user can perform a full refund for CNP transactions using Refund from POS
        TC naming code description: 100: Payment Method, 103: RemotePay, 320: TC320
    """
    expectedMessage = "Your payment is successfully completed! You may close the browser now."

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from org_employee table : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            logger.debug(f"Randomly generated amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Randomly generated order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API DETAILS for remote_pay_Initiate api : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received from remote_pay_initiate api : {response}")

            # verify whether link is generated or not
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn payment link")
            else:
                paymentLinkUrl = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"Initializing the browser")
                page.goto(paymentLinkUrl, timeout=60000)
                logger.info(f"Initializing the payment link in the browser : {paymentLinkUrl}")
                remotePayTxn = RemotePayTxnPage(page)
                remotePayTxn.clickOnCreditCardToExpand()
                remotePayTxn.enterNameOnTheCard("EzeAuto Test")
                logger.info(f"Entered the name on the card")
                remotePayTxn.enterCreditCardNumber("4000 0000 0000 1091")
                logger.info(f"Entered the credit card details on card")
                remotePayTxn.enterCreditCardExpiryMonth("3")
                logger.info(f"Entered the credit card expiry month on card")
                remotePayTxn.enterCreditCardExpiryYear("2048")
                logger.info(f"Entered the credit card expiry year on card")
                remotePayTxn.enterCreditCardCvv("111")
                logger.info(f"Entered the credit card cvv on card")
                remotePayTxn.clickOnProceedToPay()
                logger.info(f"Clicked on proceed button")
                remotePayTxn.switch_to_iframe()
                successMessage = str(remotePayTxn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {successMessage}")
                logger.info(f"Your expiryMessage is :  {expectedMessage}")
                if successMessage == expectedMessage:
                    pass
                else:
                    raise Exception("Success Message is not matching.")

            query = "select id from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch txn_id value from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching original txn_id value from txn table : {txn_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username: {app_username} and password: {app_password}")
            homePage = HomePage(app_driver)
            homePage.wait_for_navigation_to_load()
            homePage.wait_for_home_page_load()
            logger.debug("Waiting completed for txn history page.")
            homePage.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
            logger.debug(f"Clicking on refund button on app side")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side")
            payment_page.click_on_refund_full_amt()
            logger.debug(f"Clicked on refund full amount")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button and refunded full amount")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm the refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for original txn : {txn_id} : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from txn table for original txn : {txn_id} : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for original txn : {txn_id} : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from value from txn table for original txn : {txn_id} : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for original txn : {txn_id} : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for original txn : {txn_id} : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for original txn : {txn_id} : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for original txn : {txn_id} : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for original txn : {txn_id} : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for original txn : {txn_id} : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for original txn : {txn_id} : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for original txn : {txn_id} : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug( f"Fetching settlement status value from txn table for original txn : {txn_id} : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial value from txn table for original txn : {txn_id} : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for original txn : {txn_id} : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand value from txn table for original txn : {txn_id} : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type value from txn table for original txn : {txn_id} : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number value from txn table for original txn : {txn_id} : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for original txn : {txn_id} : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code value from txn table for original txn : {txn_id} : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for original txn : {txn_id} : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number value from txn table for original txn : {txn_id} : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id value from txn table for original txn : {txn_id} : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for original txn : {txn_id} : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type value from txn table for original txn : {txn_id} : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit value from txn table for original txn : {txn_id} : {card_last_four_digit_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for original txn : {txn_id} : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for original txn : {txn_id} : {payer_name_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name value from txn table for original txn : {txn_id} : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for original txn : {txn_id} : {posting_date}")
            auth_code_db = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from txn table for original txn : {txn_id} : {auth_code_db}")

            query = "select * from merchant_pg_config where org_code = '" + str(
                org_code) + "' and payment_gateway = 'CYBERSOURCE'"
            logger.debug(f"Query to fetch data from merchant_pg_config table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from merchant_pg_config table : {result}")
            tid_settings = result['tid'].values[0]
            logger.debug(f"Fetching tid value from merchant_pg_config table : {tid_settings}")

            query = "select * from terminal_info where tid='" + str(tid_settings) + "';"
            logger.debug(f"Query to fetch data from terminal_info table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from terminal_info table : {result}")
            terminal_info_id = result['id'].values[0]
            logger.debug(f"Fetching id value from terminal_info table : {terminal_info_id}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch data from cnp_txn table for original_txn_id : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from cnp_txn table for original_txn_id : {result}")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_no value from cnp_txn table for original_txn_id : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Fetching state value from cnp_txn table for original_txn_id : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from cnp_txn table for original_txn_id : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from cnp_txn table for original_txn_id : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from cnp_txn table for original_txn_id : {cnp_payment_gateway}")
            cnp_state_txn = result['state'].values[0]
            logger.debug(f"Fetching state value from cnp_txn table for original_txn_id : {cnp_state_txn}")

            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch data from cnpware_txn table for original_txn_id : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Query result from cnpware_txn table for original_txn_id : {result}")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type value from cnpware_txn table for original_txn_id : {cnpware_txn_txn_type}")
            cnpware_txn_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type value from cnpware_txn table for original_txn_id : {cnpware_txn_card_type}")
            cnpware_txn_state = result['state'].values[0]
            logger.debug(f"Fetching state value from cnpware_txn table for original_txn_id : {cnpware_txn_state}")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from cnpware_txn table for original_txn_id : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow value from cnpware_txn table for original_txn_id : {cnpware_payment_flow}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for refund txn : {result}")
            txn_id_2 = result["id"].iloc[0]
            logger.debug(f"Query to fetch data from txn table for refund txn {txn_id_2} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query to fetch result from txn table for refund txn : {result}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for refund txn : {auth_code_2}")
            original_amt_db_2 = int(result["amount_original"].iloc[0])
            logger.debug(f"Fetching amount_original from value from txn table for refund txn : {original_amt_db_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for refund txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from txn table for refund txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for refund txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for refund txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for refund txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for refund txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for refund txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for refund txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for refund txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table fro refund txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for refund txn : {settlement_status_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for refund txn : {merchant_code_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for refund txn : {order_id_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for refund txn : {org_code_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for refund txn : {txn_type_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for refund txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for refund txn : {payer_name_db_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for refund txn : {posting_date_2}")

            query = "select * from cnp_txn where txn_id='" + txn_id_2 + "';"
            logger.debug(f"Query to fetch data from cnp_txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from cnp_txn table for refund txn : {result}")
            cnp_txn_rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_no value from cnp_txn table for refund txn : {cnp_txn_rrn_2}")
            cnp_txn_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state value from cnp_txn table for refund txn : {cnp_txn_state_2}")
            cnp_txn_acquirer_code_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from cnp_txn table for refund txn : {cnp_txn_acquirer_code_2}")
            cnp_txn_auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from cnp_txn table for refund txn : {cnp_txn_auth_code_2}")
            cnp_payment_gateway_2 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from cnp_txn table for refund txn : {cnp_payment_gateway_2}")
            cnp_state_txn_2 = result['state'].values[0]
            logger.debug(f"Fetching state value from cnp_txn table for refund txn : {cnp_state_txn_2}")

            query = "select * from cnpware_txn where txn_id='" + txn_id_2 + "';"
            logger.debug(f"Query to fetch data from cnpware_txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Query result from cnpware_txn table for refund txn : {result}")
            cnpware_txn_txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type value from cnpware_txn table for refund txn : {cnpware_txn_txn_type_2}")
            cnpware_txn_card_type_2 = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type value from cnpware_txn table for refund txn : {cnpware_txn_card_type_2}")
            cnpware_txn_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state value from cnpware_txn table for refund txn : {cnpware_txn_state_2}")
            cnpware_payment_gateway_2 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from cnpware_txn table for refund txn : {cnpware_payment_gateway_2}")
            cnpware_payment_flow_2 = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow value from cnpware_txn table for refund txn : {cnpware_payment_flow_2}")

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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=posting_date)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=posting_date_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "PAY LINK",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED REFUNDED",
                    "rrn": str(cnp_txn_rrn),
                    "auth_code": auth_code_db,
                    "order_id": order_id,
                    "pmt_msg": "REFUND SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "customer_name": customer_name_db,
                    "date": date_and_time_app,

                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "PAY LINK",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(cnp_txn_rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "settle_status_2": "SETTLED",
                    "customer_name_2": customer_name_db_2,
                    "date_2": date_and_time_app_2
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund transaction")
                login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
                home_page = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for original_txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for original_txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for original_txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for original_txn : {txn_id}, {payment_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for original_txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for original_txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for original_txn : {txn_id}, {app_settlement_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for original_txn : {txn_id}, {app_date_and_time}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for original_txn : {txn_id}, {app_customer_name}")
                txn_history_page.scroll_to_text_element(value="RR NUMBER")
                logger.debug(f"Scrolled to RR Number element")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for original_txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for refunded txn : {txn_id_2}, {payment_status_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for refunded txn : {txn_id_2}, {app_customer_name_2}")
                txn_history_page.scroll_to_text_element(value="RR NUMBER")
                logger.debug(f"Scrolled to RR Number element")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for refunded txn : {txn_id_2}, {app_rrn_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rrn": app_rrn,
                    "auth_code": app_auth_code,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "date": app_date_and_time,
                    "customer_name": app_customer_name,

                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "date_2": app_date_and_time_2,
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "CNP",
                    "pmt_mode_2": "CNP",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "customer_name": customer_name_db,
                    "customer_name_2": customer_name_db_2,
                    "payer_name": payer_name_db,
                    "payer_name_2": payer_name_db_2,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "rrn": str(cnp_txn_rrn),
                    "rrn_2": str(cnp_txn_rrn_2),
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type_db,
                    "org_code": org_code_db,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": txn_type_db_2,
                    "org_code_2": org_code_db_2,
                    "auth_code": auth_code_db,
                    "date": date_and_time_api,
                    "date_2": date_and_time_api_2,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status value from original txn_id : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount value from original txn_id : {amount_api}")
                original_amount_api = float(response_1["amount"])
                logger.debug(f"Fetching original_amt value from original txn_id : {original_amount_api}")
                total_amt_api = float(response_1["totalAmount"])
                logger.debug(f"Fetching total_amt value from original txn_id : {total_amt_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode value from original txn_id : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state value from original txn_id : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn value from original txn_id : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from original txn_id : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer_code value from original txn_id : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from original txn_id : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org_code value from original txn_id : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid value from original txn_id : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid value from original txn_id : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction_type value from original txn_id : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth_code value from original txn_id : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date_and_time value from original txn_id : {date_and_time_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username value from original txn_id : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction_id value from original txn_id : {txn_id_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from original txn_id : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant_name value from original txn_id : {merchant_name_api}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching payer_name value from original txn_id : {customer_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer_name value from original txn_id : {payer_name_api}")
                order_id_api = response_1["orderNumber"]
                logger.debug(f"Fetching orderNumber value from original txn_id : {order_id_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status value from refunded txn_id : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount value from refunded txn_id : {amount_api_2}")
                original_amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching original_amt value from refunded txn_id : {original_amount_api_2}")
                total_amt_api_2 = float(response_2["totalAmount"])
                logger.debug(f"Fetching total_amt value from refunded txn_id : {total_amt_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment_mode value from refunded txn_id : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state value from refunded txn_id : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn value from refunded txn_id : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from refunded txn_id : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from refunded txn_id : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org_code value from refunded txn_id : {org_code_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction_type value from refunded txn_id : {txn_type_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date_and_time value from refunded txn_id : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username value from refunded txn_id : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction_id value from refunded txn_id : {txn_id_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching payer_name value from refunded txn_id : {customer_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer_name value from refunded txn_id : {payer_name_api_2}")
                order_id_api_2 = response_1["orderNumber"]
                logger.debug(f"Fetching orderNumber value from refunded txn_id : {order_id_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "pmt_status_2": status_api_2,
                    "pmt_state": state_api,
                    "pmt_state_2": state_api_2,
                    "pmt_mode": payment_mode_api,
                    "pmt_mode_2": payment_mode_api_2,
                    "settle_status": settlement_status_api,
                    "settle_status_2": settlement_status_api_2,
                    "txn_amt": amount_api,
                    "txn_amt_2": amount_api_2,
                    "customer_name": customer_name_api,
                    "customer_name_2": customer_name_api_2,
                    "payer_name": payer_name_api,
                    "payer_name_2": payer_name_api_2,
                    "order_id": order_id_api,
                    "order_id_2": order_id_api_2,
                    "rrn": str(rrn_api),
                    "rrn_2": str(rrn_api_2),
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "org_code_2": org_code_api_2,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
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
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "CNP",
                    "pmt_mode_2": "CNP",
                    "txn_amt": amount,
                    "txn_amt_2": amount,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "cnp_txn_state": "REFUNDED",
                    "cnp_txn_state_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "pmt_gateway": "CYBERSOURCE",
                    "pmt_gateway_2": "CYBERSOURCE",
                    "cnpware_txn_type": "REMOTE_PAY",
                    "cnpware_txn_type_2": "REFUND",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_flow_2": "None"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": payment_status_db,
                    "pmt_status_2": payment_status_db_2,
                    "pmt_state": payment_state_db,
                    "pmt_state_2": payment_state_db_2,
                    "pmt_mode": payment_mode_db,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt": amount_db,
                    "txn_amt_2": amount_db_2,
                    "order_id": order_id_db,
                    "order_id_2": order_id_db_2,
                    "cnp_txn_state": cnp_state_txn,
                    "cnp_txn_state_2": cnp_state_txn_2,
                    "settle_status": settlement_status_db,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code": acquirer_code_db,
                    "acquirer_code_2": acquirer_code_db_2,
                    "pmt_gateway": payment_gateway_db,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "cnpware_txn_type": txn_type_db,
                    "cnpware_txn_type_2": txn_type_db_2,
                    "cnpware_pmt_flow": cnpware_payment_flow,
                    "cnpware_pmt_flow_2": str(cnpware_payment_flow_2)
                }
                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=created_time_2)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(cnp_txn_rrn_2),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "payment_option": "REFUND",
                    "date": txn_date,
                    "time": txn_time
                }
                logger.info(f"expected_charge_slip_values : {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
                    "username": app_username, "password": app_password}, expected_details=expected_charge_slip_values)

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_321():
    """
        Sub Feature Code: UI_Common_Mpos_Refund_From_POS_Validate_Partial_Refund_CNP
        Sub Feature Description: Verify the user can perform a partial refund for CNP transactions using Refund from POS
        TC naming code description: 100: Payment Method, 103: RemotePay, 321: TC321
    """
    expectedMessage = "Your payment is successfully completed! You may close the browser now."

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result from the org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"org_code value from org_employee table : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            logger.debug(f"Randomly generated amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Randomly generated order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API DETAILS for remote_pay_initiate api : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received from remote_pay_initiate api : {response}")

            # verify whether link is generated or not
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn payment link")
            else:
                paymentLinkUrl = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                logger.info(f"Initializing the browser")
                page.goto(paymentLinkUrl, timeout=60000)
                logger.info(f"Initializing the payment link in the browser : {paymentLinkUrl}")
                remotePayTxn = RemotePayTxnPage(page)
                remotePayTxn.clickOnCreditCardToExpand()
                remotePayTxn.enterNameOnTheCard("EzeAuto Test")
                logger.info(f"Entered the name on the card")
                remotePayTxn.enterCreditCardNumber("4000 0000 0000 1091")
                logger.info(f"Entered the credit card details on card")
                remotePayTxn.enterCreditCardExpiryMonth("3")
                logger.info(f"Entered the credit card expiry month on card")
                remotePayTxn.enterCreditCardExpiryYear("2048")
                logger.info(f"Entered the credit card expiry year on card")
                remotePayTxn.enterCreditCardCvv("111")
                logger.info(f"Entered the credit card cvv on card")
                remotePayTxn.clickOnProceedToPay()
                logger.info(f"Clicked on proceed button")
                remotePayTxn.switch_to_iframe()
                successMessage = str(remotePayTxn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {successMessage}")
                logger.info(f"Your expiryMessage is:  {expectedMessage}")
                if successMessage == expectedMessage:
                    pass
                else:
                    raise Exception("Success Message is not matching.")

            query = "select id from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch txn_id value from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching original txn_id value from txn table : {txn_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.debug(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            homePage = HomePage(app_driver)
            homePage.wait_for_navigation_to_load()
            homePage.wait_for_home_page_load()
            logger.debug("Waiting completed for txn history page.")
            homePage.click_on_history()
            txn_history_page = TransHistoryPage(driver=app_driver)
            txn_history_page.click_on_txn_by_txn_id(txn_id=txn_id)
            logger.debug(f"Clicking on refund button on app side")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_refund_btn()
            logger.debug(f"Clicked on refund button on app side")
            payment_page.click_on_confirm_refund_btn()
            logger.debug(f"Clicked on confirm refund button on app side")
            manually_enter_amt = amount - 100
            logger.debug(f"Manually entered amount is : {manually_enter_amt}")
            logger.debug(f"Clicking on refund amount manually radio button")
            payment_page.click_on_refund_amt_manually()
            logger.debug(f"Click on refund amount manually radio button")
            logger.debug(f"Entering amount manually for refund amount manually : {manually_enter_amt}")
            payment_page.enter_refund_amt_manually(amount=manually_enter_amt)
            logger.debug(f"Entered amount manually for refund amount manually : {manually_enter_amt}")
            payment_page.click_on_refund_txn_btn()
            logger.debug(f"Clicked on refund txn button and refunded full amount")
            payment_page.enter_password_to_confirm(app_password)
            logger.debug(f"Entered password to confirm the refund")
            txn_history_page.click_back_Btn()
            logger.debug(f"Clicked on txn history back button")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result for original txn : {result}")
            auth_code_db = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for original txn : {auth_code_db}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for original txn : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from value from txn table for original txn : {amount_db}")
            original_amt_db = int(result["amount_original"].iloc[0])
            logger.debug(f"Fetching amount_original from value from txn table for original txn : {original_amt_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for original txn : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for original txn : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for original txn : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for original txn : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for original txn : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for original txn : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for original txn : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table for original txn : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for original txn : {settlement_status_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for original txn : {merchant_code_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for original txn : {order_id_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for original txn : {org_code_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for original txn : {txn_type_db}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for original txn : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for original txn : {payer_name_db}")
            merchant_name_db = result['merchant_name'].iloc[0]
            logger.debug(f"Fetching merchant_name value from txn table for original txn : {merchant_name_db}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for original txn : {posting_date}")

            query = "select * from merchant_pg_config where org_code = '" + str(
                org_code) + "' and payment_gateway = 'CYBERSOURCE'"
            logger.debug(f"Query to fetch data from merchant_pg_config table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from merchant_pg_config table : {result}")
            tid_settings = result['tid'].values[0]
            logger.debug(f"Fetching tid value from merchant_pg_config table : {tid_settings}")

            query = "select * from terminal_info where tid='" + str(tid_settings) + "';"
            logger.debug(f"Query to fetch data from terminal_info table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from terminal_info table : {result}")
            terminal_info_id = result['id'].values[0]
            logger.debug(f"Fetching id value from terminal_info table : {terminal_info_id}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch data from cnp_txn table for original_txn_id : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from cnp_txn table for original_txn_id : {result}")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_no value from cnp_txn table for original_txn_id : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Fetching state value from cnp_txn table for original_txn_id : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from cnp_txn table for original_txn_id : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from cnp_txn table for original_txn_id : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from cnp_txn table for original_txn_id : {cnp_payment_gateway}")
            cnp_state_txn = result['state'].values[0]
            logger.debug(f"Fetching state value from cnp_txn table for original_txn_id : {cnp_state_txn}")

            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch data from cnpware_txn table for original_txn_id : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Query result from cnpware_txn table for original_txn_id : {result}")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type value from cnpware_txn table for original_txn_id : {cnpware_txn_txn_type}")
            cnpware_txn_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type value from cnpware_txn table for original_txn_id : {cnpware_txn_card_type}")
            cnpware_txn_state = result['state'].values[0]
            logger.debug(f"Fetching state value from cnpware_txn table for original_txn_id : {cnpware_txn_state}")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from cnpware_txn table for original_txn_id : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow value from cnpware_txn table for original_txn_id : {cnpware_payment_flow}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query result from txn table for refund txn : {result}")
            txn_id_2 = result["id"].iloc[0]
            logger.debug(f"Query to fetch data from txn table for refund txn {txn_id_2} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Query to fetch result from txn table for refund txn : {result}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code value from txn table for refund txn : {auth_code_2}")
            original_amt_db_2 = int(result["amount_original"].iloc[0])
            logger.debug(f"Fetching amount_original from value from txn table for refund txn : {original_amt_db_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from txn table for refund txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount value from txn table for refund txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode value from txn table for refund txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status value from txn table for refund txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state value from txn table for refund txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code value from txn table for refund txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid value from txn table for refund txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid value from txn table for refund txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway value from txn table for refund txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn value from txn table fro refund txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status value from txn table for refund txn : {settlement_status_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code value from txn table for refund txn : {merchant_code_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id value from txn table for refund txn : {order_id_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code value from txn table for refund txn : {org_code_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type value from txn table for refund txn : {txn_type_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name value from txn table for refund txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name value from txn table for refund txn : {payer_name_db_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from txn table for refund txn : {posting_date_2}")

            query = "select * from cnp_txn where txn_id='" + txn_id_2 + "';"
            logger.debug(f"Query to fetch data from cnp_txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from cnp_txn table for refund txn : {result}")
            cnp_txn_rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_no value from cnp_txn table for refund txn : {cnp_txn_rrn_2}")
            cnp_txn_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state value from cnp_txn table for refund txn : {cnp_txn_state_2}")
            cnp_txn_acquirer_code_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code value from cnp_txn table for refund txn : {cnp_txn_acquirer_code_2}")
            cnp_txn_auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from cnp_txn table for refund txn : {cnp_txn_auth_code_2}")
            cnp_payment_gateway_2 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from cnp_txn table for refund txn : {cnp_payment_gateway_2}")
            cnp_state_txn_2 = result['state'].values[0]
            logger.debug(f"Fetching state value from cnp_txn table for refund txn : {cnp_state_txn_2}")

            query = "select * from cnpware_txn where txn_id='" + txn_id_2 + "';"
            logger.debug(f"Query to fetch data from cnpware_txn table for refund txn : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Query result from cnpware_txn table for refund txn : {result}")
            cnpware_txn_txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type value from cnpware_txn table for refund txn : {cnpware_txn_txn_type_2}")
            cnpware_txn_card_type_2 = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type value from cnpware_txn table for refund txn : {cnpware_txn_card_type_2}")
            cnpware_txn_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state value from cnpware_txn table for refund txn : {cnpware_txn_state_2}")
            cnpware_payment_gateway_2 = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway value from cnpware_txn table for refund txn : {cnpware_payment_gateway_2}")
            cnpware_payment_flow_2 = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow value from cnpware_txn table for refund txn : {cnpware_payment_flow_2}")

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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=posting_date)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=posting_date_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "PAY LINK",
                    "txn_id": txn_id,
                    "pmt_status": "PARTIALLY REFUNDED",
                    "rrn": str(cnp_txn_rrn),
                    "auth_code": auth_code_db,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "original_amt": "{:,.0f}".format(amount),
                    "refunded_amt": "{:,.0f}".format(manually_enter_amt),
                    "balance_amt": "{:,.0f}".format(amount - manually_enter_amt),
                    "settle_status": "SETTLED",
                    "customer_name": customer_name_db,
                    "date": date_and_time_app,

                    "txn_amt_2": "{:,.2f}".format(manually_enter_amt),
                    "pmt_mode_2": "PAY LINK",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(cnp_txn_rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "REFUND SUCCESSFUL",
                    "settle_status_2": "SETTLED",
                    "customer_name_2": customer_name_db_2,
                    "date_2": date_and_time_app_2
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund transaction")
                login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
                home_page = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for original_txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for original_txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for original_txn : {txn_id}, {app_txn_id}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for original_txn : {txn_id}, {payment_status}")
                app_original_amt = txn_history_page.fetch_original_amt_text()
                logger.debug(f"Fetching original_amt from txn history for original_txn : {txn_id}, {app_original_amt}")
                app_refunded_amt = txn_history_page.fetch_refunded_amt_text()
                logger.debug(f"Fetching refunded_amt from txn history for original_txn : {txn_id}, {app_refunded_amt}")
                app_balance_amt = txn_history_page.fetch_balance_amt_text()
                logger.debug(f"Fetching balance_amt from txn history for original_txn : {txn_id}, {app_balance_amt}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for original_txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for original_txn : {txn_id}, {app_payment_msg}")
                txn_history_page.scroll_to_text_element(value="RR NUMBER")
                logger.debug(f"Scrolled to RR Number element")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for original_txn : {txn_id}, {app_settlement_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for original_txn : {txn_id}, {app_date_and_time}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for original_txn : {txn_id}, {app_customer_name}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for original_txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for refunded txn : {txn_id_2}, {payment_status_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for refunded txn : {txn_id_2}, {app_customer_name_2}")
                txn_history_page.scroll_to_text_element(value="RR NUMBER")
                logger.debug(f"Scrolled to RR Number element")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for refunded txn : {txn_id_2}, {app_rrn_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "original_amt": app_original_amt.split('₹')[1],
                    "refunded_amt": app_refunded_amt.split('₹')[1],
                    "balance_amt": app_balance_amt.split('₹')[1],
                    "rrn": app_rrn,
                    "auth_code": app_auth_code,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "date": app_date_and_time,
                    "customer_name": app_customer_name,

                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "date_2": app_date_and_time_2,
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "CNP",
                    "pmt_mode_2": "CNP",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": float(amount),
                    "txn_amt_2": float(manually_enter_amt),
                    "customer_name": customer_name_db,
                    "customer_name_2": customer_name_db_2,
                    "payer_name": payer_name_db,
                    "payer_name_2": payer_name_db_2,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "rrn": str(cnp_txn_rrn),
                    "rrn_2": str(cnp_txn_rrn_2),
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type_db,
                    "org_code": org_code_db,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": txn_type_db_2,
                    "org_code_2": org_code_db_2,
                    "auth_code": auth_code_db,
                    "date": date_and_time_api,
                    "date_2": date_and_time_api_2,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status value from original txn_id : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount value from original txn_id : {amount_api}")
                original_amount_api = float(response_1["amount"])
                logger.debug(f"Fetching original_amt value from original txn_id : {original_amount_api}")
                total_amt_api = float(response_1["totalAmount"])
                logger.debug(f"Fetching total_amt value from original txn_id : {total_amt_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode value from original txn_id : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state value from original txn_id : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn value from original txn_id : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from original txn_id : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer_code value from original txn_id : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from original txn_id : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org_code value from original txn_id : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid value from original txn_id : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid value from original txn_id : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction_type value from original txn_id : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth_code value from original txn_id : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date_and_time value from original txn_id : {date_and_time_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username value from original txn_id : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction_id value from original txn_id : {txn_id_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external_ref_no value from original txn_id : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant_name value from original txn_id : {merchant_name_api}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching payer_name value from original txn_id : {customer_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer_name value from original txn_id : {payer_name_api}")
                order_id_api = response_1["orderNumber"]
                logger.debug(f"Fetching orderNumber value from original txn_id : {order_id_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status value from refunded txn_id : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount value from refunded txn_id : {amount_api_2}")
                original_amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching original_amt value from refunded txn_id : {original_amount_api_2}")
                total_amt_api_2 = float(response_2["totalAmount"])
                logger.debug(f"Fetching total_amt value from refunded txn_id : {total_amt_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment_mode value from refunded txn_id : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state value from refunded txn_id : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn value from refunded txn_id : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement_status value from refunded txn_id : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer_code value from refunded txn_id : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org_code value from refunded txn_id : {org_code_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction_type value from refunded txn_id : {txn_type_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date_and_time value from refunded txn_id : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username value from refunded txn_id : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction_id value from refunded txn_id : {txn_id_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching payer_name value from refunded txn_id : {customer_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer_name value from refunded txn_id : {payer_name_api_2}")
                order_id_api_2 = response_1["orderNumber"]
                logger.debug(f"Fetching orderNumber value from refunded txn_id : {order_id_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "pmt_status_2": status_api_2,
                    "pmt_state": state_api,
                    "pmt_state_2": state_api_2,
                    "pmt_mode": payment_mode_api,
                    "pmt_mode_2": payment_mode_api_2,
                    "settle_status": settlement_status_api,
                    "settle_status_2": settlement_status_api_2,
                    "txn_amt": amount_api,
                    "txn_amt_2": amount_api_2,
                    "customer_name": customer_name_api,
                    "customer_name_2": customer_name_api_2,
                    "payer_name": payer_name_api,
                    "payer_name_2": payer_name_api_2,
                    "order_id": order_id_api,
                    "order_id_2": order_id_api_2,
                    "rrn": str(rrn_api),
                    "rrn_2": str(rrn_api_2),
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "org_code_2": org_code_api_2,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
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
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "CNP",
                    "pmt_mode_2": "CNP",
                    "txn_amt": amount,
                    "txn_amt_2": manually_enter_amt,
                    "order_id": order_id,
                    "order_id_2": order_id,
                    "cnp_txn_state": "SETTLED",
                    "cnp_txn_state_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "pmt_gateway": "CYBERSOURCE",
                    "pmt_gateway_2": "CYBERSOURCE",
                    "cnpware_txn_type": "REMOTE_PAY",
                    "cnpware_txn_type_2": "REFUND",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_flow_2": "None"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": payment_status_db,
                    "pmt_status_2": payment_status_db_2,
                    "pmt_state": payment_state_db,
                    "pmt_state_2": payment_state_db_2,
                    "pmt_mode": payment_mode_db,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt": amount_db,
                    "txn_amt_2": amount_db_2,
                    "order_id": order_id_db,
                    "order_id_2": order_id_db_2,
                    "cnp_txn_state": cnp_state_txn,
                    "cnp_txn_state_2": cnp_state_txn_2,
                    "settle_status": settlement_status_db,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code": acquirer_code_db,
                    "acquirer_code_2": acquirer_code_db_2,
                    "pmt_gateway": payment_gateway_db,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "cnpware_txn_type": txn_type_db,
                    "cnpware_txn_type_2": txn_type_db_2,
                    "cnpware_pmt_flow": cnpware_payment_flow,
                    "cnpware_pmt_flow_2": str(cnpware_payment_flow_2)
                }
                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=created_time_2)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(cnp_txn_rrn_2),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(manually_enter_amt),
                    "payment_option": "REFUND",
                    "date": txn_date,
                    "time": txn_time
                }
                logger.info(f"expected_charge_slip_values : {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
                    "username": app_username, "password": app_password}, expected_details=expected_charge_slip_values)

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_card_page import CardPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_05_033():
    """
    Sub Feature Code: UI_Common_Card_Normal_EMI_Refund_Via_API_For_Fallback_Root_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
    Sub Feature Description: Performing the normal EMI refund via API transaction for fallback to root org via HDFC Dummy PG
     using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 05: NORMAL_EMI, 033: TC033
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

        query = f"select org_code from org_employee where username = {portal_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        root_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {root_org_code}")

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for normal emi setup to be enabled:  {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='INACTIVE')
        logger.debug(f"updated emi settings for {org_code} as inactive for credit card")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(3001, 4000)
            emi_plan_in_months = 3
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_bank_emi_pmt_mode()
            logger.info(f"Selected payment mode is Bank EMI")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"Selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details(api_name='Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details  : {api_details} ")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Settlement api is : {settle_response}")

            query = f"select id from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn id from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            api_details = DBProcessor.get_api_details(api_name='Offline_Refund', request_body={
                "amount": amount,
                "originalTransactionId": txn_id,
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API details  : {api_details} ")
            refund_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {refund_response}")
            refund_txn_id = refund_response.get('txnId')
            logger.debug(f"From response fetch txn_id : {refund_txn_id}")

            query = f"select * from emi where org_code='{root_org_code}' and status = 'ACTIVE' and " \
                    f"issuer_code='HDFC' and card_type='CREDIT' AND term = '{emi_plan_in_months} month' and " \
                    f"tid_type='CIB' and emi_type='NORMAL' order by created_time asc limit 1"
            logger.debug(f"Query to fetch data from the emi table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from emi table :{result}")
            interest_rate = result['interest_rate'].values[0]
            logger.debug(f"Fetching interest_rate from the emi table : {interest_rate}")
            term = result['term'].values[0]
            logger.debug(f"Fetching term from the emi table : {term}")
            scheme_code = result['scheme_code'].values[0]
            logger.debug(f"Fetching scheme_code from the emi table : {scheme_code}")

            logger.debug(f"Started calculating emi part")
            monthly_interest_rate = interest_rate / (12 * 100)
            cal_monthly_emi_amt = amount * monthly_interest_rate * (
                    (1 + monthly_interest_rate) ** emi_plan_in_months) / (
                                          (1 + monthly_interest_rate) ** emi_plan_in_months - 1)
            monthly_emi = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi}")
            cal_total_emi_amt = monthly_emi * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch txn details for original txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for original txn : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for original txn : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for original txn : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for original txn : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for original txn : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for original txn : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for original txn : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for original txn : {pmt_status}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for original txn : {issuer_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for original txn : {txn_type}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for original txn : {pmt_state}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for original txn : {payment_gateway}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table for original txn : {batch_number}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for original txn : {amount_txn}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table for original txn : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table for original txn : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table for original txn : {card_last_four_digit}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for original txn : {payment_mode}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for original txn : {merchant_name}")
            pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table for original txn : {pmt_card_bin}")
            terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table for original txn : {terminal_info_id_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for original txn : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for original txn : {tid_txn}")
            device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from the txn table for original txn : {device_serial_txn}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for original txn : {order_id_txn}")
            card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table for original txn : {card_txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for original txn : {org_code_txn}")
            emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table for original txn : {emi_type}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {posting_date}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate}")
            emi_status = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status}")
            emi_term = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term}")
            emi_loan_amount = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount}")
            emi_amount_monthly = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly}")
            emi_total_amount = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount}")
            emi_scheme_code = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code}")
            emi_txn_amount = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount}")
            emi_original_amount = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount}")

            query = f"select * from txn where id = '{refund_txn_id}'"
            logger.debug(f"Query to fetch txn details for refund txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table for refund txn : {result}")
            refund_amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for refund txn : {refund_amount_txn}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for refund txn : {refund_created_time}")
            refund_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for refund txn : {refund_acquirer_code}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for refund txn : {refund_auth_code}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for refund txn : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for refund txn : {refund_payer_name}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for refund txn : {refund_rrn}")
            refund_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for refund txn : {refund_settle_status}")
            refund_pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for refund txn : {refund_pmt_status}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for refund txn : {refund_txn_type}")
            refund_pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for refund txn : {refund_pmt_state}")
            refund_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for refund txn : {refund_payment_gateway}")
            refund_batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table for refund txn : {refund_batch_number}")
            refund_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table for refund txn : {refund_pmt_card_brand}")
            refund_pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table for refund txn : {refund_pmt_card_type}")
            refund_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table for refund txn : {refund_card_last_four_digit}")
            refund_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for refund txn : {refund_payment_mode}")
            refund_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for refund txn : {refund_merchant_name}")
            refund_pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table for refund txn : {refund_pmt_card_bin}")
            refund_terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table for refund txn : {refund_terminal_info_id_txn}")
            refund_mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for refund txn : {refund_mid_txn}")
            refund_tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for refund txn : {refund_tid_txn}")
            refund_order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for refund txn : {refund_order_id_txn}")
            refund_card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table for refund txn : {refund_card_txn_type}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for refund txn : {refund_org_code_txn}")
            refund_invoice_number = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table for refund txn : {refund_invoice_number}")
            original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching original txn_id from the txn table for refund txn : {original_txn_id}")
            refund_emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table for refund txn : {refund_emi_type}")
            refund_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {refund_posting_date}")
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
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                refund_date_and_time = date_time_converter.to_app_format(posting_date_db=refund_posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_time,
                    "device_serial": device_serial,
                    "batch_number": batch_number,
                    "card_type_desc": "*0102 EMV with PIN",
                    "mid": mid,
                    "tid": tid,
                    "customer_name": "L3TEST",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "customer": "L3TEST/CARD0010",
                    "emi_status": "PENDING",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": refund_txn_id,
                    "pmt_status_2": "REFUNDED",
                    "rr_number_2": refund_rrn,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "customer_name_2": "L3TEST",
                    "settle_status_2": "PENDING",
                    "auth_code_2": refund_auth_code,
                    "date_2": refund_date_and_time,
                    "device_serial_2": device_serial,
                    "batch_number_2": refund_batch_number,
                    "card_type_desc_2": "*0102 EMV with PIN",
                    "mid_2": mid,
                    "tid_2": tid
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.info(f"Resetting the app_driver to login again in the MPOSX application")
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the original txn : {txn_id}, {app_payment_by}")
                app_card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the original txn : {txn_id}, {app_card_type}")
                app_customer = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the original txn : {txn_id}, {app_customer}")
                app_emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the original txn : {txn_id}, {app_emi_status}")
                app_tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the original txn : {txn_id}, {app_tenure}")
                app_lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the original txn : {txn_id}, {app_lender}")
                app_monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the original txn : {txn_id}, {app_monthly_emi}")
                app_total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the original txn : {txn_id}, {app_total_interest}")
                app_total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the original txn : {txn_id}, {app_total_emi_amount}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the original txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the original txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the original txn : {txn_id}, {app_net_effective_price}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the original txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the original txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the original txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info("Fetching payment_mode from txn history for the original txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the original txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the original txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the original txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the original txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the original txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the original txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the original txn : {txn_id}, {app_device_serial}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the original txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the original txn : {txn_id}, {app_card_type_desc}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the original txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the original txn : {txn_id}, {app_tid}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the original txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_refund = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the refund txn : {refund_txn_id}, {app_amount_refund}")
                app_order_id_refund = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the refund txn : {refund_txn_id}, {app_order_id_refund}")
                app_payment_msg_refund = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the refund txn : {refund_txn_id}, {app_payment_msg_refund}")
                app_payment_mode_refund = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the refund txn : {refund_txn_id}, {app_payment_mode_refund}")
                app_payment_status_refund = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the refund txn : {refund_txn_id}, {app_payment_status_refund}")
                app_txn_id_refund = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the refund txn : {refund_txn_id}, {app_txn_id_refund}")
                app_customer_name_refund = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the refund txn : {refund_txn_id}, {app_customer_name_refund}")
                app_date_time_refund = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the refund txn : {refund_txn_id}, {app_date_time_refund}")
                app_settle_status_refund = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the refund txn : {refund_txn_id}, {app_settle_status_refund}")
                app_rrn_refund = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the refund txn : {refund_txn_id}, {app_rrn_refund}")
                app_auth_code_refund = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the refund txn : {refund_txn_id}, {app_auth_code_refund}")
                app_device_serial_refund = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the refund txn : {refund_txn_id}, {app_device_serial_refund}")
                app_batch_number_refund = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the refund txn : {refund_txn_id}, {app_batch_number_refund}")
                app_card_type_desc_refund = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the refund txn : {refund_txn_id}, {app_card_type_desc_refund}")
                app_mid_refund = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the refund txn : {refund_txn_id}, {app_mid_refund}")
                app_tid_refund = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the refund txn : {refund_txn_id}, {app_tid_refund}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": app_payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settle_status,
                    "auth_code": app_auth_code,
                    "date": app_date_time,
                    "device_serial": app_device_serial,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "mid": app_mid,
                    "tid": app_tid,
                    "customer_name": app_customer_name,
                    "pmt_by": app_payment_by,
                    "card_type": app_card_type,
                    "customer": app_customer,
                    "emi_status": app_emi_status,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1],
                    "txn_amt_2": app_amount_refund.split(' ')[1],
                    "pmt_mode_2": app_payment_mode_refund,
                    "txn_id_2": app_txn_id_refund,
                    "pmt_status_2": app_payment_status_refund.split(':')[1],
                    "rr_number_2": app_rrn_refund,
                    "order_id_2": app_order_id_refund,
                    "pmt_msg_2": app_payment_msg_refund,
                    "customer_name_2": app_customer_name_refund,
                    "settle_status_2": app_settle_status_refund,
                    "auth_code_2": app_auth_code_refund,
                    "date_2": app_date_time_refund,
                    "device_serial_2": app_device_serial_refund,
                    "batch_number_2": app_batch_number_refund,
                    "card_type_desc_2": app_card_type_desc_refund,
                    "mid_2": app_mid_refund,
                    "tid_2": app_tid_refund
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.db_datetime(date_from_db=created_time)
                refund_date_and_time = date_time_converter.db_datetime(date_from_db=refund_created_time)
                expected_api_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "rrn": rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "org_code": org_code,
                    "batch_number": batch_number,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "date": date_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "EMV with PIN",
                    "auth_code": auth_code,
                    "card_last_four_digit": "0102",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "card_type": "VISA",
                    "display_pan": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "name_on_card": "L3TEST/CARD0010",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "interest_amt": total_interest,
                    "total_emi_amt": total_emi,
                    "net_cost": total_emi,
                    "emi_type": "NORMAL_EMI",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "mid_2": mid,
                    "tid_2": tid,
                    "acquirer_code_2": "HDFC",
                    "settle_status_2": "PENDING",
                    "rrn_2": refund_rrn,
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "batch_number_2": refund_batch_number,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "date_2": refund_date_and_time,
                    "card_txn_type_desc_2": "EMV with PIN",
                    "auth_code_2": refund_auth_code,
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": refund_merchant_name,
                    "payer_name_2": "L3TEST/CARD0010",
                    "pmt_card_bin_2": "417666",
                    "card_type_2": "VISA",
                    "display_pan_2": "0102",
                    "name_on_card_2": "L3TEST/CARD0010",
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_original = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_original}")
                api_amount = response_original.get('amount')
                logger.debug(f"From response_original fetch amount for original txn : {api_amount}")
                api_payment_mode = response_original.get('paymentMode')
                logger.debug(f"From response_original fetch payment_mode for original txn : {api_payment_mode}")
                api_payment_status = response_original.get('status')
                logger.debug(f"From response_original fetch payment_status for original txn : {api_payment_status}")
                api_payment_state = response_original.get('states')[0]
                logger.debug(f"From response_original fetch payment_state for original txn : {api_payment_state}")
                api_mid = response_original.get('mid')
                logger.debug(f"From response_original fetch mid for original txn : {api_mid}")
                api_tid = response_original.get('tid')
                logger.debug(f"From response_original fetch tid for original txn : {api_tid}")
                api_acquirer_code = response_original.get('acquirerCode')
                logger.debug(f"From response_original fetch acquirer_code for original txn : {api_acquirer_code}")
                api_settle_status = response_original.get('settlementStatus')
                logger.debug(f"From response_original fetch settlement_status for original txn : {api_settle_status}")
                api_rrn = response_original.get('rrNumber')
                logger.debug(f"From response_original fetch rrn for original txn : {api_rrn}")
                api_issuer_code = response_original.get('issuerCode')
                logger.debug(f"From response_original fetch issuer_code for original txn : {api_issuer_code}")
                api_txn_type = response_original.get('txnType')
                logger.debug(f"From response_original fetch txn_type for original txn : {api_txn_type}")
                api_org_code = response_original.get('orgCode')
                logger.debug(f"From response_original fetch org_code for original txn : {api_org_code}")
                api_batch_number = response_original.get('batchNumber')
                logger.debug(f"From response_original fetch batch_number for original txn : {api_batch_number}")
                api_pmt_card_brand = response_original.get('paymentCardBrand')
                logger.debug(f"From response_original fetch payment_card_brand for original txn : {api_pmt_card_brand}")
                api_pmt_card_type = response_original.get('paymentCardType')
                logger.debug(f"From response_original fetch payment_card_type for original txn : {api_pmt_card_type}")
                api_date_time = response_original.get('createdTime')
                logger.debug(f"From response_original fetch date_time for original txn : {api_date_time}")
                api_device_serial = response_original.get('deviceSerial')
                logger.debug(f"From response_original fetch device_serial for original txn : {api_device_serial}")
                api_card_txn_type_desc = response_original.get('cardTxnTypeDesc')
                logger.debug(f"From response_original fetch card_txn_type_desc for original txn : {api_card_txn_type_desc}")
                api_merchant_name = response_original.get('merchantName')
                logger.debug(f"From response_original fetch merchant_name for original txn : {api_merchant_name}")
                api_card_last_four_digit = response_original.get('cardLastFourDigit')
                logger.debug(f"From response_original fetch card_last_four_digit for original txn : {api_card_last_four_digit}")
                api_ext_ref_number = response_original.get('externalRefNumber')
                logger.debug(f"From response_original fetch external_ref_number for original txn : {api_ext_ref_number}")
                api_pmt_card_bin = response_original.get('paymentCardBin')
                logger.debug(f"From response_original fetch payment_card_bin for original txn : {api_pmt_card_bin}")
                api_display_pan = response_original.get('displayPAN')
                logger.debug(f"From response_original fetch display_pan for original txn : {api_display_pan}")
                api_auth_code = response_original.get('authCode')
                logger.debug(f"From response_original fetch auth_code for original txn : {api_auth_code}")
                api_card_type = response_original.get('cardType')
                logger.debug(f"From response_original fetch card_type for original txn : {api_card_type}")
                api_customer_name = response_original.get('customerName')
                logger.debug(f"From response_original fetch customer_name for original txn : {api_customer_name}")
                api_payer_name = response_original.get('payerName')
                logger.debug(f"From response_original fetch payer_name for original txn : {api_payer_name}")
                api_name_on_card = response_original.get('nameOnCard')
                logger.debug(f"From response_original fetch name_on_card for original txn : {api_name_on_card}")
                api_emi_term = response_original.get('emiTerm')
                logger.debug(f"From response_original fetch emi_term for original txn : {api_emi_term}")
                api_emi_status = response_original.get('emiStatus')
                logger.debug(f"From response_original fetch emi_status for original txn : {api_emi_status}")
                api_interest_rate = response_original.get('emiInterestRate')
                logger.debug(f"From response_original fetch emi_interest_rate for original txn : {api_interest_rate}")
                api_emi_type = response_original.get('externalRefNumber7')
                logger.debug(f"From response_original fetch emi_type for original txn : {api_emi_type}")
                api_loan_amt = response_original.get('emiDetails')['loanAmount']
                logger.debug(f"From response_original fetch loan_amount for original txn : {api_loan_amt}")
                api_monthly_emi = response_original.get('emiDetails')['emi']
                logger.debug(f"From response_original fetch monthly emi for original txn : {api_monthly_emi}")
                api_interest_amt = response_original.get('emiDetails')['interestAmount']
                logger.debug(f"From response_original fetch interest_amount for original txn : {api_interest_amt}")
                api_total_emi_amt = response_original.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"From response_original fetch total emi amount for original txn : {api_total_emi_amt}")
                api_net_cost = response_original.get('emiDetails')['netCost']
                logger.debug(f"From response_original fetch net cost for original txn : {api_net_cost}")

                response_refund = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn is : {response_refund}")
                api_amount_refund = response_refund.get('amount')
                logger.debug(f"From response_refund fetch amount for refund txn : {api_amount_refund}")
                api_payment_mode_refund = response_refund.get('paymentMode')
                logger.debug(f"From response_refund fetch payment_mode for refund txn : {api_payment_mode_refund}")
                api_payment_status_refund = response_refund.get('status')
                logger.debug(f"From response_refund fetch payment_status for refund txn : {api_payment_status_refund}")
                api_payment_state_refund = response_refund.get('states')[0]
                logger.debug(f"From response_refund fetch payment_state for refund txn : {api_payment_state_refund}")
                api_mid_refund = response_refund.get('mid')
                logger.debug(f"From response_refund fetch mid for refund txn : {api_mid_refund}")
                api_tid_refund = response_refund.get('tid')
                logger.debug(f"From response_refund fetch tid for refund txn : {api_tid_refund}")
                api_acquirer_code_refund = response_refund.get('acquirerCode')
                logger.debug(f"From response_refund fetch acquirer_code for refund txn : {api_acquirer_code_refund}")
                api_settle_status_refund = response_refund.get('settlementStatus')
                logger.debug(f"From response_refund fetch settlement_status for refund txn : {api_settle_status_refund}")
                api_rrn_refund = response_refund.get('rrNumber')
                logger.debug(f"From response_refund fetch rrn for refund txn : {api_rrn_refund}")
                api_txn_type_refund = response_refund.get('txnType')
                logger.debug(f"From response_refund fetch txn_type for refund txn : {api_txn_type_refund}")
                api_org_code_refund = response_refund.get('orgCode')
                logger.debug(f"From response_refund fetch org_code for refund txn : {api_org_code_refund}")
                api_batch_number_refund = response_refund.get('batchNumber')
                logger.debug(f"From response_refund fetch batch_number for refund txn : {api_batch_number_refund}")
                api_pmt_card_brand_refund = response_refund.get('paymentCardBrand')
                logger.debug(f"From response_refund fetch payment_card_brand for refund txn : {api_pmt_card_brand_refund}")
                api_pmt_card_type_refund = response_refund.get('paymentCardType')
                logger.debug(f"From response_refund fetch payment_card_type for refund txn : {api_pmt_card_type_refund}")
                api_date_time_refund = response_refund.get('createdTime')
                logger.debug(f"From response_refund fetch date_time for refund txn : {api_date_time_refund}")
                api_card_txn_type_desc_refund = response_refund.get('cardTxnTypeDesc')
                logger.debug(f"From response_refund fetch card_txn_type_desc for refund txn : {api_card_txn_type_desc_refund}")
                api_customer_name_refund = response_refund.get('customerName')
                logger.debug(f"From response_refund fetch customer_name for refund txn : {api_customer_name_refund}")
                api_payer_name_refund = response_refund.get('payerName')
                logger.debug(f"From response_refund fetch payer_name for refund txn : {api_payer_name_refund}")
                api_merchant_name_refund = response_refund.get('merchantName')
                logger.debug(f"From response_refund fetch merchant_name for refund txn : {api_merchant_name_refund}")
                api_card_last_four_digit_refund = response_refund.get('cardLastFourDigit')
                logger.debug(f"From response_refund fetch card_last_four_digit for refund txn : {api_card_last_four_digit_refund}")
                api_ext_ref_number_refund = response_refund.get('externalRefNumber')
                logger.debug(f"From response_refund fetch external_ref_number for refund txn : {api_ext_ref_number_refund}")
                api_pmt_card_bin_refund = response_refund.get('paymentCardBin')
                logger.debug(f"From response_refund fetch payment_card_bin for refund txn : {api_pmt_card_bin_refund}")
                api_name_on_card_refund = response_refund.get('nameOnCard')
                logger.debug(f"From response_refund fetch name_on_card for refund txn : {api_name_on_card_refund}")
                api_display_pan_refund = response_refund.get('displayPAN')
                logger.debug(f"From response_refund fetch display_pan for refund txn : {api_display_pan_refund}")
                api_auth_code_refund = response_refund.get('authCode')
                logger.debug(f"From response_refund fetch auth_code for refund txn : {api_auth_code_refund}")
                api_card_type_refund = response_refund.get('cardType')
                logger.debug(f"From response_refund fetch card_type for refund txn : {api_card_type_refund}")
                api_emi_type_refund = response_original.get('externalRefNumber7')
                logger.debug(f"From response_refund fetch emi_type for refund txn : {api_emi_type_refund}")

                actual_api_values = {
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_status": api_payment_status,
                    "pmt_state": api_payment_state,
                    "mid": api_mid,
                    "tid": api_tid,
                    "acquirer_code": api_acquirer_code,
                    "settle_status": api_settle_status,
                    "rrn": api_rrn,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "org_code": api_org_code,
                    "batch_number": api_batch_number,
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
                    "card_txn_type_desc": api_card_txn_type_desc,
                    "auth_code": api_auth_code,
                    "card_last_four_digit": api_card_last_four_digit,
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "pmt_card_bin": api_pmt_card_bin,
                    "card_type": api_card_type,
                    "display_pan": api_display_pan,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "net_cost": api_net_cost,
                    "emi_type": api_emi_type,
                    "txn_amt_2": api_amount_refund,
                    "pmt_mode_2": api_payment_mode_refund,
                    "pmt_status_2": api_payment_status_refund,
                    "pmt_state_2": api_payment_state_refund,
                    "mid_2": api_mid_refund,
                    "tid_2": api_tid_refund,
                    "acquirer_code_2": api_acquirer_code_refund,
                    "settle_status_2": api_settle_status_refund,
                    "rrn_2": api_rrn_refund,
                    "txn_type_2": api_txn_type_refund,
                    "org_code_2": api_org_code_refund,
                    "batch_number_2": api_batch_number_refund,
                    "pmt_card_brand_2": api_pmt_card_brand,
                    "pmt_card_type_2": api_pmt_card_type_refund,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_refund),
                    "card_txn_type_desc_2": api_card_txn_type_desc_refund,
                    "auth_code_2": api_auth_code_refund,
                    "card_last_four_digit_2": api_card_last_four_digit_refund,
                    "customer_name_2": api_customer_name_refund,
                    "ext_ref_number_2": api_ext_ref_number_refund,
                    "merchant_name_2": api_merchant_name_refund,
                    "payer_name_2": api_payer_name_refund,
                    "pmt_card_bin_2": api_pmt_card_bin_refund,
                    "card_type_2": api_card_type_refund,
                    "display_pan_2": api_display_pan_refund,
                    "name_on_card_2": api_name_on_card_refund,
                    "emi_type_2": api_emi_type_refund
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": "L3TEST/CARD0010",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "txn_type": "CHARGE",
                    "settle_status": "SETTLED",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "03",
                    "card_last_four_digit": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "NORMAL_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "payer_name_2": "L3TEST/CARD0010",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "txn_type_2": "REFUND",
                    "settle_status_2": "PENDING",
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "417666",
                    "terminal_info_id_2": terminal_info_id,
                    "card_txn_type_2": "03",
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "orig_txn_id": txn_id,
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_txn,
                    "pmt_mode": payment_mode,
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "payer_name": payer_name,
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "pmt_gateway": payment_gateway,
                    "txn_type": txn_type,
                    "settle_status": settle_status,
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "terminal_info_id": terminal_info_id_txn,
                    "card_txn_type": card_txn_type,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name,
                    "interest_rate": emi_interest_rate,
                    "emi_status": emi_status,
                    "emi_term": emi_term,
                    "emi_type": emi_type,
                    "loan_amt": emi_loan_amount,
                    "monthly_emi": emi_amount_monthly,
                    "total_emi_amt": emi_total_amount,
                    "scheme_code": emi_scheme_code,
                    "emi_txn_amt": emi_txn_amount,
                    "emi_original_amt": emi_original_amount,
                    "txn_amt_2": refund_amount_txn,
                    "pmt_mode_2": refund_payment_mode,
                    "pmt_status_2": refund_pmt_status,
                    "pmt_state_2": refund_pmt_state,
                    "acquirer_code_2": refund_acquirer_code,
                    "payer_name_2": refund_payer_name,
                    "mid_2": refund_mid_txn,
                    "tid_2": refund_tid_txn,
                    "pmt_gateway_2": refund_payment_gateway,
                    "txn_type_2": refund_txn_type,
                    "settle_status_2": refund_settle_status,
                    "pmt_card_brand_2": refund_pmt_card_brand,
                    "pmt_card_type_2": refund_pmt_card_type,
                    "order_id_2": refund_order_id_txn,
                    "org_code_2": refund_org_code_txn,
                    "pmt_card_bin_2": refund_pmt_card_bin,
                    "terminal_info_id_2": refund_terminal_info_id_txn,
                    "card_txn_type_2": refund_card_txn_type,
                    "card_last_four_digit_2": refund_card_last_four_digit,
                    "customer_name_2": refund_customer_name,
                    "orig_txn_id": original_txn_id,
                    "emi_type_2": refund_emi_type
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.to_portal_format(created_date_db=created_time)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                expected_portal_values = {
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_time,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "auth_code_2": refund_auth_code,
                    "rrn_2": refund_rrn,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password, order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                portal_txn_id = transaction_details[1]['Transaction ID']
                portal_total_amount = transaction_details[1]['Total Amount']
                portal_auth_code = transaction_details[1]['Auth Code']
                portal_rrn = transaction_details[1]['RR Number']
                portal_txn_type = transaction_details[1]['Type']
                portal_txn_status = transaction_details[1]['Status']
                portal_user = transaction_details[1]['Username']

                portal_date_time_refund = transaction_details[0]['Date & Time']
                portal_txn_id_refund = transaction_details[0]['Transaction ID']
                portal_total_amount_refund = transaction_details[0]['Total Amount']
                portal_auth_code_refund = transaction_details[0]['Auth Code']
                portal_rrn_refund = transaction_details[0]['RR Number']
                portal_txn_type_refund = transaction_details[0]['Type']
                portal_txn_status_refund = transaction_details[0]['Status']
                portal_user_refund = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "auth_code": portal_auth_code,
                    "rrn": portal_rrn,
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type_2": portal_txn_type_refund,
                    "txn_amt_2": portal_total_amount_refund.split(' ')[1],
                    "username_2": portal_user_refund,
                    "txn_id_2": portal_txn_id_refund,
                    "auth_code_2": portal_auth_code_refund,
                    "rrn_2": portal_rrn_refund,
                    "date_time_2": portal_date_time_refund,
                    "pmt_status_2": portal_txn_status_refund
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=refund_posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": refund_rrn,
                    "AUTH CODE": refund_auth_code,
                    "CARD TYPE": "VISA",
                    "BATCH NO": refund_batch_number,
                    "TID": tid,
                    "payment_option": "REFUND",
                    "INVOICE NO": refund_invoice_number,
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "unnamed_section_text": customer_name
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=refund_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)

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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_05_034():
    """
    Sub Feature Code: UI_Common_Card_Normal_EMI_Refund_Via_API_For_Fallback_Root_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_6_Months_Tenure
    Sub Feature Description: Performing the normal EMI refund via API transaction for fallback to root org via HDFC Dummy PG
     using EMV VISA Credit card with pin for 6 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 05: NORMAL_EMI, 034: TC034
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

        query = f"select org_code from org_employee where username = {portal_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        root_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {root_org_code}")

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for normal emi setup to be enabled:  {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='INACTIVE')
        logger.debug(f"updated emi settings for {org_code} as inactive for credit card")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(3001, 4000)
            emi_plan_in_months = 6
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_bank_emi_pmt_mode()
            logger.info(f"Selected payment mode is Bank EMI")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"Selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details(api_name='Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details  : {api_details} ")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Settlement api is : {settle_response}")

            query = f"select id from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn id from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            api_details = DBProcessor.get_api_details(api_name='Offline_Refund', request_body={
                "amount": amount,
                "originalTransactionId": txn_id,
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API details  : {api_details} ")
            refund_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {refund_response}")
            refund_txn_id = refund_response.get('txnId')
            logger.debug(f"From response fetch txn_id : {refund_txn_id}")

            query = f"select * from emi where org_code='{root_org_code}' and status = 'ACTIVE' and " \
                    f"issuer_code='HDFC' and card_type='CREDIT' AND term = '{emi_plan_in_months} month' and " \
                    f"tid_type='CIB' and emi_type='NORMAL' order by created_time asc limit 1"
            logger.debug(f"Query to fetch data from the emi table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from emi table :{result}")
            interest_rate = result['interest_rate'].values[0]
            logger.debug(f"Fetching interest_rate from the emi table : {interest_rate}")
            term = result['term'].values[0]
            logger.debug(f"Fetching term from the emi table : {term}")
            scheme_code = result['scheme_code'].values[0]
            logger.debug(f"Fetching scheme_code from the emi table : {scheme_code}")

            logger.debug(f"Started calculating emi part")
            monthly_interest_rate = interest_rate / (12 * 100)
            cal_monthly_emi_amt = amount * monthly_interest_rate * (
                    (1 + monthly_interest_rate) ** emi_plan_in_months) / (
                                          (1 + monthly_interest_rate) ** emi_plan_in_months - 1)
            monthly_emi = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi}")
            cal_total_emi_amt = monthly_emi * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch txn details for original txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for original txn : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for original txn : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for original txn : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for original txn : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for original txn : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for original txn : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for original txn : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for original txn : {pmt_status}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for original txn : {issuer_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for original txn : {txn_type}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for original txn : {pmt_state}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for original txn : {payment_gateway}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table for original txn : {batch_number}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for original txn : {amount_txn}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table for original txn : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table for original txn : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table for original txn : {card_last_four_digit}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for original txn : {payment_mode}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for original txn : {merchant_name}")
            pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table for original txn : {pmt_card_bin}")
            terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table for original txn : {terminal_info_id_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for original txn : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for original txn : {tid_txn}")
            device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from the txn table for original txn : {device_serial_txn}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for original txn : {order_id_txn}")
            card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table for original txn : {card_txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for original txn : {org_code_txn}")
            emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table for original txn : {emi_type}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {posting_date}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate}")
            emi_status = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status}")
            emi_term = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term}")
            emi_loan_amount = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount}")
            emi_amount_monthly = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly}")
            emi_total_amount = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount}")
            emi_scheme_code = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code}")
            emi_txn_amount = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount}")
            emi_original_amount = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount}")

            query = f"select * from txn where id = '{refund_txn_id}'"
            logger.debug(f"Query to fetch txn details for refund txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table for refund txn : {result}")
            refund_amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for refund txn : {refund_amount_txn}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for refund txn : {refund_created_time}")
            refund_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for refund txn : {refund_acquirer_code}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for refund txn : {refund_auth_code}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for refund txn : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for refund txn : {refund_payer_name}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for refund txn : {refund_rrn}")
            refund_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for refund txn : {refund_settle_status}")
            refund_pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for refund txn : {refund_pmt_status}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for refund txn : {refund_txn_type}")
            refund_pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for refund txn : {refund_pmt_state}")
            refund_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for refund txn : {refund_payment_gateway}")
            refund_batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table for refund txn : {refund_batch_number}")
            refund_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table for refund txn : {refund_pmt_card_brand}")
            refund_pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table for refund txn : {refund_pmt_card_type}")
            refund_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table for refund txn : {refund_card_last_four_digit}")
            refund_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for refund txn : {refund_payment_mode}")
            refund_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for refund txn : {refund_merchant_name}")
            refund_pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table for refund txn : {refund_pmt_card_bin}")
            refund_terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table for refund txn : {refund_terminal_info_id_txn}")
            refund_mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for refund txn : {refund_mid_txn}")
            refund_tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for refund txn : {refund_tid_txn}")
            refund_order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for refund txn : {refund_order_id_txn}")
            refund_card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table for refund txn : {refund_card_txn_type}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for refund txn : {refund_org_code_txn}")
            refund_invoice_number = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table for refund txn : {refund_invoice_number}")
            original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching original txn_id from the txn table for refund txn : {original_txn_id}")
            refund_emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table for refund txn : {refund_emi_type}")
            refund_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {refund_posting_date}")
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
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                refund_date_and_time = date_time_converter.to_app_format(posting_date_db=refund_posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_time,
                    "device_serial": device_serial,
                    "batch_number": batch_number,
                    "card_type_desc": "*0102 EMV with PIN",
                    "mid": mid,
                    "tid": tid,
                    "customer_name": "L3TEST",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "customer": "L3TEST/CARD0010",
                    "emi_status": "PENDING",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": refund_txn_id,
                    "pmt_status_2": "REFUNDED",
                    "rr_number_2": refund_rrn,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "customer_name_2": "L3TEST",
                    "settle_status_2": "PENDING",
                    "auth_code_2": refund_auth_code,
                    "date_2": refund_date_and_time,
                    "device_serial_2": device_serial,
                    "batch_number_2": refund_batch_number,
                    "card_type_desc_2": "*0102 EMV with PIN",
                    "mid_2": mid,
                    "tid_2": tid
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.info(f"Resetting the app_driver to login again in the MPOSX application")
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the original txn : {txn_id}, {app_payment_by}")
                app_card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the original txn : {txn_id}, {app_card_type}")
                app_customer = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the original txn : {txn_id}, {app_customer}")
                app_emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the original txn : {txn_id}, {app_emi_status}")
                app_tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the original txn : {txn_id}, {app_tenure}")
                app_lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the original txn : {txn_id}, {app_lender}")
                app_monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the original txn : {txn_id}, {app_monthly_emi}")
                app_total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the original txn : {txn_id}, {app_total_interest}")
                app_total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the original txn : {txn_id}, {app_total_emi_amount}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the original txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the original txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the original txn : {txn_id}, {app_net_effective_price}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the original txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the original txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the original txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the original txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the original txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the original txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the original txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the original txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the original txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the original txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the original txn : {txn_id}, {app_device_serial}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the original txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the original txn : {txn_id}, {app_card_type_desc}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the original txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the original txn : {txn_id}, {app_tid}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the original txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_refund = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the refund txn : {refund_txn_id}, {app_amount_refund}")
                app_order_id_refund = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the refund txn : {refund_txn_id}, {app_order_id_refund}")
                app_payment_msg_refund = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the refund txn : {refund_txn_id}, {app_payment_msg_refund}")
                app_payment_mode_refund = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the refund txn : {refund_txn_id}, {app_payment_mode_refund}")
                app_payment_status_refund = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the refund txn : {refund_txn_id}, {app_payment_status_refund}")
                app_txn_id_refund = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the refund txn : {refund_txn_id}, {app_txn_id_refund}")
                app_customer_name_refund = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the refund txn : {refund_txn_id}, {app_customer_name_refund}")
                app_date_time_refund = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the refund txn : {refund_txn_id}, {app_date_time_refund}")
                app_settle_status_refund = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the refund txn : {refund_txn_id}, {app_settle_status_refund}")
                app_rrn_refund = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the refund txn : {refund_txn_id}, {app_rrn_refund}")
                app_auth_code_refund = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the refund txn : {refund_txn_id}, {app_auth_code_refund}")
                app_device_serial_refund = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the refund txn : {refund_txn_id}, {app_device_serial_refund}")
                app_batch_number_refund = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the refund txn : {refund_txn_id}, {app_batch_number_refund}")
                app_card_type_desc_refund = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the refund txn : {refund_txn_id}, {app_card_type_desc_refund}")
                app_mid_refund = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the refund txn : {refund_txn_id}, {app_mid_refund}")
                app_tid_refund = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the refund txn : {refund_txn_id}, {app_tid_refund}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": app_payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settle_status,
                    "auth_code": app_auth_code,
                    "date": app_date_time,
                    "device_serial": app_device_serial,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "mid": app_mid,
                    "tid": app_tid,
                    "customer_name": app_customer_name,
                    "pmt_by": app_payment_by,
                    "card_type": app_card_type,
                    "customer": app_customer,
                    "emi_status": app_emi_status,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1],
                    "txn_amt_2": app_amount_refund.split(' ')[1],
                    "pmt_mode_2": app_payment_mode_refund,
                    "txn_id_2": app_txn_id_refund,
                    "pmt_status_2": app_payment_status_refund.split(':')[1],
                    "rr_number_2": app_rrn_refund,
                    "order_id_2": app_order_id_refund,
                    "pmt_msg_2": app_payment_msg_refund,
                    "customer_name_2": app_customer_name_refund,
                    "settle_status_2": app_settle_status_refund,
                    "auth_code_2": app_auth_code_refund,
                    "date_2": app_date_time_refund,
                    "device_serial_2": app_device_serial_refund,
                    "batch_number_2": app_batch_number_refund,
                    "card_type_desc_2": app_card_type_desc_refund,
                    "mid_2": app_mid_refund,
                    "tid_2": app_tid_refund
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.db_datetime(date_from_db=created_time)
                refund_date_and_time = date_time_converter.db_datetime(date_from_db=refund_created_time)
                expected_api_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "rrn": rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "org_code": org_code,
                    "batch_number": batch_number,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "date": date_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "EMV with PIN",
                    "auth_code": auth_code,
                    "card_last_four_digit": "0102",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "card_type": "VISA",
                    "display_pan": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "name_on_card": "L3TEST/CARD0010",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "interest_amt": total_interest,
                    "total_emi_amt": total_emi,
                    "net_cost": total_emi,
                    "emi_type": "NORMAL_EMI",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "mid_2": mid,
                    "tid_2": tid,
                    "acquirer_code_2": "HDFC",
                    "settle_status_2": "PENDING",
                    "rrn_2": refund_rrn,
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "batch_number_2": refund_batch_number,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "date_2": refund_date_and_time,
                    "card_txn_type_desc_2": "EMV with PIN",
                    "auth_code_2": refund_auth_code,
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": refund_merchant_name,
                    "payer_name_2": "L3TEST/CARD0010",
                    "pmt_card_bin_2": "417666",
                    "card_type_2": "VISA",
                    "display_pan_2": "0102",
                    "name_on_card_2": "L3TEST/CARD0010",
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_original = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_original}")
                api_amount = response_original.get('amount')
                logger.debug(f"From response_original fetch amount for original txn : {api_amount}")
                api_payment_mode = response_original.get('paymentMode')
                logger.debug(f"From response_original fetch payment_mode for original txn : {api_payment_mode}")
                api_payment_status = response_original.get('status')
                logger.debug(f"From response_original fetch payment_status for original txn : {api_payment_status}")
                api_payment_state = response_original.get('states')[0]
                logger.debug(f"From response_original fetch payment_state for original txn : {api_payment_state}")
                api_mid = response_original.get('mid')
                logger.debug(f"From response_original fetch mid for original txn : {api_mid}")
                api_tid = response_original.get('tid')
                logger.debug(f"From response_original fetch tid for original txn : {api_tid}")
                api_acquirer_code = response_original.get('acquirerCode')
                logger.debug(f"From response_original fetch acquirer_code for original txn : {api_acquirer_code}")
                api_settle_status = response_original.get('settlementStatus')
                logger.debug(f"From response_original fetch settlement_status for original txn : {api_settle_status}")
                api_rrn = response_original.get('rrNumber')
                logger.debug(f"From response_original fetch rrn for original txn : {api_rrn}")
                api_issuer_code = response_original.get('issuerCode')
                logger.debug(f"From response_original fetch issuer_code for original txn : {api_issuer_code}")
                api_txn_type = response_original.get('txnType')
                logger.debug(f"From response_original fetch txn_type for original txn : {api_txn_type}")
                api_org_code = response_original.get('orgCode')
                logger.debug(f"From response_original fetch org_code for original txn : {api_org_code}")
                api_batch_number = response_original.get('batchNumber')
                logger.debug(f"From response_original fetch batch_number for original txn : {api_batch_number}")
                api_pmt_card_brand = response_original.get('paymentCardBrand')
                logger.debug(f"From response_original fetch payment_card_brand for original txn : {api_pmt_card_brand}")
                api_pmt_card_type = response_original.get('paymentCardType')
                logger.debug(f"From response_original fetch payment_card_type for original txn : {api_pmt_card_type}")
                api_date_time = response_original.get('createdTime')
                logger.debug(f"From response_original fetch date_time for original txn : {api_date_time}")
                api_device_serial = response_original.get('deviceSerial')
                logger.debug(f"From response_original fetch device_serial for original txn : {api_device_serial}")
                api_card_txn_type_desc = response_original.get('cardTxnTypeDesc')
                logger.debug(f"From response_original fetch card_txn_type_desc for original txn : {api_card_txn_type_desc}")
                api_merchant_name = response_original.get('merchantName')
                logger.debug(f"From response_original fetch merchant_name for original txn : {api_merchant_name}")
                api_card_last_four_digit = response_original.get('cardLastFourDigit')
                logger.debug(f"From response_original fetch card_last_four_digit for original txn : {api_card_last_four_digit}")
                api_ext_ref_number = response_original.get('externalRefNumber')
                logger.debug(f"From response_original fetch external_ref_number for original txn : {api_ext_ref_number}")
                api_pmt_card_bin = response_original.get('paymentCardBin')
                logger.debug(f"From response_original fetch payment_card_bin for original txn : {api_pmt_card_bin}")
                api_display_pan = response_original.get('displayPAN')
                logger.debug(f"From response_original fetch display_pan for original txn : {api_display_pan}")
                api_auth_code = response_original.get('authCode')
                logger.debug(f"From response_original fetch auth_code for original txn : {api_auth_code}")
                api_card_type = response_original.get('cardType')
                logger.debug(f"From response_original fetch card_type for original txn : {api_card_type}")
                api_customer_name = response_original.get('customerName')
                logger.debug(f"From response_original fetch customer_name for original txn : {api_customer_name}")
                api_payer_name = response_original.get('payerName')
                logger.debug(f"From response_original fetch payer_name for original txn : {api_payer_name}")
                api_name_on_card = response_original.get('nameOnCard')
                logger.debug(f"From response_original fetch name_on_card for original txn : {api_name_on_card}")
                api_emi_term = response_original.get('emiTerm')
                logger.debug(f"From response_original fetch emi_term for original txn : {api_emi_term}")
                api_emi_status = response_original.get('emiStatus')
                logger.debug(f"From response_original fetch emi_status for original txn : {api_emi_status}")
                api_interest_rate = response_original.get('emiInterestRate')
                logger.debug(f"From response_original fetch emi_interest_rate for original txn : {api_interest_rate}")
                api_emi_type = response_original.get('externalRefNumber7')
                logger.debug(f"From response_original fetch emi_type for original txn : {api_emi_type}")
                api_loan_amt = response_original.get('emiDetails')['loanAmount']
                logger.debug(f"From response_original fetch loan_amount for original txn : {api_loan_amt}")
                api_monthly_emi = response_original.get('emiDetails')['emi']
                logger.debug(f"From response_original fetch monthly emi for original txn : {api_monthly_emi}")
                api_interest_amt = response_original.get('emiDetails')['interestAmount']
                logger.debug(f"From response_original fetch interest_amount for original txn : {api_interest_amt}")
                api_total_emi_amt = response_original.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"From response_original fetch total emi amount for original txn : {api_total_emi_amt}")
                api_net_cost = response_original.get('emiDetails')['netCost']
                logger.debug(f"From response_original fetch net cost for original txn : {api_net_cost}")

                response_refund = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn is : {response_refund}")
                api_amount_refund = response_refund.get('amount')
                logger.debug(f"From response_refund fetch amount for refund txn : {api_amount_refund}")
                api_payment_mode_refund = response_refund.get('paymentMode')
                logger.debug(f"From response_refund fetch payment_mode for refund txn : {api_payment_mode_refund}")
                api_payment_status_refund = response_refund.get('status')
                logger.debug(f"From response_refund fetch payment_status for refund txn : {api_payment_status_refund}")
                api_payment_state_refund = response_refund.get('states')[0]
                logger.debug(f"From response_refund fetch payment_state for refund txn : {api_payment_state_refund}")
                api_mid_refund = response_refund.get('mid')
                logger.debug(f"From response_refund fetch mid for refund txn : {api_mid_refund}")
                api_tid_refund = response_refund.get('tid')
                logger.debug(f"From response_refund fetch tid for refund txn : {api_tid_refund}")
                api_acquirer_code_refund = response_refund.get('acquirerCode')
                logger.debug(f"From response_refund fetch acquirer_code for refund txn : {api_acquirer_code_refund}")
                api_settle_status_refund = response_refund.get('settlementStatus')
                logger.debug(f"From response_refund fetch settlement_status for refund txn : {api_settle_status_refund}")
                api_rrn_refund = response_refund.get('rrNumber')
                logger.debug(f"From response_refund fetch rrn for refund txn : {api_rrn_refund}")
                api_txn_type_refund = response_refund.get('txnType')
                logger.debug(f"From response_refund fetch txn_type for refund txn : {api_txn_type_refund}")
                api_org_code_refund = response_refund.get('orgCode')
                logger.debug(f"From response_refund fetch org_code for refund txn : {api_org_code_refund}")
                api_batch_number_refund = response_refund.get('batchNumber')
                logger.debug(f"From response_refund fetch batch_number for refund txn : {api_batch_number_refund}")
                api_pmt_card_brand_refund = response_refund.get('paymentCardBrand')
                logger.debug(f"From response_refund fetch payment_card_brand for refund txn : {api_pmt_card_brand_refund}")
                api_pmt_card_type_refund = response_refund.get('paymentCardType')
                logger.debug(f"From response_refund fetch payment_card_type for refund txn : {api_pmt_card_type_refund}")
                api_date_time_refund = response_refund.get('createdTime')
                logger.debug(f"From response_refund fetch date_time for refund txn : {api_date_time_refund}")
                api_card_txn_type_desc_refund = response_refund.get('cardTxnTypeDesc')
                logger.debug(f"From response_refund fetch card_txn_type_desc for refund txn : {api_card_txn_type_desc_refund}")
                api_customer_name_refund = response_refund.get('customerName')
                logger.debug(f"From response_refund fetch customer_name for refund txn : {api_customer_name_refund}")
                api_payer_name_refund = response_refund.get('payerName')
                logger.debug(f"From response_refund fetch payer_name for refund txn : {api_payer_name_refund}")
                api_merchant_name_refund = response_refund.get('merchantName')
                logger.debug(f"From response_refund fetch merchant_name for refund txn : {api_merchant_name_refund}")
                api_card_last_four_digit_refund = response_refund.get('cardLastFourDigit')
                logger.debug(f"From response_refund fetch card_last_four_digit for refund txn : {api_card_last_four_digit_refund}")
                api_ext_ref_number_refund = response_refund.get('externalRefNumber')
                logger.debug(f"From response_refund fetch external_ref_number for refund txn : {api_ext_ref_number_refund}")
                api_pmt_card_bin_refund = response_refund.get('paymentCardBin')
                logger.debug(f"From response_refund fetch payment_card_bin for refund txn : {api_pmt_card_bin_refund}")
                api_name_on_card_refund = response_refund.get('nameOnCard')
                logger.debug(f"From response_refund fetch name_on_card for refund txn : {api_name_on_card_refund}")
                api_display_pan_refund = response_refund.get('displayPAN')
                logger.debug(f"From response_refund fetch display_pan for refund txn : {api_display_pan_refund}")
                api_auth_code_refund = response_refund.get('authCode')
                logger.debug(f"From response_refund fetch auth_code for refund txn : {api_auth_code_refund}")
                api_card_type_refund = response_refund.get('cardType')
                logger.debug(f"From response_refund fetch card_type for refund txn : {api_card_type_refund}")
                api_emi_type_refund = response_original.get('externalRefNumber7')
                logger.debug(f"From response_refund fetch emi_type for refund txn : {api_emi_type_refund}")

                actual_api_values = {
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_status": api_payment_status,
                    "pmt_state": api_payment_state,
                    "mid": api_mid,
                    "tid": api_tid,
                    "acquirer_code": api_acquirer_code,
                    "settle_status": api_settle_status,
                    "rrn": api_rrn,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "org_code": api_org_code,
                    "batch_number": api_batch_number,
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
                    "card_txn_type_desc": api_card_txn_type_desc,
                    "auth_code": api_auth_code,
                    "card_last_four_digit": api_card_last_four_digit,
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "pmt_card_bin": api_pmt_card_bin,
                    "card_type": api_card_type,
                    "display_pan": api_display_pan,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "net_cost": api_net_cost,
                    "emi_type": api_emi_type,
                    "txn_amt_2": api_amount_refund,
                    "pmt_mode_2": api_payment_mode_refund,
                    "pmt_status_2": api_payment_status_refund,
                    "pmt_state_2": api_payment_state_refund,
                    "mid_2": api_mid_refund,
                    "tid_2": api_tid_refund,
                    "acquirer_code_2": api_acquirer_code_refund,
                    "settle_status_2": api_settle_status_refund,
                    "rrn_2": api_rrn_refund,
                    "txn_type_2": api_txn_type_refund,
                    "org_code_2": api_org_code_refund,
                    "batch_number_2": api_batch_number_refund,
                    "pmt_card_brand_2": api_pmt_card_brand,
                    "pmt_card_type_2": api_pmt_card_type_refund,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_refund),
                    "card_txn_type_desc_2": api_card_txn_type_desc_refund,
                    "auth_code_2": api_auth_code_refund,
                    "card_last_four_digit_2": api_card_last_four_digit_refund,
                    "customer_name_2": api_customer_name_refund,
                    "ext_ref_number_2": api_ext_ref_number_refund,
                    "merchant_name_2": api_merchant_name_refund,
                    "payer_name_2": api_payer_name_refund,
                    "pmt_card_bin_2": api_pmt_card_bin_refund,
                    "card_type_2": api_card_type_refund,
                    "display_pan_2": api_display_pan_refund,
                    "name_on_card_2": api_name_on_card_refund,
                    "emi_type_2": api_emi_type_refund
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": "L3TEST/CARD0010",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "txn_type": "CHARGE",
                    "settle_status": "SETTLED",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "03",
                    "card_last_four_digit": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "NORMAL_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "payer_name_2": "L3TEST/CARD0010",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "txn_type_2": "REFUND",
                    "settle_status_2": "PENDING",
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "417666",
                    "terminal_info_id_2": terminal_info_id,
                    "card_txn_type_2": "03",
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "orig_txn_id": txn_id,
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_txn,
                    "pmt_mode": payment_mode,
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "payer_name": payer_name,
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "pmt_gateway": payment_gateway,
                    "txn_type": txn_type,
                    "settle_status": settle_status,
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "terminal_info_id": terminal_info_id_txn,
                    "card_txn_type": card_txn_type,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name,
                    "interest_rate": emi_interest_rate,
                    "emi_status": emi_status,
                    "emi_term": emi_term,
                    "emi_type": emi_type,
                    "loan_amt": emi_loan_amount,
                    "monthly_emi": emi_amount_monthly,
                    "total_emi_amt": emi_total_amount,
                    "scheme_code": emi_scheme_code,
                    "emi_txn_amt": emi_txn_amount,
                    "emi_original_amt": emi_original_amount,
                    "txn_amt_2": refund_amount_txn,
                    "pmt_mode_2": refund_payment_mode,
                    "pmt_status_2": refund_pmt_status,
                    "pmt_state_2": refund_pmt_state,
                    "acquirer_code_2": refund_acquirer_code,
                    "payer_name_2": refund_payer_name,
                    "mid_2": refund_mid_txn,
                    "tid_2": refund_tid_txn,
                    "pmt_gateway_2": refund_payment_gateway,
                    "txn_type_2": refund_txn_type,
                    "settle_status_2": refund_settle_status,
                    "pmt_card_brand_2": refund_pmt_card_brand,
                    "pmt_card_type_2": refund_pmt_card_type,
                    "order_id_2": refund_order_id_txn,
                    "org_code_2": refund_org_code_txn,
                    "pmt_card_bin_2": refund_pmt_card_bin,
                    "terminal_info_id_2": refund_terminal_info_id_txn,
                    "card_txn_type_2": refund_card_txn_type,
                    "card_last_four_digit_2": refund_card_last_four_digit,
                    "customer_name_2": refund_customer_name,
                    "orig_txn_id": original_txn_id,
                    "emi_type_2": refund_emi_type
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.to_portal_format(created_date_db=created_time)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                expected_portal_values = {
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_time,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "auth_code_2": refund_auth_code,
                    "rrn_2": refund_rrn,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password, order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                portal_txn_id = transaction_details[1]['Transaction ID']
                portal_total_amount = transaction_details[1]['Total Amount']
                portal_auth_code = transaction_details[1]['Auth Code']
                portal_rrn = transaction_details[1]['RR Number']
                portal_txn_type = transaction_details[1]['Type']
                portal_txn_status = transaction_details[1]['Status']
                portal_user = transaction_details[1]['Username']

                portal_date_time_refund = transaction_details[0]['Date & Time']
                portal_txn_id_refund = transaction_details[0]['Transaction ID']
                portal_total_amount_refund = transaction_details[0]['Total Amount']
                portal_auth_code_refund = transaction_details[0]['Auth Code']
                portal_rrn_refund = transaction_details[0]['RR Number']
                portal_txn_type_refund = transaction_details[0]['Type']
                portal_txn_status_refund = transaction_details[0]['Status']
                portal_user_refund = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "auth_code": portal_auth_code,
                    "rrn": portal_rrn,
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type_2": portal_txn_type_refund,
                    "txn_amt_2": portal_total_amount_refund.split(' ')[1],
                    "username_2": portal_user_refund,
                    "txn_id_2": portal_txn_id_refund,
                    "auth_code_2": portal_auth_code_refund,
                    "rrn_2": portal_rrn_refund,
                    "date_time_2": portal_date_time_refund,
                    "pmt_status_2": portal_txn_status_refund
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=refund_posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": refund_rrn,
                    "AUTH CODE": refund_auth_code,
                    "CARD TYPE": "VISA",
                    "BATCH NO": refund_batch_number,
                    "TID": tid,
                    "payment_option": "REFUND",
                    "INVOICE NO": refund_invoice_number,
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "unnamed_section_text": customer_name
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=refund_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)

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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_05_035():
    """
    Sub Feature Code: UI_Common_Card_Normal_EMI_Refund_Via_API_For_Fallback_Root_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_9_Months_Tenure
    Sub Feature Description: Performing the normal EMI refund via API transaction for fallback to root org via HDFC Dummy PG
     using EMV VISA Credit card with pin for 9 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 05: NORMAL_EMI, 035: TC035
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

        query = f"select org_code from org_employee where username = {portal_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        root_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {root_org_code}")

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for normal emi setup to be enabled:  {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='INACTIVE')
        logger.debug(f"updated emi settings for {org_code} as inactive for credit card")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(3001, 4000)
            emi_plan_in_months = 9
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_bank_emi_pmt_mode()
            logger.info(f"Selected payment mode is Bank EMI")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"Selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details(api_name='Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details  : {api_details} ")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Settlement api is : {settle_response}")

            query = f"select id from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn id from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            api_details = DBProcessor.get_api_details(api_name='Offline_Refund', request_body={
                "amount": amount,
                "originalTransactionId": txn_id,
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API details  : {api_details} ")
            refund_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {refund_response}")
            refund_txn_id = refund_response.get('txnId')
            logger.debug(f"From response fetch txn_id : {refund_txn_id}")

            query = f"select * from emi where org_code='{root_org_code}' and status = 'ACTIVE' and " \
                    f"issuer_code='HDFC' and card_type='CREDIT' AND term = '{emi_plan_in_months} month' and " \
                    f"tid_type='CIB' and emi_type='NORMAL' order by created_time asc limit 1"
            logger.debug(f"Query to fetch data from the emi table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from emi table :{result}")
            interest_rate = result['interest_rate'].values[0]
            logger.debug(f"Fetching interest_rate from the emi table : {interest_rate}")
            term = result['term'].values[0]
            logger.debug(f"Fetching term from the emi table : {term}")
            scheme_code = result['scheme_code'].values[0]
            logger.debug(f"Fetching scheme_code from the emi table : {scheme_code}")

            logger.debug(f"Started calculating emi part")
            monthly_interest_rate = interest_rate / (12 * 100)
            cal_monthly_emi_amt = amount * monthly_interest_rate * (
                    (1 + monthly_interest_rate) ** emi_plan_in_months) / (
                                          (1 + monthly_interest_rate) ** emi_plan_in_months - 1)
            monthly_emi = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi}")
            cal_total_emi_amt = monthly_emi * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch txn details for original txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for original txn : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for original txn : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for original txn : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for original txn : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for original txn : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for original txn : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for original txn : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for original txn : {pmt_status}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for original txn : {issuer_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for original txn : {txn_type}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for original txn : {pmt_state}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for original txn : {payment_gateway}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table for original txn : {batch_number}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for original txn : {amount_txn}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table for original txn : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table for original txn : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table for original txn : {card_last_four_digit}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for original txn : {payment_mode}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for original txn : {merchant_name}")
            pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table for original txn : {pmt_card_bin}")
            terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table for original txn : {terminal_info_id_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for original txn : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for original txn : {tid_txn}")
            device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from the txn table for original txn : {device_serial_txn}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for original txn : {order_id_txn}")
            card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table for original txn : {card_txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for original txn : {org_code_txn}")
            emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table for original txn : {emi_type}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {posting_date}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate}")
            emi_status = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status}")
            emi_term = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term}")
            emi_loan_amount = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount}")
            emi_amount_monthly = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly}")
            emi_total_amount = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount}")
            emi_scheme_code = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code}")
            emi_txn_amount = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount}")
            emi_original_amount = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount}")

            query = f"select * from txn where id = '{refund_txn_id}'"
            logger.debug(f"Query to fetch txn details for refund txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table for refund txn : {result}")
            refund_amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for refund txn : {refund_amount_txn}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for refund txn : {refund_created_time}")
            refund_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for refund txn : {refund_acquirer_code}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for refund txn : {refund_auth_code}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for refund txn : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for refund txn : {refund_payer_name}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for refund txn : {refund_rrn}")
            refund_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for refund txn : {refund_settle_status}")
            refund_pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for refund txn : {refund_pmt_status}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for refund txn : {refund_txn_type}")
            refund_pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for refund txn : {refund_pmt_state}")
            refund_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for refund txn : {refund_payment_gateway}")
            refund_batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table for refund txn : {refund_batch_number}")
            refund_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table for refund txn : {refund_pmt_card_brand}")
            refund_pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table for refund txn : {refund_pmt_card_type}")
            refund_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table for refund txn : {refund_card_last_four_digit}")
            refund_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for refund txn : {refund_payment_mode}")
            refund_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for refund txn : {refund_merchant_name}")
            refund_pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table for refund txn : {refund_pmt_card_bin}")
            refund_terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table for refund txn : {refund_terminal_info_id_txn}")
            refund_mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for refund txn : {refund_mid_txn}")
            refund_tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for refund txn : {refund_tid_txn}")
            refund_order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for refund txn : {refund_order_id_txn}")
            refund_card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table for refund txn : {refund_card_txn_type}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for refund txn : {refund_org_code_txn}")
            refund_invoice_number = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table for refund txn : {refund_invoice_number}")
            original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching original txn_id from the txn table for refund txn : {original_txn_id}")
            refund_emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table for refund txn : {refund_emi_type}")
            refund_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {refund_posting_date}")
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
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                refund_date_and_time = date_time_converter.to_app_format(posting_date_db=refund_posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_time,
                    "device_serial": device_serial,
                    "batch_number": batch_number,
                    "card_type_desc": "*0102 EMV with PIN",
                    "mid": mid,
                    "tid": tid,
                    "customer_name": "L3TEST",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "customer": "L3TEST/CARD0010",
                    "emi_status": "PENDING",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": refund_txn_id,
                    "pmt_status_2": "REFUNDED",
                    "rr_number_2": refund_rrn,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "customer_name_2": "L3TEST",
                    "settle_status_2": "PENDING",
                    "auth_code_2": refund_auth_code,
                    "date_2": refund_date_and_time,
                    "device_serial_2": device_serial,
                    "batch_number_2": refund_batch_number,
                    "card_type_desc_2": "*0102 EMV with PIN",
                    "mid_2": mid,
                    "tid_2": tid
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.info(f"Resetting the app_driver to login again in the MPOSX application")
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the original txn : {txn_id}, {app_payment_by}")
                app_card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the original txn : {txn_id}, {app_card_type}")
                app_customer = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the original txn : {txn_id}, {app_customer}")
                app_emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the original txn : {txn_id}, {app_emi_status}")
                app_tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the original txn : {txn_id}, {app_tenure}")
                app_lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the original txn : {txn_id}, {app_lender}")
                app_monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the original txn : {txn_id}, {app_monthly_emi}")
                app_total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the original txn : {txn_id}, {app_total_interest}")
                app_total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the original txn : {txn_id}, {app_total_emi_amount}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the original txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the original txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the original txn : {txn_id}, {app_net_effective_price}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the original txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the original txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the original txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the original txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the original txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the original txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the original txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the original txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the original txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the original txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the original txn : {txn_id}, {app_device_serial}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the original txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the original txn : {txn_id}, {app_card_type_desc}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the original txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the original txn : {txn_id}, {app_tid}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the original txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_refund = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the refund txn : {refund_txn_id}, {app_amount_refund}")
                app_order_id_refund = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the refund txn : {refund_txn_id}, {app_order_id_refund}")
                app_payment_msg_refund = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the refund txn : {refund_txn_id}, {app_payment_msg_refund}")
                app_payment_mode_refund = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the refund txn : {refund_txn_id}, {app_payment_mode_refund}")
                app_payment_status_refund = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the refund txn : {refund_txn_id}, {app_payment_status_refund}")
                app_txn_id_refund = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the refund txn : {refund_txn_id}, {app_txn_id_refund}")
                app_customer_name_refund = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the refund txn : {refund_txn_id}, {app_customer_name_refund}")
                app_date_time_refund = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the refund txn : {refund_txn_id}, {app_date_time_refund}")
                app_settle_status_refund = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the refund txn : {refund_txn_id}, {app_settle_status_refund}")
                app_rrn_refund = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the refund txn : {refund_txn_id}, {app_rrn_refund}")
                app_auth_code_refund = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the refund txn : {refund_txn_id}, {app_auth_code_refund}")
                app_device_serial_refund = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the refund txn : {refund_txn_id}, {app_device_serial_refund}")
                app_batch_number_refund = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the refund txn : {refund_txn_id}, {app_batch_number_refund}")
                app_card_type_desc_refund = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the refund txn : {refund_txn_id}, {app_card_type_desc_refund}")
                app_mid_refund = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the refund txn : {refund_txn_id}, {app_mid_refund}")
                app_tid_refund = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the refund txn : {refund_txn_id}, {app_tid_refund}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": app_payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settle_status,
                    "auth_code": app_auth_code,
                    "date": app_date_time,
                    "device_serial": app_device_serial,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "mid": app_mid,
                    "tid": app_tid,
                    "customer_name": app_customer_name,
                    "pmt_by": app_payment_by,
                    "card_type": app_card_type,
                    "customer": app_customer,
                    "emi_status": app_emi_status,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1],
                    "txn_amt_2": app_amount_refund.split(' ')[1],
                    "pmt_mode_2": app_payment_mode_refund,
                    "txn_id_2": app_txn_id_refund,
                    "pmt_status_2": app_payment_status_refund.split(':')[1],
                    "rr_number_2": app_rrn_refund,
                    "order_id_2": app_order_id_refund,
                    "pmt_msg_2": app_payment_msg_refund,
                    "customer_name_2": app_customer_name_refund,
                    "settle_status_2": app_settle_status_refund,
                    "auth_code_2": app_auth_code_refund,
                    "date_2": app_date_time_refund,
                    "device_serial_2": app_device_serial_refund,
                    "batch_number_2": app_batch_number_refund,
                    "card_type_desc_2": app_card_type_desc_refund,
                    "mid_2": app_mid_refund,
                    "tid_2": app_tid_refund
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.db_datetime(date_from_db=created_time)
                refund_date_and_time = date_time_converter.db_datetime(date_from_db=refund_created_time)
                expected_api_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "rrn": rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "org_code": org_code,
                    "batch_number": batch_number,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "date": date_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "EMV with PIN",
                    "auth_code": auth_code,
                    "card_last_four_digit": "0102",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "card_type": "VISA",
                    "display_pan": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "name_on_card": "L3TEST/CARD0010",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "interest_amt": total_interest,
                    "total_emi_amt": total_emi,
                    "net_cost": total_emi,
                    "emi_type": "NORMAL_EMI",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "mid_2": mid,
                    "tid_2": tid,
                    "acquirer_code_2": "HDFC",
                    "settle_status_2": "PENDING",
                    "rrn_2": refund_rrn,
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "batch_number_2": refund_batch_number,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "date_2": refund_date_and_time,
                    "card_txn_type_desc_2": "EMV with PIN",
                    "auth_code_2": refund_auth_code,
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": refund_merchant_name,
                    "payer_name_2": "L3TEST/CARD0010",
                    "pmt_card_bin_2": "417666",
                    "card_type_2": "VISA",
                    "display_pan_2": "0102",
                    "name_on_card_2": "L3TEST/CARD0010",
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_original = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_original}")
                api_amount = response_original.get('amount')
                logger.debug(f"From response_original fetch amount for original txn : {api_amount}")
                api_payment_mode = response_original.get('paymentMode')
                logger.debug(f"From response_original fetch payment_mode for original txn : {api_payment_mode}")
                api_payment_status = response_original.get('status')
                logger.debug(f"From response_original fetch payment_status for original txn : {api_payment_status}")
                api_payment_state = response_original.get('states')[0]
                logger.debug(f"From response_original fetch payment_state for original txn : {api_payment_state}")
                api_mid = response_original.get('mid')
                logger.debug(f"From response_original fetch mid for original txn : {api_mid}")
                api_tid = response_original.get('tid')
                logger.debug(f"From response_original fetch tid for original txn : {api_tid}")
                api_acquirer_code = response_original.get('acquirerCode')
                logger.debug(f"From response_original fetch acquirer_code for original txn : {api_acquirer_code}")
                api_settle_status = response_original.get('settlementStatus')
                logger.debug(f"From response_original fetch settlement_status for original txn : {api_settle_status}")
                api_rrn = response_original.get('rrNumber')
                logger.debug(f"From response_original fetch rrn for original txn : {api_rrn}")
                api_issuer_code = response_original.get('issuerCode')
                logger.debug(f"From response_original fetch issuer_code for original txn : {api_issuer_code}")
                api_txn_type = response_original.get('txnType')
                logger.debug(f"From response_original fetch txn_type for original txn : {api_txn_type}")
                api_org_code = response_original.get('orgCode')
                logger.debug(f"From response_original fetch org_code for original txn : {api_org_code}")
                api_batch_number = response_original.get('batchNumber')
                logger.debug(f"From response_original fetch batch_number for original txn : {api_batch_number}")
                api_pmt_card_brand = response_original.get('paymentCardBrand')
                logger.debug(f"From response_original fetch payment_card_brand for original txn : {api_pmt_card_brand}")
                api_pmt_card_type = response_original.get('paymentCardType')
                logger.debug(f"From response_original fetch payment_card_type for original txn : {api_pmt_card_type}")
                api_date_time = response_original.get('createdTime')
                logger.debug(f"From response_original fetch date_time for original txn : {api_date_time}")
                api_device_serial = response_original.get('deviceSerial')
                logger.debug(f"From response_original fetch device_serial for original txn : {api_device_serial}")
                api_card_txn_type_desc = response_original.get('cardTxnTypeDesc')
                logger.debug(f"From response_original fetch card_txn_type_desc for original txn : {api_card_txn_type_desc}")
                api_merchant_name = response_original.get('merchantName')
                logger.debug(f"From response_original fetch merchant_name for original txn : {api_merchant_name}")
                api_card_last_four_digit = response_original.get('cardLastFourDigit')
                logger.debug(f"From response_original fetch card_last_four_digit for original txn : {api_card_last_four_digit}")
                api_ext_ref_number = response_original.get('externalRefNumber')
                logger.debug(f"From response_original fetch external_ref_number for original txn : {api_ext_ref_number}")
                api_pmt_card_bin = response_original.get('paymentCardBin')
                logger.debug(f"From response_original fetch payment_card_bin for original txn : {api_pmt_card_bin}")
                api_display_pan = response_original.get('displayPAN')
                logger.debug(f"From response_original fetch display_pan for original txn : {api_display_pan}")
                api_auth_code = response_original.get('authCode')
                logger.debug(f"From response_original fetch auth_code for original txn : {api_auth_code}")
                api_card_type = response_original.get('cardType')
                logger.debug(f"From response_original fetch card_type for original txn : {api_card_type}")
                api_customer_name = response_original.get('customerName')
                logger.debug(f"From response_original fetch customer_name for original txn : {api_customer_name}")
                api_payer_name = response_original.get('payerName')
                logger.debug(f"From response_original fetch payer_name for original txn : {api_payer_name}")
                api_name_on_card = response_original.get('nameOnCard')
                logger.debug(f"From response_original fetch name_on_card for original txn : {api_name_on_card}")
                api_emi_term = response_original.get('emiTerm')
                logger.debug(f"From response_original fetch emi_term for original txn : {api_emi_term}")
                api_emi_status = response_original.get('emiStatus')
                logger.debug(f"From response_original fetch emi_status for original txn : {api_emi_status}")
                api_interest_rate = response_original.get('emiInterestRate')
                logger.debug(f"From response_original fetch emi_interest_rate for original txn : {api_interest_rate}")
                api_emi_type = response_original.get('externalRefNumber7')
                logger.debug(f"From response_original fetch emi_type for original txn : {api_emi_type}")
                api_loan_amt = response_original.get('emiDetails')['loanAmount']
                logger.debug(f"From response_original fetch loan_amount for original txn : {api_loan_amt}")
                api_monthly_emi = response_original.get('emiDetails')['emi']
                logger.debug(f"From response_original fetch monthly emi for original txn : {api_monthly_emi}")
                api_interest_amt = response_original.get('emiDetails')['interestAmount']
                logger.debug(f"From response_original fetch interest_amount for original txn : {api_interest_amt}")
                api_total_emi_amt = response_original.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"From response_original fetch total emi amount for original txn : {api_total_emi_amt}")
                api_net_cost = response_original.get('emiDetails')['netCost']
                logger.debug(f"From response_original fetch net cost for original txn : {api_net_cost}")

                response_refund = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn is : {response_refund}")
                api_amount_refund = response_refund.get('amount')
                logger.debug(f"From response_refund fetch amount for refund txn : {api_amount_refund}")
                api_payment_mode_refund = response_refund.get('paymentMode')
                logger.debug(f"From response_refund fetch payment_mode for refund txn : {api_payment_mode_refund}")
                api_payment_status_refund = response_refund.get('status')
                logger.debug(f"From response_refund fetch payment_status for refund txn : {api_payment_status_refund}")
                api_payment_state_refund = response_refund.get('states')[0]
                logger.debug(f"From response_refund fetch payment_state for refund txn : {api_payment_state_refund}")
                api_mid_refund = response_refund.get('mid')
                logger.debug(f"From response_refund fetch mid for refund txn : {api_mid_refund}")
                api_tid_refund = response_refund.get('tid')
                logger.debug(f"From response_refund fetch tid for refund txn : {api_tid_refund}")
                api_acquirer_code_refund = response_refund.get('acquirerCode')
                logger.debug(f"From response_refund fetch acquirer_code for refund txn : {api_acquirer_code_refund}")
                api_settle_status_refund = response_refund.get('settlementStatus')
                logger.debug(
                    f"From response_refund fetch settlement_status for refund txn : {api_settle_status_refund}")
                api_rrn_refund = response_refund.get('rrNumber')
                logger.debug(f"From response_refund fetch rrn for refund txn : {api_rrn_refund}")
                api_txn_type_refund = response_refund.get('txnType')
                logger.debug(f"From response_refund fetch txn_type for refund txn : {api_txn_type_refund}")
                api_org_code_refund = response_refund.get('orgCode')
                logger.debug(f"From response_refund fetch org_code for refund txn : {api_org_code_refund}")
                api_batch_number_refund = response_refund.get('batchNumber')
                logger.debug(f"From response_refund fetch batch_number for refund txn : {api_batch_number_refund}")
                api_pmt_card_brand_refund = response_refund.get('paymentCardBrand')
                logger.debug(f"From response_refund fetch payment_card_brand for refund txn : {api_pmt_card_brand_refund}")
                api_pmt_card_type_refund = response_refund.get('paymentCardType')
                logger.debug(f"From response_refund fetch payment_card_type for refund txn : {api_pmt_card_type_refund}")
                api_date_time_refund = response_refund.get('createdTime')
                logger.debug(f"From response_refund fetch date_time for refund txn : {api_date_time_refund}")
                api_card_txn_type_desc_refund = response_refund.get('cardTxnTypeDesc')
                logger.debug(f"From response_refund fetch card_txn_type_desc for refund txn : {api_card_txn_type_desc_refund}")
                api_customer_name_refund = response_refund.get('customerName')
                logger.debug(f"From response_refund fetch customer_name for refund txn : {api_customer_name_refund}")
                api_payer_name_refund = response_refund.get('payerName')
                logger.debug(f"From response_refund fetch payer_name for refund txn : {api_payer_name_refund}")
                api_merchant_name_refund = response_refund.get('merchantName')
                logger.debug(f"From response_refund fetch merchant_name for refund txn : {api_merchant_name_refund}")
                api_card_last_four_digit_refund = response_refund.get('cardLastFourDigit')
                logger.debug(f"From response_refund fetch card_last_four_digit for refund txn : {api_card_last_four_digit_refund}")
                api_ext_ref_number_refund = response_refund.get('externalRefNumber')
                logger.debug(f"From response_refund fetch external_ref_number for refund txn : {api_ext_ref_number_refund}")
                api_pmt_card_bin_refund = response_refund.get('paymentCardBin')
                logger.debug(f"From response_refund fetch payment_card_bin for refund txn : {api_pmt_card_bin_refund}")
                api_name_on_card_refund = response_refund.get('nameOnCard')
                logger.debug(f"From response_refund fetch name_on_card for refund txn : {api_name_on_card_refund}")
                api_display_pan_refund = response_refund.get('displayPAN')
                logger.debug(f"From response_refund fetch display_pan for refund txn : {api_display_pan_refund}")
                api_auth_code_refund = response_refund.get('authCode')
                logger.debug(f"From response_refund fetch auth_code for refund txn : {api_auth_code_refund}")
                api_card_type_refund = response_refund.get('cardType')
                logger.debug(f"From response_refund fetch card_type for refund txn : {api_card_type_refund}")
                api_emi_type_refund = response_original.get('externalRefNumber7')
                logger.debug(f"From response_refund fetch emi_type for refund txn : {api_emi_type_refund}")

                actual_api_values = {
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_status": api_payment_status,
                    "pmt_state": api_payment_state,
                    "mid": api_mid,
                    "tid": api_tid,
                    "acquirer_code": api_acquirer_code,
                    "settle_status": api_settle_status,
                    "rrn": api_rrn,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "org_code": api_org_code,
                    "batch_number": api_batch_number,
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
                    "card_txn_type_desc": api_card_txn_type_desc,
                    "auth_code": api_auth_code,
                    "card_last_four_digit": api_card_last_four_digit,
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "pmt_card_bin": api_pmt_card_bin,
                    "card_type": api_card_type,
                    "display_pan": api_display_pan,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "net_cost": api_net_cost,
                    "emi_type": api_emi_type,
                    "txn_amt_2": api_amount_refund,
                    "pmt_mode_2": api_payment_mode_refund,
                    "pmt_status_2": api_payment_status_refund,
                    "pmt_state_2": api_payment_state_refund,
                    "mid_2": api_mid_refund,
                    "tid_2": api_tid_refund,
                    "acquirer_code_2": api_acquirer_code_refund,
                    "settle_status_2": api_settle_status_refund,
                    "rrn_2": api_rrn_refund,
                    "txn_type_2": api_txn_type_refund,
                    "org_code_2": api_org_code_refund,
                    "batch_number_2": api_batch_number_refund,
                    "pmt_card_brand_2": api_pmt_card_brand,
                    "pmt_card_type_2": api_pmt_card_type_refund,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_refund),
                    "card_txn_type_desc_2": api_card_txn_type_desc_refund,
                    "auth_code_2": api_auth_code_refund,
                    "card_last_four_digit_2": api_card_last_four_digit_refund,
                    "customer_name_2": api_customer_name_refund,
                    "ext_ref_number_2": api_ext_ref_number_refund,
                    "merchant_name_2": api_merchant_name_refund,
                    "payer_name_2": api_payer_name_refund,
                    "pmt_card_bin_2": api_pmt_card_bin_refund,
                    "card_type_2": api_card_type_refund,
                    "display_pan_2": api_display_pan_refund,
                    "name_on_card_2": api_name_on_card_refund,
                    "emi_type_2": api_emi_type_refund
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": "L3TEST/CARD0010",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "txn_type": "CHARGE",
                    "settle_status": "SETTLED",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "03",
                    "card_last_four_digit": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "NORMAL_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "payer_name_2": "L3TEST/CARD0010",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "txn_type_2": "REFUND",
                    "settle_status_2": "PENDING",
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "417666",
                    "terminal_info_id_2": terminal_info_id,
                    "card_txn_type_2": "03",
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "orig_txn_id": txn_id,
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_txn,
                    "pmt_mode": payment_mode,
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "payer_name": payer_name,
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "pmt_gateway": payment_gateway,
                    "txn_type": txn_type,
                    "settle_status": settle_status,
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "terminal_info_id": terminal_info_id_txn,
                    "card_txn_type": card_txn_type,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name,
                    "interest_rate": emi_interest_rate,
                    "emi_status": emi_status,
                    "emi_term": emi_term,
                    "emi_type": emi_type,
                    "loan_amt": emi_loan_amount,
                    "monthly_emi": emi_amount_monthly,
                    "total_emi_amt": emi_total_amount,
                    "scheme_code": emi_scheme_code,
                    "emi_txn_amt": emi_txn_amount,
                    "emi_original_amt": emi_original_amount,
                    "txn_amt_2": refund_amount_txn,
                    "pmt_mode_2": refund_payment_mode,
                    "pmt_status_2": refund_pmt_status,
                    "pmt_state_2": refund_pmt_state,
                    "acquirer_code_2": refund_acquirer_code,
                    "payer_name_2": refund_payer_name,
                    "mid_2": refund_mid_txn,
                    "tid_2": refund_tid_txn,
                    "pmt_gateway_2": refund_payment_gateway,
                    "txn_type_2": refund_txn_type,
                    "settle_status_2": refund_settle_status,
                    "pmt_card_brand_2": refund_pmt_card_brand,
                    "pmt_card_type_2": refund_pmt_card_type,
                    "order_id_2": refund_order_id_txn,
                    "org_code_2": refund_org_code_txn,
                    "pmt_card_bin_2": refund_pmt_card_bin,
                    "terminal_info_id_2": refund_terminal_info_id_txn,
                    "card_txn_type_2": refund_card_txn_type,
                    "card_last_four_digit_2": refund_card_last_four_digit,
                    "customer_name_2": refund_customer_name,
                    "orig_txn_id": original_txn_id,
                    "emi_type_2": refund_emi_type
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.to_portal_format(created_date_db=created_time)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                expected_portal_values = {
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_time,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "auth_code_2": refund_auth_code,
                    "rrn_2": refund_rrn,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password, order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                portal_txn_id = transaction_details[1]['Transaction ID']
                portal_total_amount = transaction_details[1]['Total Amount']
                portal_auth_code = transaction_details[1]['Auth Code']
                portal_rrn = transaction_details[1]['RR Number']
                portal_txn_type = transaction_details[1]['Type']
                portal_txn_status = transaction_details[1]['Status']
                portal_user = transaction_details[1]['Username']

                portal_date_time_refund = transaction_details[0]['Date & Time']
                portal_txn_id_refund = transaction_details[0]['Transaction ID']
                portal_total_amount_refund = transaction_details[0]['Total Amount']
                portal_auth_code_refund = transaction_details[0]['Auth Code']
                portal_rrn_refund = transaction_details[0]['RR Number']
                portal_txn_type_refund = transaction_details[0]['Type']
                portal_txn_status_refund = transaction_details[0]['Status']
                portal_user_refund = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "auth_code": portal_auth_code,
                    "rrn": portal_rrn,
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type_2": portal_txn_type_refund,
                    "txn_amt_2": portal_total_amount_refund.split(' ')[1],
                    "username_2": portal_user_refund,
                    "txn_id_2": portal_txn_id_refund,
                    "auth_code_2": portal_auth_code_refund,
                    "rrn_2": portal_rrn_refund,
                    "date_time_2": portal_date_time_refund,
                    "pmt_status_2": portal_txn_status_refund
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=refund_posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": refund_rrn,
                    "AUTH CODE": refund_auth_code,
                    "CARD TYPE": "VISA",
                    "BATCH NO": refund_batch_number,
                    "TID": tid,
                    "payment_option": "REFUND",
                    "INVOICE NO": refund_invoice_number,
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "unnamed_section_text": customer_name
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=refund_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)

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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_115_05_036():
    """
    Sub Feature Code: UI_Common_Card_Normal_EMI_Refund_Via_API_For_Fallback_Root_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_12_Months_Tenure
    Sub Feature Description: Performing the normal EMI refund via API transaction for fallback to root org via HDFC Dummy PG
     using EMV VISA Credit card with pin for 12 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 05: NORMAL_EMI, 036: TC036
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

        query = f"select org_code from org_employee where username = {portal_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        root_org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {root_org_code}")

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code='{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY'"
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select bank_code from bin_info where bin='417666'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["emiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for normal emi setup to be enabled:  {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='INACTIVE')
        logger.debug(f"updated emi settings for {org_code} as inactive for credit card")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(3001, 4000)
            emi_plan_in_months = 12
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_bank_emi_pmt_mode()
            logger.info(f"Selected payment mode is Bank EMI")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"Selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"Selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            api_details = DBProcessor.get_api_details(api_name='Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API details  : {api_details} ")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Settlement api is : {settle_response}")

            query = f"select id from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn id from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            api_details = DBProcessor.get_api_details(api_name='Offline_Refund', request_body={
                "amount": amount,
                "originalTransactionId": txn_id,
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API details  : {api_details} ")
            refund_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {refund_response}")
            refund_txn_id = refund_response.get('txnId')
            logger.debug(f"From response fetch txn_id : {refund_txn_id}")

            query = f"select * from emi where org_code='{root_org_code}' and status = 'ACTIVE' and " \
                    f"issuer_code='HDFC' and card_type='CREDIT' AND term = '{emi_plan_in_months} month' and " \
                    f"tid_type='CIB' and emi_type='NORMAL' order by created_time asc limit 1"
            logger.debug(f"Query to fetch data from the emi table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from emi table :{result}")
            interest_rate = result['interest_rate'].values[0]
            logger.debug(f"Fetching interest_rate from the emi table : {interest_rate}")
            term = result['term'].values[0]
            logger.debug(f"Fetching term from the emi table : {term}")
            scheme_code = result['scheme_code'].values[0]
            logger.debug(f"Fetching scheme_code from the emi table : {scheme_code}")

            logger.debug(f"Started calculating emi part")
            monthly_interest_rate = interest_rate / (12 * 100)
            cal_monthly_emi_amt = amount * monthly_interest_rate * (
                    (1 + monthly_interest_rate) ** emi_plan_in_months) / (
                                          (1 + monthly_interest_rate) ** emi_plan_in_months - 1)
            monthly_emi = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi}")
            cal_total_emi_amt = monthly_emi * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest}")

            query = f"select * from txn where id = '{txn_id}'"
            logger.debug(f"Query to fetch txn details for original txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for original txn : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for original txn : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for original txn : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for original txn : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for original txn : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for original txn : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for original txn : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for original txn : {pmt_status}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for original txn : {issuer_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for original txn : {txn_type}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for original txn : {pmt_state}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for original txn : {payment_gateway}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table for original txn : {batch_number}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for original txn : {amount_txn}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table for original txn : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table for original txn : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table for original txn : {card_last_four_digit}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for original txn : {payment_mode}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for original txn : {merchant_name}")
            pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table for original txn : {pmt_card_bin}")
            terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table for original txn : {terminal_info_id_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for original txn : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for original txn : {tid_txn}")
            device_serial_txn = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from the txn table for original txn : {device_serial_txn}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for original txn : {order_id_txn}")
            card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table for original txn : {card_txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for original txn : {org_code_txn}")
            emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table for original txn : {emi_type}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {posting_date}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate}")
            emi_status = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status}")
            emi_term = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term}")
            emi_loan_amount = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount}")
            emi_amount_monthly = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly}")
            emi_total_amount = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount}")
            emi_scheme_code = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code}")
            emi_txn_amount = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount}")
            emi_original_amount = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount}")

            query = f"select * from txn where id = '{refund_txn_id}'"
            logger.debug(f"Query to fetch txn details for refund txn from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result from txn table for refund txn : {result}")
            refund_amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for refund txn : {refund_amount_txn}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for refund txn : {refund_created_time}")
            refund_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for refund txn : {refund_acquirer_code}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for refund txn : {refund_auth_code}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for refund txn : {refund_customer_name}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for refund txn : {refund_payer_name}")
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for refund txn : {refund_rrn}")
            refund_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for refund txn : {refund_settle_status}")
            refund_pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for refund txn : {refund_pmt_status}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for refund txn : {refund_txn_type}")
            refund_pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for refund txn : {refund_pmt_state}")
            refund_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table for refund txn : {refund_payment_gateway}")
            refund_batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number from the txn table for refund txn : {refund_batch_number}")
            refund_pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table for refund txn : {refund_pmt_card_brand}")
            refund_pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table for refund txn : {refund_pmt_card_type}")
            refund_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table for refund txn : {refund_card_last_four_digit}")
            refund_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for refund txn : {refund_payment_mode}")
            refund_merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for refund txn : {refund_merchant_name}")
            refund_pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table for refund txn : {refund_pmt_card_bin}")
            refund_terminal_info_id_txn = result['terminal_info_id'].values[0]
            logger.debug(f"Fetching terminal_info_id from the txn table for refund txn : {refund_terminal_info_id_txn}")
            refund_mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for refund txn : {refund_mid_txn}")
            refund_tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for refund txn : {refund_tid_txn}")
            refund_order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for refund txn : {refund_order_id_txn}")
            refund_card_txn_type = result['card_txn_type'].values[0]
            logger.debug(f"Fetching card_txn_type from the txn table for refund txn : {refund_card_txn_type}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for refund txn : {refund_org_code_txn}")
            refund_invoice_number = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table for refund txn : {refund_invoice_number}")
            original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching original txn_id from the txn table for refund txn : {original_txn_id}")
            refund_emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table for refund txn : {refund_emi_type}")
            refund_posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {refund_posting_date}")
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
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                refund_date_and_time = date_time_converter.to_app_format(posting_date_db=refund_posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_time,
                    "device_serial": device_serial,
                    "batch_number": batch_number,
                    "card_type_desc": "*0102 EMV with PIN",
                    "mid": mid,
                    "tid": tid,
                    "customer_name": "L3TEST",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "customer": "L3TEST/CARD0010",
                    "emi_status": "PENDING",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": refund_txn_id,
                    "pmt_status_2": "REFUNDED",
                    "rr_number_2": refund_rrn,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "customer_name_2": "L3TEST",
                    "settle_status_2": "PENDING",
                    "auth_code_2": refund_auth_code,
                    "date_2": refund_date_and_time,
                    "device_serial_2": device_serial,
                    "batch_number_2": refund_batch_number,
                    "card_type_desc_2": "*0102 EMV with PIN",
                    "mid_2": mid,
                    "tid_2": tid
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.info(f"Resetting the app_driver to login again in the MPOSX application")
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the original txn : {txn_id}, {app_payment_by}")
                app_card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the original txn : {txn_id}, {app_card_type}")
                app_customer = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the original txn : {txn_id}, {app_customer}")
                app_emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the original txn : {txn_id}, {app_emi_status}")
                app_tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the original txn : {txn_id}, {app_tenure}")
                app_lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the original txn : {txn_id}, {app_lender}")
                app_monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the original txn : {txn_id}, {app_monthly_emi}")
                app_total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the original txn : {txn_id}, {app_total_interest}")
                app_total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the original txn : {txn_id}, {app_total_emi_amount}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the original txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the original txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the original txn : {txn_id}, {app_net_effective_price}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the original txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the original txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the original txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the original txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the original txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the original txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the original txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the original txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the original txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the original txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the original txn : {txn_id}, {app_device_serial}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the original txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the original txn : {txn_id}, {app_card_type_desc}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the original txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the original txn : {txn_id}, {app_tid}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the original txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=refund_txn_id)
                app_amount_refund = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the refund txn : {refund_txn_id}, {app_amount_refund}")
                app_order_id_refund = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the refund txn : {refund_txn_id}, {app_order_id_refund}")
                app_payment_msg_refund = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the refund txn : {refund_txn_id}, {app_payment_msg_refund}")
                app_payment_mode_refund = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the refund txn : {refund_txn_id}, {app_payment_mode_refund}")
                app_payment_status_refund = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the refund txn : {refund_txn_id}, {app_payment_status_refund}")
                app_txn_id_refund = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the refund txn : {refund_txn_id}, {app_txn_id_refund}")
                app_customer_name_refund = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the refund txn : {refund_txn_id}, {app_customer_name_refund}")
                app_date_time_refund = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the refund txn : {refund_txn_id}, {app_date_time_refund}")
                app_settle_status_refund = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the refund txn : {refund_txn_id}, {app_settle_status_refund}")
                app_rrn_refund = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the refund txn : {refund_txn_id}, {app_rrn_refund}")
                app_auth_code_refund = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the refund txn : {refund_txn_id}, {app_auth_code_refund}")
                app_device_serial_refund = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device_serial from txn history for the refund txn : {refund_txn_id}, {app_device_serial_refund}")
                app_batch_number_refund = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch_number from txn history for the refund txn : {refund_txn_id}, {app_batch_number_refund}")
                app_card_type_desc_refund = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card_type_desc from txn history for the refund txn : {refund_txn_id}, {app_card_type_desc_refund}")
                app_mid_refund = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid from txn history for the refund txn : {refund_txn_id}, {app_mid_refund}")
                app_tid_refund = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid from txn history for the refund txn : {refund_txn_id}, {app_tid_refund}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": app_payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settle_status,
                    "auth_code": app_auth_code,
                    "date": app_date_time,
                    "device_serial": app_device_serial,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "mid": app_mid,
                    "tid": app_tid,
                    "customer_name": app_customer_name,
                    "pmt_by": app_payment_by,
                    "card_type": app_card_type,
                    "customer": app_customer,
                    "emi_status": app_emi_status,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1],
                    "txn_amt_2": app_amount_refund.split(' ')[1],
                    "pmt_mode_2": app_payment_mode_refund,
                    "txn_id_2": app_txn_id_refund,
                    "pmt_status_2": app_payment_status_refund.split(':')[1],
                    "rr_number_2": app_rrn_refund,
                    "order_id_2": app_order_id_refund,
                    "pmt_msg_2": app_payment_msg_refund,
                    "customer_name_2": app_customer_name_refund,
                    "settle_status_2": app_settle_status_refund,
                    "auth_code_2": app_auth_code_refund,
                    "date_2": app_date_time_refund,
                    "device_serial_2": app_device_serial_refund,
                    "batch_number_2": app_batch_number_refund,
                    "card_type_desc_2": app_card_type_desc_refund,
                    "mid_2": app_mid_refund,
                    "tid_2": app_tid_refund
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.db_datetime(date_from_db=created_time)
                refund_date_and_time = date_time_converter.db_datetime(date_from_db=refund_created_time)
                expected_api_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "rrn": rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "org_code": org_code,
                    "batch_number": batch_number,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "date": date_time,
                    "device_serial": device_serial,
                    "card_txn_type_desc": "EMV with PIN",
                    "auth_code": auth_code,
                    "card_last_four_digit": "0102",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "card_type": "VISA",
                    "display_pan": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "name_on_card": "L3TEST/CARD0010",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "interest_amt": total_interest,
                    "total_emi_amt": total_emi,
                    "net_cost": total_emi,
                    "emi_type": "NORMAL_EMI",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "mid_2": mid,
                    "tid_2": tid,
                    "acquirer_code_2": "HDFC",
                    "settle_status_2": "PENDING",
                    "rrn_2": refund_rrn,
                    "txn_type_2": "REFUND",
                    "org_code_2": org_code,
                    "batch_number_2": refund_batch_number,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "date_2": refund_date_and_time,
                    "card_txn_type_desc_2": "EMV with PIN",
                    "auth_code_2": refund_auth_code,
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": refund_merchant_name,
                    "payer_name_2": "L3TEST/CARD0010",
                    "pmt_card_bin_2": "417666",
                    "card_type_2": "VISA",
                    "display_pan_2": "0102",
                    "name_on_card_2": "L3TEST/CARD0010",
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_original = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_original}")
                api_amount = response_original.get('amount')
                logger.debug(f"From response_original fetch amount for original txn : {api_amount}")
                api_payment_mode = response_original.get('paymentMode')
                logger.debug(f"From response_original fetch payment_mode for original txn : {api_payment_mode}")
                api_payment_status = response_original.get('status')
                logger.debug(f"From response_original fetch payment_status for original txn : {api_payment_status}")
                api_payment_state = response_original.get('states')[0]
                logger.debug(f"From response_original fetch payment_state for original txn : {api_payment_state}")
                api_mid = response_original.get('mid')
                logger.debug(f"From response_original fetch mid for original txn : {api_mid}")
                api_tid = response_original.get('tid')
                logger.debug(f"From response_original fetch tid for original txn : {api_tid}")
                api_acquirer_code = response_original.get('acquirerCode')
                logger.debug(f"From response_original fetch acquirer_code for original txn : {api_acquirer_code}")
                api_settle_status = response_original.get('settlementStatus')
                logger.debug(f"From response_original fetch settlement_status for original txn : {api_settle_status}")
                api_rrn = response_original.get('rrNumber')
                logger.debug(f"From response_original fetch rrn for original txn : {api_rrn}")
                api_issuer_code = response_original.get('issuerCode')
                logger.debug(f"From response_original fetch issuer_code for original txn : {api_issuer_code}")
                api_txn_type = response_original.get('txnType')
                logger.debug(f"From response_original fetch txn_type for original txn : {api_txn_type}")
                api_org_code = response_original.get('orgCode')
                logger.debug(f"From response_original fetch org_code for original txn : {api_org_code}")
                api_batch_number = response_original.get('batchNumber')
                logger.debug(f"From response_original fetch batch_number for original txn : {api_batch_number}")
                api_pmt_card_brand = response_original.get('paymentCardBrand')
                logger.debug(f"From response_original fetch payment_card_brand for original txn : {api_pmt_card_brand}")
                api_pmt_card_type = response_original.get('paymentCardType')
                logger.debug(f"From response_original fetch payment_card_type for original txn : {api_pmt_card_type}")
                api_date_time = response_original.get('createdTime')
                logger.debug(f"From response_original fetch date_time for original txn : {api_date_time}")
                api_device_serial = response_original.get('deviceSerial')
                logger.debug(f"From response_original fetch device_serial for original txn : {api_device_serial}")
                api_card_txn_type_desc = response_original.get('cardTxnTypeDesc')
                logger.debug(f"From response_original fetch card_txn_type_desc for original txn : {api_card_txn_type_desc}")
                api_merchant_name = response_original.get('merchantName')
                logger.debug(f"From response_original fetch merchant_name for original txn : {api_merchant_name}")
                api_card_last_four_digit = response_original.get('cardLastFourDigit')
                logger.debug(f"From response_original fetch card_last_four_digit for original txn : {api_card_last_four_digit}")
                api_ext_ref_number = response_original.get('externalRefNumber')
                logger.debug(f"From response_original fetch external_ref_number for original txn : {api_ext_ref_number}")
                api_pmt_card_bin = response_original.get('paymentCardBin')
                logger.debug(f"From response_original fetch payment_card_bin for original txn : {api_pmt_card_bin}")
                api_display_pan = response_original.get('displayPAN')
                logger.debug(f"From response_original fetch display_pan for original txn : {api_display_pan}")
                api_auth_code = response_original.get('authCode')
                logger.debug(f"From response_original fetch auth_code for original txn : {api_auth_code}")
                api_card_type = response_original.get('cardType')
                logger.debug(f"From response_original fetch card_type for original txn : {api_card_type}")
                api_customer_name = response_original.get('customerName')
                logger.debug(f"From response_original fetch customer_name for original txn : {api_customer_name}")
                api_payer_name = response_original.get('payerName')
                logger.debug(f"From response_original fetch payer_name for original txn : {api_payer_name}")
                api_name_on_card = response_original.get('nameOnCard')
                logger.debug(f"From response_original fetch name_on_card for original txn : {api_name_on_card}")
                api_emi_term = response_original.get('emiTerm')
                logger.debug(f"From response_original fetch emi_term for original txn : {api_emi_term}")
                api_emi_status = response_original.get('emiStatus')
                logger.debug(f"From response_original fetch emi_status for original txn : {api_emi_status}")
                api_interest_rate = response_original.get('emiInterestRate')
                logger.debug(f"From response_original fetch emi_interest_rate for original txn : {api_interest_rate}")
                api_emi_type = response_original.get('externalRefNumber7')
                logger.debug(f"From response_original fetch emi_type for original txn : {api_emi_type}")
                api_loan_amt = response_original.get('emiDetails')['loanAmount']
                logger.debug(f"From response_original fetch loan_amount for original txn : {api_loan_amt}")
                api_monthly_emi = response_original.get('emiDetails')['emi']
                logger.debug(f"From response_original fetch monthly emi for original txn : {api_monthly_emi}")
                api_interest_amt = response_original.get('emiDetails')['interestAmount']
                logger.debug(f"From response_original fetch interest_amount for original txn : {api_interest_amt}")
                api_total_emi_amt = response_original.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"From response_original fetch total emi amount for original txn : {api_total_emi_amt}")
                api_net_cost = response_original.get('emiDetails')['netCost']
                logger.debug(f"From response_original fetch net cost for original txn : {api_net_cost}")

                response_refund = [x for x in response["txns"] if x["txnId"] == refund_txn_id][0]
                logger.debug(f"Response after filtering data of refund txn is : {response_refund}")
                api_amount_refund = response_refund.get('amount')
                logger.debug(f"From response_refund fetch amount for refund txn : {api_amount_refund}")
                api_payment_mode_refund = response_refund.get('paymentMode')
                logger.debug(f"From response_refund fetch payment_mode for refund txn : {api_payment_mode_refund}")
                api_payment_status_refund = response_refund.get('status')
                logger.debug(f"From response_refund fetch payment_status for refund txn : {api_payment_status_refund}")
                api_payment_state_refund = response_refund.get('states')[0]
                logger.debug(f"From response_refund fetch payment_state for refund txn : {api_payment_state_refund}")
                api_mid_refund = response_refund.get('mid')
                logger.debug(f"From response_refund fetch mid for refund txn : {api_mid_refund}")
                api_tid_refund = response_refund.get('tid')
                logger.debug(f"From response_refund fetch tid for refund txn : {api_tid_refund}")
                api_acquirer_code_refund = response_refund.get('acquirerCode')
                logger.debug(f"From response_refund fetch acquirer_code for refund txn : {api_acquirer_code_refund}")
                api_settle_status_refund = response_refund.get('settlementStatus')
                logger.debug(
                    f"From response_refund fetch settlement_status for refund txn : {api_settle_status_refund}")
                api_rrn_refund = response_refund.get('rrNumber')
                logger.debug(f"From response_refund fetch rrn for refund txn : {api_rrn_refund}")
                api_txn_type_refund = response_refund.get('txnType')
                logger.debug(f"From response_refund fetch txn_type for refund txn : {api_txn_type_refund}")
                api_org_code_refund = response_refund.get('orgCode')
                logger.debug(f"From response_refund fetch org_code for refund txn : {api_org_code_refund}")
                api_batch_number_refund = response_refund.get('batchNumber')
                logger.debug(f"From response_refund fetch batch_number for refund txn : {api_batch_number_refund}")
                api_pmt_card_brand_refund = response_refund.get('paymentCardBrand')
                logger.debug(f"From response_refund fetch payment_card_brand for refund txn : {api_pmt_card_brand_refund}")
                api_pmt_card_type_refund = response_refund.get('paymentCardType')
                logger.debug(f"From response_refund fetch payment_card_type for refund txn : {api_pmt_card_type_refund}")
                api_date_time_refund = response_refund.get('createdTime')
                logger.debug(f"From response_refund fetch date_time for refund txn : {api_date_time_refund}")
                api_card_txn_type_desc_refund = response_refund.get('cardTxnTypeDesc')
                logger.debug(f"From response_refund fetch card_txn_type_desc for refund txn : {api_card_txn_type_desc_refund}")
                api_customer_name_refund = response_refund.get('customerName')
                logger.debug(f"From response_refund fetch customer_name for refund txn : {api_customer_name_refund}")
                api_payer_name_refund = response_refund.get('payerName')
                logger.debug(f"From response_refund fetch payer_name for refund txn : {api_payer_name_refund}")
                api_merchant_name_refund = response_refund.get('merchantName')
                logger.debug(f"From response_refund fetch merchant_name for refund txn : {api_merchant_name_refund}")
                api_card_last_four_digit_refund = response_refund.get('cardLastFourDigit')
                logger.debug(f"From response_refund fetch card_last_four_digit for refund txn : {api_card_last_four_digit_refund}")
                api_ext_ref_number_refund = response_refund.get('externalRefNumber')
                logger.debug(f"From response_refund fetch external_ref_number for refund txn : {api_ext_ref_number_refund}")
                api_pmt_card_bin_refund = response_refund.get('paymentCardBin')
                logger.debug(f"From response_refund fetch payment_card_bin for refund txn : {api_pmt_card_bin_refund}")
                api_name_on_card_refund = response_refund.get('nameOnCard')
                logger.debug(f"From response_refund fetch name_on_card for refund txn : {api_name_on_card_refund}")
                api_display_pan_refund = response_refund.get('displayPAN')
                logger.debug(f"From response_refund fetch display_pan for refund txn : {api_display_pan_refund}")
                api_auth_code_refund = response_refund.get('authCode')
                logger.debug(f"From response_refund fetch auth_code for refund txn : {api_auth_code_refund}")
                api_card_type_refund = response_refund.get('cardType')
                logger.debug(f"From response_refund fetch card_type for refund txn : {api_card_type_refund}")
                api_emi_type_refund = response_original.get('externalRefNumber7')
                logger.debug(f"From response_refund fetch emi_type for refund txn : {api_emi_type_refund}")

                actual_api_values = {
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_status": api_payment_status,
                    "pmt_state": api_payment_state,
                    "mid": api_mid,
                    "tid": api_tid,
                    "acquirer_code": api_acquirer_code,
                    "settle_status": api_settle_status,
                    "rrn": api_rrn,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "org_code": api_org_code,
                    "batch_number": api_batch_number,
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
                    "card_txn_type_desc": api_card_txn_type_desc,
                    "auth_code": api_auth_code,
                    "card_last_four_digit": api_card_last_four_digit,
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "pmt_card_bin": api_pmt_card_bin,
                    "card_type": api_card_type,
                    "display_pan": api_display_pan,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "net_cost": api_net_cost,
                    "emi_type": api_emi_type,
                    "txn_amt_2": api_amount_refund,
                    "pmt_mode_2": api_payment_mode_refund,
                    "pmt_status_2": api_payment_status_refund,
                    "pmt_state_2": api_payment_state_refund,
                    "mid_2": api_mid_refund,
                    "tid_2": api_tid_refund,
                    "acquirer_code_2": api_acquirer_code_refund,
                    "settle_status_2": api_settle_status_refund,
                    "rrn_2": api_rrn_refund,
                    "txn_type_2": api_txn_type_refund,
                    "org_code_2": api_org_code_refund,
                    "batch_number_2": api_batch_number_refund,
                    "pmt_card_brand_2": api_pmt_card_brand,
                    "pmt_card_type_2": api_pmt_card_type_refund,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_refund),
                    "card_txn_type_desc_2": api_card_txn_type_desc_refund,
                    "auth_code_2": api_auth_code_refund,
                    "card_last_four_digit_2": api_card_last_four_digit_refund,
                    "customer_name_2": api_customer_name_refund,
                    "ext_ref_number_2": api_ext_ref_number_refund,
                    "merchant_name_2": api_merchant_name_refund,
                    "payer_name_2": api_payer_name_refund,
                    "pmt_card_bin_2": api_pmt_card_bin_refund,
                    "card_type_2": api_card_type_refund,
                    "display_pan_2": api_display_pan_refund,
                    "name_on_card_2": api_name_on_card_refund,
                    "emi_type_2": api_emi_type_refund
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": "L3TEST/CARD0010",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "txn_type": "CHARGE",
                    "settle_status": "SETTLED",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "card_txn_type": "03",
                    "card_last_four_digit": "0102",
                    "customer_name": "L3TEST/CARD0010",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "NORMAL_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "payer_name_2": "L3TEST/CARD0010",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "txn_type_2": "REFUND",
                    "settle_status_2": "PENDING",
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "417666",
                    "terminal_info_id_2": terminal_info_id,
                    "card_txn_type_2": "03",
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "orig_txn_id": txn_id,
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_txn,
                    "pmt_mode": payment_mode,
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "payer_name": payer_name,
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "pmt_gateway": payment_gateway,
                    "txn_type": txn_type,
                    "settle_status": settle_status,
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "terminal_info_id": terminal_info_id_txn,
                    "card_txn_type": card_txn_type,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name,
                    "interest_rate": emi_interest_rate,
                    "emi_status": emi_status,
                    "emi_term": emi_term,
                    "emi_type": emi_type,
                    "loan_amt": emi_loan_amount,
                    "monthly_emi": emi_amount_monthly,
                    "total_emi_amt": emi_total_amount,
                    "scheme_code": emi_scheme_code,
                    "emi_txn_amt": emi_txn_amount,
                    "emi_original_amt": emi_original_amount,
                    "txn_amt_2": refund_amount_txn,
                    "pmt_mode_2": refund_payment_mode,
                    "pmt_status_2": refund_pmt_status,
                    "pmt_state_2": refund_pmt_state,
                    "acquirer_code_2": refund_acquirer_code,
                    "payer_name_2": refund_payer_name,
                    "mid_2": refund_mid_txn,
                    "tid_2": refund_tid_txn,
                    "pmt_gateway_2": refund_payment_gateway,
                    "txn_type_2": refund_txn_type,
                    "settle_status_2": refund_settle_status,
                    "pmt_card_brand_2": refund_pmt_card_brand,
                    "pmt_card_type_2": refund_pmt_card_type,
                    "order_id_2": refund_order_id_txn,
                    "org_code_2": refund_org_code_txn,
                    "pmt_card_bin_2": refund_pmt_card_bin,
                    "terminal_info_id_2": refund_terminal_info_id_txn,
                    "card_txn_type_2": refund_card_txn_type,
                    "card_last_four_digit_2": refund_card_last_four_digit,
                    "customer_name_2": refund_customer_name,
                    "orig_txn_id": original_txn_id,
                    "emi_type_2": refund_emi_type
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                date_time = date_time_converter.to_portal_format(created_date_db=created_time)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_date_db=refund_created_time)
                expected_portal_values = {
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_time,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "auth_code_2": refund_auth_code,
                    "rrn_2": refund_rrn,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password, order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                portal_txn_id = transaction_details[1]['Transaction ID']
                portal_total_amount = transaction_details[1]['Total Amount']
                portal_auth_code = transaction_details[1]['Auth Code']
                portal_rrn = transaction_details[1]['RR Number']
                portal_txn_type = transaction_details[1]['Type']
                portal_txn_status = transaction_details[1]['Status']
                portal_user = transaction_details[1]['Username']

                portal_date_time_refund = transaction_details[0]['Date & Time']
                portal_txn_id_refund = transaction_details[0]['Transaction ID']
                portal_total_amount_refund = transaction_details[0]['Total Amount']
                portal_auth_code_refund = transaction_details[0]['Auth Code']
                portal_rrn_refund = transaction_details[0]['RR Number']
                portal_txn_type_refund = transaction_details[0]['Type']
                portal_txn_status_refund = transaction_details[0]['Status']
                portal_user_refund = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "auth_code": portal_auth_code,
                    "rrn": portal_rrn,
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type_2": portal_txn_type_refund,
                    "txn_amt_2": portal_total_amount_refund.split(' ')[1],
                    "username_2": portal_user_refund,
                    "txn_id_2": portal_txn_id_refund,
                    "auth_code_2": portal_auth_code_refund,
                    "rrn_2": portal_rrn_refund,
                    "date_time_2": portal_date_time_refund,
                    "pmt_status_2": portal_txn_status_refund
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=refund_posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": refund_rrn,
                    "AUTH CODE": refund_auth_code,
                    "CARD TYPE": "VISA",
                    "BATCH NO": refund_batch_number,
                    "TID": tid,
                    "payment_option": "REFUND",
                    "INVOICE NO": refund_invoice_number,
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "unnamed_section_text": customer_name
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=refund_txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)

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

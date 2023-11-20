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
def test_common_100_115_06_009():
    """
    Sub Feature Code: UI_Common_Card_Instant_EMI_Refund_Via_API_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_3_Months_Tenure
    Sub Feature Description: Performing the instant EMI refund via API  transaction for an org (not ezetap) via HDFC Dummy PG
    using EMV VISA Credit card with pin for 3 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 06: Instant_EMI, 009: TC009
    """
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"fetching org code from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

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
        api_details["RequestBody"]["settings"]["instantEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for credit card")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            emi_plan_in_months = 3
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            amount = random.randint(3500, 4500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_payment_option_emi_on_card()
            logger.debug(f"selected payment option emi on card")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                    f"issuer_code='HDFC' and card_type='CREDIT' AND term = '{emi_plan_in_months} month' and emi_type='NORMAL'" \
                    f"and tid_type='CIB' order by created_time asc limit 1"
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
            monthly_emi_cal = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi_cal}")
            cal_total_emi_amt = monthly_emi_cal * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest_cal = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest_cal}")

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch id from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn table : {result} ")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")

            api_details = DBProcessor.get_api_details('Offline_Refund', request_body={
                "password": app_password,
                "username": app_username,
                "amount": amount,
                "originalTransactionId": txn_id
            })
            logger.debug(f"API DETAILS for Offline_Refund api : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {response}")
            txn_id_2 = response["txnId"]
            logger.debug(f"Fetching transaction id for refund from response : {txn_id_2}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for original txn : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for original txn : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for original txn : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for original txn : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for original txn : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for original txn : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for original txn : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for original txn : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for original txn : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for original txn : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for original txn : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for original txn : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table for original txn : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for original txn : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for original txn : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for original txn : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for original txn : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for original txn : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table for original txn : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for original txn : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for original txn : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for original txn : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for original txn : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for original txn : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for original txn : {card_last_four_digit_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for original txn : {merchant_name}")
            emi_type_db = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for original txn : {emi_type_db}")
            customer_name_db = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from the txn table for original txn : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for original txn : {payer_name_db}")

            query = f"select * from txn where id='{txn_id_2}'"
            logger.debug(f"Query to fetch data from txn table, for refunded txn {txn_id_2} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for refunded txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for refunded txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for refunded txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for refunded txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for refunded txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for refunded txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for refunded txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for refunded txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for refunded txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for refunded txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for refunded txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for refunded txn : {settlement_status_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for refunded txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for refunded txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for refunded txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for refunded txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for refunded txn : {order_id_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for refunded txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for refunded txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for refunded txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for refunded txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for refunded txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for refunded txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table for refunded txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for refunded txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for refunded txn : {merchant_name_2}")
            invoice_number_db_2 = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table for refunded txn : {invoice_number_db_2}")
            emi_type_db_2 = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for refunded txn : {emi_type_db_2}")
            orig_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching orig_txn_id from the txn table for refunded txn : {orig_txn_id}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate_db = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate_db}")
            emi_status_db = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status_db}")
            emi_term_db = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term_db}")
            emi_loan_amount_db = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount_db}")
            emi_amount_monthly_db = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly_db}")
            emi_total_amount_db = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount_db}")
            emi_scheme_code_db = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code_db}")
            emi_txn_amount_db = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount_db}")
            emi_original_amount_db = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount_db}")
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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=created_time)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=created_time_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "card_type_desc": "*0102 EMV with PIN",
                    "customer_name": "L3TEST",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "emi_status": "PENDING",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi_cal),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "total_interest": "{:,.2f}".format(total_interest_cal),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest_cal),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "customer": customer_name_db,
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "L3TEST",
                    "card_type_desc_2": "*0102 EMV with PIN"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login(username=app_username, password=app_password)
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the original txn : {txn_id}, {payment_by}")
                card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the original txn : {txn_id}, {card_type}")
                emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the original txn : {txn_id}, {emi_status}")
                lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the original txn : {txn_id}, {lender}")
                monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the original txn : {txn_id}, {monthly_emi}")
                total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the original txn : {txn_id}, {total_emi_amount}")
                total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the original txn : {txn_id}, {total_interest}")
                loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the original txn : {txn_id}, {loan_amount}")
                interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the original txn : {txn_id}, {interest_amount}")
                net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the original txn : {txn_id}, {net_effective_price}")
                tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the original txn : {txn_id}, {tenure}")
                customer_app = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the original txn : {txn_id}, {customer_app}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the original txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the original txn : {txn_id}, {payment_mode}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the original txn : {txn_id}, {payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the original txn : {txn_id}, {app_txn_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the original txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the original txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the original txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the original txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for theoriginal  txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the original txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the original txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the original txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the original txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the original txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the original txn : {txn_id}, {app_card_type_desc}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the original txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the refunded txn : {txn_id_2}, {payment_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the refunded txn : {txn_id_2}, {app_rrn_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the refunded txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the refunded txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the refunded txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the refunded txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the refunded txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the refunded txn : {txn_id_2}, {app_customer_name_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the refunded txn : {txn_id_2}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rrn": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "customer_name": app_customer_name,
                    "pmt_by": payment_by,
                    "card_type": card_type,
                    "emi_status": emi_status,
                    "lender": lender,
                    "monthly_emi": monthly_emi.split(' ')[1],
                    "total_emi_amt": total_emi_amount.split(' ')[1],
                    "total_interest": total_interest.split(' ')[1],
                    "loan_amt": loan_amount.split(' ')[1],
                    "interest_amt": interest_amount.split(' ')[2],
                    "net_eff_price": net_effective_price.split(' ')[1],
                    "tenure": tenure,
                    "customer": customer_app,
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
                    "card_type_desc_2": app_card_type_desc_2
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "EMV with PIN",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0102",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "display_pan": "0102",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "interest_amt": total_interest_cal,
                    "total_emi_amt": total_emi,
                    "emi_type": "NORMAL_EMI",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "name_on_card": "L3TEST/CARD0010",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "card_txn_type_2": "EMV with PIN",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "L3TEST/CARD0010",
                    "pmt_card_bin_2": "417666",
                    "name_on_card_2": "L3TEST/CARD0010",
                    "display_pan_2": "0102",
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status from response for original txn : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount from response for original txn : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode from response for original txn : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state from response for original txn : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn from response for original txn : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for original txn : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer code from response for original txn : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for original txn : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org code from response for original txn : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid from response for original txn : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid from response for original txn : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction type from response for original txn : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth code from response for original txn : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date and time from response for original txn : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device serial from response for original txn : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username from response for original txn : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction id from response for original txn : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for original txn : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for original txn : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for original txn : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch number from response for original txn : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for original txn : {card_last_four_digit_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for original txn : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant name from response for original txn : {merchant_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for original txn : {payment_card_bin_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for original txn : {display_pan_api}")
                api_emi_term = response_1.get('emiTerm')
                logger.debug(f"Fetching emi_term from response for original txn : {api_emi_term}")
                api_emi_status = response_1.get('emiStatus')
                logger.debug(f"Fetching emi_status from response for original txn : {api_emi_status}")
                api_interest_rate = response_1.get('emiInterestRate')
                logger.debug(f"Fetching emi_interest_rate from response for original txn : {api_interest_rate}")
                api_emi_type = response_1.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for original txn : {api_emi_type}")
                api_loan_amt = response_1.get('emiDetails')['loanAmount']
                logger.debug(f"Fetching loan_amount from response for original txn : {api_loan_amt}")
                api_monthly_emi = response_1.get('emiDetails')['emi']
                logger.debug(f"Fetching monthly emi from response for original txn : {api_monthly_emi}")
                api_interest_amt = response_1.get('emiDetails')['interestAmount']
                logger.debug(f"Fetching interest_amount from response for original txn : {api_interest_amt}")
                api_total_emi_amt = response_1.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"Fetching total emi amount from response for original txn : {api_total_emi_amt}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer name from response for original txn : {customer_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer name from response for original txn : {payer_name_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name on card from response for original txn : {name_on_card_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status from response for refunded txn : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount from response for refunded txn : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment mode from response for refunded txn : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state from response for refunded txn : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn from response for refunded txn : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for refunded txn : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for refunded txn : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org code from response for refunded txn : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid from response for refunded txn : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid from response for refunded txn : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction type from response for refunded txn : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth code from response for refunded txn : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date and time from response for refunded txn : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username from response for refunded txn : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction id from response for refunded txn : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for refunded txn : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for refunded txn : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for refunded txn : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch number from response for refunded txn : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for refunded txn : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer name from response for refunded txn : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for refunded txn : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant name from response for refunded txn : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer name from response for refunded txn : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for refunded txn : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name on card from response for refunded txn : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for refunded txn : {display_pan_api_2}")
                emi_type_api_2 = response_2.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for refunded txn : {emi_type_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "device_serial": device_serial_api,
                    "username": username_api,
                    "txn_id": txn_id_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_txn_type": card_txn_type_api,
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "external_ref": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "display_pan": display_pan_api,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "emi_type": api_emi_type,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "name_on_card": name_on_card_api,
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2,
                    "emi_type_2": emi_type_api_2
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
                    "txn_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "03",
                    "card_last_four_digit": "0102",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "NORMAL_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "417666",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "03",
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "payer_name_2": "L3TEST/CARD0010",
                    "emi_type_2": "NORMAL_EMI",
                    "orig_txn_id": txn_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "device_serial": device_serial_db,
                    "merchant_code": merchant_code_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "order_id": order_id_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "interest_rate": emi_interest_rate_db,
                    "emi_status": emi_status_db,
                    "emi_term": emi_term_db,
                    "emi_type": emi_type_db,
                    "loan_amt": emi_loan_amount_db,
                    "monthly_emi": emi_amount_monthly_db,
                    "total_emi_amt": emi_total_amount_db,
                    "scheme_code": emi_scheme_code_db,
                    "emi_txn_amt": emi_txn_amount_db,
                    "emi_original_amt": emi_original_amount_db,
                    "customer_name": customer_name_db,
                    "payer_name": payer_name_db,
                    "txn_amt_2": amount_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "pmt_status_2": payment_status_db_2,
                    "pmt_state_2": payment_state_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "merchant_code_2": merchant_code_db_2,
                    "pmt_card_brand_2": payment_card_brand_db_2,
                    "pmt_card_type_2": payment_card_type_db_2,
                    "order_id_2": order_id_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2,
                    "emi_type_2": emi_type_db_2,
                    "orig_txn_id": orig_txn_id
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_db=created_time_2)
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "auth_code_2": auth_code_2,
                    "rrn_2": rrn_2,
                    "date_time_2": date_and_time_portal_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                date_time = transaction_details[1]['Date & Time']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=created_time_2)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn_2),
                    "AUTH CODE": auth_code_2,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": batch_number_db_2,
                    "TID": tid,
                    "INVOICE NO": invoice_number_db_2,
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "unnamed_section_text": customer_name_db_2
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
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
def test_common_100_115_06_010():
    """
    Sub Feature Code: UI_Common_Card_Instant_EMI_Refund_Via_API_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_6_Months_Tenure
    Sub Feature Description: Performing the instant EMI refund via API  transaction for an org (not ezetap) via HDFC Dummy PG
    using EMV VISA Credit card with pin for 6 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 06: Instant_EMI, 010: TC010
    """
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"fetching org code from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

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
        api_details["RequestBody"]["settings"]["instantEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for credit card")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            emi_plan_in_months = 6
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            amount = random.randint(3500, 4500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_payment_option_emi_on_card()
            logger.debug(f"selected payment option emi on card")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                    f"issuer_code='HDFC' and card_type='CREDIT' AND term = '{emi_plan_in_months} month' and emi_type='NORMAL'" \
                    f"and tid_type='CIB' order by created_time asc limit 1"
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
            monthly_emi_cal = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi_cal}")
            cal_total_emi_amt = monthly_emi_cal * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest_cal = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest_cal}")

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch id from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn table : {result} ")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")

            api_details = DBProcessor.get_api_details('Offline_Refund', request_body={
                "password": app_password,
                "username": app_username,
                "amount": amount,
                "originalTransactionId": txn_id
            })
            logger.debug(f"API DETAILS for Offline_Refund api : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {response}")
            txn_id_2 = response["txnId"]
            logger.debug(f"Fetching transaction id for refund from response : {txn_id_2}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for original txn : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for original txn : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for original txn : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for original txn : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for original txn : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for original txn : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for original txn : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for original txn : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for original txn : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for original txn : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for original txn : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for original txn : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table for original txn : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for original txn : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for original txn : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for original txn : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for original txn : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for original txn : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table for original txn : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for original txn : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for original txn : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for original txn : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for original txn : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for original txn : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for original txn : {card_last_four_digit_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for original txn : {merchant_name}")
            emi_type_db = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for original txn : {emi_type_db}")
            customer_name_db = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from the txn table for original txn : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for original txn : {payer_name_db}")

            query = f"select * from txn where id='{txn_id_2}'"
            logger.debug(f"Query to fetch data from txn table, for refunded txn {txn_id_2} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for refunded txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for refunded txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for refunded txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for refunded txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for refunded txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for refunded txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for refunded txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for refunded txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for refunded txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for refunded txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for refunded txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for refunded txn : {settlement_status_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for refunded txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for refunded txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for refunded txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for refunded txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for refunded txn : {order_id_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for refunded txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for refunded txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for refunded txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for refunded txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for refunded txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for refunded txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table for refunded txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for refunded txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for refunded txn : {merchant_name_2}")
            invoice_number_db_2 = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table for refunded txn : {invoice_number_db_2}")
            emi_type_db_2 = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for refunded txn : {emi_type_db_2}")
            orig_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching orig_txn_id from the txn table for refunded txn : {orig_txn_id}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate_db = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate_db}")
            emi_status_db = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status_db}")
            emi_term_db = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term_db}")
            emi_loan_amount_db = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount_db}")
            emi_amount_monthly_db = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly_db}")
            emi_total_amount_db = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount_db}")
            emi_scheme_code_db = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code_db}")
            emi_txn_amount_db = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount_db}")
            emi_original_amount_db = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount_db}")
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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=created_time)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=created_time_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "card_type_desc": "*0102 EMV with PIN",
                    "customer_name": "L3TEST",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "emi_status": "PENDING",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi_cal),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "total_interest": "{:,.2f}".format(total_interest_cal),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest_cal),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "customer": customer_name_db,
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "L3TEST",
                    "card_type_desc_2": "*0102 EMV with PIN"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login(username=app_username, password=app_password)
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the original txn : {txn_id}, {payment_by}")
                card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the original txn : {txn_id}, {card_type}")
                emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the original txn : {txn_id}, {emi_status}")
                lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the original txn : {txn_id}, {lender}")
                monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the original txn : {txn_id}, {monthly_emi}")
                total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the original txn : {txn_id}, {total_emi_amount}")
                total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the original txn : {txn_id}, {total_interest}")
                loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the original txn : {txn_id}, {loan_amount}")
                interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the original txn : {txn_id}, {interest_amount}")
                net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the original txn : {txn_id}, {net_effective_price}")
                tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the original txn : {txn_id}, {tenure}")
                customer_app = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the original txn : {txn_id}, {customer_app}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the original txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the original txn : {txn_id}, {payment_mode}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the original txn : {txn_id}, {payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the original txn : {txn_id}, {app_txn_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the original txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the original txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the original txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the original txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for theoriginal  txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the original txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the original txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the original txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the original txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the original txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the original txn : {txn_id}, {app_card_type_desc}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the original txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the refunded txn : {txn_id_2}, {payment_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the refunded txn : {txn_id_2}, {app_rrn_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the refunded txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the refunded txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the refunded txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the refunded txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the refunded txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the refunded txn : {txn_id_2}, {app_customer_name_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the refunded txn : {txn_id_2}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rrn": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "customer_name": app_customer_name,
                    "pmt_by": payment_by,
                    "card_type": card_type,
                    "emi_status": emi_status,
                    "lender": lender,
                    "monthly_emi": monthly_emi.split(' ')[1],
                    "total_emi_amt": total_emi_amount.split(' ')[1],
                    "total_interest": total_interest.split(' ')[1],
                    "loan_amt": loan_amount.split(' ')[1],
                    "interest_amt": interest_amount.split(' ')[2],
                    "net_eff_price": net_effective_price.split(' ')[1],
                    "tenure": tenure,
                    "customer": customer_app,
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
                    "card_type_desc_2": app_card_type_desc_2
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "EMV with PIN",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0102",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "display_pan": "0102",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "interest_amt": total_interest_cal,
                    "total_emi_amt": total_emi,
                    "emi_type": "NORMAL_EMI",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "name_on_card": "L3TEST/CARD0010",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "card_txn_type_2": "EMV with PIN",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "L3TEST/CARD0010",
                    "pmt_card_bin_2": "417666",
                    "name_on_card_2": "L3TEST/CARD0010",
                    "display_pan_2": "0102",
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status from response for original txn : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount from response for original txn : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode from response for original txn : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state from response for original txn : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn from response for original txn : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for original txn : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer code from response for original txn : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for original txn : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org code from response for original txn : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid from response for original txn : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid from response for original txn : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction type from response for original txn : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth code from response for original txn : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date and time from response for original txn : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device serial from response for original txn : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username from response for original txn : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction id from response for original txn : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for original txn : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for original txn : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for original txn : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch number from response for original txn : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for original txn : {card_last_four_digit_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for original txn : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant name from response for original txn : {merchant_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for original txn : {payment_card_bin_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for original txn : {display_pan_api}")
                api_emi_term = response_1.get('emiTerm')
                logger.debug(f"Fetching emi_term from response for original txn : {api_emi_term}")
                api_emi_status = response_1.get('emiStatus')
                logger.debug(f"Fetching emi_status from response for original txn : {api_emi_status}")
                api_interest_rate = response_1.get('emiInterestRate')
                logger.debug(f"Fetching emi_interest_rate from response for original txn : {api_interest_rate}")
                api_emi_type = response_1.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for original txn : {api_emi_type}")
                api_loan_amt = response_1.get('emiDetails')['loanAmount']
                logger.debug(f"Fetching loan_amount from response for original txn : {api_loan_amt}")
                api_monthly_emi = response_1.get('emiDetails')['emi']
                logger.debug(f"Fetching monthly emi from response for original txn : {api_monthly_emi}")
                api_interest_amt = response_1.get('emiDetails')['interestAmount']
                logger.debug(f"Fetching interest_amount from response for original txn : {api_interest_amt}")
                api_total_emi_amt = response_1.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"Fetching total emi amount from response for original txn : {api_total_emi_amt}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer name from response for original txn : {customer_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer name from response for original txn : {payer_name_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name on card from response for original txn : {name_on_card_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status from response for refunded txn : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount from response for refunded txn : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment mode from response for refunded txn : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state from response for refunded txn : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn from response for refunded txn : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for refunded txn : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for refunded txn : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org code from response for refunded txn : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid from response for refunded txn : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid from response for refunded txn : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction type from response for refunded txn : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth code from response for refunded txn : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date and time from response for refunded txn : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username from response for refunded txn : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction id from response for refunded txn : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for refunded txn : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for refunded txn : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for refunded txn : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch number from response for refunded txn : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for refunded txn : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer name from response for refunded txn : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for refunded txn : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant name from response for refunded txn : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer name from response for refunded txn : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for refunded txn : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name on card from response for refunded txn : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for refunded txn : {display_pan_api_2}")
                emi_type_api_2 = response_2.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for refunded txn : {emi_type_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "device_serial": device_serial_api,
                    "username": username_api,
                    "txn_id": txn_id_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_txn_type": card_txn_type_api,
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "external_ref": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "display_pan": display_pan_api,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "emi_type": api_emi_type,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "name_on_card": name_on_card_api,
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2,
                    "emi_type_2": emi_type_api_2
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
                    "txn_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "03",
                    "card_last_four_digit": "0102",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "NORMAL_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "417666",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "03",
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "payer_name_2": "L3TEST/CARD0010",
                    "emi_type_2": "NORMAL_EMI",
                    "orig_txn_id": txn_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "device_serial": device_serial_db,
                    "merchant_code": merchant_code_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "order_id": order_id_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "interest_rate": emi_interest_rate_db,
                    "emi_status": emi_status_db,
                    "emi_term": emi_term_db,
                    "emi_type": emi_type_db,
                    "loan_amt": emi_loan_amount_db,
                    "monthly_emi": emi_amount_monthly_db,
                    "total_emi_amt": emi_total_amount_db,
                    "scheme_code": emi_scheme_code_db,
                    "emi_txn_amt": emi_txn_amount_db,
                    "emi_original_amt": emi_original_amount_db,
                    "customer_name": customer_name_db,
                    "payer_name": payer_name_db,
                    "txn_amt_2": amount_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "pmt_status_2": payment_status_db_2,
                    "pmt_state_2": payment_state_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "merchant_code_2": merchant_code_db_2,
                    "pmt_card_brand_2": payment_card_brand_db_2,
                    "pmt_card_type_2": payment_card_type_db_2,
                    "order_id_2": order_id_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2,
                    "emi_type_2": emi_type_db_2,
                    "orig_txn_id": orig_txn_id
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_db=created_time_2)
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "auth_code_2": auth_code_2,
                    "rrn_2": rrn_2,
                    "date_time_2": date_and_time_portal_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                date_time = transaction_details[1]['Date & Time']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=created_time_2)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn_2),
                    "AUTH CODE": auth_code_2,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": batch_number_db_2,
                    "TID": tid,
                    "INVOICE NO": invoice_number_db_2,
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "unnamed_section_text": customer_name_db_2
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
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
def test_common_100_115_06_011():
    """
    Sub Feature Code: UI_Common_Card_Instant_EMI_Refund_Via_API_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_9_Months_Tenure
    Sub Feature Description: Performing the instant EMI refund via API transaction for an org (not ezetap) via HDFC Dummy PG
    using EMV VISA Credit card with pin for 9 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 06: Instant_EMI, 011: TC011
    """
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"fetching org code from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

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
        api_details["RequestBody"]["settings"]["instantEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for credit card")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            emi_plan_in_months = 9
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            amount = random.randint(3500, 4500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_payment_option_emi_on_card()
            logger.debug(f"selected payment option emi on card")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                    f"issuer_code='HDFC' and card_type='CREDIT' AND term = '{emi_plan_in_months} month' and emi_type='NORMAL'" \
                    f"and tid_type='CIB' order by created_time asc limit 1"
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
            monthly_emi_cal = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi_cal}")
            cal_total_emi_amt = monthly_emi_cal * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest_cal = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest_cal}")

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch id from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn table : {result} ")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")

            api_details = DBProcessor.get_api_details('Offline_Refund', request_body={
                "password": app_password,
                "username": app_username,
                "amount": amount,
                "originalTransactionId": txn_id
            })
            logger.debug(f"API DETAILS for Offline_Refund api : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {response}")
            txn_id_2 = response["txnId"]
            logger.debug(f"Fetching transaction id for refund from response : {txn_id_2}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for original txn : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for original txn : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for original txn : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for original txn : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for original txn : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for original txn : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for original txn : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for original txn : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for original txn : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for original txn : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for original txn : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for original txn : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table for original txn : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for original txn : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for original txn : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for original txn : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for original txn : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for original txn : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table for original txn : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for original txn : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for original txn : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for original txn : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for original txn : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for original txn : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for original txn : {card_last_four_digit_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for original txn : {merchant_name}")
            emi_type_db = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for original txn : {emi_type_db}")
            customer_name_db = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from the txn table for original txn : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for original txn : {payer_name_db}")

            query = f"select * from txn where id='{txn_id_2}'"
            logger.debug(f"Query to fetch data from txn table, for refunded txn {txn_id_2} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for refunded txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for refunded txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for refunded txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for refunded txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for refunded txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for refunded txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for refunded txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for refunded txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for refunded txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for refunded txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for refunded txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for refunded txn : {settlement_status_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for refunded txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for refunded txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for refunded txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for refunded txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for refunded txn : {order_id_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for refunded txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for refunded txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for refunded txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for refunded txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for refunded txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for refunded txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table for refunded txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for refunded txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for refunded txn : {merchant_name_2}")
            invoice_number_db_2 = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table for refunded txn : {invoice_number_db_2}")
            emi_type_db_2 = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for refunded txn : {emi_type_db_2}")
            orig_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching orig_txn_id from the txn table for refunded txn : {orig_txn_id}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate_db = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate_db}")
            emi_status_db = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status_db}")
            emi_term_db = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term_db}")
            emi_loan_amount_db = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount_db}")
            emi_amount_monthly_db = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly_db}")
            emi_total_amount_db = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount_db}")
            emi_scheme_code_db = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code_db}")
            emi_txn_amount_db = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount_db}")
            emi_original_amount_db = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount_db}")
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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=created_time)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=created_time_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "card_type_desc": "*0102 EMV with PIN",
                    "customer_name": "L3TEST",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "emi_status": "PENDING",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi_cal),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "total_interest": "{:,.2f}".format(total_interest_cal),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest_cal),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "customer": customer_name_db,
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "L3TEST",
                    "card_type_desc_2": "*0102 EMV with PIN"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login(username=app_username, password=app_password)
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the original txn : {txn_id}, {payment_by}")
                card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the original txn : {txn_id}, {card_type}")
                emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the original txn : {txn_id}, {emi_status}")
                lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the original txn : {txn_id}, {lender}")
                monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the original txn : {txn_id}, {monthly_emi}")
                total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the original txn : {txn_id}, {total_emi_amount}")
                total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the original txn : {txn_id}, {total_interest}")
                loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the original txn : {txn_id}, {loan_amount}")
                interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the original txn : {txn_id}, {interest_amount}")
                net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the original txn : {txn_id}, {net_effective_price}")
                tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the original txn : {txn_id}, {tenure}")
                customer_app = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the original txn : {txn_id}, {customer_app}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the original txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the original txn : {txn_id}, {payment_mode}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the original txn : {txn_id}, {payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the original txn : {txn_id}, {app_txn_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the original txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the original txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the original txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the original txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for theoriginal  txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the original txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the original txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the original txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the original txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the original txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the original txn : {txn_id}, {app_card_type_desc}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the original txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the refunded txn : {txn_id_2}, {payment_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the refunded txn : {txn_id_2}, {app_rrn_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the refunded txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the refunded txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the refunded txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the refunded txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the refunded txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the refunded txn : {txn_id_2}, {app_customer_name_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the refunded txn : {txn_id_2}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rrn": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "customer_name": app_customer_name,
                    "pmt_by": payment_by,
                    "card_type": card_type,
                    "emi_status": emi_status,
                    "lender": lender,
                    "monthly_emi": monthly_emi.split(' ')[1],
                    "total_emi_amt": total_emi_amount.split(' ')[1],
                    "total_interest": total_interest.split(' ')[1],
                    "loan_amt": loan_amount.split(' ')[1],
                    "interest_amt": interest_amount.split(' ')[2],
                    "net_eff_price": net_effective_price.split(' ')[1],
                    "tenure": tenure,
                    "customer": customer_app,
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
                    "card_type_desc_2": app_card_type_desc_2
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "EMV with PIN",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0102",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "display_pan": "0102",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "interest_amt": total_interest_cal,
                    "total_emi_amt": total_emi,
                    "emi_type": "NORMAL_EMI",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "name_on_card": "L3TEST/CARD0010",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "card_txn_type_2": "EMV with PIN",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "L3TEST/CARD0010",
                    "pmt_card_bin_2": "417666",
                    "name_on_card_2": "L3TEST/CARD0010",
                    "display_pan_2": "0102",
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status from response for original txn : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount from response for original txn : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode from response for original txn : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state from response for original txn : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn from response for original txn : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for original txn : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer code from response for original txn : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for original txn : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org code from response for original txn : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid from response for original txn : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid from response for original txn : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction type from response for original txn : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth code from response for original txn : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date and time from response for original txn : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device serial from response for original txn : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username from response for original txn : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction id from response for original txn : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for original txn : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for original txn : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for original txn : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch number from response for original txn : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for original txn : {card_last_four_digit_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for original txn : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant name from response for original txn : {merchant_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for original txn : {payment_card_bin_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for original txn : {display_pan_api}")
                api_emi_term = response_1.get('emiTerm')
                logger.debug(f"Fetching emi_term from response for original txn : {api_emi_term}")
                api_emi_status = response_1.get('emiStatus')
                logger.debug(f"Fetching emi_status from response for original txn : {api_emi_status}")
                api_interest_rate = response_1.get('emiInterestRate')
                logger.debug(f"Fetching emi_interest_rate from response for original txn : {api_interest_rate}")
                api_emi_type = response_1.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for original txn : {api_emi_type}")
                api_loan_amt = response_1.get('emiDetails')['loanAmount']
                logger.debug(f"Fetching loan_amount from response for original txn : {api_loan_amt}")
                api_monthly_emi = response_1.get('emiDetails')['emi']
                logger.debug(f"Fetching monthly emi from response for original txn : {api_monthly_emi}")
                api_interest_amt = response_1.get('emiDetails')['interestAmount']
                logger.debug(f"Fetching interest_amount from response for original txn : {api_interest_amt}")
                api_total_emi_amt = response_1.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"Fetching total emi amount from response for original txn : {api_total_emi_amt}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer name from response for original txn : {customer_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer name from response for original txn : {payer_name_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name on card from response for original txn : {name_on_card_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status from response for refunded txn : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount from response for refunded txn : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment mode from response for refunded txn : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state from response for refunded txn : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn from response for refunded txn : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for refunded txn : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for refunded txn : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org code from response for refunded txn : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid from response for refunded txn : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid from response for refunded txn : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction type from response for refunded txn : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth code from response for refunded txn : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date and time from response for refunded txn : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username from response for refunded txn : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction id from response for refunded txn : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for refunded txn : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for refunded txn : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for refunded txn : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch number from response for refunded txn : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for refunded txn : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer name from response for refunded txn : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for refunded txn : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant name from response for refunded txn : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer name from response for refunded txn : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for refunded txn : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name on card from response for refunded txn : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for refunded txn : {display_pan_api_2}")
                emi_type_api_2 = response_2.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for refunded txn : {emi_type_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "device_serial": device_serial_api,
                    "username": username_api,
                    "txn_id": txn_id_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_txn_type": card_txn_type_api,
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "external_ref": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "display_pan": display_pan_api,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "emi_type": api_emi_type,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "name_on_card": name_on_card_api,
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2,
                    "emi_type_2": emi_type_api_2
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
                    "txn_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "03",
                    "card_last_four_digit": "0102",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "NORMAL_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "417666",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "03",
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "payer_name_2": "L3TEST/CARD0010",
                    "emi_type_2": "NORMAL_EMI",
                    "orig_txn_id": txn_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "device_serial": device_serial_db,
                    "merchant_code": merchant_code_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "order_id": order_id_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "interest_rate": emi_interest_rate_db,
                    "emi_status": emi_status_db,
                    "emi_term": emi_term_db,
                    "emi_type": emi_type_db,
                    "loan_amt": emi_loan_amount_db,
                    "monthly_emi": emi_amount_monthly_db,
                    "total_emi_amt": emi_total_amount_db,
                    "scheme_code": emi_scheme_code_db,
                    "emi_txn_amt": emi_txn_amount_db,
                    "emi_original_amt": emi_original_amount_db,
                    "customer_name": customer_name_db,
                    "payer_name": payer_name_db,
                    "txn_amt_2": amount_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "pmt_status_2": payment_status_db_2,
                    "pmt_state_2": payment_state_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "merchant_code_2": merchant_code_db_2,
                    "pmt_card_brand_2": payment_card_brand_db_2,
                    "pmt_card_type_2": payment_card_type_db_2,
                    "order_id_2": order_id_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2,
                    "emi_type_2": emi_type_db_2,
                    "orig_txn_id": orig_txn_id
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_db=created_time_2)
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "auth_code_2": auth_code_2,
                    "rrn_2": rrn_2,
                    "date_time_2": date_and_time_portal_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                date_time = transaction_details[1]['Date & Time']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=created_time_2)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn_2),
                    "AUTH CODE": auth_code_2,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": batch_number_db_2,
                    "TID": tid,
                    "INVOICE NO": invoice_number_db_2,
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "unnamed_section_text": customer_name_db_2
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
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
def test_common_100_115_06_012():
    """
    Sub Feature Code: UI_Common_Card_Instant_EMI_Refund_Via_API_For_An_Org_HDFC_Dummy_EMV_VISA_CreditCard_With_Pin_417666_For_12_Months_Tenure
    Sub Feature Description: Performing the instant EMI refund via API  transaction for an org (not ezetap) via HDFC Dummy PG
    using EMV VISA Credit card with pin for 12 months tenure (bin: 417666)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 06: Instant_EMI, 012: TC012
    """
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"fetching org code from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

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
        api_details["RequestBody"]["settings"]["instantEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for credit card")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            emi_plan_in_months = 12
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            amount = random.randint(3500, 4500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_CREDIT_417666")
            logger.debug(f"selected the card type as : EMV_WITH_PIN_VISA_CREDIT_417666")
            payment_page.select_payment_option_emi_on_card()
            logger.debug(f"selected payment option emi on card")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                    f"issuer_code='HDFC' and card_type='CREDIT' AND term = '{emi_plan_in_months} month' and emi_type='NORMAL'" \
                    f"and tid_type='CIB' order by created_time asc limit 1"
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
            monthly_emi_cal = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi_cal}")
            cal_total_emi_amt = monthly_emi_cal * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest_cal = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest_cal}")

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch id from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn table : {result} ")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")

            api_details = DBProcessor.get_api_details('Offline_Refund', request_body={
                "password": app_password,
                "username": app_username,
                "amount": amount,
                "originalTransactionId": txn_id
            })
            logger.debug(f"API DETAILS for Offline_Refund api : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {response}")
            txn_id_2 = response["txnId"]
            logger.debug(f"Fetching transaction id for refund from response : {txn_id_2}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for original txn : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for original txn : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for original txn : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for original txn : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for original txn : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for original txn : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for original txn : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for original txn : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for original txn : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for original txn : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for original txn : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for original txn : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table for original txn : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for original txn : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for original txn : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for original txn : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for original txn : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for original txn : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table for original txn : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for original txn : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for original txn : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for original txn : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for original txn : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for original txn : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for original txn : {card_last_four_digit_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for original txn : {merchant_name}")
            emi_type_db = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for original txn : {emi_type_db}")
            customer_name_db = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from the txn table for original txn : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for original txn : {payer_name_db}")

            query = f"select * from txn where id='{txn_id_2}'"
            logger.debug(f"Query to fetch data from txn table, for refunded txn {txn_id_2} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for refunded txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for refunded txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for refunded txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for refunded txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for refunded txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for refunded txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for refunded txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for refunded txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for refunded txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for refunded txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for refunded txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for refunded txn : {settlement_status_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for refunded txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for refunded txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for refunded txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for refunded txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for refunded txn : {order_id_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for refunded txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for refunded txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for refunded txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for refunded txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for refunded txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for refunded txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table for refunded txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for refunded txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for refunded txn : {merchant_name_2}")
            invoice_number_db_2 = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table for refunded txn : {invoice_number_db_2}")
            emi_type_db_2 = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for refunded txn : {emi_type_db_2}")
            orig_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching orig_txn_id from the txn table for refunded txn : {orig_txn_id}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate_db = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate_db}")
            emi_status_db = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status_db}")
            emi_term_db = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term_db}")
            emi_loan_amount_db = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount_db}")
            emi_amount_monthly_db = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly_db}")
            emi_total_amount_db = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount_db}")
            emi_scheme_code_db = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code_db}")
            emi_txn_amount_db = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount_db}")
            emi_original_amount_db = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount_db}")
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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=created_time)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=created_time_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "card_type_desc": "*0102 EMV with PIN",
                    "customer_name": "L3TEST",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "emi_status": "PENDING",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi_cal),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "total_interest": "{:,.2f}".format(total_interest_cal),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest_cal),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "customer": customer_name_db,
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "L3TEST",
                    "card_type_desc_2": "*0102 EMV with PIN"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login(username=app_username, password=app_password)
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the original txn : {txn_id}, {payment_by}")
                card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the original txn : {txn_id}, {card_type}")
                emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the original txn : {txn_id}, {emi_status}")
                lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the original txn : {txn_id}, {lender}")
                monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the original txn : {txn_id}, {monthly_emi}")
                total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the original txn : {txn_id}, {total_emi_amount}")
                total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the original txn : {txn_id}, {total_interest}")
                loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the original txn : {txn_id}, {loan_amount}")
                interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the original txn : {txn_id}, {interest_amount}")
                net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the original txn : {txn_id}, {net_effective_price}")
                tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the original txn : {txn_id}, {tenure}")
                customer_app = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the original txn : {txn_id}, {customer_app}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the original txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the original txn : {txn_id}, {payment_mode}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the original txn : {txn_id}, {payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the original txn : {txn_id}, {app_txn_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the original txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the original txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the original txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the original txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for theoriginal  txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the original txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the original txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the original txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the original txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the original txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the original txn : {txn_id}, {app_card_type_desc}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the original txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the refunded txn : {txn_id_2}, {payment_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the refunded txn : {txn_id_2}, {app_rrn_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the refunded txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the refunded txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the refunded txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the refunded txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the refunded txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the refunded txn : {txn_id_2}, {app_customer_name_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the refunded txn : {txn_id_2}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rrn": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "customer_name": app_customer_name,
                    "pmt_by": payment_by,
                    "card_type": card_type,
                    "emi_status": emi_status,
                    "lender": lender,
                    "monthly_emi": monthly_emi.split(' ')[1],
                    "total_emi_amt": total_emi_amount.split(' ')[1],
                    "total_interest": total_interest.split(' ')[1],
                    "loan_amt": loan_amount.split(' ')[1],
                    "interest_amt": interest_amount.split(' ')[2],
                    "net_eff_price": net_effective_price.split(' ')[1],
                    "tenure": tenure,
                    "customer": customer_app,
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
                    "card_type_desc_2": app_card_type_desc_2
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "EMV with PIN",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0102",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "417666",
                    "display_pan": "0102",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "interest_amt": total_interest_cal,
                    "total_emi_amt": total_emi,
                    "emi_type": "NORMAL_EMI",
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "name_on_card": "L3TEST/CARD0010",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "card_txn_type_2": "EMV with PIN",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "L3TEST/CARD0010",
                    "pmt_card_bin_2": "417666",
                    "name_on_card_2": "L3TEST/CARD0010",
                    "display_pan_2": "0102",
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status from response for original txn : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount from response for original txn : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode from response for original txn : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state from response for original txn : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn from response for original txn : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for original txn : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer code from response for original txn : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for original txn : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org code from response for original txn : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid from response for original txn : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid from response for original txn : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction type from response for original txn : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth code from response for original txn : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date and time from response for original txn : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device serial from response for original txn : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username from response for original txn : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction id from response for original txn : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for original txn : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for original txn : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for original txn : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch number from response for original txn : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for original txn : {card_last_four_digit_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for original txn : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant name from response for original txn : {merchant_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for original txn : {payment_card_bin_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for original txn : {display_pan_api}")
                api_emi_term = response_1.get('emiTerm')
                logger.debug(f"Fetching emi_term from response for original txn : {api_emi_term}")
                api_emi_status = response_1.get('emiStatus')
                logger.debug(f"Fetching emi_status from response for original txn : {api_emi_status}")
                api_interest_rate = response_1.get('emiInterestRate')
                logger.debug(f"Fetching emi_interest_rate from response for original txn : {api_interest_rate}")
                api_emi_type = response_1.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for original txn : {api_emi_type}")
                api_loan_amt = response_1.get('emiDetails')['loanAmount']
                logger.debug(f"Fetching loan_amount from response for original txn : {api_loan_amt}")
                api_monthly_emi = response_1.get('emiDetails')['emi']
                logger.debug(f"Fetching monthly emi from response for original txn : {api_monthly_emi}")
                api_interest_amt = response_1.get('emiDetails')['interestAmount']
                logger.debug(f"Fetching interest_amount from response for original txn : {api_interest_amt}")
                api_total_emi_amt = response_1.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"Fetching total emi amount from response for original txn : {api_total_emi_amt}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer name from response for original txn : {customer_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer name from response for original txn : {payer_name_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name on card from response for original txn : {name_on_card_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status from response for refunded txn : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount from response for refunded txn : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment mode from response for refunded txn : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state from response for refunded txn : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn from response for refunded txn : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for refunded txn : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for refunded txn : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org code from response for refunded txn : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid from response for refunded txn : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid from response for refunded txn : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction type from response for refunded txn : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth code from response for refunded txn : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date and time from response for refunded txn : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username from response for refunded txn : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction id from response for refunded txn : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for refunded txn : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for refunded txn : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for refunded txn : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch number from response for refunded txn : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for refunded txn : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer name from response for refunded txn : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for refunded txn : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant name from response for refunded txn : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer name from response for refunded txn : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for refunded txn : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name on card from response for refunded txn : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for refunded txn : {display_pan_api_2}")
                emi_type_api_2 = response_2.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for refunded txn : {emi_type_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "device_serial": device_serial_api,
                    "username": username_api,
                    "txn_id": txn_id_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_txn_type": card_txn_type_api,
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "external_ref": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "display_pan": display_pan_api,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "emi_type": api_emi_type,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "name_on_card": name_on_card_api,
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2,
                    "emi_type_2": emi_type_api_2
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
                    "txn_amt": amount,
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "417666",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "03",
                    "card_last_four_digit": "0102",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "NORMAL_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "customer_name": "L3TEST/CARD0010",
                    "payer_name": "L3TEST/CARD0010",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "CREDIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "417666",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "03",
                    "card_last_four_digit_2": "0102",
                    "customer_name_2": "L3TEST/CARD0010",
                    "payer_name_2": "L3TEST/CARD0010",
                    "emi_type_2": "NORMAL_EMI",
                    "orig_txn_id": txn_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "device_serial": device_serial_db,
                    "merchant_code": merchant_code_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "order_id": order_id_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "interest_rate": emi_interest_rate_db,
                    "emi_status": emi_status_db,
                    "emi_term": emi_term_db,
                    "emi_type": emi_type_db,
                    "loan_amt": emi_loan_amount_db,
                    "monthly_emi": emi_amount_monthly_db,
                    "total_emi_amt": emi_total_amount_db,
                    "scheme_code": emi_scheme_code_db,
                    "emi_txn_amt": emi_txn_amount_db,
                    "emi_original_amt": emi_original_amount_db,
                    "customer_name": customer_name_db,
                    "payer_name": payer_name_db,
                    "txn_amt_2": amount_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "pmt_status_2": payment_status_db_2,
                    "pmt_state_2": payment_state_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "merchant_code_2": merchant_code_db_2,
                    "pmt_card_brand_2": payment_card_brand_db_2,
                    "pmt_card_type_2": payment_card_type_db_2,
                    "order_id_2": order_id_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2,
                    "emi_type_2": emi_type_db_2,
                    "orig_txn_id": orig_txn_id
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_db=created_time_2)
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "auth_code_2": auth_code_2,
                    "rrn_2": rrn_2,
                    "date_time_2": date_and_time_portal_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                date_time = transaction_details[1]['Date & Time']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=created_time_2)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn_2),
                    "AUTH CODE": auth_code_2,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": batch_number_db_2,
                    "TID": tid,
                    "INVOICE NO": invoice_number_db_2,
                    "CARD": f"XXXX-XXXX-XXXX-0102 EMV with PIN",
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "unnamed_section_text": customer_name_db_2
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
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
def test_common_100_115_06_021():
    """
    Sub Feature Code: UI_Common_Card_Instant_EMI_Refund_Via_API_For_An_Org_HDFC_Dummy_EMV_VISA_DebitCard_With_Pin_428090_For_3_Months_Tenure
    Sub Feature Description: Performing the instant EMI refund via API  transaction for an org (not ezetap) via HDFC Dummy PG
    using EMV VISA Debit card with pin for 3 months tenure (bin: 428090)
    TC naming code description: 100: Payment Method, 115: CARD_UI, 06: Instant_EMI, 021: TC021
    """
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"fetching org code from org_employee table : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='HDFC' and payment_gateway='DUMMY' "
        logger.debug(f"Query to fetch data from the terminal_info table for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for terminal_info table : {result}")
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from the terminal_info table : mid : {mid}")
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching tid from the terminal_info table : tid : {tid}")
        device_serial = result["device_serial"].iloc[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : device_serial : {device_serial}")
        terminal_info_id = result["id"].iloc[0]
        logger.debug(f"Fetching terminal_info_id from the terminal_info table : terminal_info_id : {terminal_info_id}")

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select bank_code from bin_info where bin='428090'"
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
        api_details["RequestBody"]["settings"]["instantEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["emiEnabledForClient"] = "true"
        api_details["RequestBody"]["settings"]["offeringEmiCashback"] = "NO"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='DEBIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for debit card")

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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            emi_plan_in_months = 3
            logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")
            amount = random.randint(3500, 4500)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id,
                                                                               device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            card_page.select_cardtype(text="EMV_WITH_PIN_VISA_DEBIT_428090")
            logger.debug(f"selected the card type as : EMV_WITH_PIN_VISA_DEBIT_428090")
            payment_page.select_payment_option_emi_on_card()
            logger.debug(f"selected payment option emi on card")
            payment_page.select_emi_plan(emi_plan_in_months=emi_plan_in_months)
            logger.debug(f"selected emi plan is {emi_plan_in_months} month")
            payment_page.click_on_proceed_homepage()

            query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                    f"issuer_code='HDFC' and card_type='DEBIT' AND term = '{emi_plan_in_months} month' and emi_type='NORMAL'" \
                    f"and tid_type='CIB' order by created_time asc limit 1"
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
            monthly_emi_cal = round(cal_monthly_emi_amt, 2)
            logger.debug(f"calculated monthly_emi amount : {monthly_emi_cal}")
            cal_total_emi_amt = monthly_emi_cal * emi_plan_in_months
            total_emi = round(cal_total_emi_amt, 2)
            logger.debug(f"calculated total_emi amount : {total_emi}")
            cal_total_interest = total_emi - amount
            total_interest_cal = round(cal_total_interest, 2)
            logger.debug(f"calculated total_interest amount : {total_interest_cal}")

            api_details = DBProcessor.get_api_details('Settlement', request_body={
                "username": portal_username,
                "password": portal_password
            })
            api_details["EndPoint"] = api_details["EndPoint"] + "/" + str(terminal_info_id)
            logger.debug(f"API DETAILS : {api_details}")
            settle_response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for settlement api is : {settle_response}")

            query = f"select id from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch id from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn table : {result} ")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")

            api_details = DBProcessor.get_api_details('Offline_Refund', request_body={
                "password": app_password,
                "username": app_username,
                "amount": 1,
                "originalTransactionId": txn_id
            })
            logger.debug(f"API DETAILS for Offline_Refund api : {api_details}")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for Offline_Refund api is : {response}")
            txn_id_2 = response["txnId"]
            logger.debug(f"Fetching transaction id for refund from response : {txn_id_2}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn table, for original txn {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for original txn : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for original txn : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for original txn : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for original txn : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for original txn : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for original txn : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for original txn : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for original txn : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for original txn : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for original txn : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for original txn : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for original txn : {settlement_status_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table for original txn : {device_serial_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for original txn : {merchant_code_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for original txn : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for original txn : {payment_card_type_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for original txn : {batch_number_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for original txn : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table for original txn : {issuer_code_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for original txn : {org_code_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for original txn : {payment_card_bin_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for original txn : {terminal_info_id_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for original txn : {txn_type_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for original txn : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for original txn : {card_last_four_digit_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for original txn : {merchant_name}")
            emi_type_db = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for original txn : {emi_type_db}")
            customer_name_db = result['customer_name'].values[0]
            logger.debug(f"Fetching customer name from the txn table for original txn : {customer_name_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for original txn : {payer_name_db}")
            amount_original_db = result['amount_original'].values[0]
            logger.debug(f"Fetching amount original from txn table for original txn : {amount_original_db}")

            query = f"select * from txn where id='{txn_id_2}'"
            logger.debug(f"Query to fetch data from txn table, for refunded txn {txn_id_2} : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"result for query : {result}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table for refunded txn : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table for refunded txn : {created_time_2}")
            amount_db_2 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table for refunded txn : {amount_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table for refunded txn : {payment_mode_db_2}")
            payment_status_db_2 = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table for refunded txn : {payment_status_db_2}")
            payment_state_db_2 = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table for refunded txn : {payment_state_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table for refunded txn : {acquirer_code_db_2}")
            mid_db_2 = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table for refunded txn : {mid_db_2}")
            tid_db_2 = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table for refunded txn : {tid_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table for refunded txn : {payment_gateway_db_2}")
            rrn_2 = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table for refunded txn : {rrn_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table for refunded txn : {settlement_status_db_2}")
            merchant_code_db_2 = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table for refunded txn : {merchant_code_db_2}")
            payment_card_brand_db_2 = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table for refunded txn : {payment_card_brand_db_2}")
            payment_card_type_db_2 = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table for refunded txn : {payment_card_type_db_2}")
            batch_number_db_2 = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table for refunded txn : {batch_number_db_2}")
            order_id_db_2 = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table for refunded txn : {order_id_db_2}")
            org_code_db_2 = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table for refunded txn : {org_code_db_2}")
            payment_card_bin_db_2 = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table for refunded txn : {payment_card_bin_db_2}")
            terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table for refunded txn : {terminal_info_id_db_2}")
            txn_type_db_2 = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table for refunded txn : {txn_type_db_2}")
            card_txn_type_db_2 = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table for refunded txn : {card_txn_type_db_2}")
            card_last_four_digit_db_2 = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table for refunded txn : {card_last_four_digit_db_2}")
            customer_name_db_2 = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table for refunded txn : {customer_name_db_2}")
            payer_name_db_2 = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table for refunded txn : {payer_name_db_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table for refunded txn : {merchant_name_2}")
            invoice_number_db_2 = result['pg_invoice_number'].values[0]
            logger.debug(f"Fetching pg invoice number from the txn table for refunded txn : {invoice_number_db_2}")
            emi_type_db_2 = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi type from the txn table for refunded txn : {emi_type_db_2}")
            orig_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching orig_txn_id from the txn table for refunded txn : {orig_txn_id}")

            query = f"select * from txn_emi where id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_emi table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            logger.debug(f"Fetching result for txn_emi table : {result} ")
            emi_interest_rate_db = result['emi_interest_rate'].values[0]
            logger.debug(f"Fetching emi_interest_rate from txn_emi table : {emi_interest_rate_db}")
            emi_status_db = result['emi_status'].values[0]
            logger.debug(f"Fetching emi_status from txn_emi table : {emi_status_db}")
            emi_term_db = result['emi_term'].values[0]
            logger.debug(f"Fetching emi_term from txn_emi table : {emi_term_db}")
            emi_loan_amount_db = result['emi_loan_amount'].values[0]
            logger.debug(f"Fetching emi_loan_amount from txn_emi table : {emi_loan_amount_db}")
            emi_amount_monthly_db = result['emi_amount'].values[0]
            logger.debug(f"Fetching monthly emi_amount from txn_emi table : {emi_amount_monthly_db}")
            emi_total_amount_db = result['emi_total_amount'].values[0]
            logger.debug(f"Fetching emi_total_amount from txn_emi table : {emi_total_amount_db}")
            emi_scheme_code_db = result['emi_scheme_code'].values[0]
            logger.debug(f"Fetching emi_scheme_code from txn_emi table : {emi_scheme_code_db}")
            emi_txn_amount_db = result['txn_amount'].values[0]
            logger.debug(f"Fetching txn_amount from txn_emi table : {emi_txn_amount_db}")
            emi_original_amount_db = result['original_amount'].values[0]
            logger.debug(f"Fetching original_amount from txn_emi table : {emi_original_amount_db}")
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
                date_and_time_app = date_time_converter.to_app_format(posting_date_db=created_time)
                date_and_time_app_2 = date_time_converter.to_app_format(posting_date_db=created_time_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "card_type_desc": "*0321 EMV with PIN",
                    "customer_name": "RAJA",
                    "pmt_by": "EMV with PIN",
                    "card_type": "VISA",
                    "emi_status": "PENDING",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi_cal),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "total_interest": "{:,.2f}".format(total_interest_cal),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest_cal),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "customer": customer_name_db,
                    "txn_amt_2": "{:,.2f}".format(1.00),
                    "pmt_mode_2": "CARD",
                    "txn_id_2": txn_id_2,
                    "pmt_status_2": "REFUNDED",
                    "rrn_2": str(rrn_2),
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "settle_status_2": "PENDING",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_app_2,
                    "device_serial_2": device_serial,
                    "mid_2": mid,
                    "tid_2": tid,
                    "batch_number_2": batch_number_db_2,
                    "customer_name_2": "RAJA",
                    "card_type_desc_2": "*0321 EMV with PIN"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver.reset()
                logger.debug(f"Restarting MPOSX app after performing Offline_Refund of the transaction")
                login_page.perform_login(username=app_username, password=app_password)
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                payment_by = txn_history_page.fetch_payment_by_text()
                logger.debug(f"Fetching payment by from txn history for the original txn : {txn_id}, {payment_by}")
                card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the original txn : {txn_id}, {card_type}")
                emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the original txn : {txn_id}, {emi_status}")
                lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the original txn : {txn_id}, {lender}")
                monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the original txn : {txn_id}, {monthly_emi}")
                total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(f"Fetching total emi amount from txn history for the original txn : {txn_id}, {total_emi_amount}")
                total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the original txn : {txn_id}, {total_interest}")
                loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the original txn : {txn_id}, {loan_amount}")
                interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the original txn : {txn_id}, {interest_amount}")
                net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(f"Fetching net effective price from txn history for the original txn : {txn_id}, {net_effective_price}")
                tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the original txn : {txn_id}, {tenure}")
                customer_app = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the original txn : {txn_id}, {customer_app}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the original txn : {txn_id}, {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the original txn : {txn_id}, {payment_mode}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the original txn : {txn_id}, {payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the original txn : {txn_id}, {app_txn_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the original txn : {txn_id}, {app_rrn}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the original txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the original txn : {txn_id}, {app_payment_msg}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the original txn : {txn_id}, {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for theoriginal  txn : {txn_id}, {app_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the original txn : {txn_id}, {app_date_and_time}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the original txn : {txn_id}, {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the original txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the original txn : {txn_id}, {app_tid}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the original txn : {txn_id}, {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the original txn : {txn_id}, {app_card_type_desc}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the original txn : {txn_id}, {app_customer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the refunded txn : {txn_id_2}, {app_amount_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the refunded txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the refunded txn : {txn_id_2}, {app_txn_id_2}")
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the refunded txn : {txn_id_2}, {payment_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the refunded txn : {txn_id_2}, {app_rrn_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the refunded txn : {txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the refunded txn : {txn_id_2}, {app_payment_msg_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching txn settlement_status from txn history for the refunded txn : {txn_id_2}, {app_settlement_status_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the refunded txn : {txn_id_2}, {app_auth_code_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the refunded txn : {txn_id_2}, {app_date_and_time_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.debug(f"Fetching device serial number from txn history for the refunded txn : {txn_id_2}, {app_device_serial_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the refunded txn : {txn_id_2}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the refunded txn : {txn_id_2}, {app_tid_2}")
                app_batch_number_2 = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the refunded txn : {txn_id_2}, {app_batch_number_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the refunded txn : {txn_id_2}, {app_customer_name_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the refunded txn : {txn_id_2}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rrn": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_number,
                    "card_type_desc": app_card_type_desc,
                    "customer_name": app_customer_name,
                    "pmt_by": payment_by,
                    "card_type": card_type,
                    "emi_status": emi_status,
                    "lender": lender,
                    "monthly_emi": monthly_emi.split(' ')[1],
                    "total_emi_amt": total_emi_amount.split(' ')[1],
                    "total_interest": total_interest.split(' ')[1],
                    "loan_amt": loan_amount.split(' ')[1],
                    "interest_amt": interest_amount.split(' ')[2],
                    "net_eff_price": net_effective_price.split(' ')[1],
                    "tenure": tenure,
                    "customer": customer_app,
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "pmt_mode_2": payment_mode_2,
                    "txn_id_2": app_txn_id_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "rrn_2": app_rrn_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "settle_status_2": app_settlement_status_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "device_serial_2": app_device_serial_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "batch_number_2": app_batch_number_2,
                    "customer_name_2": app_customer_name_2,
                    "card_type_desc_2": app_card_type_desc_2
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
                date_and_time_api = date_time_converter.db_datetime(date_from_db=created_time)
                date_and_time_api_2 = date_time_converter.db_datetime(date_from_db=created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "txn_type": "CHARGE",
                    "auth_code": auth_code,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date_and_time_api,
                    "device_serial": device_serial,
                    "username": app_username,
                    "txn_id": txn_id,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "card_txn_type": "EMV with PIN",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "0321",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "428090",
                    "display_pan": "0321",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "interest_amt": total_interest_cal,
                    "total_emi_amt": total_emi,
                    "emi_type": "NORMAL_EMI",
                    "customer_name": "RAJA                     /",
                    "payer_name": "RAJA                     /",
                    "name_on_card": "RAJA                     /",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": 1.0,
                    "pmt_mode_2": "CARD",
                    "pmt_state_2": "AUTHORIZED",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "PENDING",
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": "REFUND",
                    "auth_code_2": auth_code_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_and_time_api_2,
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "card_txn_type_2": "EMV with PIN",
                    "batch_number_2": batch_number_db_2,
                    "card_last_four_digit_2": "0321",
                    "customer_name_2": "RAJA                     /",
                    "external_ref_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "payer_name_2": "RAJA                     /",
                    "pmt_card_bin_2": "428090",
                    "name_on_card_2": "RAJA                     /",
                    "display_pan_2": "0321",
                    "emi_type_2": "NORMAL_EMI"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of original txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Fetching status from response for original txn : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Fetching amount from response for original txn : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Fetching payment mode from response for original txn : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Fetching state from response for original txn : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Fetching rrn from response for original txn : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for original txn : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Fetching issuer code from response for original txn : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for original txn : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Fetching org code from response for original txn : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Fetching mid from response for original txn : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Fetching tid from response for original txn : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Fetching transaction type from response for original txn : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Fetching auth code from response for original txn : {auth_code_api}")
                date_and_time_api = response_1["createdTime"]
                logger.debug(f"Fetching date and time from response for original txn : {date_and_time_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Fetching device serial from response for original txn : {device_serial_api}")
                username_api = response_1["username"]
                logger.debug(f"Fetching username from response for original txn : {username_api}")
                txn_id_api = response_1["txnId"]
                logger.debug(f"Fetching transaction id from response for original txn : {txn_id_api}")
                payment_card_brand_api = response_1["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for original txn : {payment_card_brand_api}")
                payment_card_type_api = response_1["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for original txn : {payment_card_type_api}")
                card_txn_type_api = response_1["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for original txn : {card_txn_type_api}")
                batch_number_api = response_1["batchNumber"]
                logger.debug(f"Fetching batch number from response for original txn : {batch_number_api}")
                card_last_four_digit_api = response_1["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for original txn : {card_last_four_digit_api}")
                external_ref_number_api = response_1["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for original txn : {external_ref_number_api}")
                merchant_name_api = response_1["merchantName"]
                logger.debug(f"Fetching merchant name from response for original txn : {merchant_name_api}")
                payment_card_bin_api = response_1["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for original txn : {payment_card_bin_api}")
                display_pan_api = response_1["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for original txn : {display_pan_api}")
                api_emi_term = response_1.get('emiTerm')
                logger.debug(f"Fetching emi_term from response for original txn : {api_emi_term}")
                api_emi_status = response_1.get('emiStatus')
                logger.debug(f"Fetching emi_status from response for original txn : {api_emi_status}")
                api_interest_rate = response_1.get('emiInterestRate')
                logger.debug(f"Fetching emi_interest_rate from response for original txn : {api_interest_rate}")
                api_emi_type = response_1.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for original txn : {api_emi_type}")
                api_loan_amt = response_1.get('emiDetails')['loanAmount']
                logger.debug(f"Fetching loan_amount from response for original txn : {api_loan_amt}")
                api_monthly_emi = response_1.get('emiDetails')['emi']
                logger.debug(f"Fetching monthly emi from response for original txn : {api_monthly_emi}")
                api_interest_amt = response_1.get('emiDetails')['interestAmount']
                logger.debug(f"Fetching interest_amount from response for original txn : {api_interest_amt}")
                api_total_emi_amt = response_1.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"Fetching total emi amount from response for original txn : {api_total_emi_amt}")
                customer_name_api = response_1["customerName"]
                logger.debug(f"Fetching customer name from response for original txn : {customer_name_api}")
                payer_name_api = response_1["payerName"]
                logger.debug(f"Fetching payer name from response for original txn : {payer_name_api}")
                name_on_card_api = response_1["nameOnCard"]
                logger.debug(f"Fetching name on card from response for original txn : {name_on_card_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of refunded txn is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Fetching status from response for refunded txn : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Fetching amount from response for refunded txn : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Fetching payment mode from response for refunded txn : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Fetching state from response for refunded txn : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Fetching rrn from response for refunded txn : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Fetching settlement status from response for refunded txn : {settlement_status_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response for refunded txn : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Fetching org code from response for refunded txn : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Fetching mid from response for refunded txn : {mid_api_2}")
                tid_api_2 = response_2["tid"]
                logger.debug(f"Fetching tid from response for refunded txn : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Fetching transaction type from response for refunded txn : {txn_type_api_2}")
                auth_code_api_2 = response_2["authCode"]
                logger.debug(f"Fetching auth code from response for refunded txn : {auth_code_api_2}")
                date_and_time_api_2 = response_2["createdTime"]
                logger.debug(f"Fetching date and time from response for refunded txn : {date_and_time_api_2}")
                username_api_2 = response_2["username"]
                logger.debug(f"Fetching username from response for refunded txn : {username_api_2}")
                txn_id_api_2 = response_2["txnId"]
                logger.debug(f"Fetching transaction id from response for refunded txn : {txn_id_api_2}")
                payment_card_brand_api_2 = response_2["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response for refunded txn : {payment_card_brand_api_2}")
                payment_card_type_api_2 = response_2["paymentCardType"]
                logger.debug(f"Fetching payment card type from response for refunded txn : {payment_card_type_api_2}")
                card_txn_type_api_2 = response_2["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response for refunded txn : {card_txn_type_api_2}")
                batch_number_api_2 = response_2["batchNumber"]
                logger.debug(f"Fetching batch number from response for refunded txn : {batch_number_api_2}")
                card_last_four_digit_api_2 = response_2["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response for refunded txn : {card_last_four_digit_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Fetching customer name from response for refunded txn : {customer_name_api_2}")
                external_ref_number_api_2 = response_2["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response for refunded txn : {external_ref_number_api_2}")
                merchant_name_api_2 = response_2["merchantName"]
                logger.debug(f"Fetching merchant name from response for refunded txn : {merchant_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Fetching payer name from response for refunded txn : {payer_name_api_2}")
                payment_card_bin_api_2 = response_2["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response for refunded txn : {payment_card_bin_api_2}")
                name_on_card_api_2 = response_2["nameOnCard"]
                logger.debug(f"Fetching name on card from response for refunded txn : {name_on_card_api_2}")
                display_pan_api_2 = response_2["displayPAN"]
                logger.debug(f"Fetching display_PAN from response for refunded txn : {display_pan_api_2}")
                emi_type_api_2 = response_2.get('externalRefNumber7')
                logger.debug(f"Fetching emi_type from response for refunded txn : {emi_type_api_2}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "txn_type": txn_type_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_and_time_api),
                    "device_serial": device_serial_api,
                    "username": username_api,
                    "txn_id": txn_id_api,
                    "pmt_card_brand": payment_card_brand_api,
                    "pmt_card_type": payment_card_type_api,
                    "card_txn_type": card_txn_type_api,
                    "batch_number": batch_number_api,
                    "card_last_four_digit": card_last_four_digit_api,
                    "external_ref": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "display_pan": display_pan_api,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "emi_type": api_emi_type,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "name_on_card": name_on_card_api,
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "auth_code_2": auth_code_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_and_time_api_2),
                    "username_2": username_api_2,
                    "txn_id_2": txn_id_api_2,
                    "pmt_card_brand_2": payment_card_brand_api_2,
                    "pmt_card_type_2": payment_card_type_api_2,
                    "card_txn_type_2": card_txn_type_api_2,
                    "batch_number_2": batch_number_api_2,
                    "card_last_four_digit_2": card_last_four_digit_api_2,
                    "customer_name_2": customer_name_api_2,
                    "external_ref_2": external_ref_number_api_2,
                    "merchant_name_2": merchant_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_card_bin_2": payment_card_bin_api_2,
                    "name_on_card_2": name_on_card_api_2,
                    "display_pan_2": display_pan_api_2,
                    "emi_type_2": emi_type_api_2
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
                    "txn_amt": 1,
                    "pmt_mode": "CARD",
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "acquirer_code": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "DUMMY",
                    "settle_status": "SETTLED",
                    "device_serial": device_serial,
                    "merchant_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "DEBIT",
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "org_code": org_code,
                    "pmt_card_bin": "428090",
                    "terminal_info_id": terminal_info_id,
                    "txn_type": "CHARGE",
                    "card_txn_type": "03",
                    "card_last_four_digit": "0321",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "NORMAL_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi_cal,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "customer_name": "RAJA                     /",
                    "payer_name": "RAJA                     /",
                    "orig_amt": float(amount),
                    "txn_amt_2": 1,
                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "AUTHORIZED",
                    "acquirer_code_2": "HDFC",
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "DUMMY",
                    "settle_status_2": "PENDING",
                    "merchant_code_2": org_code,
                    "pmt_card_brand_2": "VISA",
                    "pmt_card_type_2": "DEBIT",
                    "order_id_2": order_id,
                    "org_code_2": org_code,
                    "pmt_card_bin_2": "428090",
                    "terminal_info_id_2": terminal_info_id,
                    "txn_type_2": "REFUND",
                    "card_txn_type_2": "03",
                    "card_last_four_digit_2": "0321",
                    "customer_name_2": "RAJA                     /",
                    "payer_name_2": "RAJA                     /",
                    "emi_type_2": "NORMAL_EMI",
                    "orig_txn_id": txn_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "device_serial": device_serial_db,
                    "merchant_code": merchant_code_db,
                    "pmt_card_brand": payment_card_brand_db,
                    "pmt_card_type": payment_card_type_db,
                    "order_id": order_id_db,
                    "issuer_code": issuer_code_db,
                    "org_code": org_code_db,
                    "pmt_card_bin": payment_card_bin_db,
                    "terminal_info_id": terminal_info_id_db,
                    "txn_type": txn_type_db,
                    "card_txn_type": card_txn_type_db,
                    "card_last_four_digit": card_last_four_digit_db,
                    "interest_rate": emi_interest_rate_db,
                    "emi_status": emi_status_db,
                    "emi_term": emi_term_db,
                    "emi_type": emi_type_db,
                    "loan_amt": emi_loan_amount_db,
                    "monthly_emi": emi_amount_monthly_db,
                    "total_emi_amt": emi_total_amount_db,
                    "scheme_code": emi_scheme_code_db,
                    "emi_txn_amt": emi_txn_amount_db,
                    "emi_original_amt": emi_original_amount_db,
                    "customer_name": customer_name_db,
                    "payer_name": payer_name_db,
                    "orig_amt": amount_original_db,
                    "txn_amt_2": amount_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "pmt_status_2": payment_status_db_2,
                    "pmt_state_2": payment_state_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "merchant_code_2": merchant_code_db_2,
                    "pmt_card_brand_2": payment_card_brand_db_2,
                    "pmt_card_type_2": payment_card_type_db_2,
                    "order_id_2": order_id_db_2,
                    "org_code_2": org_code_db_2,
                    "pmt_card_bin_2": payment_card_bin_db_2,
                    "terminal_info_id_2": terminal_info_id_db_2,
                    "txn_type_2": txn_type_db_2,
                    "card_txn_type_2": card_txn_type_db_2,
                    "card_last_four_digit_2": card_last_four_digit_db_2,
                    "customer_name_2": customer_name_db_2,
                    "payer_name_2": payer_name_db_2,
                    "emi_type_2": emi_type_db_2,
                    "orig_txn_id": orig_txn_id
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
                date_and_time_portal = date_time_converter.to_portal_format(created_date_db=created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_date_db=created_time_2)
                expected_portal_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_type": "CARD",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time": date_and_time_portal,
                    "pmt_status_2": "REFUNDED",
                    "pmt_type_2": "CARD",
                    "txn_amt_2": "{:,.2f}".format(1.00),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "auth_code_2": auth_code_2,
                    "rrn_2": rrn_2,
                    "date_time_2": date_and_time_portal_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                logger.debug(f"Fetching transaction details from portal : {transaction_details}")
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                date_time = transaction_details[1]['Date & Time']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time": date_time,
                    "pmt_status_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "date_time_2": date_time_2
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=created_time_2)
                expected_charge_slip_values = {
                    "CARD TYPE": "VISA",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn_2),
                    "AUTH CODE": auth_code_2,
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "REFUND",
                    "BATCH NO": batch_number_db_2,
                    "TID": tid,
                    "INVOICE NO": invoice_number_db_2,
                    "CARD": f"XXXX-XXXX-XXXX-0321 EMV with PIN",
                    "BASE AMOUNT:": "Rs.1.00",
                    "unnamed_section_text": "RAJA /"
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
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

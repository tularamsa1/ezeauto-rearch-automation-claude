import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
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
def test_common_100_103_07_003():
    """
    Sub Feature Code: UI_Common_Card_BRAND_EMI_Success_CNP_Txn_For_An_Org_HDFC_Dummy_Canara_VISA_CreditCard_400000_For_3_Months_Tenure
    Sub Feature Description: Performing the brand EMI success CNP transaction for an org (not ezetap) via HDFC Dummy PG for
    Canara issuer using VISA Credit card with pin for 3 months tenure (bin: 400000)
    TC naming code description: 100: Payment Method, 103: CNP, 07: BRAND_EMI, 003: TC003
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username,
                                                                portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Below function to update bank_code, bank for the bin: 400000
        testsuite_teardown.update_bin_info(bin_number='400000', bank_code='CANARA', bank='CANARA')

        query = f"select bank_code from bin_info where bin='400000'"
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
        api_details["RequestBody"]["settings"]["brandEmiEnabled"] = "true"
        api_details["RequestBody"]["settings"]["EMI_ON_CC_ENABLED_IN_CNP"] = "true"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions for brand emi setup to be enabled:  {response}")

        testsuite_teardown.update_emi_status_for_org(org_code=org_code, card_type='CREDIT', status='ACTIVE')
        logger.debug(f"updated emi settings for {org_code} as active for credit card")

        emi_plan_in_months = 3
        logger.debug(f"emi_plan_in_months : {emi_plan_in_months}")

        query = f"select * from emi where org_code='{org_code}' and status = 'ACTIVE' and " \
                f"issuer_code='CANARA' and card_type='CREDIT' and term = '{emi_plan_in_months} month' and emi_type='BRAND'" \
                f"and tid_type='SUBVENTION'"
        logger.debug(f"Query to fetch data from the emi table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from emi table :{result}")
        interest_rate = result['interest_rate'].values[0]
        logger.debug(f"Fetching interest_rate from the emi table : {interest_rate}")
        term = result['term'].values[0]
        logger.debug(f"Fetching term from the emi table : {term}")
        scheme_code = result['scheme_code'].values[0]
        logger.debug(f"Fetching scheme_code from the emi table : {scheme_code}")
        brand_id = result['brand'].values[0]
        logger.debug(f"Fetching brand from the emi table : {brand_id}")

        testsuite_teardown.update_brand_for_emi_plus(eze_emi_enabled=0, brand_id=brand_id)

        query = f"select * from brand where id='{brand_id}'"
        logger.debug(f"Query to fetch data from the brand table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_name = result['brand_name'].values[0]
        logger.debug(f"Fetching brand_name value from the brand table : {brand_name}")

        query = f"select * from brand_sku_details where brand_id='{str(brand_id)}' and eze_emi_enabled=b'0';"
        logger.debug(f"Query to fetch data from the brand_sku_details table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for brand table : {result}")
        brand_sku_name = result['sku_name'].values[0]
        logger.debug(f"Fetching sku_name value from the brand_sku_details table : {brand_sku_name}")
        brand_sku_category = result['sku_category'].values[0]
        logger.debug(f"Fetching sku_category value from the brand_sku_details table : {brand_sku_category}")
        brand_sku_code = result['sku_code'].values[0]
        logger.debug(f"Fetching sku_code value from the brand_sku_details table : {brand_sku_code}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, q2_log=True,
                                                   cnpwareLog=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(3001, 4000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            customer_name = 'John doe'
            logger.debug(f"customer_name : {customer_name}")
            customer_mobile = '1234567890'
            logger.debug(f"customer_mobile : {customer_mobile}")
            imei_no = random.randint(1, 500)
            logger.debug(f"Randomly generated imei number is, {imei_no}")
            api_details = DBProcessor.get_api_details('create_payment_link_emi', request_body={
                "amount": amount, "externalRefNumber": order_id,
                "username": app_username, "password": app_password,
                "customerName": customer_name, "customerMobileNumber": customer_mobile,
                "externalRefNumber3": device_serial, "emiType": "BRAND",
                "emiInput": {"brandName": brand_name, "sku": brand_sku_code, "productName": brand_sku_name},
                "productSerialNo": imei_no
            })
            response = APIProcessor.send_request(api_details)
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                # verify whether link is generated or not
                payment_link_url = response.get('paymentLink')
                logger.debug(f"Fetching payment_link : {payment_link_url}")
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.enter_card_details_emi(card_number='4000 0000 0000 0119', expiry_month='12',
                                                      expiry_year='24', cvv='123', name_on_card=customer_name)
                remote_pay_txn.click_on_proceed()
                remote_pay_txn.select_emi_plan(emi_plan_in_months)
                remote_pay_txn.click_on_proceed()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected message is:  {expected_message}")
                if success_message == expected_message:
                    pass
                else:
                    raise Exception("Success Message is not matching.")

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

            query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name_txn}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table : {pmt_status}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table : {issuer_code_txn}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table : {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table : {amount_txn}")
            pmt_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from the txn table : {pmt_card_brand}")
            pmt_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from the txn table : {pmt_card_type}")
            card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from the txn table : {card_last_four_digit}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table : {merchant_name}")
            pmt_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from the txn table : {pmt_card_bin}")
            device_serial_txn = result['external_ref3'].values[0]
            logger.debug(f"Fetching device_serial from the txn table : {device_serial_txn}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table : {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : {org_code_txn}")
            emi_type = result['external_ref7'].values[0]
            logger.debug(f"Fetching emi_type from the txn table : {emi_type}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from the txn table : {posting_date}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table : {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table : {tid_txn}")

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

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch data from the cnp_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for cnp_txn table : {result} ")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from cnp_txn table : {cnp_txn_rrn}")
            cnp_txn_payment_option = result['payment_option'].values[0]
            logger.debug(f"Fetching payment_option from cnp_txn table : {cnp_txn_payment_option}")
            cnp_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnp_txn table : {cnp_txn_payment_flow}")
            cnp_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnp_txn table : {cnp_txn_payment_status}")
            cnp_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnp_txn table : {cnp_txn_type}")
            cnp_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnp_txn table : {cnp_txn_payment_mode}")
            cnp_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnp_txn table : {cnp_txn_payment_gateway}")
            cnp_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnp_txn table : {cnp_txn_payment_state}")
            cnp_txn_payment_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from cnp_txn table : {cnp_txn_payment_card_bin}")
            cnp_txn_payment_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from cnp_txn table : {cnp_txn_payment_card_brand}")
            cnp_txn_payment_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from cnp_txn table : {cnp_txn_payment_card_type}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from cnp_txn table : {cnp_txn_acquirer_code}")
            cnp_txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from cnp_txn table : {cnp_txn_issuer_code}")
            cnp_txn_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from cnp_txn table : {cnp_txn_card_last_four_digit}")
            cnp_txn_card_device_serial = result['external_ref3'].values[0]
            logger.debug(f"Fetching device_serial from cnp_txn table : {cnp_txn_card_device_serial}")
            cnp_txn_org_code = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from cnp_txn table : {cnp_txn_org_code}")
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
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "PAY LINK",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rr_number": cnp_txn_rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "SETTLED",
                    "auth_code": auth_code,
                    "date": date_time,
                    "device_serial": device_serial,
                    "card_type_desc": "*0119",
                    "customer_name": customer_name,
                    "card_type": "VISA",
                    "customer": customer_name,
                    "customer_mobile": customer_mobile,
                    "emi_status": "PENDING",
                    "tenure": str(term) + " @ " + str(interest_rate) + "% " + "p.a.",
                    "lender": issuer_code,
                    "monthly_emi": "{:,.2f}".format(monthly_emi),
                    "total_interest": "{:,.2f}".format(total_interest),
                    "total_emi_amt": "{:,.2f}".format(total_emi),
                    "loan_amt": "{:,.2f}".format(amount),
                    "interest_amt": "{:,.2f}".format(total_interest),
                    "net_eff_price": "{:,.2f}".format(total_emi),
                    "brand": brand_name,
                    "product": brand_sku_name,
                    "imei_no": str(imei_no)
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

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
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_card_type = txn_history_page.fetch_card_type_text()
                logger.debug(f"Fetching card type from txn history for the txn : {txn_id}, {app_card_type}")
                app_customer = txn_history_page.fetch_customer_text()
                logger.debug(f"Fetching customer from txn history for the txn : {txn_id}, {app_customer}")
                app_emi_status = txn_history_page.fetch_emi_status_text()
                logger.debug(f"Fetching emi status from txn history for the txn : {txn_id}, {app_emi_status}")
                app_tenure = txn_history_page.fetch_tenure_text()
                logger.debug(f"Fetching tenure from txn history for the txn : {txn_id}, {app_tenure}")
                app_lender = txn_history_page.fetch_lender_text()
                logger.debug(f"Fetching lender from txn history for the txn : {txn_id}, {app_lender}")
                app_monthly_emi = txn_history_page.fetch_monthly_emi_text()
                logger.debug(f"Fetching monthly emi from txn history for the txn : {txn_id}, {app_monthly_emi}")
                app_total_interest = txn_history_page.fetch_total_interest_text()
                logger.debug(f"Fetching total interest from txn history for the txn : {txn_id}, {app_total_interest}")
                app_total_emi_amount = txn_history_page.fetch_total_emi_amount_text()
                logger.debug(
                    f"Fetching total emi amount from txn history for the txn : {txn_id}, {app_total_emi_amount}")
                app_loan_amount = txn_history_page.fetch_loan_amount_text()
                logger.debug(f"Fetching loan amount from txn history for the txn : {txn_id}, {app_loan_amount}")
                app_interest_amount = txn_history_page.fetch_interest_amount_text()
                logger.debug(f"Fetching interest amount from txn history for the txn : {txn_id}, {app_interest_amount}")
                app_net_effective_price = txn_history_page.fetch_net_effective_price_text()
                logger.debug(
                    f"Fetching net effective price from txn history for the txn : {txn_id}, {app_net_effective_price}")
                app_brand_name = txn_history_page.fetch_brand_text()
                logger.debug(f"Fetching brand name from txn history for the txn : {txn_id}, {app_brand_name}")
                app_imei_no = txn_history_page.fetch_imei_text()
                logger.debug(f"Fetching imei or serial no from txn history for the txn : {txn_id}, {app_imei_no}")
                app_product = txn_history_page.fetch_product_text()
                logger.debug(f"Fetching product from txn history for the txn : {txn_id}, {app_product}")
                app_payment_status = txn_history_page.fetch_emi_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {txn_id}, {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_for_cnp_emi_text()
                logger.info(f"Fetching device_serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_card = txn_history_page.fetch_card_text()
                logger.info(f"Fetching card from txn history for the txn : {txn_id}, {app_card}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the txn : {txn_id}, {app_customer_mobile}")

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
                    "card_type_desc": app_card,
                    "customer_name": app_customer_name,
                    "card_type": app_card_type,
                    "customer": app_customer,
                    "customer_mobile": app_customer_mobile,
                    "emi_status": app_emi_status,
                    "tenure": app_tenure,
                    "lender": app_lender,
                    "monthly_emi": app_monthly_emi.split(' ')[1],
                    "total_interest": app_total_interest.split(' ')[1],
                    "total_emi_amt": app_total_emi_amount.split(' ')[1],
                    "loan_amt": app_loan_amount.split(' ')[1],
                    "interest_amt": app_interest_amount.split(' ')[2],
                    "net_eff_price": app_net_effective_price.split(' ')[1],
                    "brand": app_brand_name,
                    "product": app_product,
                    "imei_no": app_imei_no
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
                expected_api_values = {
                    "txn_amt": float(amount),
                    "pmt_mode": "CNP",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "mid": mid,
                    "tid": tid,
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "rrn": cnp_txn_rrn,
                    "issuer_code": issuer_code,
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "date": date_time,
                    "device_serial": device_serial,
                    "auth_code": auth_code,
                    "card_last_four_digit": "0119",
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "400000",
                    "card_type": "VISA",
                    "display_pan": "0119",
                    "customer_name": customer_name,
                    "payer_name": customer_name,
                    "name_on_card": customer_name,
                    "customer_mobile": customer_mobile,
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_status": "PENDING",
                    "interest_rate": interest_rate,
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "interest_amt": total_interest,
                    "total_emi_amt": total_emi,
                    "net_cost": total_emi,
                    "emi_type": "BRAND_EMI",
                    "brand_name": brand_name,
                    "product_name": brand_sku_name,
                    "sku_code": brand_sku_code,
                    "product_serial": str(imei_no)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount : {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode : {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status : {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state : {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid : {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid : {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status : {api_settle_status}")
                api_rrn = response.get('rrNumber')
                logger.debug(f"From response fetch rrn : {api_rrn}")
                api_issuer_code = response.get('issuerCode')
                logger.debug(f"From response fetch issuer_code : {api_issuer_code}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type : {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code : {api_org_code}")
                api_pmt_card_brand = response.get('paymentCardBrand')
                logger.debug(f"From response fetch payment_card_brand : {api_pmt_card_brand}")
                api_pmt_card_type = response.get('paymentCardType')
                logger.debug(f"From response fetch payment_card_type : {api_pmt_card_type}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time : {api_date_time}")
                api_device_serial = response.get('externalRefNumber3')
                logger.debug(f"From response fetch device_serial : {api_device_serial}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name : {api_merchant_name}")
                api_card_last_four_digit = response.get('cardLastFourDigit')
                logger.debug(f"From response fetch card_last_four_digit : {api_card_last_four_digit}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number : {api_ext_ref_number}")
                api_pmt_card_bin = response.get('paymentCardBin')
                logger.debug(f"From response fetch payment_card_bin : {api_pmt_card_bin}")
                api_display_pan = response.get('displayPAN')
                logger.debug(f"From response fetch display_pan : {api_display_pan}")
                api_auth_code = response.get('authCode')
                logger.debug(f"From response fetch auth_code : {api_auth_code}")
                api_card_type = response.get('cardType')
                logger.debug(f"From response fetch card_type : {api_card_type}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name : {api_customer_name}")
                api_payer_name = response.get('payerName')
                logger.debug(f"From response fetch payer_name : {api_payer_name}")
                api_name_on_card = response.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card : {api_name_on_card}")
                api_customer_mobile = response.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile : {api_customer_mobile}")
                api_emi_term = response.get('emiTerm')
                logger.debug(f"From response fetch emi_term : {api_emi_term}")
                api_emi_status = response.get('emiStatus')
                logger.debug(f"From response fetch emi_status : {api_emi_status}")
                api_interest_rate = response.get('emiInterestRate')
                logger.debug(f"From response fetch emi_interest_rate : {api_interest_rate}")
                api_emi_type = response.get('externalRefNumber7')
                logger.debug(f"From response fetch emi_type : {api_emi_type}")
                api_loan_amt = response.get('emiDetails')['loanAmount']
                logger.debug(f"From response fetch loan_amount : {api_loan_amt}")
                api_monthly_emi = response.get('emiDetails')['emi']
                logger.debug(f"From response fetch monthly emi : {api_monthly_emi}")
                api_interest_amt = response.get('emiDetails')['interestAmount']
                logger.debug(f"From response fetch interest_amount : {api_interest_amt}")
                api_total_emi_amt = response.get('emiDetails')['totalAmountWithInt']
                logger.debug(f"From response fetch total emi amount : {api_total_emi_amt}")
                api_net_cost = response.get('emiDetails')['netCost']
                logger.debug(f"From response fetch net cost : {api_net_cost}")
                api_manufacturer = response['emiDetails']['manufacturer']
                logger.debug(f"From response fetch manufacturer : {api_manufacturer}")
                api_product_name = response['emiDetails']['productName']
                logger.debug(f"From response fetch product name : {api_product_name}")
                api_sku_code = response['emiDetails']['skuCode']
                logger.debug(f"From response fetch sku_code : {api_sku_code}")
                api_product_serial = response['emiDetails']['productSerial']
                logger.debug(f"From response fetch product serial : {api_product_serial}")

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
                    "pmt_card_brand": api_pmt_card_brand,
                    "pmt_card_type": api_pmt_card_type,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "device_serial": api_device_serial,
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
                    "customer_mobile": api_customer_mobile,
                    "emi_term": api_emi_term,
                    "emi_status": api_emi_status,
                    "interest_rate": api_interest_rate,
                    "loan_amt": api_loan_amt,
                    "monthly_emi": api_monthly_emi,
                    "interest_amt": api_interest_amt,
                    "total_emi_amt": api_total_emi_amt,
                    "net_cost": api_net_cost,
                    "emi_type": api_emi_type,
                    "brand_name": api_manufacturer,
                    "product_name": api_product_name,
                    "sku_code": api_sku_code,
                    "product_serial": api_product_serial
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
                    "pmt_mode": "CNP",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": issuer_code,
                    "payer_name": customer_name,
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "CYBERSOURCE",
                    "txn_type": "REMOTE_PAY",
                    "settle_status": "SETTLED",
                    "pmt_card_brand": "VISA",
                    "pmt_card_type": "CREDIT",
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "org_code": org_code,
                    "pmt_card_bin": "400000",
                    "card_last_four_digit": "0119",
                    "customer_name": customer_name,
                    "customer_mobile": customer_mobile,
                    "pmt_option": "CNP_EMI_CC",
                    "pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "interest_rate": interest_rate,
                    "emi_status": "PENDING",
                    "emi_term": f"{emi_plan_in_months} month",
                    "emi_type": "BRAND_EMI",
                    "loan_amt": float(amount),
                    "monthly_emi": monthly_emi,
                    "total_emi_amt": total_emi,
                    "scheme_code": scheme_code,
                    "emi_txn_amt": float(amount),
                    "emi_original_amt": float(amount),
                    "brand_name": api_manufacturer,
                    "sku_code": api_sku_code,
                    "product_name": api_product_name,
                    "cnp_pmt_state": "SETTLED",
                    "cnp_pmt_card_bin": "400000",
                    "cnp_pmt_card_brand": "VISA",
                    "cnp_pmt_card_type": "CREDIT",
                    "cnp_acquirer_code": "HDFC",
                    "cnp_issuer_code": issuer_code,
                    "cnp_card_last_four_digit": "0119",
                    "cnp_org_code": org_code,
                    "cnp_device_serial": device_serial
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "txn_amt": amount_txn,
                    "pmt_mode": cnp_txn_payment_mode,
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "payer_name": payer_name,
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "pmt_gateway": cnp_txn_payment_gateway,
                    "txn_type": cnp_txn_type,
                    "settle_status": settle_status,
                    "pmt_card_brand": pmt_card_brand,
                    "pmt_card_type": pmt_card_type,
                    "device_serial": device_serial_txn,
                    "order_id": order_id_txn,
                    "org_code": org_code_txn,
                    "pmt_card_bin": pmt_card_bin,
                    "card_last_four_digit": card_last_four_digit,
                    "customer_name": customer_name_txn,
                    "customer_mobile": customer_mobile_txn,
                    "pmt_option": cnp_txn_payment_option,
                    "pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
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
                    "brand_name": brand_name,
                    "product_name": brand_sku_name,
                    "sku_code": brand_sku_code,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_pmt_card_bin": cnp_txn_payment_card_bin,
                    "cnp_pmt_card_brand": cnp_txn_payment_card_brand,
                    "cnp_pmt_card_type": cnp_txn_payment_card_type,
                    "cnp_acquirer_code": cnp_txn_acquirer_code,
                    "cnp_issuer_code": cnp_txn_issuer_code,
                    "cnp_card_last_four_digit": cnp_txn_card_last_four_digit,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_device_serial": cnp_txn_card_device_serial
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
                expected_portal_values = {
                    "pmt_type": "CNP",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "date_time": date_time,
                    "pmt_status": "AUTHORIZED"
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[0]['Date & Time']
                logger.info(
                    f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[0]['Total Amount']
                logger.info(
                    f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_auth_code = transaction_details[0]['Auth Code']
                logger.info(
                    f"Fetching auth_code from portal txn history for the order_id : {order_id}, {portal_auth_code}")
                portal_txn_type = transaction_details[0]['Type']
                logger.info(
                    f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[0]['Status']
                logger.info(
                    f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")

                actual_portal_values = {
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "auth_code": portal_auth_code,
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "RRN": cnp_txn_rrn,
                    "MID": mid,
                    "TID": tid,
                    "AUTH CODE": str(auth_code).strip(),
                    "CARD TYPE": "VISA",
                    "payment_option": "EMI SALE",
                    "EMI Txn Id": txn_id,
                    "Tenure": f"{emi_plan_in_months} month",
                    "Card Issuer": "Canara Bank",
                    "Rate of Interest(P.A.)": f"{interest_rate}%",
                    "Interest Amt": "Rs." + "{:.2f}".format(total_interest),
                    "EMI Amt": "Rs." + "{:.2f}".format(monthly_emi),
                    "Total Amt with Interest": "Rs." + "{:.2f}".format(total_emi),
                    "CARD": f"XXXX-XXXX-XXXX-0119",
                    "unnamed_section_text": customer_name,
                    "Manufacturer Name": brand_name,
                    "Product Name": brand_sku_name,
                    "Product Desc": brand_sku_code,
                    "Sr. No.": str(imei_no),
                    "Mobile": customer_mobile
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
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
        try:
            testsuite_teardown.update_bin_info(bin_number='400000', bank_code='HDFC', bank='HDFC')
        except Exception as e:
            logger.exception(f"Query updation failed due to expection : {e}")
        Configuration.executeFinallyBlock(testcase_id)
import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_116_033():
    """
    Sub Feature Code: UI_Common_Card_Sale_AXIS_ATOS_TLE_Opt_Out_MC_Chip_KWD_CreditCard_With_Online_Pin_222297
    Sub Feature Description: Performing the opt out MC Chip KWD sale transaction via AXIS ATOS TLE PG using Credit card
    with online pin  (bin:222297)
    TC naming code description: 100: Payment Method, 116: CARD_DCC, 033: TC033
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

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='AXIS' and payment_gateway='ATOS_TLE' "
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["fraudRulesEnabled"] = "true"
        api_details["RequestBody"]["settings"]["DEFAULT_BANK"] = "AXIS"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions :  {response}")

        query = f"select bank_code from bin_info where bin='222297'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(5000, 9000)
            converted_amount = amount * 0.52480573
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : MC KWD chip")
            card_page.select_cardtype(text="MC KWD chip")
            logger.debug(f"selected the card type as : MC KWD chip")
            payment_page.select_currency_type_inr()
            inr_currency_rate = payment_page.fetch_inr_currency_value()
            payment_page.click_agree_and_pay()
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table : {acquirer_code_db}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table : {customer_name_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table : {device_serial_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table : {issuer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table : {payer_name_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table : {payment_card_bin_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table : {payment_card_type_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table : {payment_mode_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table : {settlement_status_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table : {payment_status_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table : {txn_type_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table : {terminal_info_id_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table : {payment_state_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table : {merchant_code_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table : {batch_number_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table : {org_code_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")

            query = f"select * from txn_dcc where txn_id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_dcc table : {query}")
            result_dcc = DBProcessor.getValueFromDB(query=query)
            dcc_amount_db = result_dcc['amount'].values[0]
            logger.debug(f"Fetching amount from txn_dcc table : {dcc_amount_db}")
            dcc_converted_amount_db = result_dcc['converted_amount'].values[0]
            logger.debug(f"Fetching dcc_converted_amount_db from txn_dcc table : {dcc_converted_amount_db}")
            dcc_conversion_rate_db = result_dcc['conversion_rate'].values[0]
            logger.debug(f"Fetching dcc_converted_amount_db from txn_dcc table : {dcc_conversion_rate_db}")
            dcc_card_holder_currency_db = result_dcc['card_holder_currency'].values[0]
            logger.debug(f"Fetching dcc_card_holder_currency_db from txn_dcc table : {dcc_card_holder_currency_db}")
            dcc_merchant_currency = result_dcc['merchant_currency'].values[0]
            logger.debug(f"Fetching dcc_merchant_currency from txn_dcc table : {dcc_merchant_currency}")
            dcc_status_db = result_dcc['status'].values[0]
            logger.debug(f"Fetching dcc_status_db from txn_dcc table : {dcc_status_db}")
            dcc_payment_card_brand_db = result_dcc['payment_card_brand'].values[0]
            logger.debug(f"Fetching dcc_payment_card_brand_db from txn_dcc table : {dcc_payment_card_brand_db}")
            dcc_markup_fee_db = result_dcc['dcc_markup_fee'].values[0]
            logger.debug(f"Fetching dcc_markup_fee_db from txn_dcc table : {dcc_markup_fee_db}")
            dcc_payment_card_bin_db = result_dcc['payment_card_bin'].values[0]
            logger.debug(f"Fetching dcc_payment_card_bin_db from txn_dcc table : {dcc_payment_card_bin_db}")
            dcc_card_last_four_digit_db = result_dcc['card_last_four_digit'].values[0]
            logger.debug(f"Fetching dcc_card_last_four_digit_db from txn_dcc table : {dcc_card_last_four_digit_db}")
            dcc_mid_db = result_dcc['dcc_mid'].values[0]
            logger.debug(f"Fetching dcc_mid_db from txn_dcc table : {dcc_mid_db}")
            dcc_tid_db = result_dcc['dcc_tid'].values[0]
            logger.debug(f"Fetching dcc_tid_db from txn_dcc table : {dcc_tid_db}")

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
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "customer_name": "MC KWD ONL PIN",
                    "card_type_desc": "*4143 EMV with Online PIN ByPass",
                    "opted_type": "No",
                    "local_card": "No",
                    "inr_currency_rate": "INR " + str(amount) + ".0"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the txn : {payment_mode}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the txn : {payment_status}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the txn : {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the txn : {app_payment_msg}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {app_txn_id}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.debug(f"Fetching customer name for the txn : {app_customer_name}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the txn : {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for the txn : {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the txn : {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for the txn : {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the txn : {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the txn : {app_tid}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the txn : {app_rrn}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the txn : {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the txn : {app_card_type_desc}")
                app_opted_dcc = txn_history_page.fetch_opted_dcc_text()
                logger.debug(f"Fetching opted card type for the txn : {app_opted_dcc}")
                app_local_card = txn_history_page.fetch_local_card_text()
                logger.debug(f"Fetching app local card for the txn : {app_local_card}")

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
                    "customer_name": app_customer_name,
                    "card_type_desc": app_card_type_desc,
                    "opted_type": app_opted_dcc,
                    "local_card": app_local_card,
                    "inr_currency_rate": inr_currency_rate
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "AXIS",
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
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "EMV with Online PIN ByPass",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "4143",
                    "customer_name": "MC KWD ONL PIN",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "payer_name": "MC KWD ONL PIN",
                    "pmt_card_bin": "222297",
                    "name_on_card": "MC KWD ONL PIN",
                    "display_pan": "4143",
                    "card_holder_currency": "JPY",
                    "payment_gateway": "ATOS_TLE"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from response : {status_api}")

                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from response : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from response : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from response : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from response : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from response : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from response : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from response : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from response : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from response : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching transaction type from response : {txn_type_api}")
                auth_code_api = response["authCode"]
                logger.debug(f"Fetching auth code from response : {auth_code_api}")
                date_and_time_api = response["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api}")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"Fetching device serial from response : {device_serial_api}")
                username_api = response["username"]
                logger.debug(f"Fetching username from response : {username_api}")
                txn_id_api = response["txnId"]
                logger.debug(f"Fetching transaction id from response : {txn_id_api}")
                payment_card_brand_api = response["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response : {payment_card_brand_api}")
                payment_card_type_api = response["paymentCardType"]
                logger.debug(f"Fetching payment card type from response : {payment_card_type_api}")
                card_txn_type_api = response["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response : {card_txn_type_api}")
                batch_number_api = response["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                customer_name_api = response["customerName"]
                logger.debug(f"Fetching customer name from response : {customer_name_api}")
                external_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response : {external_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payer_name_api = response["payerName"]
                logger.debug(f"Fetching payer name from response : {payer_name_api}")
                payment_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {payment_card_bin_api}")
                name_on_card_api = response["nameOnCard"]
                logger.debug(f"Fetching name on card from response : {name_on_card_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Fetching display_PAN from response : {display_pan_api}")
                card_holder_currency_api = response["cardHolderCurrency"]
                logger.debug(f"fetching card_holder_currency_api from response : {card_holder_currency_api}")
                payment_gateway_api = response['paymentGateway']
                logger.debug(f"fetching payment_gateway_api from response : {payment_gateway_api}")

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
                    "customer_name": customer_name_api,
                    "external_ref": external_ref_number_api,
                    "merchant_name": merchant_name_api,
                    "payer_name": payer_name_api,
                    "pmt_card_bin": payment_card_bin_api,
                    "name_on_card": name_on_card_api,
                    "display_pan": display_pan_api,
                    "card_holder_currency": card_holder_currency_api,
                    "payment_gateway": payment_gateway_api,
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
                    "txn_amt": amount,
                    "acquirer_code": "AXIS",
                    "customer_name": "MC KWD ONL PIN",
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "mid": mid,
                    "tid": tid,
                    "payer_name": "MC KWD ONL PIN",
                    "pmt_card_bin": "222297",
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "pmt_mode": "CARD",
                    "pmt_gateway": "ATOS_TLE",
                    "settle_status": "PENDING",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "txn_type": "CHARGE",
                    "terminal_info_id": terminal_info_id,
                    "merchant_code": org_code,
                    "org_code": org_code,
                    "card_txn_type": "70",
                    "card_last_four_digit": "4143",
                    "dcc_amount": amount,
                    "dcc_conversion_amount": "{:,.2f}".format(converted_amount),
                    "dcc_conversion_rate": "0.52480573",
                    "dcc_card_holder_currency": "392",
                    "dcc_merchant_currency": "INR",
                    "dcc_status": "SUCCESS",
                    "dcc_payment_card_brand": "MASTER_CARD",
                    "dcc_markup_fee": "04.50",
                    "dcc_payment_card_bin": "222297",
                    "dcc_card_last_four_digit": "4143",
                    "dcc_mid": mid,
                    "dcc_tid": tid
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
                    "customer_name": customer_name_db,
                    "payer_name": payer_name_db,
                    "dcc_amount": dcc_amount_db,
                    "dcc_conversion_amount": dcc_converted_amount_db,
                    "dcc_conversion_rate": dcc_conversion_rate_db,
                    "dcc_card_holder_currency": dcc_card_holder_currency_db,
                    "dcc_merchant_currency": dcc_merchant_currency,
                    "dcc_status": dcc_status_db,
                    "dcc_payment_card_brand": dcc_payment_card_brand_db,
                    "dcc_markup_fee": dcc_markup_fee_db,
                    "dcc_payment_card_bin": dcc_payment_card_bin_db,
                    "dcc_card_last_four_digit": dcc_card_last_four_digit_db,
                    "dcc_mid": dcc_mid_db,
                    "dcc_tid": dcc_tid_db
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "MasterCard",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + "{:,}".format(amount) + ".00",
                    "AUTH CODE": auth_code.strip(),
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "SALE",
                    "BATCH NO": batch_number_db,
                    "TID": tid
                }
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
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_116_034():
    """
    Sub Feature Code: UI_Common_Card_Sale_AXIS_ATOS_TLE_Opt_Out_MC_ctls_USD_CreditCard_With_Online_Pin_556763
    Sub Feature Description: Performing the opt Out MC ctls USD sale transaction via AXIS_ATOS_TLE PG using Credit card
    with online pin  (bin:556763)
    TC naming code description: 100: Payment Method, 116: CARD_DCC, 034: TC034
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

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for query {query} : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = f"select * from terminal_info where org_code= '{org_code}' and status = 'ACTIVE' and " \
                "acquirer_code='AXIS' and payment_gateway='ATOS_TLE' "
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

        testsuite_teardown.revert_card_payment_settings_default(org_code=org_code, portal_un=portal_username, portal_pw=portal_password)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["fraudRulesEnabled"] = "true"
        api_details["RequestBody"]["settings"]["DEFAULT_BANK"] = "AXIS"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for setting preconditions :  {response}")

        query = f"select bank_code from bin_info where bin='556763'"
        logger.debug(f"Query to fetch bank_code from the bin_info table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        issuer_code = result["bank_code"].values[0]
        logger.debug(f"Fetching bank_code from the bin_info table : bank_code : {issuer_code}")

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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(driver=app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(username=app_username, password=app_password)
            home_page = HomePage(driver=app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(5000, 5900)
            converted_amount = amount * 0.52480573
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number_and_device_serial_for_card(amt=amount, order_number=order_id, device_serial=device_serial)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            logger.debug(f"Entered device_serial is : {device_serial}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed_card(amount=amount, order_id=order_id, device_serial=device_serial)
            payment_page.click_on_Card_paymentMode()
            logger.info("Selected payment mode is Card")
            card_page = CardPage(driver=app_driver)
            logger.debug(f"selecting the card type as : MC ctls USD")
            card_page.select_cardtype(text="MC ctls USD")
            logger.debug(f"selected the card type as : MC ctls USD")
            payment_page.select_currency_type_inr()
            inr_currency_rate = payment_page.fetch_inr_currency_value()
            payment_page.click_agree_and_pay()
            payment_page.click_on_proceed_homepage()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query=query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from txn table : {txn_id} ")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer code from txn table : {acquirer_code_db}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth code from txn table : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            customer_name_db = result["customer_name"].values[0]
            logger.debug(f"Fetching customer name from txn table : {customer_name_db}")
            device_serial_db = result["device_serial"].iloc[0]
            logger.debug(f"Fetching device serial from txn table : {device_serial_db}")
            order_id_db = result["external_ref"].iloc[0]
            logger.debug(f"Fetching order id from txn table : {order_id_db}")
            issuer_code_db = result["issuer_code"].iloc[0]
            logger.debug(f"Fetching issuer code from txn table : {issuer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            payer_name_db = result["payer_name"].values[0]
            logger.debug(f"Fetching payer name from txn table : {payer_name_db}")
            payment_card_bin_db = result["payment_card_bin"].iloc[0]
            logger.debug(f"Fetching card bin number from txn table : {payment_card_bin_db}")
            payment_card_brand_db = result["payment_card_brand"].iloc[0]
            logger.debug(f"Fetching payment card brand from txn table : {payment_card_brand_db}")
            payment_card_type_db = result["payment_card_type"].iloc[0]
            logger.debug(f"Fetching payment card type from txn table : {payment_card_type_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment mode from txn table : {payment_mode_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment gateway from txn table : {payment_gateway_db}")
            rrn = result["rr_number"].iloc[0]
            logger.debug(f"Fetching rrn from txn table : {rrn}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement status from txn table : {settlement_status_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Fetching payment status from txn table : {payment_status_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            txn_type_db = result["txn_type"].iloc[0]
            logger.debug(f"Fetching txn type from txn table : {txn_type_db}")
            terminal_info_id_db = result["terminal_info_id"].iloc[0]
            logger.debug(f"Fetching terminal info id from txn table : {terminal_info_id_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Fetching payment state from txn table : {payment_state_db}")
            merchant_code_db = result["merchant_code"].iloc[0]
            logger.debug(f"Fetching merchant code from txn table : {merchant_code_db}")
            batch_number_db = result["batch_number"].iloc[0]
            logger.debug(f"Fetching batch number from txn table : {batch_number_db}")
            org_code_db = result["org_code"].iloc[0]
            logger.debug(f"Fetching org code from txn table : {org_code_db}")
            card_txn_type_db = result["card_txn_type"].iloc[0]
            logger.debug(f"Fetching card txn type from txn table : {card_txn_type_db}")
            card_last_four_digit_db = result["card_last_four_digit"].iloc[0]
            logger.debug(f"Fetching card last four digit from txn table : {card_last_four_digit_db}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant name from txn table : {merchant_name}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")

            query = f"select * from txn_dcc where txn_id='{txn_id}'"
            logger.debug(f"Query to fetch data from txn_dcc table : {query}")
            result_dcc = DBProcessor.getValueFromDB(query=query)
            dcc_amount_db = result_dcc['amount'].values[0]
            logger.debug(f"Fetching amount from txn_dcc table : {dcc_amount_db}")
            dcc_converted_amount_db = result_dcc['converted_amount'].values[0]
            logger.debug(f"Fetching dcc_converted_amount_db from txn_dcc table : {dcc_converted_amount_db}")
            dcc_conversion_rate_db = result_dcc['conversion_rate'].values[0]
            logger.debug(f"Fetching dcc_converted_amount_db from txn_dcc table : {dcc_conversion_rate_db}")
            dcc_card_holder_currency_db = result_dcc['card_holder_currency'].values[0]
            logger.debug(f"Fetching dcc_card_holder_currency_db from txn_dcc table : {dcc_card_holder_currency_db}")
            dcc_merchant_currency = result_dcc['merchant_currency'].values[0]
            logger.debug(f"Fetching dcc_merchant_currency from txn_dcc table : {dcc_merchant_currency}")
            dcc_status_db = result_dcc['status'].values[0]
            logger.debug(f"Fetching dcc_status_db from txn_dcc table : {dcc_status_db}")
            dcc_payment_card_brand_db = result_dcc['payment_card_brand'].values[0]
            logger.debug(f"Fetching dcc_payment_card_brand_db from txn_dcc table : {dcc_payment_card_brand_db}")
            dcc_markup_fee_db = result_dcc['dcc_markup_fee'].values[0]
            logger.debug(f"Fetching dcc_markup_fee_db from txn_dcc table : {dcc_markup_fee_db}")
            dcc_payment_card_bin_db = result_dcc['payment_card_bin'].values[0]
            logger.debug(f"Fetching dcc_payment_card_bin_db from txn_dcc table : {dcc_payment_card_bin_db}")
            dcc_card_last_four_digit_db = result_dcc['card_last_four_digit'].values[0]
            logger.debug(f"Fetching dcc_card_last_four_digit_db from txn_dcc table : {dcc_card_last_four_digit_db}")
            dcc_mid_db = result_dcc['dcc_mid'].values[0]
            logger.debug(f"Fetching dcc_mid_db from txn_dcc table : {dcc_mid_db}")
            dcc_tid_db = result_dcc['dcc_tid'].values[0]
            logger.debug(f"Fetching dcc_tid_db from txn_dcc table : {dcc_tid_db}")

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
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "AUTHORIZED",
                    "rrn": str(rrn),
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time_app,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number_db,
                    "card_type_desc": "*7401 CTLS",
                    "opted_type": "No",
                    "local_card": "No",
                    "inr_currency_rate": "INR " + str(amount) + ".0"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(driver=app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.debug(f"Fetching txn amount from txn history for the txn : {app_amount}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching payment mode from txn history for the txn : {payment_mode}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching status from txn history for the txn : {payment_status}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.debug(f"Fetching txn order_id from txn history for the txn : {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching txn payment msg from txn history for the txn : {app_payment_msg}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {app_txn_id}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.debug(f"Fetching date_time from txn history for the txn : {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching txn settlement_status from txn history for the txn : {app_settlement_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.debug(f"Fetching AUTH CODE from txn history for the txn : {app_auth_code}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.debug(
                    f"Fetching device serial number from txn history for the txn : {app_device_serial}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.debug(f"Fetching mid from txn history for the txn : {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.debug(f"Fetching tid from txn history for the txn : {app_tid}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn_number from txn history for the txn : {app_rrn}")
                app_batch_number = txn_history_page.fetch_batch_number_text()
                logger.debug(f"Fetching batch number for the txn : {app_batch_number}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.debug(f"Fetching card type desc for the txn : {app_card_type_desc}")
                app_opted_dcc = txn_history_page.fetch_opted_dcc_text()
                logger.debug(f"Fetching opted card type for the txn : {app_opted_dcc}")
                app_local_card = txn_history_page.fetch_local_card_text()
                logger.debug(f"Fetching app local card for the txn : {app_local_card}")

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
                    "opted_type": app_opted_dcc,
                    "local_card": app_local_card,
                    "inr_currency_rate": inr_currency_rate
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
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "CARD",
                    "pmt_state": "AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "PENDING",
                    "acquirer_code": "AXIS",
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
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "card_txn_type": "CTLS",
                    "batch_number": batch_number_db,
                    "card_last_four_digit": "7401",
                    "external_ref": order_id,
                    "merchant_name": merchant_name,
                    "pmt_card_bin": "556763",
                    "display_pan": "7401",
                    "card_holder_currency": "JPY",
                    "payment_gateway": "ATOS_TLE"

                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Fetching status from response : {status_api}")

                amount_api = float(response["amount"])
                logger.debug(f"Fetching amount from response : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching payment mode from response : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Fetching state from response : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Fetching rrn from response : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching settlement status from response : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching issuer code from response : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching acquirer code from response : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching org code from response : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Fetching mid from response : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Fetching tid from response : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching transaction type from response : {txn_type_api}")
                auth_code_api = response["authCode"]
                logger.debug(f"Fetching auth code from response : {auth_code_api}")
                date_and_time_api = response["createdTime"]
                logger.debug(f"Fetching date and time from response : {date_and_time_api}")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"Fetching device serial from response : {device_serial_api}")
                username_api = response["username"]
                logger.debug(f"Fetching username from response : {username_api}")
                txn_id_api = response["txnId"]
                logger.debug(f"Fetching transaction id from response : {txn_id_api}")
                payment_card_brand_api = response["paymentCardBrand"]
                logger.debug(f"Fetching payment card brand from response : {payment_card_brand_api}")
                payment_card_type_api = response["paymentCardType"]
                logger.debug(f"Fetching payment card type from response : {payment_card_type_api}")
                card_txn_type_api = response["cardTxnTypeDesc"]
                logger.debug(f"Fetching card txn type from response : {card_txn_type_api}")
                batch_number_api = response["batchNumber"]
                logger.debug(f"Fetching batch number from response : {batch_number_api}")
                card_last_four_digit_api = response["cardLastFourDigit"]
                logger.debug(f"Fetching card last four digit from response : {card_last_four_digit_api}")
                external_ref_number_api = response["externalRefNumber"]
                logger.debug(f"Fetching external ref number from response : {external_ref_number_api}")
                merchant_name_api = response["merchantName"]
                logger.debug(f"Fetching merchant name from response : {merchant_name_api}")
                payment_card_bin_api = response["paymentCardBin"]
                logger.debug(f"Fetching payment card bin from response : {payment_card_bin_api}")
                display_pan_api = response["displayPAN"]
                logger.debug(f"Fetching display_PAN from response : {display_pan_api}")
                card_holder_currency_api = response["cardHolderCurrency"]
                logger.debug(f"fetching card_holder_currency_api from response : {card_holder_currency_api}")
                payment_gateway_api = response['paymentGateway']
                logger.debug(f"fetching payment_gateway_api from response : {payment_gateway_api}")

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
                    "card_holder_currency": card_holder_currency_api,
                    "payment_gateway": payment_gateway_api,
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
                    "txn_amt": amount,
                    "acquirer_code": "AXIS",
                    "device_serial": device_serial,
                    "order_id": order_id,
                    "issuer_code": issuer_code,
                    "mid": mid,
                    "tid": tid,
                    "pmt_card_bin": "556763",
                    "pmt_card_brand": "MASTER_CARD",
                    "pmt_card_type": "CREDIT",
                    "pmt_mode": "CARD",
                    "pmt_gateway": "ATOS_TLE",
                    "settle_status": "PENDING",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "AUTHORIZED",
                    "txn_type": "CHARGE",
                    "terminal_info_id": terminal_info_id,
                    "merchant_code": org_code,
                    "org_code": org_code,
                    "card_txn_type": "91",
                    "card_last_four_digit": "7401",
                    "dcc_amount": amount,
                    "dcc_conversion_amount": "{:,.2f}".format(converted_amount),
                    "dcc_conversion_rate": "0.52480573",
                    "dcc_card_holder_currency": "392",
                    "dcc_merchant_currency": "INR",
                    "dcc_status": "SUCCESS",
                    "dcc_payment_card_brand": "MASTER_CARD",
                    "dcc_markup_fee": "04.50",
                    "dcc_payment_card_bin": "556763",
                    "dcc_card_last_four_digit": "7401",
                    "dcc_mid": mid,
                    "dcc_tid": tid
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
                    "dcc_amount": dcc_amount_db,
                    "dcc_conversion_amount": dcc_converted_amount_db,
                    "dcc_conversion_rate": dcc_conversion_rate_db,
                    "dcc_card_holder_currency": dcc_card_holder_currency_db,
                    "dcc_merchant_currency": dcc_merchant_currency,
                    "dcc_status": dcc_status_db,
                    "dcc_payment_card_brand": dcc_payment_card_brand_db,
                    "dcc_markup_fee": dcc_markup_fee_db,
                    "dcc_payment_card_bin": dcc_payment_card_bin_db,
                    "dcc_card_last_four_digit": dcc_card_last_four_digit_db,
                    "dcc_mid": dcc_mid_db,
                    "dcc_tid": dcc_tid_db
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                expected_charge_slip_values = {
                    "CARD TYPE": "MasterCard",
                    "merchant_ref_no": "Ref # " + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + "{:,}".format(amount) + ".00",
                    "AUTH CODE": auth_code.strip(),
                    "date": txn_date,
                    "time": txn_time,
                    "payment_option": "SALE",
                    "BATCH NO": batch_number_db,
                    "TID": tid
                }
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
        Configuration.executeFinallyBlock(testcase_id)
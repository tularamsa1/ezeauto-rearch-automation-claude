import time
import pytest
import random
import string
import sys
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.sa.app_card_page import CardPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, receipt_validator, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_500_503_052():
    """
        Sub Feature Code: UI_Common_P2P_Card_Start_API_PreAuth_Partial_Confirm_Success_Txn_From_Device
        Sub Feature Description: Send pre_auth notification from start api and perform the partial confirm success txn
        TC naming code description: 500: P2P, 503: P2P_Card, 052: TC 052
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch data from org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Value of org_code from org_employee table : {org_code}")

        query = "select * from app_key where org_code ='" + str(org_code) + "'"
        logger.debug(f"Query to fetch data from app_key table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from app_key table : {result}")
        app_key = result['app_key'].values[0]
        logger.debug(f"Value of app_key from app_key table : {app_key}")

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch data from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from terminal_info table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Value of mid from terminal_info table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Value of tid from terminal_info table : {tid}")

        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = ("select sett.setting_value from setting sett LEFT JOIN org_employee "
                 "empl on empl.id=sett.entity_id where empl.username ='") + str(
            app_username) + "'and sett.setting_name='onlyP2PUser';"
        logger.debug(f"Query to fetch setting_value from the DB for the user {app_username}: {query}")
        result = DBProcessor.getValueFromDB(query)

        if (len(result)) >= 1:
            # If current app_user is onlyP2P allowed user
            current_setting_val = result['setting_value'].values[0]
            logger.debug(f"Query result, 'onlyP2PUser' setting_value of {app_username}: {current_setting_val}")
            if current_setting_val == "true":
                logger.info(f"Current app user is only P2P allowed user")
            else:
                logger.error(f"Current app user can do normal transactions as well")
        else:
            logger.error(f"Current app user can do normal transactions as well")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, commx_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"Loaded on home page")

            device_serial = GlobalVariables.str_device_id
            logger.info(f"Device_serial value is {device_serial}")

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification")
            try:
                actual_notification = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.info(f"P2P notification message on device is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device. Actual notification: {actual_notification}")

            app_driver.back()

            amount = random.randint(200, 500)
            logger.info(f"Randomly generated amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Randomly generated order_id is: {order_id}")
            ext_ref_number = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Randomly generated ext_ref_number is: {ext_ref_number}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "txnType": "PRE_AUTH",
                "customerMobileNumber": "8553641330",
                "customerEmail": "ranjitha.d@ezetap.com",
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start}")
            request_id = resp_start['p2pRequestId']
            logger.debug(f"Value of request_id from P2P start API is : {request_id}")
            start_success = resp_start['success']
            logger.debug(f"Value of success from P2P start API is : {start_success}")

            time.sleep(2)

            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype("CTLS_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : CTLS_VISA_CREDIT_417666")
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on txn popup for preauth")

            query = (f"select * from txn where org_code='{org_code}' and payment_mode='CARD'"
                     f" and device_serial='{device_serial}' and external_ref='{order_id}' "
                     f"order by created_time desc limit 1 ;")
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            preauth_txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id value from the txn table : {preauth_txn_id}")

            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_back_btn_in_enter_amt_window()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=preauth_txn_id)
            txn_history_page.click_on_confirm_pre_auth()
            logger.debug(f"Clicked on confirm pre_auth button")

            pre_auth_amt = amount - 100
            logger.debug(f"Pre_auth amount for confirmation is : {pre_auth_amt}")
            txn_history_page.click_on_confirmation_btn_for_amt(pre_auth_amt)
            logger.debug(f"Entered the confirm pre_auth amount : {pre_auth_amt}")
            card_page = CardPage(app_driver)
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on confirm pre_auth popup")

            query = (f"select * from txn where org_code='{org_code}' and"
                     f" payment_mode='CARD' and device_serial='{device_serial}'"
                     f" and external_ref='{order_id}' order by created_time desc limit 1 ;")
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching original txn_id value from the txn table : {original_txn_id}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id value from the txn table : {txn_id}")

            query = f"select * from txn where id='{original_txn_id}';"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth for first txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth for first txn : {result}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table after confirm pre_auth for first txn : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table after confirm pre_auth for first txn : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table after confirm pre_auth for first txn : {batch_number}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from the txn table after confirm pre_auth for first txn : {posting_date}")

            payment_status = txn_history_page.fetch_txn_status_text()
            logger.info(f"Fetching payment status value from txn history for the txn : {original_txn_id}, {payment_status}")
            payment_mode = txn_history_page.fetch_txn_type_text()
            logger.info(f"Fetching payment mode value from txn history for the txn : {original_txn_id}, {payment_mode}")
            app_txn_id = txn_history_page.fetch_txn_id_text()
            logger.info(f"Fetching txn_id value from txn history for the txn : {original_txn_id}, {app_txn_id}")
            app_amount = txn_history_page.fetch_txn_amount_text()
            logger.info(f"Fetching amount value from txn history for the txn : {original_txn_id}, {app_amount}")
            app_settlement_status = txn_history_page.fetch_settlement_status_text()
            logger.info(f"Fetching settlement status value from txn history for the txn : {original_txn_id}, {app_settlement_status}")
            app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
            logger.info(f"Fetching payment msg value from txn history for the txn : {original_txn_id}, {app_payment_msg}")
            app_date_and_time = txn_history_page.fetch_date_time_text()
            logger.info(f"Fetching date and time value from txn history for the txn : {original_txn_id}, {app_date_and_time}")
            app_rrn = txn_history_page.fetch_RRN_text()
            logger.info(f"Fetching rrn value from txn history for the txn : {original_txn_id}, {app_rrn}")
            app_auth_code = txn_history_page.fetch_auth_code_text()
            logger.info(f"Fetching auth_cde value from txn history for the txn : {original_txn_id}, {app_auth_code}")
            app_batch_no = txn_history_page.fetch_batch_number_text()
            logger.info(f"Fetching batch number value from txn history for the txn : {original_txn_id}, {app_batch_no}")
            app_device_serial = txn_history_page.fetch_device_serial_text()
            logger.info(f"Fetching device serial from txn history for the txn : {original_txn_id}, {app_device_serial}")
            app_order_id = txn_history_page.fetch_order_id_text()
            logger.info(f"Fetching txn order id value from txn history for the txn : {original_txn_id}, {app_order_id}")
            app_mid = txn_history_page.fetch_mid_text()
            logger.info(f"Fetching mid value from txn history for the txn : {original_txn_id}, {app_mid}")
            app_tid = txn_history_page.fetch_tid_text()
            logger.info(f"Fetching tid value from txn history for the txn : {original_txn_id}, {app_tid}")
            app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
            logger.info(f"Fetching card type value from txn history for the txn : {original_txn_id}, {app_card_type_desc}")

            query = f"select * from txn where id='{txn_id}' ;"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth for second txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth for second txn : {result}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table after confirm pre_auth for second txn : {rrn_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table after confirm pre_auth for second txn : {auth_code_2}")
            batch_number_2 = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table after confirm pre_auth for second txn : {batch_number_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from the txn table after confirm pre_auth for second txn : {posting_date_2}")

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
                date_and_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                date_and_time_2 = date_time_converter.to_app_format(posting_date_db=posting_date_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": original_txn_id,
                    "pmt_status": "CNF_PRE_AUTH",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number,
                    "card_type_desc": "*0018 CTLS",

                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:,.2f}".format(pre_auth_amt),
                    "settle_status_2": "PENDING",
                    "txn_id_2": txn_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    "rr_number_2": rrn_2,
                    "auth_code_2": auth_code_2,
                    "device_serial_2": device_serial,
                    "batch_number_2": batch_number_2,
                    "order_id_2": order_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "card_type_desc_2": "*0018 CTLS"
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver.back()
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment status value from txn history for the txn : {txn_id}, {payment_status_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode value from txn history for the txn : {txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id value from txn history for the txn : {txn_id}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching amount value from txn history for the txn : {txn_id}, {app_amount_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status value from txn history for the txn : {txn_id}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching payment msg value from txn history for the txn : {txn_id}, {app_payment_msg_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time value from txn history for the txn : {txn_id}, {app_date_and_time_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn value from txn history for the txn : {txn_id}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_cde value from txn history for the txn : {txn_id}, {app_auth_code_2}")
                app_batch_no_2 = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch number value from txn history for the txn : {txn_id}, {app_batch_no_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the txn : {txn_id}, {app_device_serial_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id value from txn history for the txn : {txn_id}, {app_order_id_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid value from txn history for the txn : {txn_id}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid value from txn history for the txn : {txn_id}, {app_tid_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card type value from txn history for the txn : {txn_id}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_no,
                    "card_type_desc": app_card_type_desc,

                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "settle_status_2": app_settlement_status_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "date_2": app_date_and_time_2,
                    "rr_number_2": app_rrn_2,
                    "auth_code_2": app_auth_code_2,
                    "device_serial_2": app_device_serial_2,
                    "batch_number_2": app_batch_no_2,
                    "order_id_2": app_order_id_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "card_type_desc_2": app_card_type_desc_2
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(posting_date_db=posting_date_2)
                expected_charge_slip_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'BATCH NO': batch_number, 'CARD TYPE': 'VISA',
                    'payment_option': 'SALE', 'TID': tid,
                    'time': txn_time, 'AUTH CODE': str(auth_code)
                }
                chargeslip_val_result = receipt_validator.perform_charge_slip_validations(original_txn_id,
                       {"username": app_username,"password": app_password},expected_charge_slip_values)

                expected_charge_slip_values_2 = {
                    'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(pre_auth_amt) + ".00", 'date': txn_date_2,
                    'BATCH NO': batch_number, 'CARD TYPE': 'VISA',
                    'payment_option': 'SALE', 'TID': tid,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_2)
                }

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id,
                     {"username": app_username,"password": app_password}, expected_charge_slip_values_2)

                if chargeslip_val_result and chargeslip_val_result_2:
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
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_500_503_053():
    """
        Sub Feature Code: UI_Common_P2P_Card_Start_API_PreAuth_Full_Confirm_Success_Txn_From_Device
        Sub Feature Description: Send pre_auth notification from start api and perform the full confirm success txn
        TC naming code description: 500: P2P, 503: P2P_Card, 053: TC 053
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch data from org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Value of org_code from org_employee table : {org_code}")

        query = "select * from app_key where org_code ='" + str(org_code) + "'"
        logger.debug(f"Query to fetch data from app_key table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from app_key table : {result}")
        app_key = result['app_key'].values[0]
        logger.debug(f"Value of app_key from app_key table : {app_key}")

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch data from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from terminal_info table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Value of mid from terminal_info table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Value of tid from terminal_info table : {tid}")

        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = ("select sett.setting_value from setting sett LEFT JOIN org_employee empl"
                 " on empl.id=sett.entity_id where empl.username ='") + str(
            app_username) + "'and sett.setting_name='onlyP2PUser';"
        logger.debug(f"Query to fetch setting_value from the DB for the user {app_username}: {query}")
        result = DBProcessor.getValueFromDB(query)

        if (len(result)) >= 1:
            # If current app_user is onlyP2P allowed user
            current_setting_val = result['setting_value'].values[0]
            logger.debug(f"Query result, 'onlyP2PUser' setting_value of {app_username}: {current_setting_val}")
            if current_setting_val == "true":
                logger.info(f"Current app user is only P2P allowed user")
            else:
                logger.error(f"Current app user can do normal transactions as well")
        else:
            logger.error(f"Current app user can do normal transactions as well")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, commx_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"Loaded on home page")

            device_serial = GlobalVariables.str_device_id
            logger.info(f"Device_serial value is : {device_serial}")

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification")
            try:
                actual_notification = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.info(f"P2P notification message on device is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device. Actual notification: {actual_notification}")

            app_driver.back()

            amount = random.randint(200, 500)
            logger.info(f"Randomly generated amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Randomly generated order_id is: {order_id}")
            ext_ref_number = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Randomly generated ext_ref_number is: {ext_ref_number}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "txnType": "PRE_AUTH",
                "customerMobileNumber": "8553641330",
                "customerEmail": "ranjitha.d@ezetap.com",
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start}")
            request_id = resp_start['p2pRequestId']
            logger.debug(f"Value of request_id from P2P start API is : {request_id}")
            start_success = resp_start['success']
            logger.debug(f"Value of success from P2P start API is : {start_success}")

            time.sleep(2)

            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype("CTLS_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : CTLS_VISA_CREDIT_417666")
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on txn popup for preauth")

            query = (f"select * from txn where org_code='{org_code}' and payment_mode='CARD'"
                     f" and device_serial='{device_serial}' and external_ref='{order_id}' order by created_time desc limit 1 ;")
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from txn table : {result}")
            preauth_txn_id = result['id'].values[0]
            logger.debug(f"Fetching preauth_txn_id value from the txn table : {preauth_txn_id}")

            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_back_btn_in_enter_amt_window()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=preauth_txn_id)
            txn_history_page.click_on_confirm_pre_auth()
            logger.debug(f"Clicked on confirm pre_auth button")

            logger.debug(f"Pre_auth amount for confirmation is : {amount}")
            txn_history_page.click_on_confirmation_btn_for_amt(amount)
            logger.debug(f"Entered the confirm pre_auth amount is : {amount}")
            card_page = CardPage(app_driver)
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on confirm pre_auth popup")

            query = (f"select * from txn where org_code='{org_code}' and"
                     f" payment_mode='CARD' and device_serial='{device_serial}'"
                     f" and external_ref='{order_id}' order by created_time desc limit 1 ;")
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from txn table : {result}")
            original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"Fetching original txn_id value from the txn table : {original_txn_id}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id value from the txn table : {txn_id}")

            query = f"select * from txn where id='{original_txn_id}';"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth for first txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth for first txn : {result}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table after confirm pre_auth for first txn : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table after confirm pre_auth for first txn : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table after confirm pre_auth for first txn : {batch_number}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from the txn table after confirm pre_auth for first txn : {posting_date}")

            payment_status = txn_history_page.fetch_txn_status_text()
            logger.info(f"Fetching payment status value from txn history for the txn : {original_txn_id}, {payment_status}")
            payment_mode = txn_history_page.fetch_txn_type_text()
            logger.info(f"Fetching payment mode value from txn history for the txn : {original_txn_id}, {payment_mode}")
            app_txn_id = txn_history_page.fetch_txn_id_text()
            logger.info(f"Fetching txn_id value from txn history for the txn : {original_txn_id}, {app_txn_id}")
            app_amount = txn_history_page.fetch_txn_amount_text()
            logger.info(f"Fetching amount value from txn history for the txn : {original_txn_id}, {app_amount}")
            app_settlement_status = txn_history_page.fetch_settlement_status_text()
            logger.info(f"Fetching settlement status value from txn history for the txn : {original_txn_id}, {app_settlement_status}")
            app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
            logger.info(f"Fetching payment msg value from txn history for the txn : {original_txn_id}, {app_payment_msg}")
            app_date_and_time = txn_history_page.fetch_date_time_text()
            logger.info(f"Fetching date and time value from txn history for the txn : {original_txn_id}, {app_date_and_time}")
            app_rrn = txn_history_page.fetch_RRN_text()
            logger.info(f"Fetching rrn value from txn history for the txn : {original_txn_id}, {app_rrn}")
            app_auth_code = txn_history_page.fetch_auth_code_text()
            logger.info(f"Fetching auth_cde value from txn history for the txn : {original_txn_id}, {app_auth_code}")
            app_batch_no = txn_history_page.fetch_batch_number_text()
            logger.info(f"Fetching batch number value from txn history for the txn : {original_txn_id}, {app_batch_no}")
            app_device_serial = txn_history_page.fetch_device_serial_text()
            logger.info(f"Fetching device serial from txn history for the txn : {original_txn_id}, {app_device_serial}")
            app_order_id = txn_history_page.fetch_order_id_text()
            logger.info(f"Fetching txn order id value from txn history for the txn : {original_txn_id}, {app_order_id}")
            app_mid = txn_history_page.fetch_mid_text()
            logger.info(f"Fetching mid value from txn history for the txn : {original_txn_id}, {app_mid}")
            app_tid = txn_history_page.fetch_tid_text()
            logger.info(f"Fetching tid value from txn history for the txn : {original_txn_id}, {app_tid}")
            app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
            logger.info(f"Fetching card type value from txn history for the txn : {original_txn_id}, {app_card_type_desc}")

            query = f"select * from txn where id='{txn_id}' ;"
            logger.debug(f"Query to fetch data from the txn table after confirm pre_auth for second txn : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for txn table after confirm pre_auth for second txn : {result}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table after confirm pre_auth for second txn : {rrn_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table after confirm pre_auth for second txn : {auth_code_2}")
            batch_number_2 = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table after confirm pre_auth for second txn : {batch_number_2}")
            posting_date_2 = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date value from the txn table after confirm pre_auth for second txn : {posting_date_2}")

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
                date_and_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                date_and_time_2 = date_time_converter.to_app_format(posting_date_db=posting_date_2)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": original_txn_id,
                    "pmt_status": "CNF_PRE_AUTH",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number,
                    "card_type_desc": "*0018 CTLS",

                    "pmt_mode_2": "CARD",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "settle_status_2": "PENDING",
                    "txn_id_2": txn_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    "rr_number_2": rrn_2,
                    "auth_code_2": auth_code_2,
                    "device_serial_2": device_serial,
                    "batch_number_2": batch_number_2,
                    "order_id_2": order_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "card_type_desc_2": "*0018 CTLS"
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver.back()
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment status value from txn history for the txn : {txn_id}, {payment_status_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode value from txn history for the txn : {txn_id}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id value from txn history for the txn : {txn_id}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching amount value from txn history for the txn : {txn_id}, {app_amount_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status value from txn history for the txn : {txn_id}, {app_settlement_status_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching payment msg value from txn history for the txn : {txn_id}, {app_payment_msg_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time value from txn history for the txn : {txn_id}, {app_date_and_time_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn value from txn history for the txn : {txn_id}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_cde value from txn history for the txn : {txn_id}, {app_auth_code_2}")
                app_batch_no_2 = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch number value from txn history for the txn : {txn_id}, {app_batch_no_2}")
                app_device_serial_2 = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the txn : {txn_id}, {app_device_serial_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id value from txn history for the txn : {txn_id}, {app_order_id_2}")
                app_mid_2 = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid value from txn history for the txn : {txn_id}, {app_mid_2}")
                app_tid_2 = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid value from txn history for the txn : {txn_id}, {app_tid_2}")
                app_card_type_desc_2 = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card type value from txn history for the txn : {txn_id}, {app_card_type_desc_2}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_no,
                    "card_type_desc": app_card_type_desc,

                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "settle_status_2": app_settlement_status_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "date_2": app_date_and_time_2,
                    "rr_number_2": app_rrn_2,
                    "auth_code_2": app_auth_code_2,
                    "device_serial_2": app_device_serial_2,
                    "batch_number_2": app_batch_no_2,
                    "order_id_2": app_order_id_2,
                    "mid_2": app_mid_2,
                    "tid_2": app_tid_2,
                    "card_type_desc_2": app_card_type_desc_2
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(posting_date_db=posting_date_2)
                expected_charge_slip_values = {
                    'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'BATCH NO': batch_number, 'CARD TYPE': 'VISA',
                    'payment_option': 'SALE', 'TID': tid,
                    'time': txn_time, 'AUTH CODE': str(auth_code)
                }
                chargeslip_val_result = receipt_validator.perform_charge_slip_validations(original_txn_id,
                    {"username": app_username,"password": app_password}, expected_charge_slip_values)

                expected_charge_slip_values_2 = {
                    'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'BATCH NO': batch_number, 'CARD TYPE': 'VISA',
                    'payment_option': 'SALE', 'TID': tid,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_2)
                }

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id,
                     {"username": app_username, "password": app_password},expected_charge_slip_values_2)

                if chargeslip_val_result and chargeslip_val_result_2:
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
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_500_503_054():
    """
        Sub Feature Code: UI_Common_P2P_Card_Start_API_PreAuth_Release_Txn_From_Device
        Sub Feature Description: Send pre_auth notification from start api and perform the release txn
        TC naming code description: 500: P2P, 503: P2P_Card, 054: TC 054
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch data from org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Value of org_code from org_employee table : {org_code}")

        query = "select * from app_key where org_code ='" + str(org_code) + "'"
        logger.debug(f"Query to fetch data from app_key table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from app_key table : {result}")
        app_key = result['app_key'].values[0]
        logger.debug(f"Value of app_key from app_key table : {app_key}")

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch data from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from terminal_info table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Value of mid from terminal_info table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Value of tid from terminal_info table : {tid}")

        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = ("select sett.setting_value from setting sett LEFT JOIN org_employee empl "
                 "on empl.id=sett.entity_id where empl.username ='") + str(
            app_username) + "'and sett.setting_name='onlyP2PUser';"
        logger.debug(f"Query to fetch setting_value from the DB for the user {app_username}: {query}")
        result = DBProcessor.getValueFromDB(query)

        if (len(result)) >= 1:
            # If current app_user is onlyP2P allowed user
            current_setting_val = result['setting_value'].values[0]
            logger.debug(f"Query result, 'onlyP2PUser' setting_value of {app_username}: {current_setting_val}")
            if current_setting_val == "true":
                logger.info(f"Current app user is only P2P allowed user")
            else:
                logger.error(f"Current app user can do normal transactions as well")
        else:
            logger.error(f"Current app user can do normal transactions as well")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, commx_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"Loaded on home page")

            device_serial = GlobalVariables.str_device_id
            logger.info(f"Device_serial value is : {device_serial}")

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification")
            try:
                actual_notification = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.info(f"P2P notification message on device is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device. Actual notification: {actual_notification}")

            app_driver.back()

            amount = random.randint(200, 500)
            logger.info(f"Randomly generated amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Randomly generated order_id is: {order_id}")
            ext_ref_number = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.info(f"Randomly generated ext_ref_number is: {ext_ref_number}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "txnType": "PRE_AUTH",
                "customerMobileNumber": "8553641330",
                "customerEmail": "ranjitha.d@ezetap.com",
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for P2P start API is : {resp_start}")
            request_id = resp_start['p2pRequestId']
            logger.debug(f"Value of request_id from P2P start API is : {request_id}")
            start_success = resp_start['success']
            logger.debug(f"Value of success from P2P start API is : {start_success}")

            time.sleep(2)

            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype("CTLS_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : CTLS_VISA_CREDIT_417666")
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on txn popup for preauth")

            query = (f"select * from txn where org_code='{org_code}' and payment_mode='CARD'"
                     f" and device_serial='{device_serial}' and external_ref='{order_id}' order by created_time desc limit 1 ;")
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            preauth_txn_id = result['id'].values[0]
            logger.debug(f"Fetching preauth_txn_id value from the txn table : {preauth_txn_id}")

            payment_page = PaymentPage(driver=app_driver)
            payment_page.click_on_back_btn_in_enter_amt_window()
            home_page.click_on_history()
            txn_history_page = TransHistoryPage(app_driver)
            txn_history_page.click_on_transaction_by_txn_id(txn_id=preauth_txn_id)
            txn_history_page.click_on_release_pre_auth()
            logger.debug(f"Clicked on release pre_auth button")
            txn_history_page.click_on_conf_pre_auth_popup()
            logger.debug(f"Clicked on confirm pre_auth popup")

            query = (f"select * from txn where org_code='{org_code}' and "
                     f"payment_mode='CARD' and device_serial='{device_serial}' and"
                     f" external_ref='{order_id}' order by created_time desc limit 1 ;")
            logger.debug(f"Query to fetch data from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table : {result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id value from the txn table : {txn_id}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code}")
            batch_number = result['batch_number'].values[0]
            logger.debug(f"Fetching batch_number value from the txn table : {batch_number}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")

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
                date_and_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                expected_app_values = {
                    "txn_amt": "{:,.2f}".format(amount),
                    "pmt_mode": "CARD",
                    "txn_id": txn_id,
                    "pmt_status": "REL_PRE_AUTH",
                    "rr_number": rrn,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "settle_status": "PENDING",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "device_serial": device_serial,
                    "mid": mid,
                    "tid": tid,
                    "batch_number": batch_number,
                    "card_type_desc": "*0018 CTLS",
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment status value from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode value from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id value from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching amount value from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement status value from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching payment msg value from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date and time value from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn value from txn history for the txn : {txn_id}, {app_rrn}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_cde value from txn history for the txn : {txn_id}, {app_auth_code}")
                app_batch_no = txn_history_page.fetch_batch_number_text()
                logger.info(f"Fetching batch number value from txn history for the txn : {txn_id}, {app_batch_no}")
                app_device_serial = txn_history_page.fetch_device_serial_text()
                logger.info(f"Fetching device serial from txn history for the txn : {txn_id}, {app_device_serial}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order id value from txn history for the txn : {txn_id}, {app_order_id}")
                app_mid = txn_history_page.fetch_mid_text()
                logger.info(f"Fetching mid value from txn history for the txn : {txn_id}, {app_mid}")
                app_tid = txn_history_page.fetch_tid_text()
                logger.info(f"Fetching tid value from txn history for the txn : {txn_id}, {app_tid}")
                app_card_type_desc = txn_history_page.fetch_card_type_desc_text()
                logger.info(f"Fetching card type value from txn history for the txn : {txn_id}, {app_card_type_desc}")

                actual_app_values = {
                    "txn_amt": app_amount.split(' ')[1],
                    "pmt_mode": payment_mode,
                    "txn_id": app_txn_id,
                    "pmt_status": payment_status.split(':')[1],
                    "rr_number": app_rrn,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "settle_status": app_settlement_status,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "device_serial": app_device_serial,
                    "mid": app_mid,
                    "tid": app_tid,
                    "batch_number": app_batch_no,
                    "card_type_desc": app_card_type_desc
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_500_503_055():
    """
        Sub Feature Code: UI_Common_P2P_Card_Disconnect_Wifi_Start_API_Two_PreAuth_Request_From_Device_Cancel_First_Request
        Sub Feature Description: Disconnect the wifi from the device, trigger two pre_auth requests and reconnect the device with wifi
        cancel the first pre_auth request and check the second preauth pop up
        TC naming code description: 500: P2P, 503: P2P_Card, 055: TC 055
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch data from org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Value of org_code from org_employee table : {org_code}")

        query = "select * from app_key where org_code ='" + str(org_code) + "'"
        logger.debug(f"Query to fetch data from app_key table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from app_key table : {result}")
        app_key = result['app_key'].values[0]
        logger.debug(f"Value of app_key from app_key table : {app_key}")

        query = "select * from terminal_info where org_code='" + str(
            org_code) + "' and payment_gateway ='HDFC' and acquirer_code = 'HDFC' and status='ACTIVE';"
        logger.debug(f"Query to fetch data from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result from terminal_info table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Value of mid from terminal_info table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Value of tid from terminal_info table : {tid}")

        testsuite_teardown.revert_p2p_settings(portal_username, portal_password, app_username, app_password, org_code)

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = ("select sett.setting_value from setting sett LEFT JOIN org_employee "
                 "empl on empl.id=sett.entity_id where empl.username ='") + str(
            app_username) + "'and sett.setting_name='onlyP2PUser';"
        logger.debug(f"Query to fetch setting_value from the DB for the user {app_username}: {query}")
        result = DBProcessor.getValueFromDB(query)

        if (len(result)) >= 1:
            # If current app_user is onlyP2P allowed user
            current_setting_val = result['setting_value'].values[0]
            logger.debug(f"Query result, 'onlyP2PUser' setting_value of {app_username}: {current_setting_val}")
            if current_setting_val == "true":
                logger.info(f"Current app user is only P2P allowed user")
            else:
                logger.error(f"Current app user can do normal transactions as well")
        else:
            logger.error(f"Current app user can do normal transactions as well")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, commx_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id, "true")
            login_page = LoginPage(app_driver)
            login_page.perform_login_for_pax(app_username, app_password, Pax_Device=True)
            logger.info(f"Logged into MPOSX application using username : {app_username} and password : {app_password}")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"Loaded on home page")

            device_serial = GlobalVariables.str_device_id
            logger.info(f"Device_serial value is : {device_serial}")

            # Checking redis connection
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification")
            try:
                actual_notification = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device")
            expected_notification = "Push 2 Pay is ON"
            logger.info(f"Expected P2P notification message is : {expected_notification}")

            if actual_notification == expected_notification:
                logger.info(f"P2P notification message on device is as expected")
            else:
                app_driver.back()
                raise Exception(f"P2P notification mismatch on device. Actual notification: {actual_notification}")

            app_driver.back()

            amount = random.randint(100, 200)
            logger.debug(f"randomly generated value for amount_2 is : {amount}")
            ext_ref_number = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.debug(f"randomly generated value for external reference number is : {ext_ref_number}")
            push_to = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "txnType": "PRE_AUTH",
                "customerMobileNumber": "8553641330",
                "customerEmail": "ranjitha.d@ezetap.com",
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response for first notification is : {resp_start}")
            start_p2p_request_id = resp_start['p2pRequestId']
            logger.debug(f"Value of request_id from first notification is : {start_p2p_request_id}")
            start_success = resp_start['success']
            logger.debug(f"Value of success from first notification is : {start_success}")
            time.sleep(2)

            #Second notification
            amount_2 = random.randint(100, 200)
            logger.debug(f"randomly generated value for amount_2 is : {amount_2}")
            ext_ref_number_2 = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            logger.debug(f"randomly generated value for ext_ref_number_2 is : {ext_ref_number_2}")
            push_to_2 = {"deviceId": "" + device_serial + "|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount_2,
                "txnType": "PRE_AUTH",
                "customerMobileNumber": "8553641330",
                "customerEmail": "ranjitha.d@ezetap.com",
                "externalRefNumber": ext_ref_number_2,
                "pushTo": push_to_2
            })
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"Response for second notification is : {resp_start}")
            start_p2p_request_id_2 = resp_start['p2pRequestId']
            logger.debug(f"Value of request_id from second notification is : {start_p2p_request_id_2}")
            start_success_2 = resp_start['success']
            logger.debug(f"Value of request_id from second notification is : {start_success_2}")
            time.sleep(2)

            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response for first notification from status api is : {response}")
            status_success = response['success']
            logger.debug(f"Fetching success value from first notification response is : {status_success}")
            status_message_code = response['messageCode']
            logger.debug(f"Fetching message_code value from first notification response is : {status_message_code}")
            status_message = response['message']
            logger.debug(f"Fetching message value from first notification response is : {status_message}")
            status_real_code = response['realCode']
            logger.debug(f"Fetching real_code value from first notification response is : {status_real_code}")

            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id_2
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response for second notification from status api is : {response}")
            status_success_2 = response['success']
            logger.debug(f"Fetching success value from second notification response is : {status_success_2}")
            status_message_code_2 = response['messageCode']
            logger.debug(f"Fetching message_code value from second notification response is : {status_message_code_2}")
            status_message_2 = response['message']
            logger.debug(f"Fetching message value from second notification response is : {status_message_2}")
            status_real_code_2 = response['realCode']
            logger.debug(f"Fetching real_code value from second notification response is : {status_real_code_2}")
            status_username_2 = response['username']
            logger.debug(f"Fetching username value from second notification response is : {status_username_2}")
            status_p2p_request_id_2 = response['p2pRequestId']
            logger.debug(f"Fetching p2pRequestId value from second notification response is : {status_p2p_request_id_2}")

            # turn off the wifi
            app_driver.toggle_wifi()
            logger.debug(f"Turned off network")

            time.sleep(2)
            # turn on the wifi
            app_driver.toggle_wifi()
            logger.debug(f"Turned on network again")

            # Checking redis connection after wifi is turned on
            redis_data = "b'" + device_serial + "|ezetap_android|" + org_code + "'"
            redis_conn = DBProcessor.get_redis_data(redis_data)
            if redis_conn:
                pass
            if not redis_conn:
                raise Exception("Could not find P2P connection in redis server after network reconnection")

            # Checking P2P notification
            app_driver.open_notifications()
            logger.info(f"Pulled notification bar for checking P2P notification after network reconnection")
            try:
                actual_notification2 = home_page.check_p2p_notification()
            except:
                app_driver.back()
                raise Exception(f"Exception in locating P2P notification on device after network reconnection")

            logger.info(f"Expected P2P notification message after network reconnection is : {expected_notification}")

            if actual_notification2 == expected_notification:
                logger.info(f"P2P notification message on device after network reconnection is as expected")
            else:
                app_driver.back()
                raise Exception(
                    f"P2P notification mismatch on device after network reconnection. Actual notification: {actual_notification2}")

            app_driver.back()
            time.sleep(2)

            api_details = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for Cancelling the first notification is : {response}")
            cancel_error_code = response['errorCode']
            logger.debug(f"Fetching error_code value from first notification response is : {cancel_error_code}")
            cancel_error_message = response['errorMessage']
            logger.debug(f"Fetching error_message value from first notification response is : {cancel_error_message}")
            cancel_message = response['message']
            logger.debug(f"Fetching message value from first notification response is : {cancel_message}")
            cancel_real_code = response['realCode']
            logger.debug(f"Fetching real_code value from first notification response is : {cancel_real_code}")
            cancel_success = response['success']
            logger.debug(f"Fetching success value from first notification response is : {cancel_success}")
            cancel_message_code = response['messageCode']
            logger.debug(f"Fetching message_code value from first notification response is : {cancel_message_code}")

            time.sleep(2)

            payment_page = PaymentPage(app_driver)
            payment_page.click_on_cancel_p2p_request_ok()


            #check status api after txn cancelled using API
            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"After Cancelling the first notification, response obtained for Status api is : {response}")
            status_success_3 = response['success']
            logger.debug(f"After Cancelling the first notification, value of success from status api is : {status_success_3}")
            status_message_code_3 = response['messageCode']
            logger.debug(f"After Cancelling the first notification, value of message_code from status api is : {status_message_code_3}")
            status_message_3 = response['message']
            logger.debug(f"After Cancelling the first notification, value of message from status api is : {status_message_3}")
            status_real_code_3 = response['realCode']
            logger.debug(f"After Cancelling the first notification, value of real_code from status api is : {status_real_code_3}")
            start_success_3 = resp_start['success']
            logger.debug(f"After Cancelling the first notification, value of success from status api is : {status_success_3}")

            time.sleep(2)

            card_page = CardPage(app_driver)
            logger.debug(f"Selecting the card type as : CTLS_VISA_CREDIT_417666")
            card_page.select_cardtype("CTLS_VISA_CREDIT_417666")
            logger.debug(f"Selected the card type as : CTLS_VISA_CREDIT_417666")
            card_page.click_on_ok_error_msg()
            logger.debug(f"Clicked on txn popup for preauth")

            api_details = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": start_p2p_request_id_2
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"After second payment is completed : {response}")
            status_success_4 = response['success']
            logger.debug(f"Fetching success value after payment is successful from status api : {status_success_4}")
            status_message_code_4 = response['messageCode']
            logger.debug(f"Fetching message_code value after payment is successful from status api : {status_message_code_4}")
            status_message_4 = response['message']
            logger.debug(f"Fetching message value after payment is successful from status api : {status_message_4}")
            status_real_code_4 = response['realCode']
            logger.debug(f"Fetching real_code value after payment is successful from status api : {status_real_code_4}")
            status_username_4 = resp_start['username']
            logger.debug(f"Fetching username value after payment is successful from status api : {status_username_4}")
            status_p2p_request_id_4 = resp_start['p2pRequestId']
            logger.debug(f"Fetching p2pRequestId value after payment is successful from status api : {status_p2p_request_id_4}")

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

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")

            try:
                expected_api_values = {
                    "start_success": True,
                    "status_success": True,
                    "status_msg": "Notification has been received on POS Device.",
                    "status_msg_code": "P2P_DEVICE_RECEIVED",
                    "status_real_code": "P2P_DEVICE_RECEIVED",
                    "status_success_2": True,
                    "status_msg_code_2": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "status_real_code_2": "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "status_msg_2": "PushToPay Notification has been Canceled from Billing/External System.",
                    "status_username_2": app_username,
                    "status_req_id_2": start_p2p_request_id,

                    "start_success_3": True,
                    "status_success_3": True,
                    "status_msg_3": "Notification has been received on POS Device.",
                    "status_msg_code_3": "P2P_DEVICE_RECEIVED",
                    "status_real_code_3": "P2P_DEVICE_RECEIVED",
                    "status_success_4": True,
                    "status_msg_code_4": "P2P_STATUS_IN_RECEIVED_FROM_EXTERNAL_SYSTEM",
                    "status_real_code_4": "P2P_STATUS_IN_RECEIVED_FROM_EXTERNAL_SYSTEM",
                    "status_msg_4": "PushToPay Notification has been received from Billing/External System.",
                    "status_username_4": app_username,
                    "status_req_id_4": start_p2p_request_id,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "start_success": start_success,
                    "status_success": status_success,
                    "status_msg": status_message,
                    "status_msg_code": status_message_code,
                    "status_real_code": status_real_code,
                    "status_success_2": status_success_2,
                    "status_msg_code_2": status_message_code_2,
                    "status_real_code_2": status_real_code_2,
                    "status_msg_2": status_message_2,
                    "status_username_2": status_username_2,
                    "status_req_id_2": status_p2p_request_id_2,

                    "start_success_3": start_success_3,
                    "status_success_3": status_success_3,
                    "status_msg_3": status_message_3,
                    "status_msg_code_3": status_message_code_3,
                    "status_real_code_3": status_real_code_3,
                    "status_success_4": status_success_4,
                    "status_msg_code_4": status_message_code_4,
                    "status_real_code_4": status_real_code_4,
                    "status_msg_4": status_message_4,
                    "status_username_4": status_username_4,
                    "status_req_id_4": status_p2p_request_id_4,
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
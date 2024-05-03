import sys
from datetime import datetime
import pytest
import random
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_300_302_021():
    """
    Sub Feature Code: UI_Common_Config_Airtel_Verify_Fetch_For_Postpaid_Mobile_LOB (Sub_lob : Postpaid_Bill_Collection)
    Sub Feature Description: Verify fetch is successful for postpaid mobile lob (sub_lob: postpaid bill collection)
    TC naming code description: 100: Payment Method, 300: Config, 302: Airtel, 021: TC021
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
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)----------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_pg = LoginPage(app_driver)
            login_pg.perform_login(app_username, app_password)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            home_pg = HomePage(app_driver)
            home_pg.click_on_start_btn()
            logger.debug(f"clicked on the Start button")
            home_pg.click_on_postpaid_mobile_LOB()
            logger.debug(f"Clicked on the Post Paid lob")
            ph_number = "9861137533"
            home_pg.click_on_postpaid_bill_collection_active(ph_number)
            logger.info(f"Clicked on postpaid bill collection sub lob and entered postpaid bill collection details")
            try:
                home_pg.click_on_fetch_btn()
                message = "clicked on fetch button"
                customer_details_txt = home_pg.fetch_customer_details_txt()
                logger.debug(f"fetched customer_details text from amount page : {customer_details_txt}")
                checkout_btn_txt = home_pg.fetch_checkout_btn_txt()
                logger.debug(f"fetched checkout_button text from amount page : {checkout_btn_txt}")
            except Exception as e:
                message = (f"unable to click on fetch button or Customer Details and Check out button is not visible in "
                           f"amount screen: {e}")
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
                expected_app_values = {"message": "clicked on fetch button",
                                       "amt_screen_check_1": "Customer Details",
                                       "amt_screen_check_2": "Checkout"
                                       }

                actual_app_values = {"message": message,
                                     "amt_screen_check_1": customer_details_txt,
                                     "amt_screen_check_2": checkout_btn_txt
                                     }
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
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_300_302_022():
    """
    Sub Feature Code: UI_Common_Config_Airtel_Verify_Success_Cash_Txn_For_postpaid_LOB (Sub_lob : postpaid_Bill_Collection_Active)
    Sub Feature Description: Verify success cash txn postpaid mobile lob (sub_lob postpaid bill collection active)
    TC naming code description: 100: Payment Method, 300: Config, 302: Airtel, 022: TC022
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
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True,config_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_pg = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_pg.perform_login(app_username, app_password)
            home_pg = HomePage(app_driver)
            home_pg.click_on_start_btn()
            home_pg.click_on_postpaid_mobile_LOB()
            logger.debug("Clicked on the postpaid-Mobile LOB")
            ph_number = "9861137533"
            home_pg.click_on_postpaid_bill_collection_active(ph_number)
            logger.debug("clicked on bill collection Sub Lob of postpaid-mobile LOB and all the bill collection details")
            home_pg.click_on_fetch_btn()
            home_pg.click_on_check_out_btn()
            logger.debug(f"Clicked on checkout btn")
            payment_pg = PaymentPage(app_driver)
            payment_pg.click_on_cash_payment_mode_and_confirm_btn()
            logger.debug('clicked on the Cash mode and confirm button on the LOB page')
            payment_pg.click_on_proceed_homepage()

            query = f"select * from txn where org_code ='{org_code}' order by created_time Desc limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            customer_mobile = result['customer_mobile'].iloc[0]
            logger.debug(f"Fetching customer_mobile from txn table : {customer_mobile}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            status_db = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            external_ref4_db = result['external_ref4'].values[0]
            logger.debug(f"fetched external_ref4 from txn table is : {external_ref4_db}")
            external_ref5_db = result['external_ref5'].values[0]
            logger.debug(f"fetched external_ref5 from txn table is : {external_ref5_db}")
            auth_code_db = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code_db}")
            merchant_name_db = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name_db}")
            merchant_code_db = result['merchant_code'].values[0]
            logger.debug(f"Fetching merchant_code from txn table : {merchant_code_db}")
            txn_type_db = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table : {txn_type_db}")
            user_mobile_db = result['user_mobile'].values[0]
            logger.debug(f"Fetching user_mobile from txn table : {user_mobile_db}")
            username_db = result['username'].values[0]
            logger.debug(f"Fetching username from txn table : {username_db}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            amount_original_db = result['amount_original'].iloc[0]
            logger.debug(f"Fetching amount_original from txn table : {amount_original_db}")

            api_details = DBProcessor.get_api_details('txnlist', request_body={
                "username": app_username,
                "password": app_password
            })
            logger.debug(f"API DETAILS for txn : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction list api is : {response}")
            response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
            logger.debug(f"Response after filtering data of current txn is : {response}")
            external_ref4 = response['externalRefNumber4']
            logger.debug(f"Value of external_ref4 obtained from txnlist api : {external_ref4}")
            external_ref5 = response['externalRefNumber5']
            logger.debug(f"Value of external_ref5 obtained from txnlist api : {external_ref5}")
            org_code_api = response['orgCode']
            logger.debug(f"Value of orgCode obtained from txnlist api : {org_code_api}")
            order_no_api = response['orderNumber']
            logger.debug(f"Value of orderNumber obtained from txnlist api : {order_no_api}")

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
                expected_app_values = {
                    "pmt_mode": "Cash Payment",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": f"{amount_db:,}.00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_name": customer_mobile,
                    "order_id": external_ref,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                txn_history_page = TransHistoryPage(app_driver)
                home_pg.click_on_history()
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching txn customer mobile from txn history for the txn : {txn_id}, {app_customer_mobile}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "customer_name": app_customer_mobile,
                    "order_id": app_order_id,
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "txn_amt": amount_db,
                    "pmt_mode": "CASH",
                    "user_mobile": app_username,
                    "txn_type": txn_type,
                    "acquirer_code": "NONE" if auth_code_db is None else auth_code_db,
                    "order_no": external_ref,
                    "total_amt": float(amount_db),
                    "org_code": org_code_txn,
                    "merchant_code": org_code,
                    "merchant_name": merchant_name_db,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                status_api = response["status"]
                logger.debug(f"Value of status no obtained from txnlist api : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"Value of amount no obtained from txnlist api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Value of payment mode no obtained from txnlist api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Value of state no obtained from txnlist api : {state_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Value of txn type no obtained from txnlist api : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"Value of date api no obtained from txnlist api : {date_api}")
                user_mobile_api = response['userMobile']
                logger.debug(f"Value of user mobile no obtained from txnlist api : {user_mobile_api}")
                settle_status_api = response['settlementStatus']
                logger.debug(f"Value of settlementStatus obtained from txnlist api : {settle_status_api}")
                acquirer_code_api = response['acquirerCode']
                logger.debug(f"Value of acquirerCode obtained from txnlist api : {acquirer_code_api}")
                total_amt_api = response['totalAmount']
                logger.debug(f"Value of totalAmount obtained from txnlist api : {total_amt_api}")
                org_code_api = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {org_code_api}")
                merchant_code_api = response['merchantCode']
                logger.debug(f"Value of merchantCcode obtained from txnlist api : {merchant_code_api}")
                merchant_name_api = response['merchantName']
                logger.debug(f"Value of merchantName obtained from txnlist api : {merchant_name_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "settle_status": settle_status_api,
                    "pmt_state": state_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "user_mobile": user_mobile_api,
                    "txn_type": txn_type_api,
                    "acquirer_code": acquirer_code_api,
                    "order_no": order_no_api,
                    "total_amt": total_amt_api,
                    "org_code": org_code_api,
                    "merchant_code": merchant_code_api,
                    "merchant_name": merchant_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
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
                expected_db_values = {
                    "pmt_state": "SETTLED",
                    "user_mobile": app_username,
                    "user_name": app_username,
                    "txn_type": "CHARGE",
                    "pmt_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "pmt_mode": "CASH",
                    "org_code": org_code_api,
                    "merchant_code": org_code,
                    "external_ref": order_no_api,
                    "txn_amt": amount_db,
                    "amt_original": amount_db,
                    "external_ref4": external_ref4,
                    "external_ref5": external_ref5
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_state": state_db,
                    "user_mobile": user_mobile_db,
                    "user_name": username_db,
                    "txn_type": txn_type_db,
                    "pmt_status": status_db,
                    "settle_status": settlement_status_db,
                    "pmt_mode": payment_mode_db,
                    "org_code": org_code,
                    "merchant_code": merchant_code_db,
                    "external_ref": external_ref,
                    "txn_amt": amount_db,
                    "amt_original": amount_original_db,
                    "external_ref4": external_ref4_db,
                    "external_ref5": external_ref5_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CASH",
                    "txn_amt": f"{amount_db:,}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code_db is None else auth_code_db,
                    "rrn": "-" if rrn is None else rrn,
                    "labels": "LAPU,postpaid,OR"
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(
                    app_un=app_username, app_pw=app_password, order_id=external_ref)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code_portal: {auth_code_portal}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number: {rr_number}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "labels": labels
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        # if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
        #     logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
        #     try:
        #         txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
        #         expected_charge_slip_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(external_ref),
        #                                        'BASE AMOUNT:': f"Rs.{amount_db:,}.00",
        #                                        'date': txn_date,
        #                                        'time': txn_time
        #                                        }
        #         receipt_validator.perform_charge_slip_validations(txn_id,
        #                                                           {"username": app_username, "password": app_password},
        #                                                           expected_charge_slip_values)
        #     except Exception as e:
        #         Configuration.perform_charge_slip_val_exception(testcase_id, e)
        #     logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_300_302_023():
    """
    Sub Feature Code: UI_Common_Config_Airtel_Verify_Fetch_For_Prepaid_Mobile_LOB (Sub_lob : Pre_Paid_Recharge)
    Sub Feature Description: Verify fetch is successful for prepaid mobile lob (sub_lob pre paid-recharge)
    TC naming code description: 100: Payment Method, 300: Config, 302: Airtel, 023: TC023
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
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details for config airtel is : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_pg = LoginPage(app_driver)
            login_pg.perform_login(app_username, app_password)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            home_pg = HomePage(app_driver)
            home_pg.click_on_start_btn()
            logger.debug(f"Clicked on start button on the home page")
            home_pg.click_on_prepaid_mobile_LOB()
            logger.debug(f"clicked on the prepaid mobile lob")
            ph_number = "9642595990"
            amount = random.randint(1, 100)
            home_pg.enter_prepaid_recharge_details(ph_number, amount)
            logger.debug("clicked on pre paid mobile recharge Sub Lob of pre paid-mobile LOB and entered the details")
            try:
                home_pg.click_on_fetch_btn()
                message = "clicked on fetch button"
                customer_details_txt = home_pg.fetch_customer_details_txt()
                logger.debug(f"fetched customer_details text from amount page : {customer_details_txt}")
                checkout_btn_txt = home_pg.fetch_checkout_btn_txt()
                logger.debug(f"fetched checkout_button text from amount page : {checkout_btn_txt}")
            except Exception as e:
                message = (f"unable to clicked on fetch button or Customer Details and Check out button is not"
                           f" visible in amount screen : {e}")
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
                expected_app_values = {"message": "clicked on fetch button",
                                       "amt_screen_check_1": "Customer Details",
                                       "amt_screen_check_2": "Checkout"
                                       }

                actual_app_values = {"message": message,
                                     "amt_screen_check_1": customer_details_txt,
                                     "amt_screen_check_2": checkout_btn_txt
                                     }

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
def test_common_100_300_302_024():
    """
    Sub Feature Code: UI_Common_Config_Airtel_Verify_Fetch_For_New_Activation_LOB (Sub_lob : Mobile_Activation_Butterfly)
    Sub Feature Description: Verify fetch is successful for new activation mobile lob (sub_lob : Mobile Activation Butterfly)
    TC naming code description: 100: Payment Method, 300: Config, 302: Airtel, 024: TC024
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
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True,config_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_pg = LoginPage(app_driver)
            login_pg.perform_login(app_username, app_password)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            home_pg = HomePage(app_driver)
            home_pg.click_on_start_btn()
            logger.debug(f"Clicked on the Start button on the home page")
            home_pg.click_on_new_activation_LOB()
            logger.debug(f"Clicked on the new Activation Lob")
            caf_no = "test_" + str(random.randint(1, 500))
            ph_number = "9642595990"
            order_number = datetime.now().strftime('%m%d%H%M%S')
            home_pg.enter_mobile_activation_butterfly_details(caf_no, ph_number, order_number)
            logger.debug("clicked on new activation butterfly Sub Lob of postpaid-mobile LOB and enter the details")
            try:
                home_pg.click_on_fetch_btn()
                message = "clicked on fetch button"
                customer_details_txt = home_pg.fetch_customer_details_txt()
                logger.debug(f"fetched customer_details text from amount page : {customer_details_txt}")
                checkout_btn_txt = home_pg.fetch_checkout_btn_txt()
                logger.debug(f"fetched checkout_button text from amount page : {checkout_btn_txt}")
            except Exception as e:
                message = (f"unable to click on fetch button or Customer Details and Check out button is not visible in "
                           f"amount screen: {e}")
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
                expected_app_values = {"message": "clicked on fetch button",
                                       "amt_screen_check_1": "Customer Details",
                                       "amt_screen_check_2": "Checkout"
                                       }

                actual_app_values = {"message": message,
                                     "amt_screen_check_1": customer_details_txt,
                                     "amt_screen_check_2": checkout_btn_txt
                                     }
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
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_300_302_025():
    """
    Sub Feature Code: UI_Common_Config_Airtel_Verify_Success_Cash_Txn_For_New_Activation_LOB (Sub_lob : Mobile_Activation_Butterfly)
    Sub Feature Description: Verify success cash txn new activation mobile lob (sub_lob Mobile Activation Butterfly)
    TC naming code description: 100: Payment Method, 300: Config, 302: Airtel, 025: TC025
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
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={"username": portal_username,
                                                                                       "password": portal_password,
                                                                                       "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["configFlowEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True,config_log=True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_pg = LoginPage(app_driver)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_pg.perform_login(app_username, app_password)
            home_pg = HomePage(app_driver)
            home_pg.click_on_start_btn()
            home_pg.click_on_new_activation_LOB()
            caf_no = "test_" + str(random.randint(1, 500))
            order_number = datetime.now().strftime('%m%d%H%M%S')
            ph_number = "9642595990"
            home_pg.enter_mobile_activation_butterfly_details(caf_no, ph_number, order_number)
            logger.debug("clicked on new activation butterfly Sub Lob of new activation LOB and enter the details")
            home_pg.click_on_fetch_btn()
            logger.debug(f"Clicked on the fetch details button")
            home_pg.click_on_check_out_btn()
            logger.debug(f"Clicked on the Checkout button")
            payment_pg = PaymentPage(app_driver)
            home_pg.enter_mobile_number(ph_number)
            payment_pg.click_on_cash_payment_mode_and_confirm_btn()
            logger.debug('clicked on the cash mode and confirm on the LOB page')
            payment_pg.click_on_proceed_homepage()

            query = f"select * from txn where org_code ='{org_code}' order by created_time Desc limit 1;"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            customer_mobile = result['customer_mobile'].iloc[0]
            logger.debug(f"Fetching customer_mobile from txn table : {customer_mobile}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            status_db = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            external_ref4_db = result['external_ref4'].values[0]
            logger.debug(f"fetched external_ref4 from txn table is : {external_ref4_db}")
            external_ref5_db = result['external_ref5'].values[0]
            logger.debug(f"fetched external_ref5 from txn table is : {external_ref5_db}")
            auth_code_db = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code_db}")
            merchant_name_db = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name_db}")
            merchant_code_db = result['merchant_code'].values[0]
            logger.debug(f"Fetching merchant_code from txn table : {merchant_code_db}")
            txn_type_db = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table : {txn_type_db}")
            user_mobile_db = result['user_mobile'].values[0]
            logger.debug(f"Fetching user_mobile from txn table : {user_mobile_db}")
            username_db = result['username'].values[0]
            logger.debug(f"Fetching username from txn table : {username_db}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            amount_original_db = result['amount_original'].iloc[0]
            logger.debug(f"Fetching amount_original from txn table : {amount_original_db}")
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
                expected_app_values = {
                    "pmt_mode": "Cash Payment",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": f"{amount_db:,}.00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_name": customer_mobile,
                    "order_id": external_ref,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                txn_history_page = TransHistoryPage(app_driver)
                home_pg.click_on_history()
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(
                    f"Fetching txn customer mobile from txn history for the txn : {txn_id}, {app_customer_mobile}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "customer_name": app_customer_mobile,
                    "order_id": app_order_id,
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "txn_amt": amount_db,
                    "pmt_mode": "CASH",
                    "user_mobile": app_username,
                    "txn_type": txn_type,
                    "acquirer_code": "NONE" if auth_code_db is None else auth_code_db,
                    "order_no": external_ref,
                    "total_amt": float(amount_db),
                    "org_code": org_code_txn,
                    "merchant_code": org_code,
                    "merchant_name": merchant_name_db,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                org_code_api = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {org_code_api}")
                order_no_api = response['orderNumber']
                logger.debug(f"Value of orderNumber obtained from txnlist api : {order_no_api}")
                status_api = response["status"]
                logger.debug(f"Value of status no obtained from txnlist api : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"Value of amount no obtained from txnlist api : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Value of payment mode no obtained from txnlist api : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Value of state no obtained from txnlist api : {state_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Value of txn type no obtained from txnlist api : {txn_type_api}")
                date_api = response["createdTime"]
                logger.debug(f"Value of date api no obtained from txnlist api : {date_api}")
                user_mobile_api = response['userMobile']
                logger.debug(f"Value of user mobile no obtained from txnlist api : {user_mobile_api}")
                settle_status_api = response['settlementStatus']
                logger.debug(f"Value of settlementStatus obtained from txnlist api : {settle_status_api}")
                acquirer_code_api = response['acquirerCode']
                logger.debug(f"Value of acquirerCode obtained from txnlist api : {acquirer_code_api}")
                total_amt_api = response['totalAmount']
                logger.debug(f"Value of totalAmount obtained from txnlist api : {total_amt_api}")
                org_code_api = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {org_code_api}")
                merchant_code_api = response['merchantCode']
                logger.debug(f"Value of merchantCcode obtained from txnlist api : {merchant_code_api}")
                merchant_name_api = response['merchantName']
                logger.debug(f"Value of merchantName obtained from txnlist api : {merchant_name_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "settle_status": settle_status_api,
                    "pmt_state": state_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "user_mobile": user_mobile_api,
                    "txn_type": txn_type_api,
                    "acquirer_code": acquirer_code_api,
                    "order_no": order_no_api,
                    "total_amt": total_amt_api,
                    "org_code": org_code_api,
                    "merchant_code": merchant_code_api,
                    "merchant_name": merchant_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
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
                    expected_db_values = {
                        "pmt_state": "SETTLED",
                        "user_mobile": app_username,
                        "user_name": app_username,
                        "txn_type": "CHARGE",
                        "pmt_status": "AUTHORIZED",
                        "settle_status": "SETTLED",
                        "pmt_mode": "CASH",
                        "org_code": org_code_api,
                        "merchant_code": org_code,
                        "external_ref": order_no_api,
                        "txn_amt": amount_db,
                        "amt_original": amount_db,
                        }
                    logger.debug(f"expected_db_values: {expected_db_values}")

                    actual_db_values = {
                        "pmt_state": state_db,
                        "user_mobile": user_mobile_db,
                        "user_name": username_db,
                        "txn_type": txn_type_db,
                        "pmt_status": status_db,
                        "settle_status": settlement_status_db,
                        "pmt_mode": payment_mode_db,
                        "org_code": org_code,
                        "merchant_code": merchant_code_db,
                        "external_ref": external_ref,
                        "txn_amt": amount_db,
                        "amt_original": amount_original_db,
                       }
                    logger.debug(f"actual_db_values : {actual_db_values}")
                    Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
                except Exception as e:
                    Configuration.perform_db_val_exception(testcase_id, e)
                logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CASH",
                    "txn_amt": f"{amount_db:,}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code_db is None else auth_code_db,
                    "rrn": "-" if rrn is None else rrn,
                    "labels": "LAPU,postpaid,OR"
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(
                    app_un=app_username, app_pw=app_password, order_id=external_ref)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code_portal: {auth_code_portal}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number: {rr_number}")

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "labels": labels
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        # if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
        #     logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
        #     try:
        #         txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
        #         expected_charge_slip_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(external_ref),
        #                                        'BASE AMOUNT:': f"Rs.{amount_db:,}.00",
        #                                        'date': txn_date,
        #                                        'time': txn_time
        #                                        }
        #         receipt_validator.perform_charge_slip_validations(txn_id,
        #                                                           {"username": app_username, "password": app_password},
        #                                                           expected_charge_slip_values)
        #     except Exception as e:
        #         Configuration.perform_charge_slip_val_exception(testcase_id, e)
        #     logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
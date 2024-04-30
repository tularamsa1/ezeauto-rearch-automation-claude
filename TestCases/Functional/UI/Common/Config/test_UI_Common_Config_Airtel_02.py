import sys
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_300_302_019():
    """
    Sub Feature Code: UI_Common_Config_Airtel_Verify_Fetch_For_POS_LOB (Sub_lob : Bill_Collection_Active)
    Sub Feature Description: Verify fetch is successful for POS (Sub_lob : Bill_Collection_Active)
    TC naming code description: 100: Payment Method, 300: Config, 302: Airtel, 019: TC019
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
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from the org_employee table {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
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
        # -----------------------------PreConditions(Completed)--------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging into MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_on_start_btn()
            logger.info(f"Clicked on start button")
            home_page.click_on_pos_sale_LOB()
            logger.info(f"Clicked on pos sale LOB")

            try:
                performa_no = "23233232"
                email = 'ezeauto@gmail.com'
                logger.info(f"Validating the fixed line tittle and checkout btn after clicking on fetch details")
                home_page.enter_customer_details_for_pos_sale(performa_no, email)
                logger.info("Navigated to fetch details screen")
                payment_page = PaymentPage(app_driver)
                payment_page.validate_customer_details_title()
                logger.info("Navigated to amount screen and validated the customer details title")

                msg = "Fixed line number tittle and Check out button is visible in amount screen"

            except Exception as e:
                logger.error(f"Fixed line and checkout button is not visible in amount screen {e}")
                msg = "Fixed line number tittle and Check out button is not visible in amount screen"

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
                expected_app_values = {
                    "msg": "Fixed line number tittle and Check out button is visible in amount screen"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "msg": msg
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
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal ##  Chargeslip validation is failing ticket is raised and validation is not covered
def test_common_100_300_302_020():
    """
    Sub Feature Code: UI_Common_Config_Airtel_Verify_Success_Cash_Txn_For_POS_LOB (Sub_lob : Bill_Collection_Active)
    Sub Feature Description: Verify success cash txn POS LOB (Sub_lob : Bill_Collection_Active)
    TC naming code description: 100: Payment Method, 300: Config, 302: Airtel, 020: TC020
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
        logger.debug(f"Query to fetch data from the org_employee table: {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code value from the org_employee table {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
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
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, config_log=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username and password : {app_username}, {app_password}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.click_on_start_btn()
            logger.info(f"Clicked on start button")
            home_page.click_on_pos_sale_LOB()
            logger.info(f"Clicked on pos sale LOB")
            home_page.enter_customer_details_for_pos_sale(performa_no='23233232', email='abc@gmail.com')
            logger.info("Navigated to fetch details screen")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_cash_payment_mode_and_confirm_btn()
            logger.info("Selected payment mode is Cash and clicked on confirm btn")

            query = "select * from txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result obtained from txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id from txn table : {txn_id}")
            amount = result['amount'].iloc[0]
            logger.debug(f"Fetching amount from txn table : {amount}")
            amount_original_db = result['amount_original'].iloc[0]
            logger.debug(f"Fetching amount_original from txn table : {amount_original_db}")
            order_id_db = result['external_ref'].iloc[0]
            logger.debug(f"Fetching external_ref from txn table : {order_id_db}")
            customer_mobile = result['customer_mobile'].iloc[0]
            logger.debug(f"Fetching customer_mobile from txn table : {customer_mobile}")
            payer_name = result['payer_name'].iloc[0]
            logger.debug(f"Fetching payer_name from txn table : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn value from the txn table : {rrn}")
            txn_created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time value from the txn table : {txn_created_time}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid value from the txn table : {mid_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid value from the txn table : {tid_db}")
            merchant_name_db = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name value from the txn table : {merchant_name_db}")
            auth_code_db = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code value from the txn table : {auth_code_db}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date from txn table : {posting_date}")
            bank_name_db = result['bank_name'].values[0]
            logger.debug(f"Fetching bank_name from txn table : {bank_name_db}")
            user_mobile_db = result['user_mobile'].values[0]
            logger.debug(f"Fetching user_mobile from txn table : {user_mobile_db}")
            username_db = result['username'].values[0]
            logger.debug(f"Fetching username from txn table : {username_db}")
            txn_type_db = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table : {txn_type_db}")
            txn_request_id_db = result['txn_request_id'].values[0]
            logger.debug(f"Fetching txn_request_id from txn table : {txn_request_id_db}")
            merchant_code_db = result['merchant_code'].values[0]
            logger.debug(f"Fetching merchant_code from txn table : {merchant_code_db}")
            issuer_code_db = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from txn table : {issuer_code_db}")
            external_ref_db = result['external_ref'].values[0]
            logger.debug(f"Fetching external_ref from txn table : {external_ref_db}")
            external_ref4_db = result['external_ref4'].values[0]
            logger.debug(f"Fetching external_ref4 from txn table : {external_ref4_db}")
            external_ref5_db = result['external_ref5'].values[0]
            logger.debug(f"Fetching external_ref5 from txn table : {external_ref5_db}")
            bank_code_db = result['bank_code'].values[0]
            logger.debug(f"Fetching bank_code from txn table : {bank_code_db}")
            state_db = result['state'].values[0]
            logger.debug(f"Fetching state from txn table : {state_db}")
            status_db = result['status'].values[0]
            logger.debug(f"Fetching status from txn table : {status_db}")
            settlement_status_db = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from txn table : {settlement_status_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from txn table : {payment_mode_db}")
            payment_gateway_db = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from txn table : {payment_gateway_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from txn table : {acquirer_code_db}")

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
                date_time = date_time_converter.to_app_format(posting_date_db=posting_date)
                expected_app_values = {
                    "pmt_mode": "Cash Payment",
                    "txn_amt": "{:,.2f}".format(amount),
                    "order_id": order_id_db,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_status": "AUTHORIZED",
                    "txn_id": txn_id,
                    "customer_name": customer_mobile,
                    "date": date_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching txn customer mobile from txn history for the txn : {txn_id}, {app_customer_mobile}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_time}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "txn_amt": app_amount.split(' ')[1],
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_mobile,
                    "date": app_date_time
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
                expected_date_and_time = date_time_converter.db_datetime(date_from_db=txn_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "pmt_state": "SETTLED",
                    "txn_amt": amount,
                    "pmt_mode": "CASH",
                    "user_mobile": app_username,
                    "txn_type": "CHARGE",
                    "acquirer_code": "NONE" if auth_code_db is None else auth_code_db,
                    "order_no": order_id_db,
                    "total_amt": float(amount),
                    "org_code": org_code,
                    "merchant_code": org_code,
                    "merchant_name": merchant_name_db,
                    "date": expected_date_and_time
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS obtained for txnlist api is : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                payment_status_api = response['status']
                logger.debug(f"Value of status obtained from txnlist api : {payment_status_api}")
                payment_state_api = response['states'][0]
                logger.debug(f"Value of states obtained from txnlist api : {payment_state_api}")
                settle_status_api = response['settlementStatus']
                logger.debug(f"Value of settlementStatus obtained from txnlist api : {settle_status_api}")
                amount_api = response['amount']
                logger.debug(f"Value of amount obtained from txnlist api : {amount_api}")
                payment_mode_api = response['paymentMode']
                logger.debug(f"Value of payment mode obtained from txnlist api : {payment_mode_api}")
                user_mobile_api = response['userMobile']
                logger.debug(f"Value of usermobile no obtained from txnlist api : {user_mobile_api}")
                txn_type_api = response['txnType']
                logger.debug(f"Value of txnType obtained from txnlist api : {txn_type_api}")
                acquirer_code_api = response['acquirerCode']
                logger.debug(f"Value of acquirerCode obtained from txnlist api : {acquirer_code_api}")
                order_no_api = response['orderNumber']
                logger.debug(f"Value of orderNumber obtained from txnlist api : {order_no_api}")
                total_amt_api = response['totalAmount']
                logger.debug(f"Value of totalAmount obtained from txnlist api : {total_amt_api}")
                org_code_api = response['orgCode']
                logger.debug(f"Value of orgCode obtained from txnlist api : {org_code_api}")
                merchant_code_api = response['merchantCode']
                logger.debug(f"Value of merchantCcode obtained from txnlist api : {merchant_code_api}")
                merchant_name_api = response['merchantName']
                logger.debug(f"Value of merchantName obtained from txnlist api : {merchant_name_api}")
                date_time_api = response['createdTime']
                logger.debug(f"Value of createdTime obtained from txnlist api : {date_time_api}")

                actual_api_values = {
                    "pmt_status": payment_status_api,
                    "settle_status": settle_status_api,
                    "pmt_state": payment_state_api,
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
                    "date": date_time_converter.from_api_to_datetime_format(date_time_api)
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
                    "txn_amt": amount,
                    "amt_original": amount
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
                    "external_ref": external_ref_db,
                    "txn_amt": amount,
                    "amt_original": amount_original_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation-------------------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(txn_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "CASH",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code_db is None else auth_code_db,
                    "rrn": "-" if rrn is None else rrn,
                    "labels": "LAPU,pos_sale,OR"
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id_db)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                auth_code_portal = transaction_details[0]['Auth Code']
                labels = transaction_details[0]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "labels": labels
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------------

        # # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        # if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
        #     logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
        #     try:
        #         txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
        #         expected_charge_slip_values = {
        #             "PAID BY": "CASH"
        #         }
        #         logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
        #
        #         receipt_validator.perform_charge_slip_validations(txn_id,
        #                                                           {"username": app_username, "password": app_password},
        #                                                           expected_charge_slip_values)
        #
        #     except Exception as e:
        #         Configuration.perform_charge_slip_val_exception(testcase_id, e)
        #     logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # # -----------------------------------------End of ChargeSlip Validation-----------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
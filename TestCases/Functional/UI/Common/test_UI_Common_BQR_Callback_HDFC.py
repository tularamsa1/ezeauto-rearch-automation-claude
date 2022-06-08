import pytest
import random
from datetime import datetime
from Configuration import Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor
from Utilities.ConfigReader import read_config


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_001(): #Make sure to add the test case name as same as the sub feature code.

    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""


        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            driver = GlobalVariables.appDriver
            loginPage = LoginPage(driver)
            username = read_config("credentials", 'username_HDFC')
            password = read_config("credentials", 'password')
            org_code = read_config("testdata", "org_code_hdfc")
            loginPage.perform_login(username, password)
            homePage = HomePage(driver)
            homePage.check_home_page_logo()
            amount = random.randint(301, 1000)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Bqr_paymentMode()
            text = paymentPage.validate_upi_bqr_payment_screen()
            assert text == "Scan QR code using"
            query = "select * from bharatqr_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            print("TXN ID Value:", txn_id)
            print(auth_code)
            print(rrn)
            payload = {
            "PRIMARY_ID": txn_id,
            "SECONDARY_ID": "0",
            "MERCHANT_PAN": "5676560099999",
            "TXN_ID": "E020045812tyd",
            "TXN_DATE_TIME": "20180206102037",
            "TXN_AMOUNT" : '%.2f' %amount,
            "AUTH_CODE": auth_code,
            "RRN": rrn,
            "TIP_AMOUNT": 0,
            "CONSUMER_PAN": "7C845A9BF346F0E6C5A2F9D91186F2F26EA71165160FC53AE5A8E8E43B1C57BA",
            "STATUS_CODE": "00",
            "STATUS_DESC": "success"
                }

            response = APIProcessor.post(payload, "callback_hdfc")
            print("API Res:", response)
            print("API RESP STATUS", response["STATUS_DESC"])
            assert response["STATUS_DESC"]=="Success"
            app_payment_status = paymentPage.fetch_payment_status()
            assert app_payment_status == "Payment Successful"
            paymentPage.click_on_proceed_homepage()

            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "AUTHORIZED", "Payment mode": "Bharat QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}

                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]


                # app_payment_mode = paymentPage.fetch_payment_mode()
                # app_payment_amt = paymentPage.fetch_payment_amount().split()[1]
                # app_txn_id, app_status = paymentPage.get_transaction_details()

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"AUTHORIZED","Amount": amount, "Payment Mode": "BHARATQR"}
                payload = {"username": username, "password": password}
                response = APIProcessor.post(payload, 'txnList')
                print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api=''
                for li in list:
                    if li["txnId"] == txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode":"BHARATQR" , "Payment amount":amount}
                #
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"BHARATQR" , "Payment amount":str(amount)}
                #
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = read_config("credentials", 'username_portal')
                password_portal = read_config('credentials', 'password_portal')
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name(read_config("testdata", "org_code_hdfc"))
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id)
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_common_100_102_001")




@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_002(): #Make sure to add the test case name as same as the sub feature code.

    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""


        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            driver = GlobalVariables.appDriver
            loginPage = LoginPage(driver)
            username = read_config("credentials", 'username_HDFC')
            password = read_config("credentials", 'password')
            org_code = read_config("testdata", "org_code_hdfc")
            loginPage.perform_login(username, password)
            homePage = HomePage(driver)
            homePage.check_home_page_logo()
            amount = random.randint(101, 200)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Bqr_paymentMode()
            text = paymentPage.validate_upi_bqr_payment_screen()
            assert text == "Scan QR code using"
            query = "select * from bharatqr_txn where org_code='" + org_code + "' order by created_time desc limit 1"
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            print("TXN ID Value:", txn_id)
            print(auth_code)
            print(rrn)
            payload = {
            "PRIMARY_ID": txn_id,
            "SECONDARY_ID": "0",
            "MERCHANT_PAN": "5676560099999",
            "TXN_ID": "E020045812tyd",
            "TXN_DATE_TIME": "20180206102037",
            "TXN_AMOUNT" : '%.2f' %amount,
            "AUTH_CODE": auth_code,
            "RRN": rrn,
            "TIP_AMOUNT": 0,
            "CONSUMER_PAN": "7C845A9BF346F0E6C5A2F9D91186F2F26EA71165160FC53AE5A8E8E43B1C57BA",
            "STATUS_CODE": "00",
            "STATUS_DESC": "success"
                }

            response = APIProcessor.post(payload, "callback_hdfc")
            print("API Res:", response)
            print("API RESP STATUS", response["STATUS_DESC"])
            assert response["STATUS_CODE"]=="01"
            app_payment_status = paymentPage.fetch_payment_status()
            assert app_payment_status == "Payment Failed"
            paymentPage.click_on_proceed_homepage()
            paymentPage.click_on_back_btn()


            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "FAILED", "Payment mode": "Bharat QR", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}
                homePage.click_on_back_btn_enter_amt_page()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------

                expectedAPIValues = {"Payment Status":"FAILED","Amount": amount, "Payment Mode": "BHARATQR"}
                payload = {"username": username, "password": password}
                response = APIProcessor.post(payload, 'txnList')
                print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api=''
                for li in list:
                    if li["txnId"] == txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment mode":"BHARATQR" , "Payment amount":amount}
                #
                query = "select status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Failed", "Payment mode":"BHARATQR" , "Payment amount":str(amount)}
                #
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = read_config("credentials", 'username_portal')
                password_portal = read_config('credentials', 'password_portal')
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name(read_config("testdata", "org_code_hdfc"))
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                portal_status = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portal_txn_type = homePagePortal.fetch_transaction_type_from_transaction_id(txn_id)
                portal_amt = homePagePortal.fetch_amount_from_transaction_id(txn_id)
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_common_100_102_002")
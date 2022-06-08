import json
import random
import time
from datetime import datetime
import allure
import pandas as pd
import pytest
import requests
from allure_commons.types import AttachmentType
from Configuration import TestSuiteSetup, Configuration
from DataProvider import GlobalVariables
from DataProvider.config import TestData
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Initiate qr by app and perform pure upi success callback
def test_com_100_101_004():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True   # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '5784758454'
            password = 'A123456'
            loginPage.perform_login(username, password)
            amount = random.randint(300, 399)
            order_number = random.randint(1, 1000)  # generate order id based on the current system time
            homePage = HomePage(driver)

            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Upi_paymentMode()

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'UPIHDFCBANKHDFCPG';"
            result = DBProcessor.getValueFromDB(query)
            pgMerchantId = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]

            query = "select * from upi_txn where org_code = 'UPIHDFCBANKHDFCPG' order by created_time desc limit 1;"
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['txn_id'].values[0]
            rrn = random.randint(1111110, 9999999)

            # add properly
            print("pgMerchantId", pgMerchantId)
            print("Txn_id", Txn_id)
            print("vpa", vpa)
            print('rrn', rrn)

            df_curl = pd.read_excel('/home/ezetap/EzeAuto/TestCases/curl_data.xlsx', sheet_name='Sheet')
            df_curl.set_index('type', inplace=True)
            curl_data = df_curl['curl_data']['success']
            print(type(curl_data))
            curl_data = str(curl_data)

            print("")
            print(type(curl_data))
            curl = curl_data.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa', str(vpa), 1).replace('rrn',str(rrn),1)
            print(curl)
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl, get_pty=True)

            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            payLoad = "pgMerchantId=" + str(pgMerchantId) + "&meRes=" + str(data_buffer)

            url = "https://dev11.ezetap.com/api/2.0/upimerchant/hdfc/callBackUpiMerchantRes"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=payLoad)
            print("Callback response: ",response.text)

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "AUTHORIZED", "Payment mode": "UPI", "Amount": str(amount)}
                # time.sleep(5)
                paymentPage.click_on_proceed_homepage()
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(driver)
                txnHistoryPage.click_first_amount_field()
                payment_status = txnHistoryPage.fetch_txn_status_text()
                print(payment_status)
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                print(payment_mode)
                txn_id = txnHistoryPage.fetch_txn_id_text()
                print(txn_id)
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                print(app_amount)
                Payment_Status =  payment_status.split(':')[1]
                print(Payment_Status)
                actualAppValues = {"Payment Status": Payment_Status, "Payment mode": payment_mode,
                                   "Amount": app_amount.split(' ')[1]}
                                   # "Amount": str(amount)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                              attachment_type=AttachmentType.PNG)
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": username, "password": password}
                response = APIProcessor.post(payload, TestData.API)
                print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for li in list:
                    if li["txnId"] == Txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment State": "SETTLED", "Payment mode": "UPI", "Payment amount": amount,
                                    "UPI_Txn_Status": "AUTHORIZED"}
                query = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                expectedPortalValues = {"Payment State": "Authorized", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                # time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                print("Status of txn:", portalStatus)
                # if portalStatus == 'Settled':
                #     portalStatus = 'AUTHORIZED'
                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_004")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Initiate qr by api and perform checkStatus by api for success using magic number
def test_com_100_101_005():
    # Make sure to add the test case name as same as the sub feature code.
    try:# -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True   # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            username = '5784758454'
            password = 'A123456'
            amount = random.randint(300, 399)

            url = "https://dev11.ezetap.com/api/2.0/merchant/upi/qrcode/generate"

            payload = json.dumps({
                "amount": str(amount),
                "username": username,
                "password": password
            })
            headers = {
                'Content-Type': 'application/json',
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            json_resp = json.loads(response.text)
            Txn_id = json_resp["txnId"]
            print(json_resp)

            url = "https://dev11.ezetap.com/api/2.0/payment/status"

            payload = json.dumps({
                "username": "5784758454",
                "password": "A123456",
                "txnId": str(Txn_id)
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment mode": "UPI","Status": "AUTHORIZED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                loginPage = LoginPage(driver)
                loginPage.perform_login(username, password)
                homePage = HomePage(driver)
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(driver)
                txnHistoryPage.click_first_amount_field()
                payment_status = txnHistoryPage.fetch_txn_status_text()
                print(payment_status)
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                print(payment_mode)
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                print(app_txn_id)
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                print(app_amount)
                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": username, "password": password}
                response = APIProcessor.post(payload, TestData.API)
                print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for li in list:
                    if li["txnId"] == Txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment State": "SETTLED", "Payment mode": "UPI", "Payment amount": amount,
                                    "UPI_Txn_Status":"AUTHORIZED"}
                query_in_txn = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_txn)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query_in_upi_txn = "select status from upi_txn where txn_id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_upi_txn)
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status":upi_status_db}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Authorized", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                #
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()

                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)
                #
                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                        "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_005")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Initiate qr by app and perform pure upi failed callback
def test_com_100_101_006():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True   # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '5784758454'
            password = 'A123456'
            loginPage.perform_login(username, password)
            amount = random.randint(300, 399)
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Upi_paymentMode()

            query = (
                "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'UPIHDFCBANKHDFCPG';")
            result = DBProcessor.getValueFromDB(query)
            pgMerchantId = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]

            query = ("select * from upi_txn where org_code = 'UPIHDFCBANKHDFCPG' order by created_time desc limit 1;")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['txn_id'].values[0]

            print("pgMerchantId", pgMerchantId)
            print("Txn_id", Txn_id)
            print("vpa", vpa)

            df_curl = pd.read_excel('/home/ezetap/EzeAuto/TestCases/curl_data.xlsx', sheet_name='Sheet')
            df_curl.set_index('type', inplace=True)
            curl_data = df_curl['curl_data']['fail']
            print(type(curl_data))
            curl_data = str(curl_data)

            print("")
            print(type(curl_data))
            print(curl_data.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',
                                                                                                           str(vpa), 1))
            curl = curl_data.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',
                                                                                                            str(vpa), 1)
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl, get_pty=True)

            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            payLoad = "pgMerchantId=" + str(pgMerchantId) + "&meRes=" + str(data_buffer)

            url = "https://dev11.ezetap.com/api/2.0/upimerchant/hdfc/callBackUpiMerchantRes"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=payLoad)
            print("Callback response: ", response.text)

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "FAILED", "Payment mode": "UPI", "Amount": str(amount)}
                # time.sleep(10)
                driver.reset()
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                # time.sleep(10)
                # elements = driver.find_elements(By.ID, "com.ezetap.service.demo:id/tvAmount")
                # elements[0].click()
                txnHistoryPage = TransHistoryPage(driver)
                txnHistoryPage.click_first_amount_field()
                # payment_status = str(driver.find_element(By.ID, "com.ezetap.service.demo:id/tvTxnFinalStatus").text)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                print(payment_status)
                # payment_mode = driver.find_element(By.ID, "com.ezetap.service.demo:id/tvTransactionType").text
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                print(payment_mode)
                # basePage = BasePage(driver)
                # txn_id = basePage.fetch_text((By.XPATH, "//*[@text='TRANSACTION ID']/following-sibling::android.widget.TextView"))
                txn_id = txnHistoryPage.fetch_txn_id_text()
                print(txn_id)
                # app_amount = str(driver.find_element(By.ID, "com.ezetap.service.demo:id/tvTxnAmount").text)
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                print(app_amount)
                # time.sleep(5)
                # payment_status = paymentPage.fetch_payment_status()
                # payment_mode = paymentPage.fetch_payment_mode()
                # txn_id, status = paymentPage.get_transaction_details()
                # paymentPage.click_on_proceed_homepage()
                actualAppValues = {"Payment Status": payment_status.split(':')[1], "Payment mode": payment_mode,
                                   "Amount": app_amount.split(' ')[1]}
                # "Amount": str(amount)}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": username, "password": password}
                response = APIProcessor.post(payload, TestData.API)
                print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for li in list:
                    if li["txnId"] == Txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                expectedDBValues = {"Payment Status": "FAILED", "Payment State": "FAILED", "Payment mode": "UPI", "Payment amount": amount, "UPI_Txn_Status": "FAILED"}
                query = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')

                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                print("Status of txn:", portalStatus)
                # if portalStatus == 'Failed':
                #     portalStatus = 'FAILED'
                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_006")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Initiate qr by api and perform checkStatus by api for failed using magic number
def test_com_100_101_007():
    # Make sure to add the test case name as same as the sub feature code.
    try:# -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True   # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            username = '5784758454'
            password = 'A123456'
            amount = random.randint(101, 200)

            url = "https://dev11.ezetap.com/api/2.0/merchant/upi/qrcode/generate"

            payload = json.dumps({
                "amount": str(amount),
                "username": username,
                "password": password
            })
            headers = {
                'Content-Type': 'application/json',
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            json_resp = json.loads(response.text)
            Txn_id = json_resp["txnId"]
            print(json_resp)

            url = "https://dev11.ezetap.com/api/2.0/payment/status"

            payload = json.dumps({
                "username": "5784758454",
                "password": "A123456",
                "txnId": str(Txn_id)
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment mode": "UPI","Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                loginPage = LoginPage(driver)
                loginPage.perform_login(username, password)
                homePage = HomePage(driver)
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(driver)
                txnHistoryPage.click_first_amount_field()
                payment_status = txnHistoryPage.fetch_txn_status_text()
                print(payment_status)
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                print(payment_mode)
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                print(app_txn_id)
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                print(app_amount)
                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": username, "password": password}
                response = APIProcessor.post(payload, TestData.API)
                print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for li in list:
                    if li["txnId"] == Txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment State": "FAILED", "Payment mode": "UPI", "Payment amount": amount,
                                    "UPI_Txn_Status":"FAILED"}
                query_in_txn = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_txn)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query_in_upi_txn = "select status from upi_txn where txn_id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_upi_txn)
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status":upi_status_db}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                #
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()

                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                print("Status of txn:", portalStatus)

                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)
                #
                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                        "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_007")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Initiate qr by app and perform checkStatus by api for success using magic number
def test_com_100_101_008(): #Make sure to add the test case name as same as the sub feature code.

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
            # Write the test case execution code block here
            driver = GlobalVariables.appDriver
            loginPage = LoginPage(driver)
            username = '5784758454'
            password = 'A123456'
            # org_code = read_config("testdata", "org_code_hdfc")
            loginPage.perform_login(username, password)
            homePage = HomePage(driver)
            homePage.check_home_page_logo()
            amount = random.randint(200,300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            print("Order id", order_id)
            homePage.enter_amount_and_order_number(amount, order_id)
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Upi_paymentMode()
            # text = paymentPage.validate_upi_bqr_payment_screen()
            # assert text == "Scan QR code using"
            query = ("select * from upi_txn where org_code = 'UPIHDFCBANKHDFCPG' order by created_time desc limit 1;")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["txn_id"].iloc[0]

            url = "https://dev11.ezetap.com/api/2.0/payment/status"

            payload = json.dumps({
                "username": "5784758454",
                "password": "A123456",
                "txnId": str(txn_id)
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            response = json.loads(response.text)
            print("API Res:", response)
            print("API RESP settlementStatus", response["settlementStatus"])

            assert response["settlementStatus"]=="SETTLED"

            driver.terminate_app("com.ezetap.basicapp")
            driver.activate_app("com.ezetap.basicapp")
            loginPage = LoginPage(driver)
            loginPage.perform_login(username, password)
            homePage = HomePage(driver)
            homePage.check_home_page_logo()
            homePage.enter_amount_and_order_number(amount, order_id)
            homePage.perform_check_status()
            paymentPage = PaymentPage(driver)
            app_payment_status = paymentPage.fetch_payment_status()
            assert app_payment_status == "Payment Successful"
            paymentPage.click_on_proceed_homepage()
            paymentPage.click_back_btn_upi_bqr_payment_screen()
            homePage.click_on_back_btn_enter_amt_page()
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
                expectedAppValues = {"Payment Status": "AUTHORIZED", "Payment mode": "UPI", "Payment Txn ID": txn_id, "Payment Amt": str(amount)}

                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(driver)
                transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]

                actualAppValues = {"Payment Status": app_payment_status.split(':')[1], "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt)}
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

                expectedAPIValues = {"Payment Status":"AUTHORIZED","Amount": amount, "Payment Mode": "UPI"}
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
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment State": "SETTLED", "Payment mode": "UPI",
                                    "Payment amount": amount, "UPI_Txn_Status": "AUTHORIZED"}
                query_in_txn = "select state,status,amount,payment_mode,external_ref from txn where id='" + txn_id + "';"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_txn)
                print(result)
                status_db = result["status"].iloc[0]
                print(status_db)
                payment_mode_db = result["payment_mode"].iloc[0]
                print(payment_mode_db)
                amount_db = int(result["amount"].iloc[0])
                print(amount_db)
                state_db = result["state"].iloc[0]
                print(state_db)

                query_in_upi_txn = "select status from upi_txn where txn_id='" + txn_id + "';"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_upi_txn)
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                expectedPortalValues = {"Payment State": "Settled", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')
                # time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                print("Status of txn:", portalStatus)
                # if portalStatus == 'Settled':
                #     portalStatus = 'AUTHORIZED'
                text = homePagePortal.fetch_status_from_transaction_id(txn_id)
                print("State of txn:", text)

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------


    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_008")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Initiate qr by app and perform pure upi expired callback
def test_com_100_101_009():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True   # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '5784758454'
            password = 'A123456'
            loginPage.perform_login(username, password)
            amount = random.randint(201, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage = HomePage(driver)
            homePage.enter_amount_and_order_number(amount, order_id)
            paymentPage = PaymentPage(driver)
            paymentPage.check_payment_page()
            paymentPage.click_on_Upi_paymentMode()

            query = (
                "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'UPIHDFCBANKHDFCPG';")
            result = DBProcessor.getValueFromDB(query)
            pgMerchantId = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]

            query = ("select * from upi_txn where org_code = 'UPIHDFCBANKHDFCPG' order by created_time desc limit 1;")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['txn_id'].values[0]

            print("pgMerchantId", pgMerchantId)
            print("Txn_id", Txn_id)
            print("vpa", vpa)

            df_curl = pd.read_excel('/home/ezetap/EzeAuto/TestCases/curl_data.xlsx', sheet_name='Sheet')
            df_curl.set_index('type', inplace=True)
            curl_data = df_curl['curl_data']['expire']
            print(type(curl_data))
            curl_data = str(curl_data)

            print("")
            print(type(curl_data))
            print(curl_data.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',
                                                                                                           str(vpa), 1))
            curl = curl_data.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',
                                                                                                            str(vpa), 1)
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl, get_pty=True)

            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            payLoad = "pgMerchantId=" + str(pgMerchantId) + "&meRes=" + str(data_buffer)

            url = "https://dev11.ezetap.com/api/2.0/upimerchant/hdfc/callBackUpiMerchantRes"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=payLoad)
            print("Callback response: ", response.text)

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "EXPIRED", "Payment mode": "UPI", "Amount": str(amount)}
                driver.reset()
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(driver)
                txnHistoryPage.click_first_amount_field()
                payment_status = txnHistoryPage.fetch_txn_status_text()
                print(payment_status)
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                print(payment_mode)
                txn_id = txnHistoryPage.fetch_txn_id_text()
                print(txn_id)
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                print(app_amount)

                actualAppValues = {"Payment Status": payment_status.split(':')[1], "Payment mode": payment_mode,
                                   "Amount": app_amount.split(' ')[1]}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                expectedAPIValues = {"Payment Status": "EXPIRED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": username, "password": password}
                response = APIProcessor.post(payload, TestData.API)
                print(response)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for li in list:
                    if li["txnId"] == Txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                expectedDBValues = {"Payment Status": "EXPIRED", "Payment State": "EXPIRED", "Payment mode": "UPI", "Payment amount": amount, "UPI_Txn_Status": "EXPIRED"}
                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                expectedPortalValues = {"Payment State": "Expired", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('UPIHDFCBANKHDFCPG')

                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                print("Status of txn:", portalStatus)

                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                print("Portal Validation failed due to exception - " + str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_com_100_101_009")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)


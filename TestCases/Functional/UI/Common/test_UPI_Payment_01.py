import random
import time
import requests
from datetime import datetime
import allure
import pandas as pd
import pytest
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
def test_UI_Common_PM_UPI_Success_Via_Pure_UPI_Callback_HDFC():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True   # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False)
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
            time.sleep(20)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Upi_paymentMode()

            query1 = (
                "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'UPIHDFCBANKHDFCPG';")
            q1_result = DBProcessor.getValueFromDB(query1)
            pgMerchantId = q1_result['pgMerchantId'].values[0]
            vpa = q1_result['vpa'].values[0]

            query2 = ("select * from upi_txn where org_code = 'UPIHDFCBANKHDFCPG' order by created_time desc limit 1;")
            q2_result = DBProcessor.getValueFromDB(query2)
            Txn_id = q2_result['txn_id'].values[0]
            rrn = random.randint(1111110, 9999999)

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
                time.sleep(5)
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
                print("&&&&&&&&&&&&&&&&&&&&")
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
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode": "UPI", "Payment amount": amount,
                                    "UPI_Txn_Status": "AUTHORIZED"}
                query_in_txn = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_txn)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                query_in_upi_txn = "select status from upi_txn where txn_id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_upi_txn)
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
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
                expectedPortalValues = {"Payment Status": "AUTHORIZED", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
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
                if portalStatus == 'Settled':
                    portalStatus = 'AUTHORIZED'
                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)

                actualPortalValues = {"Payment Status": str(portalStatus), "Payment Type": portalType,
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
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
        Configuration.executeFinallyBlock("test_UI_Common_PM_UPI_Success_Via_Pure_UPI_Callback_HDFC")
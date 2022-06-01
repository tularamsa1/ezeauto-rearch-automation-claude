# Locators
import pytest
import json
import random
import string
import time
from datetime import datetime

import pandas as pd
import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import Utilities.DBProcessor
from Configuration import TestSuiteSetup, Configuration
from DataProvider import GlobalVariables
from DataProvider.config import TestData
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import BasePage, PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor

tbl_txns_xpath = "//table[@id='table_txns']"
tbl_txnsHeader_xpath = "//table[@id='table_txns']/thead"
tbl_txnsBody_xpath = "//table[@id='table_txns']/tbody"
tbl_txnsRows_xpath = "//table[@id='table_txns']/tbody/tr"
tbl_txnsCols_xpath = "//table[@id='table_txns']/thead//th"
ddl_transaction_xpath = "//a[text()='Transactions ']"
mnu_transactionSearch_xpath = "//a[text()='Search']"


def get_transaction_details_for_portal(driver, txn_id):
    transactionRow = ""
    rowID = "ENT" + txn_id
    transactionDetails = {}
    total_transactions_count = len(driver.find_elements(By.XPATH, tbl_txnsRows_xpath))
    total_attributes_count = len(driver.find_elements(By.XPATH, tbl_txnsCols_xpath))

    for row in range(1, total_transactions_count + 1):
        element = driver.find_element(By.XPATH, tbl_txnsRows_xpath + "[" + str(row) + "]")
        if element.get_attribute("id") == rowID:
            transactionRow = row
            break
    for col in range(1, total_attributes_count):
        attribute = driver.find_element(By.XPATH, tbl_txnsCols_xpath + "[" + str(col) + "]").get_attribute("aria-label")
        if attribute.__contains__(": activate to sort column ascending"):
            attribute = attribute.replace(": activate to sort column ascending", "")
        attributeValue = driver.find_element(By.XPATH, tbl_txnsRows_xpath + "[" + str(transactionRow) + "]/td[" + str(
            col) + "]").text
        transactionDetails[attribute] = attributeValue
    return transactionDetails


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_Common_PM_UPI_Callback_Success_HDFC_07():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '4455778875'
            password = 'q121212'
            loginPage.perform_login(username, password)
            amount = random.randint(300, 399)
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            time.sleep(20)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Upi_paymentMode()

            query1 = (
                "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'SANDEEPTEST_6979';")
            q1_result = DBProcessor.getValueFromDB(query1)
            pgMerchantId = q1_result['pgMerchantId'].values[0]
            vpa = q1_result['vpa'].values[0]

            query2 = ("select * from upi_txn where org_code = 'SANDEEPTEST_6979' order by created_time desc limit 1;")
            q2_result = DBProcessor.getValueFromDB(query2)
            Txn_id = q2_result['txn_id'].values[0]
            rrn = random.randint(1111110, 9999999)

            print("pgMerchantId", pgMerchantId)
            print("Txn_id", Txn_id)
            print("vpa", vpa)
            print('rrn', rrn)

            # import csv
            # mycsv = csv.reader(
            #     open("/home/ezetap/EzeAuto/TestCases/curl_data_callback.csv"))
            # curl_data = ''
            # for row in mycsv:
            #     curl_data = row[0]
            # print("")
            # print(type(curl_data))
            # print(curl_data.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',
            #                                                                                                str(vpa), 1))
            # curl = curl_data.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',
            #                                                                                                 str(vpa), 1)
            #
            # data_buffer = ''
            # ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl, get_pty=True)
            # for line in iter(lambda: ssh_stdout.readline(), ''):
            #     data_buffer += line
            #
            # payLoad = "pgMerchantId=" + str(pgMerchantId) + "&meRes=" + str(data_buffer)
            # url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "upiCallback")
            # headers = {'Content-Type': 'application/x-www-form-urlencoded/json'}
            # callback_resp = requests.post(url, headers=headers, data=json.dumps(payLoad))
            #
            # print("Callback response: ", callback_resp)
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
            # url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "upiCallback")
            # headers = {'Content-Type': 'application/x-www-form-urlencoded/json'}
            # callback_resp = requests.post(url, headers=headers, data=json.dumps(payLoad))
            import requests

            url = "https://dev11.ezetap.com/api/2.0/upimerchant/hdfc/callBackUpiMerchantRes"

            # payload = "pgMerchantId=554455445456789&meRes=6D21A614BF76D52D36E138D7ECCA747E6139F2B6FB30CA8FEC310E067D6B55F050F8150467F16A92EF3BA2DDA27600087ECBFF276ACBFAEA8579F74913876CAC158675FCB53AF43F39491B512432306B2FFA4C3247A2BDE27724860E925DC00127720ED48B30828CEA98FE1938323BA53B4D845755C8FAF449260A7CE7BEC805283F01CBFD0B27CFA345180364967380B811D2D4793A2227BAD6420DF443D1159E3D7030CA0E97FA75B152FDE36F4F59175BD721107598F9C9D6F99A7B6EF45FA948C2BDB8892C907BA16A45026A6C69287A076BBAD442DD86BB1B6927690077C9C8A8DB02471D4796F1EACE9753B0F40F2DB1122A1B5EBCC02EEAA1031C76B4D173D0388A6BD77E9C1426DEEDD56CD192614D0226E2EF8EF333909AFA64DBB7C6EB9449F08EEB9EA919461DAF83A13D8974F7DC562ECC5D57CA39843FA6EFD4"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': 'jsessionid=041ee04a-65a3-4247-a343-375d1a3a1e10'
            }

            response = requests.request("POST", url, headers=headers, data=payLoad)

            print("Callback response: ",response.text)

            # print("Callback response: ", json.loads(callback_resp.text))

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
                # driver.reset()
                # username = '4455778875'
                # password = 'q121212'
                # loginPage.perform_login(username, password)
                # homepage_text = homePage.check_home_page_logo()
                # assert homepage_text == TestData.HOMEPAGE_TEXT
                paymentPage.click_on_proceed_homepage()
                homePage.click_on_history()
                # time.sleep(10)
                # # elements = driver.find_elements(By.ID, "com.ezetap.service.demo:id/tvAmount")
                # # elements[0].click()
                txnHistoryPage = TransHistoryPage(driver)
                txnHistoryPage.click_first_amount_field()
                # # payment_status = str(driver.find_element(By.ID, "com.ezetap.service.demo:id/tvTxnFinalStatus").text)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                print(payment_status)
                # # payment_mode = driver.find_element(By.ID, "com.ezetap.service.demo:id/tvTransactionType").text
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                print(payment_mode)
                # # basePage = BasePage(driver)
                # # txn_id = basePage.fetch_text((By.XPATH, "//*[@text='TRANSACTION ID']/following-sibling::android.widget.TextView"))
                txn_id = txnHistoryPage.fetch_txn_id_text()
                print(txn_id)
                # # app_amount = str(driver.find_element(By.ID, "com.ezetap.service.demo:id/tvTxnAmount").text)
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                print(app_amount)
                # time.sleep(5)
                # payment_status = paymentPage.fetch_payment_status()
                # payment_mode = paymentPage.fetch_payment_mode()
                # txn_id, status = paymentPage.get_transaction_details()
                print("&&&&&&&&&&&&&&&&&&&&")
                Payment_Status =  payment_status.split(':')[1]
                print(Payment_Status)
                paymentPage.click_on_proceed_homepage()
                actualAppValues = {"Payment Status": payment_status.split(':')[1], "Payment mode": payment_mode,
                                   # "Amount": app_amount.split(' ')[1]}
                                   "Amount": str(amount)}
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
                payload = {"username": "4455778875", "password": "q121212"}
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
                #
                query_in_txn = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_txn)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
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
                                        "Amount": "Rs." + str(amount) + ".00", "Username": "4455778875"}
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name('SANDEEPTEST_6979')
                time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                # text = homePagePortal.fetch_status_from_transaction_id(txn_id)

                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)

                actualPortalValues = {"Payment Status": str(text), "Payment Type": portalType,
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
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_Common_PM_UPI_Callback_Success_HDFC_07")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_Common_PM_UPI_Callback_Failed_HDFC_09():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '4455778875'
            password = 'q121212'
            loginPage.perform_login(username, password)
            amount = random.randint(300, 399)
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            time.sleep(20)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Upi_paymentMode()

            query1 = (
                "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'SANDEEPTEST_6979';")
            q1_result = DBProcessor.getValueFromDB(query1)
            pgMerchantId = q1_result['pgMerchantId'].values[0]
            vpa = q1_result['vpa'].values[0]

            query2 = ("select * from upi_txn where org_code = 'SANDEEPTEST_6979' order by created_time desc limit 1;")
            q2_result = DBProcessor.getValueFromDB(query2)
            Txn_id = q2_result['txn_id'].values[0]

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
            url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "upiCallback")
            headers = {'Content-Type': 'application/x-www-form-urlencoded/json'}
            callback_resp = requests.post(url, headers=headers, data=json.dumps(payLoad))

            print("Callback response: ", callback_resp)

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
                time.sleep(10)
                driver.reset()
                username = '4455778875'
                password = 'q121212'
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                time.sleep(10)
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
                expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": "4455778875", "password": "q121212"}
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
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode": "UPI", "Payment amount": amount}
                query = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db}
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
                expectedPortalValues = {"Payment Status": "Authorized", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": "4455778875"}
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name('SANDEEPTEST_6979')
                time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                # text = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
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
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_Common_PM_UPI_Callback_Failed_HDFC_09")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_Common_PM_UPI_RefundByAPI_HDFC_10():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '4455332211'
            password = 'qwerty123'
            loginPage.perform_login(username, password)
            amount = random.randint(300, 399)
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            time.sleep(20)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Upi_paymentMode()

            # time.sleep(5)
            paymentPage.click_back_btn_upi_bqr_payment_screen()
            paymentPage.click_cancel_btn_upi_bqr_payment_screen()

            # time.sleep(5)
            Txn_id, status = paymentPage.get_transaction_details()
            paymentPage.click_on_proceed_homepage()
            refund_payload = {
                "appKey": "fbf0a43f-0331-4c9f-925a-cbbfb913e19e",
                "username": "4455332211",
                "amount": amount,
                "originalTransactionId": str(Txn_id)
            }

            refund_response = APIProcessor.post(refund_payload, "unified_refund")
            print("refund_response", refund_response)

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
                expectedAppValues = {"Payment Status": "AUTHORIZED_REFUNDED", "Payment mode": "UPI",
                                     "Amount": str(amount), "Txn_id": str(Txn_id)}
                time.sleep(2)
                driver.reset()
                username = '4455332211'
                password = 'qwerty123'
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                time.sleep(10)
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

                actualAppValues = {"Payment Status": payment_status.split(':')[1], "Payment mode": payment_mode,
                                   "Amount": app_amount.split(' ')[1], "Txn_id": str(txn_id)}
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
                expectedAPIValues = {"Payment Status": "AUTHORIZED_REFUNDED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": "4455332211", "password": "qwerty123"}
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
                expectedDBValues = {"Payment Status": "AUTHORIZED_REFUNDED", "Payment mode": "UPI",
                                    "Payment amount": amount, "UPI_Txn_Status": "AUTHORIZED_REFUNDED"}
                query_in_txn = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_txn)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
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
                expectedPortalValues = {"Payment Status": "Authorized Refunded", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": "4455778875"}
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name('SANDEEPTEST_6979')
                time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                actualPortalValues = {"Payment Status": str(text), "Payment Type": portalType,
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
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_Common_PM_UPI_RefundByAPI_HDFC_10")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_Common_PM_UPI_UPG_Authorized_HDFC_11():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '4455778875'
            password = 'q121212'
            homePage = HomePage(driver)

            query1 = (
                "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'SANDEEPTEST_6979';")
            q1_result = DBProcessor.getValueFromDB(query1)
            pgMerchantId = q1_result['pgMerchantId'].values[0]

            print("pgMerchantId", pgMerchantId)

            df_curl = pd.read_excel('/home/ezetap/EzeAuto/TestCases/curl_data.xlsx', sheet_name='Sheet')
            df_curl.set_index('type', inplace=True)

            curl_data = df_curl['curl_data']['success']
            print(type(curl_data))
            curl_data = str(curl_data)

            print("")
            request_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            # vpa = ''.join(random.choice(string.ascii_lowercase) for _ in range(4)) + '@' + ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
            vpa = 'abccccc@ybl'
            amount = random.randint(300, 399)
            rrn = random.randint(1111110, 9999999)

            print("request_id", request_id)
            print("vpa", vpa)
            print("amount", amount)
            print("rrn", rrn)

            print(type(curl_data))
            print(curl_data.replace('Txn_id', request_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',str(vpa),1).replace('1036901', str(rrn), 1))
            curl = curl_data.replace('Txn_id', request_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',str(vpa),1).replace('1036901', str(rrn), 1)
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line

            payLoad = "pgMerchantId=" + str(pgMerchantId) + "&meRes=" + str(data_buffer)

            print("payLoad", payLoad)
            # url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "upiCallback")
            # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            # # headers = {'Content-Type': 'application/json'}
            # print("url", url)

            # import requests

            url = "https://dev11.ezetap.com/api/2.0/upimerchant/hdfc/callBackUpiMerchantRes"

            payload = payLoad
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            # response = requests.post(url, headers=headers, data=json.dumps(payload))

            print("Callback response: ",response.text)

            # callback_resp = requests.post(url, headers=headers, data=json.dumps(payLoad))
            # callback_resp = json.loads(callback_resp.text)
            # print("Callback response: ", callback_resp)
            time.sleep(15)
            query2 = (
                    "select * from invalid_pg_request where request_id ='" + request_id + "';")
            print(query2)
            q2_result = DBProcessor.getValueFromDB(query2)
            print(q2_result)
            Txn_id = q2_result['txn_id'].iloc[0]

            print("Txn_id: ", Txn_id)

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
                expectedAppValues = {"Payment Status": "UPG_AUTHORIZED", "Payment mode": "UPI", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                time.sleep(2)
                # username = '4455778875'
                # password = 'q121212'
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                time.sleep(10)
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
                                   "Amount": app_amount.split(' ')[1], "Txn_id": txn_id}
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
                expectedAPIValues = {"Payment Status": "UPG_AUTHORIZED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": "4455778875", "password": "q121212"}
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
                expectedDBValues = {"Payment Status": "UPG_AUTHORIZED", "Payment mode": "UPI", "Payment amount": amount, "UPI_Txn_Status":"UPG AUTHORIZED"}
                query_in_txn = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_txn)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
                query_in_upi_txn = "select status from upi_txn where txn_id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_upi_txn)
                upi_status_db = result["status"].iloc[0]

                # query_in_invalidPgRequest =
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
                expectedPortalValues = {"Payment Status": "Upg Authorized", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": "EZETAP"}
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name('SANDEEPTEST_6979')
                time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                actualPortalValues = {"Payment Status": str(text), "Payment Type": portalType,
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
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_Common_PM_UPI_UPG_Authorized_HDFC_11")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_Common_PM_UPI_UPG_Auth_Refunded_HDFC_12():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        setting_update_url = 'https://dev11.ezetap.com/api/2.0/setting/update/'
        setting_update_payload = {
            "username": "9660867344",
            "password": "A123456",
            "entityName": "org",
            "settings": {
                "upgRefundEnabled": "true",
                "upgAutoRefundEnabled": "true"
            },
            "settingForOrgCode": "SANDEEPTEST_6979"
        }
        setting_update_resp = requests.post(setting_update_url, headers={'Content-Type': 'application/json'}, data=json.dumps(setting_update_payload))
        setting_update_resp = json.loads(setting_update_resp.text)
        print(setting_update_resp)

        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '4455778875'
            password = 'q121212'
            homePage = HomePage(driver)

            query1 = (
                "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'SANDEEPTEST_6979';")
            q1_result = DBProcessor.getValueFromDB(query1)
            pgMerchantId = q1_result['pgMerchantId'].values[0]

            print("pgMerchantId", pgMerchantId)

            df_curl = pd.read_excel('/home/ezetap/EzeAuto/TestCases/curl_data.xlsx', sheet_name='Sheet')
            df_curl.set_index('type', inplace=True)
            curl_data = df_curl['curl_data']['success']
            print(type(curl_data))
            curl_data = str(curl_data)

            print("")
            request_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            # vpa = ''.join(random.choice(string.ascii_lowercase) for _ in range(4)) + '@' + ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
            vpa = 'abccccc@ybl'
            amount = random.randint(300, 399)
            rrn = random.randint(1111110, 9999999)

            print("request_id", request_id)
            print("vpa", vpa)
            print("amount", amount)
            print("rrn", rrn)

            print(type(curl_data))
            print(curl_data.replace('Txn_id', request_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',str(vpa),1).replace('rrn', str(rrn), 1))
            curl = curl_data.replace('Txn_id', request_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',str(vpa),1).replace('rrn', str(rrn), 1)
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line

            payLoad = "pgMerchantId=" + str(pgMerchantId) + "&meRes=" + str(data_buffer)

            print("payLoad", payLoad)
            # url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "upiCallback")
            # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            # headers = {'Content-Type': 'application/json'}
            # print("url", url)

            # import requests

            url = "https://dev11.ezetap.com/api/2.0/upimerchant/hdfc/callBackUpiMerchantRes"

            payload = payLoad
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print("Callback response: ", response.text)

            # callback_resp = requests.post(url, headers=headers, data=json.dumps(payLoad))
            # callback_resp = json.loads(callback_resp.text)
            # print("Callback response: ", callback_resp)
            # time.sleep(15)
            query2 = ("select * from invalid_pg_request where request_id ='" + request_id + "';")
            print(query2)
            q2_result = DBProcessor.getValueFromDB(query2)
            print(q2_result)
            Txn_id = q2_result['txn_id'].iloc[0]
            print("Txn_id: ", Txn_id)

            refund_payload = {
                "appKey": "fbf0a43f-0331-4c9f-925a-cbbfb913e19e",
                "username": "4455332211",
                "amount": amount,
                "originalTransactionId": str(Txn_id)
            }

            upg_refund_response = APIProcessor.post(refund_payload, "unified_refund")
            print("refund_response", upg_refund_response)

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
                expectedAppValues = {"Payment Status": "UPG_AUTH_REFUNDED", "Payment mode": "UPI", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                time.sleep(2)
                # username = '4455778875'
                # password = 'q121212'
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                time.sleep(10)
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
                                   "Amount": app_amount.split(' ')[1], "Txn_id": txn_id}
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
                expectedAPIValues = {"Payment Status": "UPG_AUTH_REFUNDED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": "4455778875", "password": "q121212"}
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
                expectedDBValues = {"Payment Status": "UPG_AUTH_REFUNDED", "Payment mode": "UPI", "Payment amount": amount, "UPI_Txn_Status":"UPG_AUTH_REFUNDED"}
                query_in_txn = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_txn)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
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
                expectedPortalValues = {"Payment Status": "UPG_AUTH_REFUNDED", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": "EZETAP"}
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name('SANDEEPTEST_6979')
                time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                # text = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
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
        setting_update_url = 'https://dev11.ezetap.com/api/2.0/setting/update/'
        setting_update_payload = {
            "username": "9660867344",
            "password": "A123456",
            "entityName": "org",
            "settings": {
                "upgRefundEnabled": "false",
                "upgAutoRefundEnabled": "false"
            },
            "settingForOrgCode": "SANDEEPTEST_6979"
        }
        setting_update_resp = requests.post(setting_update_url, headers={'Content-Type': 'application/json'},
                                            data=json.dumps(setting_update_payload))
        setting_update_resp = json.loads(setting_update_resp.text)
        print(setting_update_resp)
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_Common_PM_UPI_UPG_Auth_Refunded_HDFC_12")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_Common_PM_UPI_UPG_Failed_HDFC_13():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '4455778875'
            password = 'q121212'
            homePage = HomePage(driver)

            query1 = ("select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'SANDEEPTEST_6979';")
            q1_result = DBProcessor.getValueFromDB(query1)
            pgMerchantId = q1_result['pgMerchantId'].values[0]

            print("pgMerchantId", pgMerchantId)

            df_curl = pd.read_excel('/home/ezetap/EzeAuto/TestCases/curl_data.xlsx', sheet_name='Sheet')
            df_curl.set_index('type', inplace=True)
            curl_data = df_curl['curl_data']['fail']
            print(type(curl_data))
            curl_data = str(curl_data)

            print("")
            request_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            # vpa = ''.join(random.choice(string.ascii_lowercase) for _ in range(4)) + '@' + ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
            vpa = 'abccccc@ybl'
            amount = random.randint(300, 399)
            rrn = random.randint(1111110, 9999999)

            print("request_id", request_id)
            print("vpa", vpa)
            print("amount", amount)
            print("rrn", rrn)

            print(type(curl_data))
            curl = curl_data.replace('Txn_id', request_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',str(vpa),1).replace('rrn', str(rrn), 1)

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line

            payLoad = "pgMerchantId=" + str(pgMerchantId) + "&meRes=" + str(data_buffer)

            print("payLoad", payLoad)
            # url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "upiCallback")
            # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            # headers = {'Content-Type': 'application/json'}
            # print("url", url)

            url = "https://dev11.ezetap.com/api/2.0/upimerchant/hdfc/callBackUpiMerchantRes"

            payload = payLoad
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print("Callback response: ", response.text)

            # callback_resp = requests.post(url, headers=headers, data=json.dumps(payLoad))
            # callback_resp = json.loads(callback_resp.text)
            # print("Callback response: ", callback_resp)
            time.sleep(10)
            query2 = ("select * from invalid_pg_request where request_id ='" + request_id + "';")
            print(query2)
            q2_result = DBProcessor.getValueFromDB(query2)
            print(q2_result)
            Txn_id = q2_result['txn_id'].iloc[0]
            print("Txn_id", Txn_id)

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
                expectedAppValues = {"Payment Status": "UPG_FAILED", "Payment mode": "UPI", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                time.sleep(2)
                # username = '4455778875'
                # password = 'q121212'
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                time.sleep(10)
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
                                   "Amount": app_amount.split(' ')[1], "Txn_id": txn_id}
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
                expectedAPIValues = {"Payment Status": "UPG_FAILED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": "4455778875", "password": "q121212"}
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
                expectedDBValues = {"Payment Status": "UPG_FAILED", "Payment mode": "UPI", "Payment amount": amount, "UPI_Txn_Status":"UPG_FAILED"}
                query_in_txn = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query_in_txn)
                result = DBProcessor.getValueFromDB(query_in_txn)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                # Write the test case DB validation code block here. Set this to pass if not required.
                #
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
                expectedPortalValues = {"Payment Status": "UPG_FAILED", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": "EZETAP"}
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name('SANDEEPTEST_6979')
                time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                text = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
                actualPortalValues = {"Payment Status": str(text), "Payment Type": portalType,
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
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_Common_PM_UPI_UPG_Failed_HDFC_13")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_Common_PM_UPI_Callback_Success_AfterExpiry_HDFC_04():
    # Make sure to add the test case name as same as the sub feature code.
    try:
        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '4455778875'
            password = 'q121212'
            loginPage.perform_login(username, password)
            amount = random.randint(1, 100)
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            time.sleep(20)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Upi_paymentMode()

            query1 = (
                "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = 'SANDEEPTEST_6979';")
            q1_result = DBProcessor.getValueFromDB(query1)
            pgMerchantId = q1_result['pgMerchantId'].values[0]
            vpa = q1_result['vpa'].values[0]

            query2 = ("select * from upi_txn where org_code = 'SANDEEPTEST_6979' order by created_time desc limit 1;")
            q2_result = DBProcessor.getValueFromDB(query2)
            Txn_id = q2_result['txn_id'].values[0]

            print("pgMerchantId", pgMerchantId)
            print("Txn_id", Txn_id)
            print("vpa", vpa)

            df_curl = pd.read_excel('/home/ezetap/EzeAuto/TestCases/curl_data.xlsx', sheet_name='Sheet')
            df_curl.set_index('type', inplace=True)
            curl_data = df_curl['curl_data']['success']
            print(type(curl_data))
            curl_data = str(curl_data)

            print("")
            print(type(curl_data))
            print(curl_data.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',str(vpa), 1))
            curl = curl_data.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1).replace('vpa',str(vpa), 1).replace('rrn', str(1036901), 1)
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line

            payLoad = "pgMerchantId=" + str(pgMerchantId) + "&meRes=" + str(data_buffer)
            url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "upiCallback")
            headers = {'Content-Type': 'application/x-www-form-urlencoded/json'}

            # Adding time to expire the qr code(Callback success after expiry)
            time.sleep(120)
            callback_resp = requests.post(url, headers=headers, data=json.dumps(payLoad))
            print("Callback response: ", json.loads(callback_resp.text))

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
                time.sleep(10)
                driver.reset()
                username = '4455778875'
                password = 'q121212'
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                time.sleep(10)
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
                expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "UPI"}
                payload = {"username": "4455778875", "password": "q121212"}
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
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode": "UPI", "Payment amount": amount}
                query = "select status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                actualDBValues = {"Payment Status": status_db, "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db}
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
                expectedPortalValues = {"Payment Status": "Authorized", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": "4455778875"}
                driver_ui = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(driver_ui)
                username_portal = '9660867344'
                password_portal = 'A123456'
                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(driver_ui)
                homePagePortal.search_merchant_name('SANDEEPTEST_6979')
                time.sleep(2)
                homePagePortal.click_switch_button()
                homePagePortal.click_transaction_search_menu()
                # text = homePagePortal.fetch_status_from_transaction_id(txn_id)
                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                print("Status of txn:", portalStatus)
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
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_Common_PM_UPI_Callback_Success_AfterExpiry_HDFC_04")

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

# Locators
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


@pytest.mark.usefixtures("log_on_success")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UPI_Payment(method_setup, appium_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True

    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        # username = ConfigReader.read_config("credentials", 'username_dev11')
        # password = ConfigReader.read_config("credentials", 'password_dev11')
        username = '4455445456'
        password = 'q121212'
        loginPage.perform_login(username, password)
        amount = random.randint(300, 399)
        order_number = random.randint(1, 1000)
        homePage = HomePage(driver)
        homePage.enter_amount_and_order_number(amount, order_number)
        paymentPage = PaymentPage(driver)
        paymentPage.click_on_Upi_paymentMode()

        time.sleep(15)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "com.ezetap.service.demo:id/ibtnBack")))
        driver.find_element(By.ID, "com.ezetap.service.demo:id/ibtnBack").click()
        driver.find_element(By.ID, "com.ezetap.service.demo:id/btnYesCancelPayment").click()
        driver.find_element(By.ID, "com.ezetap.service.demo:id/btnViewDetails").click()

        query1 = (
            "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = "
            "'SANDEEPTEST_6979';")
        result1 = Utilities.DBProcessor.getValueFromDB(query1)
        pgMerchantId = result1['pgMerchantId'].values[0]

        query2 = "select * from upi_txn where org_code = 'SANDEEPTEST_6979' order by created_time desc limit 1;"
        result2 = Utilities.DBProcessor.getValueFromDB(query2)
        Txn_id = result2['txn_id'].values[0]

        print("pgMerchantId", pgMerchantId)
        print("Txn_id", Txn_id)

        import csv
        mycsv = csv.reader(open("/DataProvider/rerun.csv"))
        text = ''
        for row in mycsv:
            text = row[0]

        curl = text.replace('Txn_id', Txn_id, 1).replace('amount', str(amount) + ".00", 1)

        data_buffer = ''
        ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl, get_pty=True)
        for line in iter(lambda: ssh_stdout.readline(), ''):
            data_buffer += line

        payLoad = "pgMerchantId=" + str(pgMerchantId) + "&meRes=" + str(data_buffer)

        print(payLoad)

        print(data_buffer)

        ReportProcessor.get_TC_Exe_Time()
    except Exception as e:
        print(e)
        ReportProcessor.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_MPOS_PM_UPI_Success_HDFC_01():
    try:
        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '4455445456'
            password = 'q121212'
            loginPage.perform_login(username, password)
            amount = random.randint(300, 399)
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            # time.sleep(2)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Upi_paymentMode()

            paymentPage.click_back_btn_upi_bqr_payment_screen()
            paymentPage.click_cancel_btn_upi_bqr_payment_screen()

            Txn_id, status = paymentPage.get_transaction_details()
            paymentPage.click_on_proceed_homepage()

            # ------------------------------------------------------------------------------------------------
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
                expectedAppValues = {"Payment mode": "UPI",
                                     "Status": "AUTHORIZED", "Amount": str(amount), "Txn_id": Txn_id}
                # payment_status = paymentPage.fetch_payment_status()
                # payment_mode = paymentPage.fetch_payment_mode()
                # txn_id, status = paymentPage.get_transaction_details()
                # paymentPage.click_on_proceed_homepage()
                homePage.click_on_history()
                # time.sleep(5)
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
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                print(app_txn_id)
                # app_amount = str(driver.find_element(By.ID, "com.ezetap.service.demo:id/tvTxnAmount").text)
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
                payload = {"username": "4455445456", "password": "q121212"}
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
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode": "UPI", "Payment amount": amount, "UPI_Txn_Status":"AUTHORIZED"}
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
                expectedPortalValues = {"Payment Status": "Authorized", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                #
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

                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                # portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                # print("Status of txn:", portalStatus)

                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)
                #
                actualPortalValues = {"Payment Status": text, "Payment Type": portalType,
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
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        # Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_UI_MPOS_PM_UPI_Success_HDFC_01")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_MPOS_PM_UPI_Failure_HDFC_02():  # Make sure to add the test case name as same as the sub feature code.
    try:
        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            username = '4455778875'
            password = 'q121212'
            loginPage.perform_login(username, password)
            amount = random.randint(101, 200)
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            # time.sleep(40)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Upi_paymentMode()

            # time.sleep(5)
            paymentPage.click_back_btn_upi_bqr_payment_screen()
            paymentPage.click_cancel_btn_upi_bqr_payment_screen()

            query1 = ("select * from upi_txn where org_code = 'SANDEEPTEST_6979' order by created_time desc limit 1;")
            q1_result = DBProcessor.getValueFromDB(query1)
            Txn_id = q1_result['txn_id'].values[0]

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
                expectedAppValues = {"Payment Status": "FAILED", "Payment mode": "UPI", "Amount": str(amount),
                                     "Txn_id": str(Txn_id)}
                time.sleep(2)
                driver.reset()
                username = '4455778875'
                password = 'q121212'
                loginPage.perform_login(username, password)
                homepage_text = homePage.check_home_page_logo()
                assert homepage_text == TestData.HOMEPAGE_TEXT
                homePage.click_on_history()
                # time.sleep(5)
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
                                   "Amount": app_amount.split(' ')[1], "Txn_id": txn_id}
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
                payload = {"username": "4455445456", "password": "q121212"}
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
                expectedDBValues = {"Payment Status": "FAILED", "Payment mode": "UPI", "Payment amount": amount, "UPI_Txn_Status":"AUTHORIZED"}
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
                expectedPortalValues = {"Payment Status": "Failed", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
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

                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                # portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                # print("Status of txn:", portalStatus)

                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)

                actualPortalValues = {"Payment Status": text, "Payment Type": portalType,
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
        Configuration.executeFinallyBlock("test_UI_MPOS_PM_UPI_Failure_HDFC_02")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_MPOS_PM_UPI_Pending_HDFC_05():
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
            amount = random.randint(51, 100)
            if amount == 55:
                amount = 56
            order_number = random.randint(1, 1000)
            homePage = HomePage(driver)
            # time.sleep(40)
            homePage.enter_amount_and_order_number(amount, order_number)
            paymentPage = PaymentPage(driver)
            paymentPage.click_on_Upi_paymentMode()

            # time.sleep(5)
            paymentPage.click_back_btn_upi_bqr_payment_screen()
            paymentPage.click_cancel_btn_upi_bqr_payment_screen()

            query1 = ("select * from upi_txn where org_code = 'SANDEEPTEST_6979' order by created_time desc limit 1;")
            q1_result = DBProcessor.getValueFromDB(query1)
            Txn_id = q1_result['txn_id'].values[0]

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
                expectedAppValues = {"Payment Status": "PENDING", "Payment mode": "UPI", "Amount": str(amount),
                                     "Txn_id": str(Txn_id)}
                time.sleep(20)
                driver.reset()
                username = '4455778875'
                password = 'q121212'
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

                actualAppValues = {"Payment Status": payment_status.split(':')[1], "Payment mode": payment_mode,
                                   "Amount": app_amount.split(' ')[1], "Txn_id": txn_id}
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
                expectedAPIValues = {"Payment Status": "PENDING", "Amount": amount, "Payment Mode": "UPI"}
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
                expectedDBValues = {"Payment Status": "PENDING", "Payment mode": "UPI", "Payment amount": amount, "UPI_Txn_Status":"PENDING"}
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
                expectedPortalValues = {"Payment Status": "Failed", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
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

                portalValuesDict = get_transaction_details_for_portal(driver_ui, Txn_id)
                portalType = portalValuesDict['Type']
                # portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                # print("Status of txn:", portalStatus)

                text = homePagePortal.fetch_status_from_transaction_id(Txn_id)
                print("Status of txn:", text)
                actualPortalValues = {"Payment Status": text, "Payment Type": portalType,
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
        Configuration.executeFinallyBlock("test_UI_MPOS_PM_UPI_Pending_HDFC_05")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_MPOS_PM_UPI_Refund_HDFC_03():
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

            time.sleep(5)
            paymentPage.click_back_btn_upi_bqr_payment_screen()
            paymentPage.click_cancel_btn_upi_bqr_payment_screen()

            time.sleep(5)
            Txn_id, status = paymentPage.get_transaction_details()

            paymentPage.click_on_proceed_homepage()

            Txn_id = str(Txn_id)
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
            basepage = BasePage(driver_ui)
            print("//a[@id='" + str(Txn_id) + "']")
            basepage.perform_click((By.XPATH, "//a[@id='" + str(Txn_id) + "']"))
            time.sleep(10)
            # element = WebDriverWait(driver_ui, 100).until(EC.element_to_be_clickable((By.XPATH, "//a[@id="+str(txn_id)+"]")))
            # element.click()
            driver_ui.find_element(By.XPATH, "//*[@id='" + str(
                Txn_id) + "_div']//button[@class='btn btn-mini btn-primary']").click()
            time.sleep(20)
            # driver_ui.find_element(By.XPATH, "//input[@id='userrefund_refund']").click()
            driver_ui.find_element(By.XPATH, "//input[@id='userrefund_refund']").clear()
            driver_ui.find_element(By.XPATH, "//input[@id='userrefund_refund']").send_keys(amount)
            time.sleep(20)
            # basepage.perform_click((By.XPATH, "//button[@type='button' and @onclick='confirmRefund()']"))
            driver_ui.find_element(By.XPATH, "//button[@type='button' and @onclick='confirmRefund()']").click()
            time.sleep(20)
            alert = driver_ui.switch_to.alert
            alert_text = alert.text
            print(alert_text)
            alert.accept()

            time.sleep(15)

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
                username = '4455778875'
                password = 'q121212'
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
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                print(app_txn_id)
                # app_amount = str(driver.find_element(By.ID, "com.ezetap.service.demo:id/tvTxnAmount").text)
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                print(app_amount)

                actualAppValues = {"Payment Status": payment_status.split(':')[1], "Payment mode": payment_mode,
                                   "Amount": app_amount.split(' ')[1], "Txn_id": str(app_txn_id)}
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
                expectedDBValues = {"Payment Status": "AUTHORIZED_REFUNDED", "Payment mode": "UPI",
                                    "Payment amount": amount, "UPI_Txn_Status":"AUTHORIZED_REFUNDED"}
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
                # driver_ui = GlobalVariables.portalDriver
                # loginPagePortal = PortalLoginPage(driver_ui)
                # username_portal = '9660867344'
                # password_portal = 'A123456'
                # loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                # homePagePortal = PortalHomePage(driver_ui)
                # homePagePortal.search_merchant_name('SANDEEPTEST_6979')
                # time.sleep(2)
                # homePagePortal.click_switch_button()
                # homePagePortal.click_transaction_search_menu()
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
        Configuration.executeFinallyBlock("test_UI_MPOS_PM_UPI_Refund_HDFC_03")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_MPOS_PM_UPI_Expire_HDFC_06():
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

            query = "select * from setting where org_code = 'SANDEEPTEST_6979' AND setting_name = 'upiCollectExpiryTime';"
            print("Query:", query)
            result = DBProcessor.getValueFromDB(query)
            upiCollectExpiryTime = result["upiCollectExpiryTime"].iloc[0]

            query = "select * from setting where org_code = 'SANDEEPTEST_6979' AND setting_name = 'upiQRExpiryTime';"
            print("Query:", query)
            result = DBProcessor.getValueFromDB(query)
            upiQRExpiryTime = result["upiQRExpiryTime"].iloc[0]

            query1 = ("select * from upi_txn where org_code = 'SANDEEPTEST_6979' order by created_time desc limit 1;")
            q1_result = DBProcessor.getValueFromDB(query1)
            Txn_id = q1_result['txn_id'].values[0]

            time.sleep(upiQRExpiryTime * 60)

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
                expectedAppValues = {"Payment Status": "EXPIRED", "Payment mode": "UPI", "Amount": str(amount), "Txn_id":Txn_id}
                time.sleep(2)
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

                actualAppValues = {"Payment Status": payment_status.split(':')[1], "Payment mode": payment_mode,
                                   "Amount": app_amount.split(' ')[1], "Txn_id":txn_id}
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
                expectedDBValues = {"Payment Status": "EXPIRED", "Payment mode": "UPI", "Payment amount": amount, "UPI_Txn_Status":"EXPIRED"}
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
                                  "Payment amount": amount_db, "UPI_Txn_Status":upi_status_db}
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
                expectedPortalValues = {"Payment Status": "Expired", "Payment Type": "UPI",
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
                portalValuesDict = get_transaction_details_for_portal(driver_ui, txn_id)
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
        Configuration.executeFinallyBlock("test_UI_MPOS_PM_UPI_Expire_HDFC_06")

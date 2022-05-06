from datetime import datetime
import pytest

from DataProvider import GlobalVariables
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from DataProvider.config import TestData
from TestCases import setUp
from Utilities.configReader import read_config


@pytest.mark.usefixtures("log_on_success")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_UI_SA_CheckStatus_UPI_01(method_setup,appium_driver, ui_driver):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True

  #  =============Execution Block=====================

    try:
        driver = GlobalVariables.appDriver
        loginPage = LoginPage(driver)
        username = read_config("credentials", 'username_dev11')
        password = read_config("credentials", 'password_dev11')
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homepage_text = homePage.check_home_page_logo()
        assert homepage_text == TestData.HOMEPAGE_TEXT
        amount = TestData.AMOUNT
        order_num = TestData.ORDER_NUMBER
        homePage.enter_amount_and_order_number(amount, order_num)
        paymentPage = PaymentPage(driver)
        paymentPage.click_on_Upi_paymentMode()
        text = paymentPage.validate_upi_bqr_payment_screen()
        assert text == "Scan QR code using"
        driver.terminate_app("com.ezetap.basicapp")
        driver.activate_app("com.ezetap.basicapp")
        loginPage = LoginPage(driver)
        loginPage.perform_login(username, password)
        homePage = HomePage(driver)
        homePage.enter_amount_and_order_number(amount, order_num)
        homePage.perform_check_status()

        setUp.get_TC_Exe_Time()
    except Exception as e:
        print(e)
        setUp.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

    else:
        # ======================Validation Block==========================
        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        txn_id = ""
        status = ""

        # ====================APP validation==========================
        try:
            paymentPage = PaymentPage(driver)
            payment_status = paymentPage.fetch_payment_status()
            txn_id, status = paymentPage.get_transaction_details()
            paymentPage.click_on_proceed_homepage()

            expectedAPPValues = "Payment Successful:"+payment_status
        except Exception as e:
            print("Exception:", e)
            print("APP Validation did not complete due to exception")
            print("")
            expectedAPPValues = "Failed"
            GlobalVariables.EXCEL_App_Val = "Fail"
            success_Val_Execution = False

    # ==========================Portal validation===============================
        try:
            driver_ui = GlobalVariables.portalDriver
            loginPagePortal = PortalLoginPage(driver_ui)
            username_portal = read_config("credentials", 'username_portal')
            password_portal = read_config('credentials', 'password_portal')
            loginPagePortal.perform_login_to_portal(username_portal, password_portal)
            homePagePortal = PortalHomePage(driver_ui)
            homePagePortal.search_merchant_name(read_config("testdata","org_code"))
            homePagePortal.click_switch_button()
            homePagePortal.click_transaction_search_menu()
            text = homePagePortal.fetch_status_from_transaction_id(txn_id)
            print("Status of txn:", text)
            expectedPortalValues = "" + status + ":" + text + "ss"
            print("Expected portal values", expectedPortalValues)
        except Exception as e:
            print(e)
            print("Portal Validation did not complete due to exception")
            print("")
            expectedPortalValues = "Failed"
            GlobalVariables.EXCEL_Portal_Val = "Fail"
            success_Val_Execution = False

        # ===================DB validation=====================================

        try:

            query = "select status,amount,payment_mode,external_ref from txn where id='"+txn_id+"'"
           # query = "select status from txn where rr_number='" +rr_num+ "'"
            print("Query:", query)
            result = setUp.getValueFromDB(query)
            status_db = result["status"].iloc[0]
            payment_mode_db = result["payment_mode"].iloc[0]
            amount_db = int(result["amount"].iloc[0])

            print("Result DB:", result)
            expectedDBValues = ""+status+":"+status_db+",UPI:"+payment_mode_db+","+str(amount)+":"+str(amount_db)+""
           # expectedDBValues = status+":"+status_db,"UPI:"+payment_mode_db,amount+":"+str(amount_db)#,order_num+":"+order_num_db
            print("Expected DB values:", expectedDBValues)
        except Exception as e:
            print(e)
            print("DB Validation did not complete due to exception")
            print("")
            expectedDBValues = "Failed"
            GlobalVariables.EXCEL_DB_Val = "Fail"
            success_Val_Execution = False

        # -------------------API validation---------------------------------
        try:
            response = setUp.post(TestData.payload, TestData.API)
            print("API Response:",response)
            list = response["txns"]
            status_api = ''
            amount_api = ''
            for li in list:
                if li["txnId"] == txn_id:
                    status_api = li["status"]
                    amount_api = int(li["amount"])
#--------"expected:actual,expected:actual,expected:actual,expected:actual"
            expectedAPIValues =""+status+":"+status_api+","+str(amount)+":"+str(amount_api)+""
            print(expectedAPIValues)
        except Exception as e:
            print(e)
            print("API Validation did not complete due to exception")
            print("")
            expectedAPIValues = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        success = setUp.validateValues(expectedAPIValues, expectedDBValues, expectedPortalValues, expectedAPPValues)
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()

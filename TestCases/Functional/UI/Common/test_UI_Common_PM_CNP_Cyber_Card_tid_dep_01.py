import random
import time
from datetime import datetime, timedelta
import sys

import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.portal_remotePayPage import remotePayTxnPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter,  merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_149():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_Success_Cyber
    Sub Feature Description: Verification of a Remote Pay successful credit card txn
    TC naming code description:
    100: Payment Method
    103: RemotePay
    149: TC_149
    """

    expected_message = "Your payment is successfully completed! You may close the browser now."

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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'CYBERSOURCE' and payment_mode = 'CNP';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")


        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 500)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            # added the acqutn hdfc and payment_gateway is hdfc
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
                                                           payment_gateway="HDFC")

            # device = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
            #                                                         payment_gateway="CYBERSOURCE") #device value will be none

            print("device serial is :", device_serial)

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password,
                                                                    "deviceSerial" : device_serial
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")
            print("response is:",response)

            if response['success'] == False:
                raise Exception("Api could not initate a cnp txn.")

            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                portal_driver = TestSuiteSetup.initialize_portal_driver()
                portal_driver.get(payment_link_url)
                remote_pay_txn = remotePayTxnPage(portal_driver)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("4000 0000 0000 0002")
                remote_pay_txn.enterCreditCardExpiryMonth("12")
                remote_pay_txn.enterCreditCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.clickOnSubmitButton()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expiryMessage is:  {expected_message}")

                if success_message == expected_message:
                    pass
                else:
                    raise Exception("Success Message is not matching.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Query result, txn_issuer_code : {txn_issuer_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")
            txn_terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(f"Query result, tid from db : {txn_terminal_info_id}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")
            txn_state = result['state'].values[0]
            logger.debug(f"Query result, db txn_state from db : {txn_state}")


            query = "select * from merchant_pg_config where org_code = '" + str(org_code) + "' and payment_gateway = 'CYBERSOURCE'"
            logger.debug(f"Query to fetch tid from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            tid_settings = result['tid'].values[0]
            logger.info(f"tid from setting is: {tid_settings}")

            query = "select * from terminal_info where tid='" + str(tid_settings) + "';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            terminal_info_id = result['id'].values[0]
            logger.info(f"id from setting is: {tid_settings}")
            mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid}")
            device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {device_serial}")


            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]

            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            cnpware_txn_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_card_type : {cnpware_txn_card_type}")
            cnpware_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnpware_txn_state : {cnpware_txn_state}")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]

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
                date_and_time = date_time_converter.to_app_format(posting_date)

                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "AUTHORIZED",
                                     "txn_amt": str(amount),
                                     "txn_id": txn_id,
                                     "rrn": cnp_txn_rrn,
                                     "order_id": order_id,
                                     "msg": "PAYMENT SUCCESSFUL",
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     "auth_code": txn_auth_code,
                                     "date": date_and_time
                                     }

                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                logger.debug("Login completed in the app.")
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.debug("Waiting completed for txn history page.")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)


                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {payment_rrn}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")


                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],
                                   "txn_id": app_txn_id,
                                   "rrn": payment_rrn,
                                   "order_id": payment_order_id,
                                   "msg": payment_status_msg,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   "auth_code": payment_auth_code,
                                   "date": app_date_and_time
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)

            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info(f"Started API validation for the test case : {testcase_id}")
                date = date_time_converter.db_datetime(posting_date)

                expectedAPIValues = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "CNP",
                    "cnp_pmt_card_brand": "VISA",
                    "cnp_pmt_card_type": "CREDIT",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "HDFC",
                    "settle_status": "SETTLED",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "org_code": org_code,
                    "date": date,
                    "tid" : txn_tid,
                    "mid": txn_mid,
                    "device_serial": txn_device_serial,
                }

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": app_username,
                                                                                      "password": app_password,
                                                                                      "txnId": txn_id})
                response = APIProcessor.send_request(api_details)

                status_api = response["status"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                amount_api = response["amount"]
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                payment_card_brand = response["paymentCardBrand"]
                logger.debug(f"Fetching Transaction payment Card Brand from transaction api : {payment_card_brand} ")
                payment_card_type = response["paymentCardType"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {payment_card_type} ")
                acquirer_code__api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {acquirer_code__api} ")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {settlement_status_api} ")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {issuer_code_api} ")
                txn_type_api = response["txnType"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {txn_type_api} ")
                date_api = response["postingDate"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {date_api} ")
                org_code_api = response["orgCode"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {org_code_api} ")
                tid_api = response["tid"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {tid_api} ")
                mid_api = response["mid"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {mid_api} ")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {device_serial_api} ")


                actualAPIValues = {
                                    "pmt_status": status_api,
                                    "txn_amt": amount_api,
                                    "pmt_mode": payment_mode_api,
                                    "cnp_pmt_card_brand": payment_card_brand,
                                    "cnp_pmt_card_type": payment_card_type,
                                    "pmt_state": txn_state,
                                    "acquirer_code": acquirer_code__api,
                                    "settle_status": settlement_status_api,
                                    "issuer_code": issuer_code_api,
                                    "txn_type": txn_type_api,
                                    "org_code": org_code_api,
                                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                                    "tid": tid_api,
                                    "mid": mid_api,
                                    "device_serial": device_serial_api
                                }

                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")

            try:
                expectedDBValues = {
                                    "pmt_status": "AUTHORIZED",
                                    "pmt_state": "SETTLED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "SETTLED",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "auth_code": txn_auth_code,
                                    "cnp_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow": "REMOTEPAY",
                                    "pmt_intent_status": "COMPLETED",
                                    "tid": txn_tid,
                                    "mid": txn_mid,
                                    "device_serial": txn_device_serial,
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0])  # Amount should not be converted to int
                settle_status_db = result["settlement_status"].iloc[0]
                pmt_state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                tid_db = result['tid'].iloc[0]
                mid_db = result['mid'].iloc[0]
                device_serial_db = result['device_serial'].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                actualDBValues = {
                                  "pmt_status": pmt_status_db,
                                  "pmt_state": pmt_state_db,
                                  "pmt_mode": pmt_mode_db,
                                  "txn_amt": txn_amt_db,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "auth_code": cnp_txn_auth_code,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  "pmt_intent_status": payment_intent_status,
                                  "tid": tid_db,
                                  "mid": mid_db,
                                  "device_serial" : device_serial_db
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # # -----------------------------------------Start of ChargeSlip Validation---------------------------------

        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")

            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                logger.info(f"date and time is: {txn_date},{txn_time}")

                expectedValues = {'CARD TYPE': 'VISA',
                                  'merchant_ref_no': 'Ref # ' + str(order_id),
                                  'RRN': str(cnp_txn_rrn),
                                  'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                  'date': txn_date,
                                  'time': txn_time,
                                  "AUTH CODE": txn_auth_code
                                  }

                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expectedValues)
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
def test_common_100_103_150():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_Failed_Cyber
    Sub Feature Description: Tid Dep - Verification of failed remote pay credit card txn for cybersource pg
    TC naming code description:
    100: Payment Method
    103: RemotePay
    150: TC_150
    """
    expected_failed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact support@ezetap.com for further clarifications."

    try:
        # -------------------------------Reset Settings to default(started)--------------------------------------------

        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'CYBERSOURCE' and payment_mode = 'CNP';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        #-----------------------------------------Start of Test Execution---------------------------------------------------

        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            # added the acqutn hdfc and payment_gateway is hdfc
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
                                                                    payment_gateway="HDFC")
            print("device serial is :", device_serial)

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password,
                                                                    "deviceSerial": device_serial
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")
            print("response is:", response)

            if response['success'] == False:
                raise Exception("Api could not initate a cnp txn.")
            else:
                response = APIProcessor.send_request(api_details)
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                ui_driver.get(payment_link_url)
                remote_pay_txn = remotePayTxnPage(ui_driver)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("4111 1111 1111 1111")
                remote_pay_txn.enterCreditCardExpiryMonth("12")
                remote_pay_txn.enterCreditCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()

            time.sleep(5)
            remote_pay_txn.wait_for_failed_message()
            failed_message = str(remote_pay_txn.failedScreenMessage())
            logger.info(f"Your failed Message is:  {failed_message}")

            if failed_message == expected_failed_message:
                pass
            else:
                logger.info(f"expected failed message is: {failed_message}")
                logger.info(f"actual failed message is: {expected_failed_message}")
                raise Exception(f"failed Messages are not matching")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")


            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
                                     "txn_amt": str(amount),
                                     "txn_id": txn_id,
                                     "order_id": order_id,
                                     "msg": "PAYMENT FAILED",
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     "date": date_and_time
                                     }

                logger.debug(f"expectedAppValues: {expectedAppValues}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)

                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")


                actualAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
                                     "txn_amt": app_amount.split(' ')[1],
                                     "txn_id": app_txn_id,
                                     "order_id": payment_order_id,
                                     "msg": payment_status_msg,
                                     "customer_name": payment_customer_name,
                                     "settle_status": payment_settlement_status,
                                     "date": app_date_and_time
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")

                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)

            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")

            try:
                date = date_time_converter.db_datetime(posting_date)
                expectedAPIValues = {"pmt_status": "FAILED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state":"FAILED",
                                     "acquirer_code":"HDFC",
                                     "settle_status":"FAILED",
                                     "issuer_code":"HDFC",
                                     "txn_type":"REMOTE_PAY",
                                     "org_code":org_code,
                                     "date": date,
                                     "tid": txn_tid,
                                     "mid": txn_mid,
                                     "device_serial": txn_device_serial,
                                     }

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username, "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.info(f"response from api details : {api_details}")
                response_in_list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"]) #Not a correct way of doing it.
                        acquirer_code__api = elements["acquirerCode"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        txn_type_api = elements["txnType"]
                        org_code_api = elements["orgCode"]
                        date_api = elements["postingDate"]
                        tid_api = elements["tid"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {tid_api} ")
                        mid_api = elements["mid"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {mid_api} ")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {device_serial_api} ")


                actualAPIValues = {"pmt_status": status_api,
                                    "txn_amt": amount_api,
                                    "pmt_mode": "CNP",
                                    "pmt_state": cnp_txn_state,
                                    "acquirer_code": acquirer_code__api,
                                    "settle_status": settlement_status_api,
                                    "issuer_code": issuer_code_api,
                                    "txn_type": txn_type_api,
                                    "org_code": org_code_api,
                                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                                    "tid": tid_api,
                                    "mid": mid_api,
                                    "device_serial": device_serial_api
                                  }

                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")

            try:
                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "FAILED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "FAILED",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_flow": "REMOTEPAY",
                                    "auth_code": txn_auth_code,
                                    "cnp_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow": "REMOTEPAY",
                                    "pmt_intent_status": "ACTIVE",
                                    "tid": txn_tid,
                                    "mid": txn_mid,
                                    "device_serial": txn_device_serial,
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0])
                settle_status_db = result["settlement_status"].iloc[0]
                pmt_state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                mid_db = result['mid'].iloc[0]
                tid_db = result['tid'].iloc[0]
                device_serial_db = result["device_serial"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                cnpware_txn_txn_type = result['txn_type'].values[0]
                logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
                cnpware_txn_card_type = result['payment_card_type'].values[0]
                logger.debug(f"Query result, cnpware_txn_card_type : {cnpware_txn_card_type}")
                cnpware_txn_state = result['state'].values[0]
                logger.debug(f"Query result, cnpware_txn_state : {cnpware_txn_state}")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
                cnpware_payment_flow = result['payment_flow'].values[0]


                actualDBValues = {"pmt_status": pmt_status_db,
                                    "pmt_state": pmt_state_db,
                                    "pmt_mode": pmt_mode_db,
                                    "txn_amt": txn_amt_db,
                                    "settle_status":settle_status_db,
                                    "pmt_gateway":payment_gateway_db,
                                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                                    "cnpware_pmt_flow":cnpware_payment_flow,
                                    "auth_code": cnp_txn_auth_code,
                                    "cnp_pmt_gateway": cnp_payment_gateway,
                                    "pmt_flow": cnp_payment_flow,
                                    "pmt_intent_status": payment_intent_status,
                                    "mid" : mid_db,
                                    "tid" : tid_db,
                                    "device_serial" : device_serial_db
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -------------------------------------------End of Validation---------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
            # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)









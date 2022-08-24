import random
import shutil
import sys
import time
from datetime import datetime
import pytest
from termcolor import colored
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from PageFactory.portal_remotePayPage import remotePayTxnPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


# @pytest.mark.usefixtures("log_on_success", "method_setup")
# @pytest.mark.apiVal
# @pytest.mark.dbVal
# @pytest.mark.portalVal
# @pytest.mark.appVal
# @pytest.mark.chargeSlipVal
# def test_common_100_103_077():
#     """
#     Sub Feature Code: UI_Common_PM_CNP_ChargeSlip_Val_debit_Card_Success_Cyber
#     Sub Feature Description: Verification of a charge slip validation for debit card txn via CNP link
#     TC naming code description:
#     100: Payment Method
#     103: RemotePay
#     077: TC_077
#     """
#     expectedSuccessMessage = "Your payment is successfully completed! You may close the browser now."
#     try:
#         testcase_id = sys._getframe().f_code.co_name
#         GlobalVariables.time_calc.setup.resume()
#         logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
#
#         # -------------------------------Reset Settings to default(started)--------------------------------------------
#         logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
#         logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
#         app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
#         logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
#         app_username = app_cred['Username']
#         app_password = app_cred['Password']
#         portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
#         logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
#         portal_username = portal_cred['Username']
#         portal_password = portal_cred['Password']
#
#         query = "select org_code from org_employee where username='" + str(app_username) + "';"
#         logger.debug(f"Query to fetch org_code from the DB : {query}")
#         result = DBProcessor.getValueFromDB(query)
#         org_code = result['org_code'].values[0]
#         logger.debug(f"Query result, org_code : {org_code}")
#
#         query = "update remotepay_setting set setting_value= '1' where setting_name='rmpayBumpCount' and org_code='" + org_code + "';"
#         logger.debug(f"Query to update remote pay settings is : {query}")
#         result = DBProcessor.setValueToDB(query)
#         logger.debug(f"Result for remote pay setting is: {result}")
#
#         testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
#                                                                portal_un=portal_username,
#                                                                portal_pw=portal_password, payment_gateway='CYBERSOURCE')
#
#         logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
#         # -------------------------------Reset Settings to default(completed)-------------------------------------------
#         # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
#         logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
#
#         # Write the setup code here
#
#         GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
#         logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
#         # -----------------------------PreConditions(Completed)-----------------------------
#
#         #---------------------------------------------------------------------------------------------------------
#         Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)
#
#         GlobalVariables.time_calc.setup.end()
#         logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
#
#         #-----------------------------------------Start of Test Execution-------------------------------------
#         try:
#             # ------------------------------------------------------------------------------------------------
#             logger.info(f"Starting execution for the test case : {testcase_id}")
#             GlobalVariables.time_calc.execution.start()
#             logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
#
#             amount = random.randint(300, 399)
#             order_id = datetime.now().strftime('%m%d%H%M%S')
#             api_details = DBProcessor.get_api_details('Remotepay_Intiate',
#                                                       request_body={"amount": amount, "externalRefNumber": order_id,
#                                                                     "username": app_username, "password": app_password})
#
#             response = APIProcessor.send_request(api_details)
#             if response['success'] == False:
#                 raise Exception ("Api could not initate a cnp txn.")
#             else:
#                 ui_driver = TestSuiteSetup.initialize_portal_driver()
#                 paymentLinkUrl = response['paymentLink']
#                 payment_intent_id = response.get('paymentIntentId')
#                 logger.info("Opening the link in the browser")
#                 ui_driver.get(paymentLinkUrl)
#                 remotePayUpiCollectTxn = remotePayTxnPage(ui_driver)
#                 remotePayUpiCollectTxn.clickOnRemotePayUPI()
#                 remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
#                 logger.info("Opening UPI Collect to start the txn.")
#                 remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
#                 remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
#                 remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
#                 remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
#                 logger.info("VPA validation completed.")
#                 remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()
#
#
#             query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
#             logger.debug(f"Query to fetch Txn_id from the DB : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             Txn_id = result['id'].values[0]
#             query = "select * from cnp_txn where txn_id='" + Txn_id + "';"
#             logger.debug(f"Query to fetch Txn_id from the DB : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             rrn = result['rr_number'].values[0]
#             txn_id = result['txn_id'].values[0]
#             payment_gateway = result['payment_gateway'].values[0]
#             payment_mode = result['payment_mode'].values[0]
#             payment_flow = result['payment_flow'].values[0]
#             payment_option = result['payment_option'].values[0]
#             payment_option_value1 = result['payment_option_value1'].values[0]
#             payment_status = result['payment_status'].values[0]
#             state = result['state'].values[0]
#             payment_card_brand = result['payment_card_brand'].values[0]
#             payment_card_type = result['payment_card_type'].values[0]
#             acquirer_code = result['acquirer_code'].values[0]
#             issuer_code = result['issuer_code'].values[0]
#             org_code = result['org_code'].values[0]
#             logger.debug(f"Query result, Txn_id : {Txn_id}")
#             logger.debug(f"Query result from cnp_txn, Txn_id : {txn_id}")
#             logger.debug(f"Query result, rrn : {rrn}")
#             logger.debug(f"Query result from cnp_txn, payment_gateway : {payment_gateway}")
#             logger.debug(f"Query result from cnp_txn, payment_mode : {payment_mode}")
#             logger.debug(f"Query result from cnp_txn, payment_flow : {payment_flow}")
#             logger.debug(f"Query result from cnp_txn, payment_option : {payment_option}")
#             logger.debug(f"Query result from cnp_txn, payment_option_value1 : {payment_option_value1}")
#             logger.debug(f"Query result from cnp_txn, payment_status : {payment_status}")
#             logger.debug(f"Query result from cnp_txn, state : {state}")
#             logger.debug(f"Query result from cnp_txn, payment_card_brand : {payment_card_brand}")
#             logger.debug(f"Query result from cnp_txn, payment_card_type : {payment_card_type}")
#             logger.debug(f"Query result from cnp_txn, acquirer_code : {acquirer_code}")
#             logger.debug(f"Query result from cnp_txn, issuer_code : {issuer_code}")
#             logger.debug(f"Query result from cnp_txn, org_code : {org_code}")
#
#             query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
#                 order_id) + "';"
#             logger.debug(f"Query to fetch Txn_id from the DB : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             txn_txn_id = result['id'].values[0]
#             txn_customer_name = result['customer_name'].values[0]
#             txn_payer_name = result['payer_name'].values[0]
#             txn_settle_status = result['settlement_status'].values[0]
#             txn_auth_code = result['auth_code'].values[0]
#             txn_issuer_code = result['issuer_code'].values[0]
#             txn_bank_name = result['bank_name'].values[0]
#             txn_acquirer_code = result['acquirer_code'].values[0]
#             txn_settlement_status = result['settlement_status'].values[0]
#             txn_payment_mode = result['payment_mode'].values[0]
#             txn_amount = result['amount'].values[0]
#             txn_posting_date = result['posting_date'].values[0]
#
#             logger.debug(f"Query result, txn_txn_id : {txn_txn_id}")
#             logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
#             logger.debug(f"Query result, txn_payer_name : {txn_payer_name}")
#             logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
#             logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
#             logger.debug(f"Query result, txn_issuer_code : {txn_issuer_code}")
#             logger.debug(f"Query result, txn_bank_name : {txn_bank_name}")
#             logger.debug(f"Query result, txn_acquirer_code : {txn_acquirer_code}")
#             logger.debug(f"Query result, txn_settlement_status : {txn_settlement_status}")
#             logger.debug(f"Query result, txn_payment_mode : {txn_payment_mode}")
#             logger.debug(f"Query result, txn_amount : {txn_amount}")
#
#             query = "select * from cnp_txn where txn_id='" + txn_txn_id + "';"
#             logger.debug(f"Query to fetch Txn_id from the DB : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             cnp_txn_rrn = result['rr_number'].values[0]
#             cnp_txn_state = result['state'].values[0]
#             cnp_txn_acquirer_code = result['acquirer_code'].values[0]
#             cnp_txn_card_type = result['payment_card_type'].values[0]
#             cnp_txn_external_ref = result['external_ref'].values[0]
#             cnp_txn_auth_code = result['auth_code'].values[0]
#             # cnp_txn_amount = result['amount'].values[0]
#             cnp_payment_gateway = result['payment_gateway'].values[0]
#             cnp_payment_flow = result['payment_flow'].values[0]
#
#             logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
#             logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
#             logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
#             logger.debug(f"Query result, cnp_txn_card_type : {cnp_txn_card_type}")
#             logger.debug(f"Query result, cnp_txn_external_ref : {cnp_txn_external_ref}")
#             logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
#             # logger.debug(f"Query result, cnp_txn_amount : {cnp_txn_amount}")
#             logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
#
#             query = "select * from cnpware_demo.cnpware_txn where txn_id='" + txn_txn_id + "';"
#             logger.debug(f"Query to fetch Txn_id from the DB : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             cnpware_txn_txn_type = result['txn_type'].values[0]
#             cnpware_txn_rrn_number = result['rr_number'].values[0]
#             cnpware_txn_acquirer_code = result['acquirer_code'].values[0]
#             cnpware_txn_card_type = result['payment_card_type'].values[0]
#             cnpware_txn_external_ref = result['external_ref'].values[0]
#             cnpware_txn_auth_code = result['auth_code'].values[0]
#             cnpware_txn_state = result['state'].values[0]
#             cnpware_txn_amount = result['amount'].values[0]
#             cnpware_payment_gateway = result['payment_gateway'].values[0]
#             cnpware_payment_flow = result['payment_flow'].values[0]
#
#             logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
#             logger.debug(f"Query result, cnpware_txn_rrn_number : {cnpware_txn_rrn_number}")
#             logger.debug(f"Query result, cnpware_txn_acquirer_code : {cnpware_txn_acquirer_code}")
#             logger.debug(f"Query result, cnpware_txn_card_type : {cnpware_txn_card_type}")
#             logger.debug(f"Query result, cnpware_txn_external_ref : {cnpware_txn_external_ref}")
#             logger.debug(f"Query result, cnpware_txn_auth_code : {cnpware_txn_auth_code}")
#             logger.debug(f"Query result, cnpware_txn_state : {cnpware_txn_state}")
#             logger.debug(f"Query result, cnpware_txn_amount : {cnpware_txn_amount}")
#             logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
#             # ------------------------------------------------------------------------------------------------
#             GlobalVariables.EXCEL_TC_Execution = "Pass"
#             GlobalVariables.time_calc.execution.pause()
#             logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
#             logger.info(f"Execution is completed for the test case : {testcase_id}")
#         except Exception as e:
#             Configuration.perform_exe_exception(testcase_id)
#             pytest.fail("Test case execution failed due to the exception -" + str(e))
#         # -----------------------------------------End of Test Execution--------------------------------------
#         # -----------------------------------------Start of Validation----------------------------------------
#         logger.info(f"Starting Validation for the test case : {testcase_id}")
#         GlobalVariables.time_calc.validation.start()
#         logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
#         # -----------------------------------------Start of App Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "app_validation")) == "True":
#             logger.info(f"Started APP validation for the test case : {testcase_id}")
#             try:
#                 # --------------------------------------------------------------------------------------------
#                 date_and_time = date_time_converter.to_app_format(txn_posting_date)
#                 expectedAppValues = {"pmt_mode": "PAY LINK",
#                                      "pmt_status": "AUTHORIZED",
#                                      "txn_amt": str(amount),
#                                      "txn_id": txn_txn_id,
#                                      "rrn": cnp_txn_rrn,
#                                      "order_id": order_id,
#                                      "msg": "PAYMENT SUCCESSFUL",
#                                      "customer_name": txn_customer_name,
#                                      "settle_status": txn_settle_status,
#                                      "auth_code": txn_auth_code,
#                                      "date": date_and_time
#                                      }
#                 logger.debug(f"expectedAppValues: {expectedAppValues}")
#                 app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
#                 loginPage = LoginPage(app_driver)
#                 loginPage.perform_login(app_username, app_password)
#                 homePage = HomePage(app_driver)
#                 homePage.wait_for_navigation_to_load()
#                 homePage.check_home_page_logo()
#                 homePage.wait_for_home_page_load()
#                 homePage.click_on_history()
#                 txnHistoryPage = TransHistoryPage(app_driver)
#                 # txnHistoryPage.click_on_transaction_by_order_id(order_id)
#                 txnHistoryPage.click_on_transaction_by_txn_id(txn_txn_id)
#                 payment_status = txnHistoryPage.fetch_txn_status_text()
#                 logger.info(f"Fetching status from txn history for the txn : {txn_txn_id}, {payment_status}")
#                 payment_mode = txnHistoryPage.fetch_txn_type_text()
#                 logger.info(f"Fetching payment mode from txn history for the txn : {txn_txn_id}, {payment_mode}")
#                 app_txn_id = txnHistoryPage.fetch_txn_id_text()
#                 logger.info(f"Fetching txn_id from txn history for the txn : {txn_txn_id}, {app_txn_id}")
#                 app_amount = txnHistoryPage.fetch_txn_amount_text()
#                 logger.info(f"Fetching txn amount from txn history for the txn : {txn_txn_id}, {app_amount}")
#                 payment_rrn = txnHistoryPage.fetch_RRN_text()
#                 logger.info(f"Fetching txn rrn from txn history for the txn : {txn_txn_id}, {payment_rrn}")
#                 payment_orderId = txnHistoryPage.fetch_order_id_text()
#                 logger.info(f"Fetching txn orderId from txn history for the txn : {txn_txn_id}, {payment_orderId}")
#                 payment_status_msg = txnHistoryPage.fetch_txn_payment_msg_text()
#                 logger.info(f"Fetching txn status message from txn history for the txn : {txn_txn_id}, {payment_status_msg}")
#                 app_date_and_time = txnHistoryPage.fetch_date_time_text()
#                 logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
#                 payment_customer_name = txnHistoryPage.fetch_customer_name_text()
#                 logger.info(
#                     f"Fetching txn customer name from txn history for the txn : {txn_txn_id}, {payment_customer_name}")
#                 payment_settlement_status = txnHistoryPage.fetch_settlement_status_text()
#                 logger.info(
#                     f"Fetching txn settlement status from txn history for the txn : {txn_txn_id}, {payment_settlement_status}")
#
#                 payment_auth_code = txnHistoryPage.fetch_auth_code_text()
#                 logger.info(f"Fetching txn auth code from txn history for the txn : {txn_txn_id}, {payment_auth_code}")
#                 actualAppValues = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
#                                    "txn_amt": app_amount.split(' ')[1],
#                                    "txn_id": app_txn_id,
#                                    "rrn": payment_rrn,
#                                    "order_id": payment_orderId,
#                                    "msg": payment_status_msg,
#                                    "customer_name": payment_customer_name,
#                                    "settle_status": payment_settlement_status,
#                                    "auth_code": payment_auth_code,
#                                    "date": app_date_and_time}
#
#                 logger.debug(f"actualAppValues: {actualAppValues}")
#                 Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
#             except Exception as e:
#                 Configuration.perform_app_val_exception(testcase_id, e)
#             logger.info(f"Completed APP validation for the test case : {testcase_id}")
#         # -----------------------------------------End of App Validation---------------------------------------
#         # -----------------------------------------Start of API Validation------------------------------------
#         if (ConfigReader.read_config("Validations", "api_validation")) == "True":
#             try:
#                 # --------------------------------------------------------------------------------------------
#                 date = date_time_converter.db_datetime(txn_posting_date)
#                 logger.info(f"Started API validation for the test case : {testcase_id}")
#                 expectedAPIValues = {"pmt_status": "AUTHORIZED", "txn_amt": amount,
#                                      "pmt_mode": "CNP", "pmt_state": cnp_txn_state,
#                                      "acquirer_code": cnp_txn_acquirer_code, "settle_status": txn_settle_status,
#                                      "rrn": cnp_txn_rrn, "issuer_code": txn_issuer_code,
#                                      "txn_type": cnpware_txn_txn_type,
#                                      "org_code": org_code,
#                                      "date": date
#                                      }
#                 logger.debug(f"expectedAPIValues: {expectedAPIValues}")
#                 # Use txn details
#                 api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
#                                                                                    "password": app_password})
#                 response = APIProcessor.send_request(api_details)
#                 responseInList = response["txns"]
#                 status_api = ''
#                 amount_api = ''
#                 payment_mode_api = ''
#                 for elements in responseInList:
#                     if elements["txnId"] == txn_txn_id:
#                         status_api = elements["status"]
#                         amount_api = int(elements["amount"])
#                         acquirer_code__api = elements["acquirerCode"]
#                         settlementStatus_api = elements["settlementStatus"]
#                         rrNumber_api = elements["rrNumber"]
#                         issuerCode_api = elements["issuerCode"]
#                         txnType_api = elements["txnType"]
#                         orgCode_api = elements["orgCode"]
#
#                 actualAPIValues = {"pmt_status": status_api, "txn_amt": amount_api,
#                                    "pmt_mode": "CNP", "pmt_state": cnp_txn_state,
#                                    "acquirer_code": acquirer_code__api, "settle_status": settlementStatus_api,
#                                    "rrn": rrNumber_api, "issuer_code": issuerCode_api,
#                                    "txn_type": txnType_api, "org_code": orgCode_api,
#                                    "date": date}
#
#                 logger.debug(f"actualAPIValues: {actualAPIValues}")
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
#             except Exception as e:
#                 Configuration.perform_api_val_exception(testcase_id, e)
#             logger.info(f"Completed API validation for the test case : {testcase_id}")
#         # -----------------------------------------End of API Validation---------------------------------------
#         # -----------------------------------------Start of DB Validation--------------------------------------
#         if (ConfigReader.read_config("Validations", "db_validation")) == "True":
#             try:
#                 # Add other tables for validation as well.
#                 # --------------------------------------------------------------------------------------------
#                 logger.info(f"Started DB validation for the test case : {testcase_id}")
#                 expectedDBValues = {"pmt_status": "AUTHORIZED",
#                                     "pmt_state": "SETTLED",
#                                     "pmt_mode": "CNP",
#                                     "txn_amt": amount,
#                                     "settle_status": "SETTLED",
#                                     "pmt_gateway": "CYBERSOURCE",
#                                     "payment_mode": "CNP",
#                                     "auth_code": txn_auth_code,
#                                     "cnp_pmt_gateway": "CYBERSOURCE",
#                                     "cnpware_pmt_gateway": "CYBERSOURCE",
#                                     "pmt_flow": cnpware_payment_flow,
#                                     "pmt_intent_status":"COMPLETED"
#                                     }
#
#                 logger.debug(f"expectedDBValues: {expectedDBValues}")
#                 query = "select * from txn where id='" + txn_txn_id + "'"
#                 logger.debug(f"Query to fetch data from txn table : {query}")
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Query result : {result}")
#                 pmt_status_db = result["status"].iloc[0]
#                 pmt_mode_db = result["payment_mode"].iloc[0]
#                 txn_amt_db = int(result["amount"].iloc[0])
#                 bank_name_db = result["bank_name"].iloc[0]
#                 settle_status_db = result["settlement_status"].iloc[0]
#                 pmt_state_db = result["state"].iloc[0]
#                 payment_gateway_db = result["payment_gateway"].iloc[0]
#
#                 query = "select * from payment_intent where id='" + payment_intent_id + "'"
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Query result : {result}")
#                 payment_intent_status = result["status"].iloc[0]
#
#                 actualDBValues = {"pmt_status": pmt_status_db,
#                                   "pmt_state": pmt_state_db,
#                                   "pmt_mode": pmt_mode_db,
#                                   "txn_amt": amount,
#                                   "settle_status": settle_status_db,
#                                   "pmt_gateway": payment_gateway_db,
#                                   "payment_mode": pmt_mode_db,
#                                   "auth_code": cnp_txn_auth_code,
#                                   "cnp_pmt_gateway": cnp_payment_gateway,
#                                   "cnpware_pmt_gateway": cnpware_payment_gateway,
#                                   "pmt_flow": cnp_payment_flow,
#                                   "pmt_intent_status":payment_intent_status
#                                   }
#
#                 logger.debug(f"actualDBValues : {actualDBValues}")
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
#             except Exception as e:
#                 Configuration.perform_db_val_exception(testcase_id, e)
#             logger.info(f"Completed DB validation for the test case : {testcase_id}")
#         # -----------------------------------------End of DB Validation---------------------------------------
#         # -----------------------------------------Start of Portal Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
#             logger.info(f"Started Portal validation for the test case : {testcase_id}")
#             try:
#                 # --------------------------------------------------------------------------------------------
#                 expected_portal_values = {}
#                 #
#                 # Write the test case Portal validation code block here. Set this to pass if not required.
#                 #
#                 actual_portal_values = {}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
#                                                 actualPortal=actual_portal_values)
#             except Exception as e:
#                 Configuration.perform_portal_val_exception(testcase_id, e)
#             logger.info(f"Completed Portal validation for the test case : {testcase_id}")
#         # -----------------------------------------End of Portal Validation---------------------------------------
#         if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
#             logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
#             try:
#                 txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_posting_date)
#                 expectedValues = {'CARD TYPE': 'VISA',
#                                   'merchant_ref_no': 'Ref # ' + str(order_id),
#                                   'RRN': str(cnp_txn_rrn),
#                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
#                                   'date': txn_date, "time":txn_time,
#                                   "AUTH CODE": txn_auth_code}
#
#                 receipt_validator.perform_charge_slip_validations(txn_txn_id,
#                                                                   {"username": app_username, "password": app_password},
#                                                                   expectedValues)
#             except Exception as e:
#                 Configuration.perform_charge_slip_val_exception(testcase_id, e)
#             logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
#         # -----------------------------------------End of ChargeSlip Validation---------------------------------------
#         GlobalVariables.time_calc.validation.end()
#         logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
#         logger.info(f"Completed Validation for the test case : {testcase_id}")
#     # -------------------------------------------End of Validation---------------------------------------------
#     finally:
#         query = "update remotepay_setting set setting_value=10 where setting_name='rmpayBumpCount' and org_code='" + org_code + "';"
#         logger.debug(f"Query to update remote pay settings is : {query}")
#         result = DBProcessor.setValueToDB(query)
#         logger.info(f"In finally, remote pay setting is: {result}")
#         Configuration.executeFinallyBlock(testcase_id)
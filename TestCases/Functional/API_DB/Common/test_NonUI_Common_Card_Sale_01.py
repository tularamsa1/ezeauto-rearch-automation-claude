from datetime import time

import pytest
import random
import json
import requests
import sys
from termcolor import colored
import shutil
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_400_401_001():
    """
        Sub Feature Code: NonUI_Common_Card_Sale
        Sub Feature Description:
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = True, config_log= False,closedloop_log=False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            original_amount = random.randint(10,1000)
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Card_Sale_EMV_Debit_VISA', request_body={"amount": original_amount, "externalRefNumber" : "UFAZMJK1ON071341J1" + str(random.randint(0,9))})
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']

                api_details = DBProcessor.get_api_details('Card_Sale_EMV_Debit_VISA_Confirm',
                                                          request_body={"txnId": txn_id ,
                                                                        })
                confirm_response = APIProcessor.send_request(api_details)
                confirm_success = confirm_response['success']
            else:
                logger.error("Card payment Failed")



            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in exept block of testcase function before pytest fails".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

         # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if confirm_success == True:
                    expectedAPIValues = {"success": True, "txn_amt": original_amount, "pmt_mode":"CARD","pmt_status":"AUTHORIZED",
                                        "pmt_state":"AUTHORIZED", "settle_status": "PENDING", "pmt_card_bin":GlobalVariables.HDFC_VISA_DEBIT_BIN,
                                         "pmt_card_brand":"VISA", "pmt_card_type":"DEBIT", "card_txn_type":"EMV", "txn_type":"CHARGE"}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    amount = float(confirm_response['amount'])
                    payment_mode = confirm_response['paymentMode']
                    payment_status = confirm_response['status']
                    payment_state = confirm_response['states'][0]
                    settlement_status = confirm_response['settlementStatus']
                    payment_card_bin = confirm_response['paymentCardBin']
                    payment_card_brand = confirm_response['paymentCardBrand']
                    payment_card_type = confirm_response['paymentCardType']
                    card_txn_type = confirm_response['cardTxnTypeDesc']
                    txn_type = confirm_response['txnType']
                    logger.info(f"API Result: Fetch Response of Card Payment: {card_payment_success}, {amount}, {payment_mode}, {payment_status},{settlement_status},{payment_mode}, {payment_state}, {settlement_status},{payment_card_bin},{payment_card_brand}, {payment_card_type}, {card_txn_type},{txn_type}")

                    actualAPIValues = {"success": confirm_success,"txn_amt": amount, "pmt_mode":payment_mode,"pmt_status":payment_status,
                                        "pmt_state":payment_state, "settle_status":settlement_status, "pmt_card_bin":payment_card_bin,
                                         "pmt_card_brand":payment_card_brand, "pmt_card_type":payment_card_type, "card_txn_type":card_txn_type, "txn_type":txn_type}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    logger.error("confirm card Payment is not successfull")

            except Exception as e:
                msg = "Card Payment Failed"
                print("API Validation failed due to exception - "+str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")


        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        # if (ConfigReader.read_config("Validations", "db_validation")) == "True":
        #     logger.info(f"Started DB validation for the test case : {testcase_id}")
        #     try:
        #         logger.debug(f"Agency Balance before Top Up : {agency_balance_before}")
        #         logger.debug(f"Actual amount for Top Up  : {original_amount}")
        #
        #         expectedDBValues = {"txn_amt":original_amount,"pmt_mode":payment_mode, "settle_status":settlement_status,
        #                             "pmt_status":status,
        #                             "agency_balance": (agency_balance_before + original_amount)}
        #         logger.debug(f"expectedDBValues: {expectedDBValues}")
        #
        #         query_txn = "select id, amount, payment_mode, settlement_status, status from txn where id = '"+txn_id+"';"
        #         result_txn = DBProcessor.getValueFromDB(query_txn)
        #         logger.debug(f"Query result URL: {result_txn}")
        #
        #         txn_amt = float(result_txn["amount"].iloc[0])
        #         pmt_mode = result_txn["payment_mode"].iloc[0]
        #         settle_status = result_txn["settlement_status"].iloc[0]
        #         pmt_status = result_txn["status"].iloc[0]
        #
        #         query_wallet = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        #         logger.debug(f"Query to fetch data from account table : {query_wallet}")
        #         result_wallet = DBProcessor.getValueFromDB(query_wallet, "closedloop")
        #         logger.debug(f"Query result URL: {result_wallet}")
        #         bal_after_posting = float(result_wallet["balance"].iloc[0])
        #
        #
        #         actualDBValues = {"txn_amt":txn_amt,"pmt_mode":pmt_mode, "settle_status":settle_status,
        #                             "pmt_status":pmt_status,"agency_balance": bal_after_posting}
        #         logger.debug(f"actualDBValues : {actualDBValues}")
        #         Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
        #
        #     except Exception as e:
        #         print("DB Validation failed due to exception - "+str(e))
        #         msg = msg + "DB Validation did not complete due to exception.\n"
        #         GlobalVariables.bool_val_exe = False
        #         GlobalVariables.str_db_val_result= 'Fail'
        #
        #     logger.info(f"Completed DB validation for the test case : {testcase_id}")
        #
        #
        # # -----------------------------------------End of DB Validation---------------------------------------
        # GlobalVariables.time_calc.validation.end()
        # print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))
import random
import re
import shutil
import time
from datetime import datetime, date
import pytest
import sys
from termcolor import colored

from Configuration import Configuration
from DataProvider import GlobalVariables, GlobalConstants
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, merchant_creator, \
    Ezewallet_Setup
from Utilities.execution_log_processor import EzeAutoLogger


logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_001():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_DigitalTopUp_Agent
        Sub Feature Description: API to perform a Digital TopUp of an Agent using Card Payment
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False, closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            original_amount = random.randint(100,1000)
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=Ezewallet_Setup.org_code,acquisition="HDFC",payment_gateway="DUMMY")
            api_details = DBProcessor.get_api_details('Digital_Agent_TopUp_Card', request_body={"deviceSerial":device_serial,"username": Ezewallet_Setup.agent_user, "password": Ezewallet_Setup.agent_password,
                                                                        "amount": original_amount, "externalRefNumber" : "UFAZMJK1ON071341J1" + str(random.randint(0,9))})
            response = APIProcessor.send_request(api_details)

            card_payment_success = response['success']
            amount = float(response['amount'])
            txn_id = response['txnId']
            status = response['status']
            payment_mode = response['paymentMode']
            settlement_status = response['settlementStatus']
            account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of Card Payment - Digital Agent Top Up: {card_payment_success}, {amount},{payment_mode},{settlement_status}, {txn_id}, {status}, {account_label}")

            GlobalVariables.selftopup_amt += original_amount
            GlobalVariables.selftopup_count += 1

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

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if card_payment_success == True:
                    expectedAPIValues = {"success": True, "txn_amt": original_amount, "pmt_status":"AUTHORIZED",
                                         "settle_status":"PENDING",
                                        "pmt_mode":"CARD","account_label": "TOPUP", "balance":agent_balance_before+original_amount}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    query = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
                    result = DBProcessor.getValueFromDB(query, "closedloop")
                    bal_after_posting = float(result["balance"].iloc[0])

                    actualAPIValues = {"success": card_payment_success, "txn_amt": amount, "pmt_status":status,
                                       "settle_status": settlement_status,
                                       "pmt_mode": payment_mode,"account_label": account_label, "balance":bal_after_posting}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                    if GlobalVariables.str_api_val_result == "Pass":
                        logger.info("Posting is Successfull")
                    else:
                        logger.error("Posting is Unsuccesfull")
                else:
                    raise Exception("Card Payment is not successfull")



            except Exception as e:
                msg = "Digital Top up has been failed for an Agent" + Ezewallet_Setup.agent_user
                print("API Validation failed due to exception - "+str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")


        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Top Up : {agent_balance_before}")
                logger.debug(f"Actual amount for Top Up  : {original_amount}")

                expectedDBValues = {"txn_amt":original_amount,"pmt_mode":payment_mode, "settle_status":settlement_status,
                                    "pmt_status":status,"agent_balance": (agent_balance_before + original_amount)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select id, amount, payment_mode, settlement_status, status from txn where id = '" + txn_id + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result URL: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]

                query_wallet = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
                logger.debug(f"Query to fetch data from account table : {query_wallet}")
                result_wallet = DBProcessor.getValueFromDB(query_wallet, "closedloop")
                logger.debug(f"Query result URL: {result_wallet}")
                bal_after_posting = float(result_wallet["balance"].iloc[0])
                actualDBValues = {"txn_amt":txn_amt,"pmt_mode":pmt_mode, "settle_status":settle_status,
                                    "pmt_status":pmt_status,"agent_balance": bal_after_posting}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

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




@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_002():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_DigitalTopUp_Agent_UPI
        Sub Feature Description: API to perform a Digital TopUp of an Agent using UPI Payment and validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            original_amount = random.randint(200,300)
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Digital_Agent_TopUp_UPI', request_body={"username": Ezewallet_Setup.agent_user,
                                                                                               "password": Ezewallet_Setup.agent_password,
                                                                                                "amount": original_amount})
            response = APIProcessor.send_request(api_details)

            upi_payment_success = response['success']
            amount = float(response['amount'])
            txn_id = response['txnId']
            payment_mode = response['paymentMode']
            status = response['status']
            settlement_status = response['settlementStatus']
            account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of UPI QR generation: {upi_payment_success}, {amount}, {txn_id},{payment_mode},{settlement_status}, {status}, {account_label}")

            if upi_payment_success == True:
                time.sleep(2)
                api_details = DBProcessor.get_api_details('Confirm_UPI',
                                                          request_body={"username": Ezewallet_Setup.agent_user,
                                                                        "password": Ezewallet_Setup.agent_password,
                                                                        "txnId": txn_id})
                response = APIProcessor.send_request(api_details)
                confirm_upi_success = response['success']
                error_code = response['errorCode']
                real_code = response['realCode']
                confirm_amount = response['amount']
                confirm_settlement_status = response['settlementStatus']
                confirm_status = response['status']
                confirm_accountlabel = response['accountLabel']
                confirm_payment_mode = response['paymentMode']
                logger.info(f"API Result: Fetch Response of UPI confirm - Digital Agent Top Up: {confirm_upi_success}, {error_code}, {real_code},{confirm_amount},{confirm_payment_mode},{confirm_status}, {confirm_settlement_status}, {confirm_accountlabel}")

                GlobalVariables.selftopup_amt += original_amount
                GlobalVariables.selftopup_count += 1

            else:
                logger.error("UPI QR generation is not successfull")

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

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:

                expectedAPIValues = {"success": True, "txn_amt": original_amount, "pmt_status":"PENDING",
                                    "settle_status":"PENDING","account_label": "TOPUP","pmt_mode":"UPI",
                                      "confirm_success":False,"error_code":"EZETAP_0000703","real_code":"STOP_PAYMENT_NOT_ALLOWED_FOR_AUTHORIZED_TRANSACTION",
                                     "confirm_amt":original_amount,"confirm_settle_status":"SETTLED", "confirm_pmt_status":"AUTHORIZED",
                                     "confirm_account_label":"TOPUP","confirm_pmt_mode":"UPI","balance":agent_balance_before+original_amount}

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                query = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
                result = DBProcessor.getValueFromDB(query, "closedloop")
                bal_after_posting = float(result["balance"].iloc[0])

                actualAPIValues = {"success": True, "txn_amt": original_amount, "pmt_status":status,
                                    "settle_status":settlement_status,"account_label":account_label,"pmt_mode":payment_mode,
                                      "confirm_success":confirm_upi_success,"error_code":error_code,"real_code":real_code,
                                     "confirm_amt":confirm_amount,"confirm_settle_status":confirm_settlement_status, "confirm_pmt_status":confirm_status,
                                     "confirm_account_label":confirm_accountlabel,"confirm_pmt_mode":confirm_payment_mode,"balance":bal_after_posting}
                logger.debug(f"actualAPIValues: {actualAPIValues}")


                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)



            except Exception as e:
                msg = "Digital Top up has been failed for an Agent" + Ezewallet_Setup.agent_user
                print("API Validation failed due to exception - "+str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")


        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Top Up : {agent_balance_before}")
                logger.debug(f"Actual amount for Top Up  : {original_amount}")

                expectedDBValues = {"txn_amt": original_amount, "pmt_mode": confirm_payment_mode,
                                    "settle_status": confirm_settlement_status,
                                    "pmt_status": confirm_status,"agent_balance": (agent_balance_before + original_amount)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select id, amount, payment_mode, settlement_status, status from txn where id = '" + txn_id + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result URL: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]

                query_wallet = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
                logger.debug(f"Query to fetch data from account table : {query_wallet}")
                result_wallet = DBProcessor.getValueFromDB(query_wallet, "closedloop")
                logger.debug(f"Query result URL: {result_wallet}")
                bal_after_posting = float(result_wallet["balance"].iloc[0])
                actualDBValues = {"txn_amt": txn_amt, "pmt_mode": pmt_mode, "settle_status": settle_status,
                                  "pmt_status": pmt_status, "agent_balance": bal_after_posting}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

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




@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_003():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_DigitalTopUp_Agent_for_higher_amount
        Sub Feature Description: API to perform a Digital TopUp of an Agent using Card Payment af higher amount and validate the result
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            original_amount = random.randint(100000,1000000)
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=Ezewallet_Setup.org_code,acquisition="HDFC",payment_gateway="DUMMY")
            api_details = DBProcessor.get_api_details('Digital_Agent_TopUp_Card', request_body={"deviceSerial":device_serial,"username": Ezewallet_Setup.agent_user, "password": Ezewallet_Setup.agent_password,
                                                                        "amount": original_amount, "externalRefNumber" : "UFAZMJK1ON071341J1" + str(random.randint(0,9))})
            response = APIProcessor.send_request(api_details)

            card_payment_success = response['success']
            error_code = response['errorCode']
            error_message = response['errorMessage']
            real_code = response['realCode']
            api_message_text = response['apiMessageText']
            api_message_title = response['apiMessageTitle']
            username = response['username']
            logger.info(f"API Result: Fetch Response of Card Payment - Digital Agent Top Up: {card_payment_success},{error_code}, {error_message}, {real_code}, {api_message_text}, {api_message_title},{username}")

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

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:

                expectedAPIValues = {"success": False, "error_code": "EZETAP_0000164", "error_message":"Transaction declined. Amount entered is more than maximum allowed for the transaction. Maximum Allowed: 100000"
                                    , "api_message_text":"EZETAP_0000164 Transaction declined. Amount entered is more than maximum allowed for the transaction. Maximum Allowed: 100000","real_code":"AMOUNT_MORE_THAN_ALLWD",
                                    "api_message_title":"DECLINED","username":Ezewallet_Setup.agent_user}

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")


                actualAPIValues = {"success": card_payment_success, "error_code": error_code, "error_message":error_message
                                    , "api_message_text":api_message_text,"real_code":real_code,
                                    "api_message_title":api_message_title,"username":username}
                logger.debug(f"actualAPIValues: {actualAPIValues}")


                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                msg = "Digital Top up has been failed for an Agent" + Ezewallet_Setup.agent_user
                print("API Validation failed due to exception - "+str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")


        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Top Up : {agent_balance_before}")
                logger.debug(f"Actual amount for Top Up  : {original_amount}")

                expectedDBValues = {"agent_balance": agent_balance_before}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                bal_after_posting = float(result["balance"].iloc[0])
                actualDBValues = {"agent_balance": bal_after_posting}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

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





@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_004():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Cash_collection
        Sub Feature Description: API to perform a Cash payment as a BILLPAY and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_Setup.org_code + "';"
        balance = DBProcessor.getValueFromDB(settlement_bal_check, "closedloop")
        settlement_bal_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Cash_Collection', request_body={"username": Ezewallet_Setup.agent_user,
                                                                                       "password": Ezewallet_Setup.agent_password})
            response = APIProcessor.send_request(api_details)

            original_amount_cashpay = float(api_details["RequestBody"]["amount"])
            cash_payment_success = response['success']
            username = response['username']
            amount = float(response['amount'])
            txn_id = response['txnId']
            status = response['status']
            settlement_status = response['settlementStatus']
            clw_status = response['clwStatus']
            account_label = response['accountLabel']
            payment_mode = response['paymentMode']

            logger.info(f"API Result: Fetch Response of Cash Payment - BILLPAY: {cash_payment_success}, {original_amount_cashpay},{payment_mode} {username}, {amount},{settlement_status}, {clw_status}, {txn_id}, {status}, {account_label}")

            GlobalVariables.cash_txn_id = txn_id
            GlobalVariables.collection_amt += original_amount_cashpay
            GlobalVariables.collection_count += 1

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

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if cash_payment_success == True:
                    expectedAPIValues = {"success": True, "username": Ezewallet_Setup.agent_user, "txn_amt": original_amount_cashpay, "pmt_status":"AUTHORIZED",
                                         "settle_status":"SETTLED","account_label": "BILLPAY","clw_status": "SUCCESS",
                                         "balance":agent_balance_before - original_amount_cashpay}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    query_agent_bal = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
                    result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                    agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])

                    actualAPIValues = {"success": cash_payment_success, "username": username, "txn_amt": amount, "pmt_status":status,
                                        "settle_status":settlement_status,"account_label": account_label,"clw_status":clw_status,
                                        "balance":agentbal_after_cash_payment}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Cash Payment is not successfull")

            except Exception as e:
                msg = "Cash Payment has been failed" + Ezewallet_Setup.agent_user
                print("API Validation failed due to exception - "+str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")


        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Cash Payment : {agent_balance_before}")
                logger.debug(f"Actual amount for BILLPAY  : {original_amount_cashpay}")

                expectedDBValues = {"txn_amt":original_amount_cashpay,"pmt_mode":payment_mode, "settle_status":settlement_status,
                                    "pmt_status":status,"agent_balance": agent_balance_before - original_amount_cashpay,
                                    "settlement_balance": settlement_bal_before + original_amount_cashpay}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select id, amount, payment_mode, settlement_status, status from txn where id = '" + txn_id + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result URL: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]

                query_agent_bal = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_Setup.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_cash_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"txn_amt":txn_amt,"pmt_mode":pmt_mode, "settle_status":settle_status,
                                    "pmt_status":pmt_status,"agent_balance": agentbal_after_cash_payment,
                                    "settlement_balance": settlementbal_after_cash_payment}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_005():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Refund_Cash_collected_BILLPAY
        Sub Feature Description: API to perform a Refund txn for the cash collected as a BILLPAY and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_Setup.org_code + "';"
        balance = DBProcessor.getValueFromDB(settlement_bal_check, "closedloop")
        settlement_bal_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,config_log=False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))
            api_details = DBProcessor.get_api_details('Refund_cash_Payment',
                                                      request_body={"username": Ezewallet_Setup.agent_user,
                                                                    "password": Ezewallet_Setup.agent_password,
                                                                    "originalTransactionId": GlobalVariables.cash_txn_id})
            response = APIProcessor.send_request(api_details)

            original_amount_refunded = float(api_details["RequestBody"]["amount"])
            refund_payment_success = response['success']
            username = response['username']
            amount = float(response['amount'])
            txn_id = response['txnId']
            txn_type = response['txnType']
            status = response['status']
            settlement_status = response['settlementStatus']
            account_label = response['accountLabel']
            payment_mode = response['paymentMode']
            logger.info(f"API Result: Fetch Response of Refund Payment: {refund_payment_success},{txn_type},{payment_mode},{original_amount_refunded}, {username}, {amount},{settlement_status}, {txn_id}, {status}, {account_label}")


            GlobalVariables.refund_amt += original_amount_refunded
            GlobalVariables.refund_count += 1
            GlobalVariables.collection_amt -= original_amount_refunded
            GlobalVariables.collection_count -= 1

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored(
                "Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                     "="), 'cyan'))
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in exept block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if refund_payment_success == True:
                    expectedAPIValues = {"success": True, "username": Ezewallet_Setup.agent_user,
                                         "txn_amt": original_amount_refunded, "pmt_status": "REFUNDED",
                                         "settle_status": "SETTLED", "account_label": "BILLPAY",
                                         "balance": agent_balance_before + original_amount_refunded}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    query_agent_bal = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
                    result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                    agentbal_after_refund = float(result_agent_bal["balance"].iloc[0])

                    actualAPIValues = {"success": refund_payment_success, "username": username, "txn_amt": amount,
                                       "pmt_status": status,
                                       "settle_status": settlement_status, "account_label": account_label,
                                       "balance": agentbal_after_refund}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Refund Payment is not successfull")

            except Exception as e:
                msg = "Refund Payment has been failed" + Ezewallet_Setup.agent_user
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Refund Payment : {agent_balance_before}")
                logger.debug(f"Actual amount for Refund  : {original_amount_refunded}")

                expectedDBValues = {"txn_amt":original_amount_refunded,"pmt_mode":payment_mode, "settle_status":settlement_status,
                                    "pmt_status":status,"agent_balance": agent_balance_before + original_amount_refunded,
                                    "settlement_balance": settlement_bal_before -  original_amount_refunded}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select id, amount, payment_mode, settlement_status, status from txn where id = '" + txn_id + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result URL: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]

                query_agent_bal = "select balance from account where entity_id = '" + Ezewallet_Setup.agent_user + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_Setup.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_cash_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"txn_amt":txn_amt,"pmt_mode":pmt_mode, "settle_status":settle_status,
                                    "pmt_status":pmt_status,"agent_balance": agentbal_after_cash_payment,
                                  "settlement_balance": settlementbal_after_cash_payment}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")

        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))










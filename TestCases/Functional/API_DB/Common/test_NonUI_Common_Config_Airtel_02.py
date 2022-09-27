import json
from datetime import datetime
import pytest
from termcolor import colored
import shutil
import requests
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_302_006():
    """
        Sub Feature Code: NonUI_Common_Config_Airtel_fetch_get_postpaid_Account
        Sub Feature Description: fetching details of Airtel Merchant having key "get_postpaid_Account" via fetch/data API
        TC naming code description:
        300: Config
        302: Airtel
        006: TC006
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------


        GlobalVariables.setupCompletedSuccessfully = True
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,config_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
            api_details = DBProcessor.get_api_details('fetch_get_postpaid_Account')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            msg = response['data']['response'][0]['msg']
            current_outstanding = response['data']['response'][0]['currentOutstanding']
            min_amt = response['data']['response'][0]['_minAmount']
            airtel_no = response['data']['response'][0]['airtelNo']
            classification = response['data']['response'][0]['classification']
            customer_name = response['data']['response'][0]['customerName']
            usimuser = response['data']['response'][0]['uSimUser']
            customer_account_id = response['data']['response'][0]['customerAccountId']
            customer_class = response['data']['response'][0]['customerClass']
            airtel_customer = response['data']['response'][0]['airtelCustomer']
            segment = response['data']['response'][0]['segment']
            amt_field = response['data']['response'][0]['_amountField']
            invoice_no = response['data']['response'][0]['invoiceNo']
            max_amt = response['data']['response'][0]['_maxAmount']

            logger.info(f"API Result: Fetch Response for Airtel Merchant : {success},{msg},{current_outstanding},{min_amt},{airtel_no},{classification},"
                f"{customer_name}, {usimuser},{customer_account_id},{customer_class},{airtel_customer},{segment},{amt_field},{invoice_no},{max_amt}")

            # ------------------------------------------------------------------------------------------------
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
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "msg": "success", "current_outstanding": "214", "min_amt": "1",
                                      "airtel_no": "1-3775086096255",
                                      "classification": "B2C", "customer_name": "Kuvadiya", "usimuser": "NO",
                                      "customer_account_id": "1-3775086096255",
                                      "customer_class": "NO", "airtel_customer": "No", "segment": "Corporate",
                                      "amt_field": "214.49",
                                      "invoice_no": "BM2324I001297728", "max_amt": "50000"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "msg": msg, "current_outstanding": current_outstanding,
                                    "min_amt": min_amt, "airtel_no": airtel_no,
                                    "classification": classification, "customer_name": customer_name,
                                    "usimuser": usimuser, "customer_account_id": customer_account_id,
                                    "customer_class": customer_class, "airtel_customer": airtel_customer,
                                    "segment": segment, "amt_field": amt_field,
                                    "invoice_no": invoice_no, "max_amt": max_amt}

                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = { "Result": '{"success": true, "data": {"response": [{"msg": "success", "currentOutstanding": "214", "_minAmount": "1", "airtelNo": "1-3775086096255", "classification": "B2C", "customerName": "Kuvadiya", "uSimUser": "NO", "customerAccountId": "1-3775086096255", "customerClass": "NO", "airtelCustomer": "No", "segment": "Corporate", "_amountField": "214.49", "invoiceNo": "BM2324I001297728", "_maxAmount": "50000"}]}}'}
                # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                # actualAPIValues2 = {"Result": response_data}
                # logger.debug(f"actualAPIValues: {actualAPIValues2}")
                #
                # Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/QcZuZJ/application/K1VtY7/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_postpaid_Account') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
                result = DBProcessor.getValueFromDB(query, "config")
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))



        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='AIRTELULB540943' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result) > 1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))





@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_302_007():
    """
        Sub Feature Code: NonUI_Common_Config_Airtel_fetch_get_fixedLine_Mobile
        Sub Feature Description: fetching details of Airtel Merchant having key "get_fixedLine_Mobile" via fetch/data API
        TC naming code description:
        300: Config
        302: Airtel
        007: TC007
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------


        GlobalVariables.setupCompletedSuccessfully = True
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,config_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
            api_details = DBProcessor.get_api_details('fetch_get_fixedLine_Mobile')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            msg = response['data']['response'][0]['msg']
            current_outstanding = response['data']['response'][0]['currentOutstanding']
            min_amt = response['data']['response'][0]['_minAmount']
            airtel_no = response['data']['response'][0]['airtelNo']
            classification = response['data']['response'][0]['classification']
            customer_name = response['data']['response'][0]['customerName']
            usimuser = response['data']['response'][0]['uSimUser']
            customer_account_id = response['data']['response'][0]['customerAccountId']
            customer_class = response['data']['response'][0]['customerClass']
            airtel_customer = response['data']['response'][0]['airtelCustomer']
            segment = response['data']['response'][0]['segment']
            amt_field = response['data']['response'][0]['_amountField']
            invoice_no = response['data']['response'][0]['invoiceNo']
            max_amt = response['data']['response'][0]['_maxAmount']

            logger.info(
                f"API Result: Fetch Response for Airtel Merchant : {success},{msg},{current_outstanding},{min_amt},{airtel_no},{classification},"
                f"{customer_name}, {usimuser},{customer_account_id},{customer_class},{airtel_customer},{segment},{amt_field},{invoice_no},{max_amt}")

            # ------------------------------------------------------------------------------------------------
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
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "msg": "success", "current_outstanding": "590", "min_amt": "1",
                                      "airtel_no": "01141550070",
                                      "classification": "B2C", "customer_name": "OM FASTNER", "usimuser": "NO",
                                      "customer_account_id": "7035432683",
                                      "customer_class": "NO", "airtel_customer": "No", "segment": "Commercial",
                                      "amt_field": "589.64",
                                      "invoice_no": "HT2307I001735709", "max_amt": "50000"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "msg": msg, "current_outstanding": current_outstanding,
                                    "min_amt": min_amt, "airtel_no": airtel_no,
                                    "classification": classification, "customer_name": customer_name,
                                    "usimuser": usimuser, "customer_account_id": customer_account_id,
                                    "customer_class": customer_class, "airtel_customer": airtel_customer,
                                    "segment": segment, "amt_field": amt_field,
                                    "invoice_no": invoice_no, "max_amt": max_amt}

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"msg": "success", "currentOutstanding": "590", "_minAmount": "1", "airtelNo": "01141550070", "classification": "B2C", "customerName": "OM FASTNER", "uSimUser": "NO", "customerAccountId": "7035432683", "customerClass": "NO", "airtelCustomer": "No", "segment": "Commercial", "_amountField": "589.64", "invoiceNo": "HT2307I001735709", "_maxAmount": "50000"}]}}'}
                # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                # actualAPIValues2 = {"Result": response_data}
                # logger.debug(f"actualAPIValues: {actualAPIValues2}")
                #
                # Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/QcZuZJ/application/Wg0jZL/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_fixedLine_Mobile') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
                result = DBProcessor.getValueFromDB(query, "config")
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))




        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='AIRTELULB540943' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result) > 1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_302_008():
    """
        Sub Feature Code: NonUI_Common_Config_Airtel_fetch_get_fixedLine_Account
        Sub Feature Description: fetching details of Airtel Merchant having key "get_fixedLine_Account" via fetch/data API
        TC naming code description:
        300: Config
        302: Airtel
        008: TC008
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------


        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,config_log=True)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
            api_details = DBProcessor.get_api_details('fetch_get_fixedLine_Account')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            msg = response['data']['response'][0]['msg']
            current_outstanding = response['data']['response'][0]['currentOutstanding']
            min_amt = response['data']['response'][0]['_minAmount']
            airtel_no = response['data']['response'][0]['airtelNo']
            classification = response['data']['response'][0]['classification']
            customer_name = response['data']['response'][0]['customerName']
            usimuser = response['data']['response'][0]['uSimUser']
            customer_account_id = response['data']['response'][0]['customerAccountId']
            customer_class = response['data']['response'][0]['customerClass']
            airtel_customer = response['data']['response'][0]['airtelCustomer']
            segment = response['data']['response'][0]['segment']
            amt_field = response['data']['response'][0]['_amountField']
            invoice_no = response['data']['response'][0]['invoiceNo']
            max_amt = response['data']['response'][0]['_maxAmount']

            logger.info(f"API Result: Fetch Response for Airtel Merchant : {success},{msg},{current_outstanding},{min_amt},{airtel_no},{classification},"
                f"{customer_name}, {usimuser},{customer_account_id},{customer_class},{airtel_customer},{segment},{amt_field},{invoice_no},{max_amt}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))
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
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "msg": "success", "current_outstanding": "0", "min_amt": "1",
                                      "airtel_no": "12299726",
                                      "classification": "B2C", "customer_name": "Meenakshi", "usimuser": "NO",
                                      "customer_account_id": "12299726",
                                      "customer_class": "NO", "airtel_customer": "No", "segment": "Home",
                                      "amt_field": "0.07",
                                      "invoice_no": "HT2329I001253462", "max_amt": "50000"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "msg": msg, "current_outstanding": current_outstanding,
                                    "min_amt": min_amt, "airtel_no": airtel_no,
                                    "classification": classification, "customer_name": customer_name,
                                    "usimuser": usimuser, "customer_account_id": customer_account_id,
                                    "customer_class": customer_class, "airtel_customer": airtel_customer,
                                    "segment": segment, "amt_field": amt_field,
                                    "invoice_no": invoice_no, "max_amt": max_amt}

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"msg": "success", "currentOutstanding": "0", "_minAmount": "1", "airtelNo": "12299726", "classification": "B2C", "customerName": "Meenakshi", "uSimUser": "NO", "customerAccountId": "12299726", "customerClass": "NO", "airtelCustomer": "No", "segment": "Home", "_amountField": "0.07", "invoiceNo": "HT2329I001253462", "_maxAmount": "50000"}]}}'}
                # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                # actualAPIValues2 = {"Result": response_data}
                # logger.debug(f"actualAPIValues: {actualAPIValues2}")
                #
                # Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/QcZuZJ/application/EUki2j/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_fixedLine_Account') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
                result = DBProcessor.getValueFromDB(query, "config")
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))




        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='AIRTELULB540943' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result) > 1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))




@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_302_009():
    """
        Sub Feature Code: NonUI_Common_Config_Airtel_fetch_get_prepaid_details
        Sub Feature Description: fetching details of Airtel Merchant having key "get_prepaid_details" via fetch/data API
        TC naming code description:
        300: Config
        302: Airtel
        009: TC009
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,config_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
            api_details = DBProcessor.get_api_details('fetch_get_prepaid_details')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            msg = response['data']['response'][0]['msg']
            cust_cat = response['data']['response'][0]['cust_cat']
            si = response['data']['response'][0]['si']
            cust_type = response['data']['response'][0]['cust_type']
            si_lob = response['data']['response'][0]['si_lob']
            si_sts = response['data']['response'][0]['si_sts']
            arpu = response['data']['response'][0]['arpu']
            circle = response['data']['response'][0]['circle']
            act_date = response['data']['response'][0]['act_date']
            si_seg = response['data']['response'][0]['si_seg']
            cust_tier = response['data']['response'][0]['cust_tier']

            logger.info(f"API Result: Fetch Response for Airtel Merchant : {success},{msg},{cust_cat},{si},{cust_type},{si_lob},"
                f"{si_sts}, {arpu},{circle},{act_date},{si_seg},{cust_tier}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))
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
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "msg": "success" ,"cust_cat": "SILVERNEW" ,"si": "919988735802" ,"cust_type": "SILVERNEW" ,
                                      "si_lob": "PREPAID" ,"si_sts": "ACTIV" , "arpu": "0" ,"circle": "Punjab" ,"act_date": "20220506131650" ,
                                      "si_seg": "Silver 3" ,"cust_tier":"SILVER"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "msg": msg ,"cust_cat": cust_cat,"si": si ,"cust_type": cust_type,
                                      "si_lob": si_lob ,"si_sts": si_sts , "arpu":arpu,"circle": circle ,"act_date": act_date,
                                      "si_seg": si_seg ,"cust_tier":cust_tier}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"msg": "success", "cust_cat": "SILVERNEW", "si": "919988735802", "cust_type": "SILVERNEW", "si_lob": "PREPAID", "si_sts": "ACTIV", "arpu": "0", "circle": "Punjab", "act_date": "20220506131650", "si_seg": "Silver 3", "cust_tier": "SILVER"}]}}'}
                # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                # actualAPIValues2 = {"Result": response_data}
                # logger.debug(f"actualAPIValues: {actualAPIValues2}")
                #
                # Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/QcZuZJ/application/9fGxOs/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_prepaid_details') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
                result = DBProcessor.getValueFromDB(query, "config")
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))



        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='AIRTELULB540943' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result) > 1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_302_010():
    """
            Sub Feature Code: NonUI_Common_Config_Airtel_fetch_get_active_butterfly
            Sub Feature Description: fetching details of Airtel Merchant having key "get_active_butterfly" via fetch/data API
            TC naming code description:
            300: Config
            302: Airtel
            010: TC010
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,config_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
            api_details = DBProcessor.get_api_details('fetch_get_active_butterfly')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            msg = response['data']['response'][0]['msg']
            order_no = response['data']['response'][0]['orderNo']
            min_amt = response['data']['response'][0]['_minAmount']
            amt = response['data']['response'][0]['Amount']
            field_label = response['data']['response'][0]['field_label']
            caf_number1 = response['data']['response'][0]['cafNumber1']
            airtel_no = response['data']['response'][0]['airtelNo']
            type = response['data']['response'][0]['type']
            sales_channel_id = response['data']['response'][0]['salesChannelId']
            caf_number = response['data']['response'][0]['cafNumber']
            order_no1 = response['data']['response'][0]['orderNo1']
            field_key = response['data']['response'][0]['field_key']
            amt_field = response['data']['response'][0]['_amountField']
            field_value = response['data']['response'][0]['field_value']
            vanity_charges = response['data']['response'][0]['vanityCharges']
            max_amount = response['data']['response'][0]['_maxAmount']
            circle = response['data']['response'][0]['circle']
            airtel_no1 = response['data']['response'][0]['airtelNo1']
            total = response['data']['response'][0]['0Li+1::null::1-HIVF::23']

            logger.info(
                f"API Result: Fetch Response for Airtel Merchant : {success},{msg},{order_no},{min_amt},{amt},{field_label},"
                f"{caf_number1}, {airtel_no},{type},{sales_channel_id},{caf_number},{order_no1},{field_key},{amt_field},{field_value}"
                f"{vanity_charges},{max_amount},{circle},{airtel_no1},{total}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))
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
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "msg": "success" ,"order_no": "21-4186354405372" ,"min_amt": "0.01" ,
                                    "amt": "2500" ,"field_label": "Vanity Charge" ,
                                    "caf_number1": """{"name":"accountId","value":"D274391527"},{"description":"CAF No.","name":"accountId","value":"D274391527"},{"name":"ref","value":"D274391527"},""" ,
                                    "airtel_no": "9898863555" ,"type": "CAFNumber" ,"sales_channel_id": "-11557" ,"caf_number": "D274391527" ,
                                    "order_no1": """{"name": "orderNumber","value": "21-4186354405372","description": null},{"name": "orderNumber","value": "21-4186354405372","description": "Order No."},""" ,
                                    "field_key": "0Li+1::null::1-HIVF::23" ,"amt_field": "2500" ,"field_value": "2500" ,
                                    "vanity_charges": "2500" ,"max_amount": "1000000" ,"circle": "GJ" ,
                                    "airtel_no1":"""{"name": "airtelNo","value": "9898863555","description": "Airtel No."},{"name": "airtelNo","value": "9898863555","description": "Proposed Phone No."},""", "total":"2500"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "msg": msg ,"order_no": order_no ,"min_amt": min_amt ,
                                    "amt": amt ,"field_label": field_label ,
                                    "caf_number1": caf_number1 ,
                                    "airtel_no": airtel_no,"type": type,"sales_channel_id":sales_channel_id,"caf_number": caf_number,
                                    "order_no1": order_no1 ,
                                    "field_key": field_key ,"amt_field":amt_field,"field_value": field_value ,
                                    "vanity_charges": vanity_charges ,"max_amount": max_amount ,"circle": circle ,
                                    "airtel_no1":airtel_no1, "total":total}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"msg": "success", "orderNo": "21-4186354405372", "_minAmount": "0.01", "Amount": "2500", "field_label": "Vanity Charge", "cafNumber1": "{"name":"accountId","value":"D274391527"},{"description":"CAF No.","name":"accountId","value":"D274391527"},{"name":"ref","value":"D274391527"},", "airtelNo": "9898863555", "type": "CAFNumber", "salesChannelId": "-11557", "cafNumber": "D274391527", "orderNo1": "{"name": "orderNumber","value": "21-4186354405372","description": null},{"name": "orderNumber","value": "21-4186354405372","description": "Order No."},", "field_key": "0Li+1::null::1-HIVF::23", "_amountField": "2500", "field_value": "2500", "vanityCharges": "2500", "_maxAmount": "1000000", "circle": "GJ", "airtelNo1": "{"name": "airtelNo","value": "9898863555","description": "Airtel No."},{"name": "airtelNo","value": "9898863555","description": "Proposed Phone No."},", "0Li+1::null::1-HIVF::23": "2500"}]}}'}
                # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                # actualAPIValues2 = {"Result": response_data.replace("\\", "")}
                # logger.debug(f"actualAPIValues: {actualAPIValues2}")
                #
                # Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/QcZuZJ/application/PdIlZB/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_active_butterfly') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
                result = DBProcessor.getValueFromDB(query, "config")
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))



        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='AIRTELULB540943' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result) > 1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
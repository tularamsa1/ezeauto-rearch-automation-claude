import json
import random
import shutil
from datetime import datetime
import pytest
import requests
from termcolor import colored

from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, Config_processor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_301_001():
    """
        Sub Feature Code: NonUI_Common_Config_Goa_fetch_get_tax_outstandingV3
        Sub Feature Description: fetching details of Goa Merchant having key "get_tax_outstandingV3" via fetch/data API
        TC naming code description:
        300: Config
        301: Goa
        001: TC001
    """

    try:
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            org_code = Config_processor.get_config_details_from_excel("Goa")["MerchantCode"]
            username = Config_processor.get_config_details_from_excel("Goa")["Username"]
            password = Config_processor.get_config_details_from_excel("Goa")["Password"]
            api_details = DBProcessor.get_api_details('fetch_get_tax_outstandingV3', request_body={"username":username, "password":password})
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            sanitation_total = response['data']['response'][0]['SANITATION_TOTAL']
            mun_id = response['data']['response'][0]['MUN_ID']
            occupier_name = response['data']['response'][0]['OCCUPIER_NAME']
            demand_warrant = response['data']['response'][0]['DEMAND_WARRANT']
            coln_arrears = response['data']['response'][0]['COLN_ARREARS']
            demand_current = response['data']['response'][0]['DEMAND_CURRENT']
            order_no = response['data']['response'][0]['ORDER_NO']
            interest = response['data']['response'][0]['INTEREST']
            demand_interest = response['data']['response'][0]['DEMAND_INTEREST']
            aggregator =  response['data']['response'][0]['AGGREGATOR']
            coln_notice = response['data']['response'][0]['COLN_NOTICE']
            demand_arrears = response['data']['response'][0]['DEMAND_ARREARS']
            coln_interest = response['data']['response'][0]['COLN_INTEREST']
            tax_total = response['data']['response'][0]['TAX_TOTAL']
            address = response['data']['response'][0]['ADDRESS']
            coln_current = response['data']['response'][0]['COLN_CURRENT']
            coln_warrant = response['data']['response'][0]['COLN_WARRANT']
            outstanding = response['data']['response'][0]['OUTSTANDING']
            name_owner = response['data']['response'][0]['NAME_OWNER']
            amt_payable = response['data']['response'][0]['AMOUNT_PAYABLE']
            receipt_no = response['data']['response'][0]['RECEIPT_NO']
            house_no = response['data']['response'][0]['HOUSE_NO']
            demand_notice = response['data']['response'][0]['DEMAND_NOTICE']
            logger.info(f"API Result: Fetch Response for Goa Merchant : {success}, {sanitation_total}, {mun_id},{occupier_name},"
                        f"{demand_warrant}, {coln_arrears},{demand_current},{order_no}, {interest},{demand_interest},"
                        f"{aggregator}, {coln_notice},{demand_arrears},{coln_interest}, {tax_total},{address},"
                        f"{coln_current}, {coln_warrant},{outstanding},{name_owner}, {amt_payable},{receipt_no},"
                        f"{house_no},{demand_notice}")

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
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True,"sanitation_total": "0" , "mun_id": "05" ,"occupier_name": "RAHIMA S. SHAIKH (BUS. ACT.)" ,
                                      "demand_warrant": "0" ,
                                      "coln_arrears": "0" ,"demand_current": "784" ,"order_no": "24094041*05*19I/186/CL/4/1*0*0" , "interest": "0" ,
                                      "demand_interest": "0" ,"aggregator": "EZETAP" , "coln_notice": "0" ,"demand_arrears": "0" ,
                                     "coln_interest": "0" , "tax_total": "784" ,"address": "NEAR RASTOLI TEMPLE, NEW VADDEM, VASCO." ,"coln_current": "0" , "coln_warrant": "0" ,
                                      "outstanding": "Y" ,"name_owner": "FRANCIS JHON RODRIGUES" , "amt_payable": "784" ,
                                      "receipt_no": "5202203062" ,"house_no": "19I/186/CL/4/1" ,"demand_notice":"0"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "sanitation_total": sanitation_total , "mun_id": mun_id ,"occupier_name": occupier_name,
                                      "demand_warrant": demand_warrant ,
                                      "coln_arrears":coln_arrears,"demand_current": demand_current ,"order_no": order_no , "interest": interest ,
                                      "demand_interest": demand_interest,"aggregator": aggregator , "coln_notice": coln_notice,"demand_arrears": demand_arrears ,
                                     "coln_interest": coln_interest, "tax_total": tax_total,"address": address ,"coln_current": coln_current , "coln_warrant": coln_warrant,
                                      "outstanding": outstanding ,"name_owner": name_owner , "amt_payable": amt_payable ,
                                      "receipt_no": receipt_no ,"house_no": house_no,"demand_notice":demand_notice}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues1, actualAPI=actualAPIValues1)

                #Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"SANITATION_TOTAL": "0", "MUN_ID": "05", "OCCUPIER_NAME": "RAHIMA S. SHAIKH (BUS. ACT.)", "DEMAND_WARRANT": "0", "COLN_ARREARS": "0", "DEMAND_CURRENT": "784", "ORDER_NO": "24094041*05*19I/186/CL/4/1*0*0", "INTEREST": "0", "DEMAND_INTEREST": "0", "AGGREGATOR": "EZETAP", "COLN_NOTICE": "0", "DEMAND_ARREARS": "0", "COLN_INTEREST": "0", "TAX_TOTAL": "784", "ADDRESS": "NEAR RASTOLI TEMPLE, NEW VADDEM, VASCO.", "COLN_CURRENT": "0", "COLN_WARRANT": "0", "OUTSTANDING": "Y", "NAME_OWNER": "FRANCIS JHON RODRIGUES", "AMOUNT_PAYABLE": "784", "RECEIPT_NO": "5202203062", "HOUSE_NO": "19I/186/CL/4/1", "DEMAND_NOTICE": "0"}]}}'}
                # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                # actualAPIValues2 = {"Result" : response_data}
                # logger.debug(f"actualAPIValues: {actualAPIValues2}")
                #
                # Validator.validationAgainstAPI(expectedAPI= expectedAPIValues2, actualAPI=actualAPIValues2)
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/yVFHCb/application/W6VTJB/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_tax_outstandingV3') and active = 1);"
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
            query = "select * from ca_usergroup_org_map where org_code='"+org_code+"' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")#check for length validation
            logger.debug(f"Query result URL: {result}")
            if len(result)>1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

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
def test_common_300_301_002():
    """
            Sub Feature Code: NonUI_Common_Config_Goa_fetch_get_trade_outstanding
            Sub Feature Description: fetching details of Goa Merchant having key "get_trade_outstanding" via fetch/data API
            TC naming code description:
            300: Config
            301: Goa
            002: TC002
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        # ---------------------------------------------------------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

            org_code = Config_processor.get_config_details_from_excel("Goa")["MerchantCode"]
            username = Config_processor.get_config_details_from_excel("Goa")["Username"]
            password = Config_processor.get_config_details_from_excel("Goa")["Password"]
            api_details = DBProcessor.get_api_details('fetch_get_trade_outstanding', request_body={"username":username, "password":password})
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            message = response['data']['response'][0]['MSG']
            error_code = response['data']['response'][0]['ERROR_CODE']
            logger.info(f"API Result: Fetch Response for Goa Merchant : {success}, {message}, {error_code}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,  "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "msg": "Record not found", "error_code": "7"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")

                actualAPIValues1 = {"success": success, "msg": message, "error_code": error_code}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"MSG": "Record not found", "ERROR_CODE": "7"}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/yVFHCb/application/yMDc9v/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_trade_outstanding') and active = 1);"
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
            query = "select * from ca_usergroup_org_map where org_code='"+org_code+"' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result)>1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))





@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_301_003():
    """
            Sub Feature Code: NonUI_Common_Config_Goa_fetch_get_rental_outstanding
            Sub Feature Description: fetching details of Goa Merchant having key "get_rental_outstanding" via fetch/data API
            TC naming code description:
            300: Config
            301: Goa
            003: TC003
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------


        GlobalVariables.setupCompletedSuccessfully = True
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

            org_code = Config_processor.get_config_details_from_excel("Goa")["MerchantCode"]
            username = Config_processor.get_config_details_from_excel("Goa")["Username"]
            password = Config_processor.get_config_details_from_excel("Goa")["Password"]
            api_details = DBProcessor.get_api_details('fetch_get_rental_outstanding', request_body={"username":username, "password":password})
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            lease_no = response['data']['response'][0]['LEASE_NO']
            mun_id = response['data']['response'][0]['MUN_ID']
            demand_warrant = response['data']['response'][0]['DEMAND_WARRANT']
            coln_arrears = response['data']['response'][0]['COLN_ARREARS']
            demand_current = response['data']['response'][0]['DEMAND_CURRENT']
            order_no = response['data']['response'][0]['ORDER_NO']
            service_tax = response['data']['response'][0]['SERVICETAX']
            demand_interest = response['data']['response'][0]['DEMAND_INTEREST']
            aggregator = response['data']['response'][0]['AGGREGATOR']
            demand_arrears = response['data']['response'][0]['DEMAND_ARREARS']
            stax_rate = response['data']['response'][0]['STAX_RATE']
            coln_interest = response['data']['response'][0]['COLN_INTEREST']
            address = response['data']['response'][0]['ADDRESS']
            coln_current = response['data']['response'][0]['COLN_CURRENT']
            coln_warrant = response['data']['response'][0]['COLN_WARRANT']
            outstanding = response['data']['response'][0]['OUTSTANDING']
            amt_payable = response['data']['response'][0]['AMOUNT_PAYABLE']
            lessee_name = response['data']['response'][0]['LESSEE_NAME']
            receipt_no = response['data']['response'][0]['RECEIPT_NO']
            demand_notice = response['data']['response'][0]['DEMAND_NOTICE']
            logger.info(f"API Result: Fetch Response for Goa Merchant : {success}, {lease_no}, {mun_id},"
                f"{demand_warrant}, {coln_arrears},{demand_current},{order_no}, {service_tax},{demand_interest},"
                f"{aggregator},{demand_arrears},{stax_rate}, {coln_interest},{address},"
                f"{coln_current}, {coln_warrant},{outstanding},{amt_payable},{lessee_name}, {receipt_no},"
                f"{demand_notice}")
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
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "lease_no": "15/95" , "mun_id": "06" ,"demand_warrant": "0" , "coln_arrears": "0" ,
                                      "demand_current": "2048" ,
                                      "order_no": "03102054*06*15/95*369*0" , "service_tax": "369" ,"demand_interest": "0" ,
                                      "aggregator": "EZETAP" ,"demand_arrears": "0" ,
                                      "stax_rate": "18.0000" , "coln_interest": "0" ,"address": "95  MUNICIPAL MARKET   (4,8,7)  " ,"coln_current": "0" ,
                                      "coln_warrant": "0" ,
                                      "outstanding": "Y" ,"amt_payable": "2417" ,"lessee_name": "JERONIMO D`SOUZA" , "receipt_no": "6202200985" ,"demand_notice":"0"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")

                actualAPIValues1 = {"success": success,"lease_no": lease_no , "mun_id": mun_id,"demand_warrant":demand_warrant , "coln_arrears": coln_arrears,
                                      "demand_current": demand_current,
                                      "order_no": order_no, "service_tax": service_tax,"demand_interest": demand_interest,
                                      "aggregator": aggregator ,"demand_arrears": demand_arrears ,
                                      "stax_rate": stax_rate, "coln_interest": coln_interest ,"address": address ,"coln_current":coln_current ,
                                      "coln_warrant": coln_warrant ,
                                      "outstanding": outstanding ,"amt_payable": amt_payable ,"lessee_name": lessee_name , "receipt_no": receipt_no,"demand_notice":demand_notice}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"LEASE_NO": "15/95", "MUN_ID": "06", "DEMAND_WARRANT": "0", "COLN_ARREARS": "0", "DEMAND_CURRENT": "2048", "ORDER_NO": "03102054*06*15/95*369*0", "SERVICETAX": "369", "DEMAND_INTEREST": "0", "AGGREGATOR": "EZETAP", "DEMAND_ARREARS": "0", "STAX_RATE": "18.0000", "COLN_INTEREST": "0", "ADDRESS": "95  MUNICIPAL MARKET   (4,8,7)  ", "COLN_CURRENT": "0", "COLN_WARRANT": "0", "OUTSTANDING": "Y", "AMOUNT_PAYABLE": "2417", "LESSEE_NAME": "JERONIMO D`SOUZA", "RECEIPT_NO": "6202200985", "DEMAND_NOTICE": "0"}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/yVFHCb/application/TyGgZf/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_rental_outstanding') and active = 1);"
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
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))


        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='"+org_code+"' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result)>1:
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



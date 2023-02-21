from datetime import datetime
import pytest
import json
from termcolor import colored
import shutil
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, Config_processor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_304_001():
    """
            Sub Feature Code: NonUI_Common_Config_BMC_fetch_get_mp_property_details
            Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "get_mp_property_details" via fetch/data API
            TC naming code description:
            300: Config
            304: BMC
            001: TC001
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

            org_code = Config_processor.get_config_details_from_excel("BMC")["MerchantCode"]
            username = Config_processor.get_config_details_from_excel("BMC")["Username"]
            password = Config_processor.get_config_details_from_excel("BMC")["Password"]
            api_details = DBProcessor.get_api_details('fetch_get_mp_property_details', request_body={"username":username, "password":password})
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            # prop_id = response['data']['response'][0]['d']['Propid']
            # mobile_no = response['data']['response'][0]['d']['MobileNo']
            # email_id = response['data']['response'][0]['d']['EmailId']
            # address = response['data']['response'][0]['d']['Address']
            arrear_tax = response['data']['response'][0]['d']['ArrearTax']
            message = response['data']['response'][0]['d']['Message']
            zone = response['data']['response'][0]['d']['Zone']
            la_discount = response['data']['response'][0]['d']['LaDiscount']
            total_payable = response['data']['response'][0]['d']['TotalPayable']
            # ulb = response['data']['response'][0]['d']['Ulb']
            msg_type = response['data']['response'][0]['d']['MsgType']
            current_year_tax = response['data']['response'][0]['d']['CurrentYearTax']
            # la_open = response['data']['response'][0]['d']['LaOpen']
            # ward = response['data']['response'][0]['d']['Ward']
            # full_name = response['data']['response'][0]['d']['FullName']
            penality = response['data']['response'][0]['d']['Penality']
            # aadhar_card = response['data']['response'][0]['d']['AadharCard']
            id = response['data']['response'][0]['d']['__metadata']['id']
            type = response['data']['response'][0]['d']['__metadata']['type']
            uri = response['data']['response'][0]['d']['__metadata']['uri']
            # trans_id = response['data']['response'][0]['d']['Transid']
            # father_name = response['data']['response'][0]['d']['FatherName']

            logger.info(f"API Result: Fetch Response for BMC Merchant : {success}, {arrear_tax}, {message}, {zone},"
                        f"{la_discount},{total_payable},{msg_type},{current_year_tax},{penality},{id},{type},{uri}")

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
                expectedAPIValues1 = {"success": True, "arrear_tax": "0.000" , "message": "No authorization to view given property!!" ,
                                      "zone": "00" ,"la_discount": "0.000" ,"total_payable": "0.000" ,"msg_type": "E" ,
                                      "current_year_tax": "0.000" ,"penality": "0.000" ,"id": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/TransactionDetailsCollection('')" ,
                                      "type": "ZPT_DP_SRV.TransactionDetails" ,"uri":"https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/TransactionDetailsCollection('')"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "arrear_tax": arrear_tax , "message": message,
                                      "zone": zone ,"la_discount": la_discount ,"total_payable":total_payable,"msg_type":msg_type ,
                                      "current_year_tax": current_year_tax ,"penality": penality ,"id": id ,
                                      "type": type ,"uri":uri}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"d": {"Propid": "", "MobileNo": "", "EmailId": "", "Address": "", "ArrearTax": "0.000", "Message": "No authorization to view given property!!", "Zone": "00", "LaDiscount": "0.000", "TotalPayable": "0.000", "Ulb": "", "MsgType": "E", "CurrentYearTax": "0.000", "LaOpen": "", "Ward": "", "FullName": "", "Penality": "0.000", "AadharCard": "", "__metadata": {"id": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/TransactionDetailsCollection("")", "type": "ZPT_DP_SRV.TransactionDetails", "uri": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/TransactionDetailsCollection("")"}, "Transid": "", "FatherName": ""}}]}}'}
                # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                # actualAPIValues2 = {"Result": response_data.replace("'", '"')}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/l2ikZo/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_mp_property_details') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")#change in all TCS
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
def test_common_300_304_002():
    """
            Sub Feature Code: NonUI_Common_Config_BMC_fetch_BMC_water
            Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "BMC_water" via fetch/data API
            TC naming code description:
            300: Config
            304: BMC
            002: TC002
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

            org_code = Config_processor.get_config_details_from_excel("BMC")["MerchantCode"]
            username = Config_processor.get_config_details_from_excel("BMC")["Username"]
            password = Config_processor.get_config_details_from_excel("BMC")["Password"]
            api_details = DBProcessor.get_api_details('fetch_BMC_water', request_body={"username":username, "password":password})
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            ex_name = response['data']['response'][0]['data']['ExName']
            ex_father_name = response['data']['response'][0]['data']['ExFatherName']
            ex_connection_no = response['data']['response'][0]['data']['ExConnectionNo']
            ex_zone = response['data']['response'][0]['data']['ExZone']
            ex_colony = response['data']['response'][0]['data']['ExColony']
            ex_ward = response['data']['response'][0]['data']['ExWard']
            ex_address = response['data']['response'][0]['data']['ExAddress']
            fy_1 = response['data']['response'][0]['data']['ExWaterBillDetails']['item'][0]['FiscalYear']
            amt_1 = response['data']['response'][0]['data']['ExWaterBillDetails']['item'][0]['Amount']
            fy_2 = response['data']['response'][0]['data']['ExWaterBillDetails']['item'][1]['FiscalYear']
            amt_2 = response['data']['response'][0]['data']['ExWaterBillDetails']['item'][1]['Amount']
            fy_3 = response['data']['response'][0]['data']['ExWaterBillDetails']['item'][2]['FiscalYear']
            amt_3 = response['data']['response'][0]['data']['ExWaterBillDetails']['item'][2]['Amount']
            fy_4 = response['data']['response'][0]['data']['ExWaterBillDetails']['item'][3]['FiscalYear']
            amt_4 = response['data']['response'][0]['data']['ExWaterBillDetails']['item'][3]['Amount']
            success_1 = response['data']['response'][0]['success']
            txn_ref = response['data']['response'][0]['txnRef']
            total_tax = response['data']['response'][0]['tax']['totalTax']
            current_tax = response['data']['response'][0]['tax']['currentTax']
            arrears = response['data']['response'][0]['tax']['Arrears']
            logger.info(f"API Result: Fetch Response for BMC Merchant : {success}, {ex_name}. {ex_father_name},{ex_connection_no},"
                        f"{ex_zone},{ex_colony},{ex_ward},{ex_address},{fy_1},{amt_1},{fy_2},{amt_2}, {fy_3},{amt_3}, {fy_4},{amt_4},"
                        f"{success_1},{txn_ref},{total_tax},{current_tax},{arrears}")

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
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "ex_name":"???? ???????", "ex_father_name": "." ,"ex_connection_no": "2000019368" ,
                                      "ex_zone": "???? ???. 7" ,"ex_colony": "?? ?? ???" ,"ex_ward": "32 - ????? ??? ?????" ,
                                      "ex_address": "- 228 ?????? ???? ??.??. ???" ,"fy_1": "2019" ,"amt_1": "2484.0" ,"fy_2": "2020" ,
                                      "amt_2": "2484.0" , "fy_3": "2021" ,"amt_3": "2484.0" , "fy_4": "2022" ,"amt_4": "2520.0" ,
                                      "success_1": True ,"txn_ref": "220927E1664279896495" ,"total_tax": 9972 ,"current_tax": 0 ,"arrears":9972}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "ex_name":ex_name, "ex_father_name": ex_father_name ,"ex_connection_no": ex_connection_no ,
                                      "ex_zone": ex_zone ,"ex_colony": ex_colony,"ex_ward": ex_ward,
                                      "ex_address": ex_address ,"fy_1": fy_1 ,"amt_1": amt_1 ,"fy_2": fy_2 ,
                                      "amt_2": amt_2 , "fy_3":fy_3,"amt_3": amt_3 , "fy_4":fy_4,"amt_4": amt_4 ,
                                      "success_1":success_1,"txn_ref": txn_ref ,"total_tax": total_tax ,"current_tax": current_tax,"arrears":arrears}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"data": {"ExName": "???? ???????", "ExFatherName": ".", "ExConnectionNo": "2000019368", "ExZone": "???? ???. 7", "ExColony": "?? ?? ???", "ExWard": "32 - ????? ??? ?????", "ExAddress": "- 228 ?????? ???? ??.??. ???", "ExWaterBillDetails": {"item": [{"FiscalYear": "2019", "Amount": "2484.0"}, {"FiscalYear": "2020", "Amount": "2484.0"}, {"FiscalYear": "2021", "Amount": "2484.0"}, {"FiscalYear": "2022", "Amount": "2520.0"}]}}, "success": True, "txnRef": "220713E1657715913502", "tax": {"totalTax": 9972, "currentTax": 2520, "Arrears": 7452}}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/vhmMW5/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'BMC_water') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")#change in all TCS
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
def test_common_300_304_003():
    """
            Sub Feature Code: NonUI_Common_Config_BMC_fetch_BMC_prop
            Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "BMC_prop" via fetch/data API
            TC naming code description:
            300: Config
            304: BMC
            003: TC003
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

            org_code = Config_processor.get_config_details_from_excel("BMC")["MerchantCode"]
            username = Config_processor.get_config_details_from_excel("BMC")["Username"]
            password = Config_processor.get_config_details_from_excel("BMC")["Password"]
            api_details = DBProcessor.get_api_details('fetch_BMC_prop', request_body={"username":username, "password":password})
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            ex_name = response['data']['response'][0]['data']['ExName']
            fy_1 = response['data']['response'][0]['data']['ExDemandDetails']['item'][0]['FiscalYear']
            amt_1 = response['data']['response'][0]['data']['ExDemandDetails']['item'][0]['Amount']
            fy_2 = response['data']['response'][0]['data']['ExDemandDetails']['item'][1]['FiscalYear']
            amt_2 = response['data']['response'][0]['data']['ExDemandDetails']['item'][1]['Amount']
            ex_property_id = response['data']['response'][0]['data']['ExPropertyid']
            ex_father_name = response['data']['response'][0]['data']['ExFatherName']
            ex_zone = response['data']['response'][0]['data']['ExZone']
            ex_circle = response['data']['response'][0]['data']['ExCircle']
            ex_colony = response['data']['response'][0]['data']['ExColony']
            ex_ward = response['data']['response'][0]['data']['ExWard']
            ex_address = response['data']['response'][0]['data']['ExAddress']
            success_1 = response['data']['response'][0]['success']
            txn_ref = response['data']['response'][0]['txnRef']
            total_tax = response['data']['response'][0]['tax']['totalTax']
            current_tax = response['data']['response'][0]['tax']['currentTax']
            arrears = response['data']['response'][0]['tax']['Arrears']
            logger.info(f"API Result: Fetch Response for BMC Merchant : {success}, {ex_name}.{fy_1},{amt_1},{fy_2},{amt_2},"
                        f"{ex_property_id}, {ex_father_name},{ex_zone},{ex_circle},{ex_colony},{ex_ward},{ex_address},"
                        f"{success_1},{txn_ref},{total_tax},{current_tax},{arrears}")

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
                expectedAPIValues1 = {"success": True, "ex_name":"???? ???????","fy_1": "2022" ,"amt_1": "720.0" ,"fy_2": "2022" ,"amt_2": "3666.0" ,
                                      "ex_property_id": "1000097140" , "ex_father_name": "???.???? ??????" ,"ex_zone": "???? ???. 18" ,
                                      "ex_circle": "?????????? ???. 4" ,"ex_colony": " ?????? ??????? ????? ???" ,"ex_ward": "82 - ????? ???" ,
                                      "ex_address": "??-402, ?????? ?????,?????" ,"success_1": True ,"txn_ref": "220927E1664281071721" ,
                                      "total_tax": 4386 ,"current_tax": 0 ,"arrears":4386}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "ex_name":ex_name,"fy_1": fy_1 ,"amt_1":amt_1,"fy_2":fy_2 ,"amt_2":amt_2 ,
                                      "ex_property_id": ex_property_id , "ex_father_name": ex_father_name ,"ex_zone": ex_zone,
                                      "ex_circle": ex_circle ,"ex_colony": ex_colony,"ex_ward": ex_ward ,
                                      "ex_address": ex_address ,"success_1": success_1 ,"txn_ref":txn_ref ,
                                      "total_tax":total_tax ,"current_tax": current_tax ,"arrears":arrears}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"data": {"ExName": "???? ???????", "ExDemandDetails": {"item": [{"FiscalYear": "2022", "Amount": "720.0"}, {"FiscalYear": "2022", "Amount": "3666.0"}]}, "ExPropertyid": "1000097140", "ExFatherName": "???.???? ??????", "ExZone": "???? ???. 18", "ExCircle": "?????????? ???. 4", "ExColony": " ?????? ??????? ????? ???", "ExWard": "82 - ????? ???", "ExAddress": "??-402, ?????? ?????,?????"}, "success": True, "txnRef": "220713E1657715913659", "tax": {"totalTax": 4386, "currentTax": 4386, "Arrears": 0}}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/f8Yyjc/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'BMC_prop') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")#change in all TCS
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
def test_common_300_304_004():
        """
                Sub Feature Code: NonUI_Common_Config_BMC_fetch_get_mp_property_update_details
                Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "get_mp_property_update_details" via fetch/data API
                TC naming code description:
                300: Config
                304: BMC
                004: TC004
        """
        try:
            GlobalVariables.time_calc.setup.resume()
            print(
                colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))
            # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

            GlobalVariables.setupCompletedSuccessfully = True
            Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,middlewareLog=False,config_log=True)

            msg = ""
            GlobalVariables.time_calc.setup.end()
            print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))

            # -----------------------------------------Start of Test Execution-------------------------------------
            try:
                # ------------------------------------------------------------------------------------------------
                GlobalVariables.time_calc.execution.start()
                print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

                org_code = Config_processor.get_config_details_from_excel("BMC")["MerchantCode"]
                username = Config_processor.get_config_details_from_excel("BMC")["Username"]
                password = Config_processor.get_config_details_from_excel("BMC")["Password"]
                api_details = DBProcessor.get_api_details('fetch_get_mp_property_update_details', request_body={"username":username, "password":password})
                response = APIProcessor.send_request(api_details)
                response_data = json.dumps(response)
                success = response['success']
                message = response['data']['response'][0]['d']['Message']
                system = response['data']['response'][0]['d']['System']
                type = response['data']['response'][0]['d']['Type']
                number = response['data']['response'][0]['d']['Number']
                id = response['data']['response'][0]['d']['Id']
                row = response['data']['response'][0]['d']['Row']
                id_1 = response['data']['response'][0]['d']['__metadata']['id']
                type_1 = response['data']['response'][0]['d']['__metadata']['type']
                uri = response['data']['response'][0]['d']['__metadata']['uri']
                log_msg_no = response['data']['response'][0]['d']['LogMsgNo']

                logger.info(f"API Result: Fetch Response for BMC Merchant : {success}, {message}, {system}, {type},"
                            f"{number},{id},{row},{id_1},{type_1},{uri},{log_msg_no}")
                # ------------------------------------------------------------------------------------------------
                GlobalVariables.EXCEL_TC_Execution = "Pass"
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in try block of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
            except Exception as e:
                if GlobalVariables.time_calc.execution.is_started and (
                not GlobalVariables.time_calc.execution.is_paused):
                    GlobalVariables.time_calc.execution.pause()
                    print(colored(
                        "Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(
                            shutil.get_terminal_size().columns, "="), 'cyan'))
                GlobalVariables.time_calc.execution.resume()
                print(colored("Execution Timer resumed in exept block of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
                GlobalVariables.EXCEL_TC_Execution = "Fail"
                GlobalVariables.Incomplete_ExecutionCount += 1
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in exept block of testcase function before pytest fails".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
                pytest.fail("Test case execution failed due to the exception -" + str(e))
            # -----------------------------------------End of Test Execution--------------------------------------

            # -----------------------------------------Start of Validation----------------------------------------
            GlobalVariables.time_calc.validation.start()
            print(
                colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            # # -----------------------------------------Start of API Validation------------------------------------
            if (ConfigReader.read_config("Validations", "api_validation")) == "True":
                try:
                    # --------------------------------------------------------------------------------------------
                    expectedAPIValues1 = {"success": True,
                                         "message": "Transaction Successfully Posted into the System" , "system": "P01CLNT500" , "type": "S" ,"number": "001" ,
                                          "id": "ZPT_MC_DP" ,"row": 0 ,"id_1": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/BapiRet2Collection('S')" ,
                                          "type_1": "ZPT_DP_SRV.BapiRet2" ,"uri": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/BapiRet2Collection('S')" ,
                                          "log_msg_no":"000000"}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                    actualAPIValues1 = {"success": success,  "message": message , "system":system, "type": type ,"number": number,
                                          "id": id,"row": row ,"id_1":id_1 ,
                                          "type_1": type_1 ,"uri": uri ,
                                          "log_msg_no":log_msg_no}
                    logger.debug(f"actualAPIValues: {actualAPIValues1}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues1, actualAPI=actualAPIValues1)

                    # Whole String comparision
                    # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"d": {"Message": "Transaction Successfully Posted into the System", "LogNo": "", "System": "P01CLNT500", "Field": "", "Type": "S", "Number": "001", "MessageV4": "", "MessageV3": "", "Parameter": "", "Id": "ZPT_MC_DP", "Row": 0, "__metadata": {"id": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/BapiRet2Collection("S")", "type": "ZPT_DP_SRV.BapiRet2", "uri": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/BapiRet2Collection("S")"}, "LogMsgNo": "000000", "MessageV2": "", "MessageV1": ""}}]}}'}
                    # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                    # actualAPIValues2 = {"Result": response_data.replace("'", '"')}
                    # logger.debug(f"actualAPIValues: {actualAPIValues2}")
                    #
                    # Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
                except Exception as e:
                    print("API Validation failed due to exception - " + str(e))
                    msg = msg + "API Validation did not complete due to exception.\n"
                    GlobalVariables.bool_val_exe = False
                    GlobalVariables.str_api_val_result = "Fail"

            # # -----------------------------------------End of API Validation---------------------------------------
            #
            # # -----------------------------------------Start of DB Validation--------------------------------------
            if (ConfigReader.read_config("Validations", "db_validation")) == "True":
                try:
                    # --------------------------------------------------------------------------------------------
                    expectedDBValues = {
                        "url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/sx9b1V/"}
                    logger.debug(f"expectedDBValues: {expectedDBValues}")

                    query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_mp_property_update_details') and active = 1);"
                    logger.debug(f"Query to fetch data from external_api_adapter table : {query}")  # change in all TCS
                    result = DBProcessor.getValueFromDB(query, "config")
                    logger.debug(f"Query result URL: {result}")
                    url_db = result["url"].iloc[0]
                    actualDBValues = {"url": url_db}
                    logger.debug(f"actualDBValues : {actualDBValues}")
                    # ---------------------------------------------------------------------------------------------
                    Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                except Exception as e:
                    print("DB Validation failed due to exception - " + str(e))
                    msg = msg + "DB Validation did not complete due to exception.\n"
                    GlobalVariables.bool_val_exe = False
                    GlobalVariables.str_db_val_result = 'Fail'

            # # -----------------------------------------End of DB Validation---------------------------------------
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
            print(colored("Execution Timer resumed in finally block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))



            if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
                query = "select * from ca_usergroup_org_map where org_code='"+org_code+"' and is_active;"
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
            print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_304_005():
    """
            Sub Feature Code: NonUI_Common_Config_BMC_fetch_get_mp_water_details
            Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "get_mp_water_details" via fetch/data API
            TC naming code description:
            300: Config
            304: BMC
            005: TC005
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

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))

            org_code = Config_processor.get_config_details_from_excel("BMC")["MerchantCode"]
            username = Config_processor.get_config_details_from_excel("BMC")["Username"]
            password = Config_processor.get_config_details_from_excel("BMC")["Password"]
            api_details = DBProcessor.get_api_details('fetch_get_mp_water_details', request_body={"username":username, "password":password})
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            company_name = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['CompanyName']
            mobile_number = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['MobileNumber']
            address = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['Address']
            bill_month = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['BillMonth']
            lt_ht = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['LT_HT']
            ca_number = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['CANumber']
            amount = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['Amount']
            consumer_name = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['ConsumerName']
            division = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['Division']
            invoice_no = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['InvoiceNO']
            due_date = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['DueDate']
            sub_division = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['SubDivision']

            logger.info(f"API Result: Fetch Response for BMC Merchant : {success}, {company_name}. {mobile_number},{address},"
                        f"{bill_month},{lt_ht},{ca_number},{amount},{consumer_name},{division},{invoice_no},{due_date},{sub_division}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns,
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
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "company_name":"SOUTH BIHAR POWER DISTRIBUTION COMPANY LTD",
                                      "mobile_number": "7050292987" ,"address": " HDUMABD KI . . 804408" ,"bill_month": "MAY-2022" ,
                                      "lt_ht": "URBAN" ,"ca_number": "102486309" ,"amount": "772" ,"consumer_name": "MD EHTESHAM ANSARI ." ,
                                      "division": "Jehanabad" ,"invoice_no": "10115629079" ,"due_date": "2022-05-22" ,"sub_division":"Jehanabad"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "company_name":company_name,
                                      "mobile_number":mobile_number ,"address": address ,"bill_month": bill_month ,
                                      "lt_ht": lt_ht ,"ca_number": ca_number ,"amount": amount ,"consumer_name": consumer_name ,
                                      "division": division,"invoice_no": invoice_no ,"due_date": due_date ,"sub_division":sub_division}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"Body": {"BillDetailsResponse": {"BillDetailsResult": {"CompanyName": "SOUTH BIHAR POWER DISTRIBUTION COMPANY LTD", "MobileNumber": "7050292987", "Address": " HDUMABD KI . . 804408", "BillMonth": "MAY-2022", "LT_HT": "URBAN", "CANumber": "102486309", "Amount": "772", "ConsumerName": "MD EHTESHAM ANSARI .", "Division": "Jehanabad", "InvoiceNO": "10115629079", "DueDate": "2022-05-22", "SubDivision": "Jehanabad"}}}}]}}'}
                # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                # actualAPIValues2 = {"Result": response_data}
                # logger.debug(f"actualAPIValues: {actualAPIValues2}")
                #
                # Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"

        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/5dhnHE/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_mp_water_details') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")  # change in all TCS
                result = DBProcessor.getValueFromDB(query, "config")
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

        # # -----------------------------------------End of DB Validation---------------------------------------
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



        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='"+org_code+"' and is_active;"
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
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))





from datetime import datetime
import pytest
import json
from termcolor import colored
import shutil
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
@pytest.mark.appVal
def test_common_300_303_001():
    """
        Sub Feature Code: NonUI_Common_Config_GWMC_fetch_User_Charges_Tax_PullV2
        Sub Feature Description: fetching details of GWMC Merchant having key "User_Charges_Tax_PullV2" via fetch/data API
        TC naming code description:
        300: Config
        303: GWMC
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
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('fetch_User_Charges_Tax_PullV2')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            id = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['id']
            is_data_set = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['IsDataSet']
            min_occurs = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['minOccurs']
            max_occurs = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['maxOccurs']
            min_occurs_1 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][0]['minOccurs']
            name_1 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][0]['name']
            type_1 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][0]['type']
            min_occurs_2 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][1]['minOccurs']
            name_2 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][1]['name']
            type_2 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][1]['type']
            min_occurs_3 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][2]['minOccurs']
            name_3 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][2]['name']
            type_3 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][2]['type']
            min_occurs_4 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][3]['minOccurs']
            name_4 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][3]['name']
            type_4 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][3]['type']
            min_occurs_5 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][4]['minOccurs']
            name_5 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][4]['name']
            type_5 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][4]['type']
            min_occurs_6 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][5]['minOccurs']
            name_6 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][5]['name']
            type_6 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][5]['type']
            min_occurs_7 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][6]['minOccurs']
            name_7 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][6]['name']
            type_7 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][6]['type']
            min_occurs_8 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][7]['minOccurs']
            name_8 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][7]['name']
            type_8 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][7]['type']
            min_occurs_9 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][8]['minOccurs']
            name_9 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][8]['name']
            type_9 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][8]['type']
            min_occurs_10 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][9]['minOccurs']
            name_10 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][9]['name']
            type_10 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][9]['type']
            name_11 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['complexType']['choice']['element']['name']
            name_12 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['name']
            use_current_locale = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['element']['UseCurrentLocale']
            curr_amt = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['CURRAMT']
            owner_of_the_shop = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['OWNEROFTHESHOP']
            arr_amt = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['ARRAMT']
            gid = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['GID']
            closing = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['CLOSING']
            house_no = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['HOUSENO']
            city_name = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['CITY_NAME']
            shop_name = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['SHOP_NAME']
            id_1 = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['id']
            row_order = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['rowOrder']
            shop_id = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['SHOPID']
            gname = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['GNAME']

            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {id}, {is_data_set},{min_occurs}, {max_occurs},{min_occurs_1},{name_1},{type_1},"
                        f"{min_occurs_2},{name_2},{type_2},{min_occurs_3},{name_3},{type_3},{min_occurs_4},{name_4},{type_4},{min_occurs_5},{name_5},{type_5},"
                        f"{min_occurs_6},{name_6},{type_6},{min_occurs_7},{name_7},{type_7},{min_occurs_8},{name_8},{type_8},{min_occurs_9},{name_9},{type_9},{min_occurs_10},{name_10},{type_10},"
                        f"{name_11},{name_12},{use_current_locale},{curr_amt},{owner_of_the_shop},{arr_amt},{gid},{closing},{house_no},{city_name},{shop_name},"
                        f"{id_1},{row_order},{shop_id},{gname}")

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
                expectedAPIValues1 = {"success": True, "id": "NewDataSet" , "is_data_set": "true" ,"min_occurs": "0" ,
                                      "max_occurs": "unbounded" ,"min_occurs_1": "0" ,"name_1": "SHOPID" ,"type_1": "xs:double" ,
                                      "min_occurs_2": "0" ,"name_2": "HOUSENO" ,"type_2": "xs:string" ,"min_occurs_3": "0" ,
                                      "name_3": "CITY_NAME" ,"type_3": "xs:string" ,"min_occurs_4": "0" ,"name_4": "SHOP_NAME" ,
                                      "type_4": "xs:string" ,"min_occurs_5": "0" ,"name_5": "OWNEROFTHESHOP" ,"type_5": "xs:string" ,
                                      "min_occurs_6": "0" ,"name_6": "ARRAMT" ,"type_6": "xs:decimal" ,"min_occurs_7": "0" ,"name_7": "CURRAMT" ,
                                      "type_7": "xs:decimal" ,"min_occurs_8": "0" ,"name_8": "CLOSING" ,"type_8": "xs:decimal" ,
                                      "min_occurs_9": "0" ,"name_9": "GNAME" ,"type_9": "xs:string" ,"min_occurs_10": "0" ,"name_10": "GID" ,
                                      "type_10": "xs:double" ,"name_11": "gcharges_demand" ,"name_12": "NewDataSet" ,"use_current_locale": "true" ,
                                      "curr_amt": "0" ,"owner_of_the_shop": "BHARAT NARANG" ,"arr_amt": "0" ,"gid": "25" ,"closing": "0" ,
                                      "house_no": "#7-1-89" ,"city_name": "BALASAMUDRAM" ,"shop_name": "ASIAN SRIDEVI SCREEN 3" ,
                                      "id_1": "gcharges_demand1" ,"row_order": "0" ,"shop_id": "18324" ,"gname":"CINEMA HALLS AND ENTERTINMENT"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "id": id , "is_data_set": is_data_set ,"min_occurs":min_occurs,
                                      "max_occurs": max_occurs ,"min_occurs_1":min_occurs_1 ,"name_1": name_1 ,"type_1": type_1 ,
                                      "min_occurs_2": min_occurs_2,"name_2": name_2 ,"type_2": type_2 ,"min_occurs_3":min_occurs_3,
                                      "name_3": name_3 ,"type_3": type_3 ,"min_occurs_4": min_occurs_4 ,"name_4": name_4,
                                      "type_4": type_4 ,"min_occurs_5": min_occurs_5 ,"name_5": name_5 ,"type_5": type_5 ,
                                      "min_occurs_6": min_occurs_6,"name_6":name_6 ,"type_6": type_6 ,"min_occurs_7": min_occurs_7 ,"name_7": name_7 ,
                                      "type_7": type_7 ,"min_occurs_8": min_occurs_8 ,"name_8": name_8 ,"type_8":type_8 ,
                                      "min_occurs_9": min_occurs_9,"name_9": name_9 ,"type_9": type_9,"min_occurs_10":min_occurs_10 ,"name_10": name_10 ,
                                      "type_10": type_10 ,"name_11": name_11 ,"name_12": name_12 ,"use_current_locale": use_current_locale ,
                                      "curr_amt": curr_amt,"owner_of_the_shop":owner_of_the_shop ,"arr_amt": arr_amt ,"gid": gid ,"closing": closing ,
                                      "house_no": house_no,"city_name": city_name,"shop_name": shop_name,
                                      "id_1": id_1 ,"row_order":row_order,"shop_id": shop_id ,"gname":gname}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")
        #          ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"Body": {"userchargesdemandResponse": {"userchargesdemandResult": {"schema": {"id": "NewDataSet", "element": {"IsDataSet": "true", "complexType": {"choice": {"minOccurs": "0", "maxOccurs": "unbounded", "element": {"complexType": {"sequence": {"element": [{"minOccurs": "0", "name": "SHOPID", "type": "xs:double"}, {"minOccurs": "0", "name": "HOUSENO", "type": "xs:string"}, {"minOccurs": "0", "name": "CITY_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "SHOP_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "OWNEROFTHESHOP", "type": "xs:string"}, {"minOccurs": "0", "name": "ARRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CURRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CLOSING", "type": "xs:decimal"}, {"minOccurs": "0", "name": "GNAME", "type": "xs:string"}, {"minOccurs": "0", "name": "GID", "type": "xs:double"}]}}, "name": "gcharges_demand"}}}, "name": "NewDataSet", "UseCurrentLocale": "true"}}, "diffgram": {"NewDataSet": {"gcharges_demand": {"CURRAMT": "0", "OWNEROFTHESHOP": "BHARAT NARANG", "ARRAMT": "0", "GID": "25", "CLOSING": "0", "HOUSENO": "#7-1-89", "CITY_NAME": "BALASAMUDRAM", "SHOP_NAME": "ASIAN SRIDEVI SCREEN 3", "id": "gcharges_demand1", "rowOrder": "0", "SHOPID": "18324", "GNAME": "CINEMA HALLS AND ENTERTINMENT"}}}}}}}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/ZStN9b/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'User_Charges_Tax_PullV2') and active = 1);"
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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
def test_common_300_303_002():
    """
        Sub Feature Code: NonUI_Common_Config_GWMC_fetch_Meter_Charges_Tax_PullV2
        Sub Feature Description: fetching details of GWMC Merchant having key "Meter_Charges_Tax_PullV2" via fetch/data API
        TC naming code description:
        300: Config
        303: GWMC
        002: TC002

    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

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
            api_details = DBProcessor.get_api_details('fetch_Meter_Charges_Tax_PullV2')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            id = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['id']
            is_data_set = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['IsDataSet']
            min_occurs = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['minOccurs']
            max_occurs = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['maxOccurs']
            min_occurs_1 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][0]['minOccurs']
            name_1 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][0]['name']
            type_1 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][0]['type']
            min_occurs_2 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][1]['minOccurs']
            name_2 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][1]['name']
            type_2 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][1]['type']
            min_occurs_3 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][2]['minOccurs']
            name_3 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][2]['name']
            type_3 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][2]['type']
            min_occurs_4 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][3]['minOccurs']
            name_4 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][3]['name']
            type_4 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][3]['type']
            min_occurs_5 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][4]['minOccurs']
            name_5 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][4]['name']
            type_5 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][4]['type']
            min_occurs_6 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][5]['minOccurs']
            name_6 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][5]['name']
            type_6 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][5]['type']
            min_occurs_7 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][6]['minOccurs']
            name_7 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][6]['name']
            type_7 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][6]['type']
            min_occurs_8 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][7]['minOccurs']
            name_8 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][7]['name']
            type_8 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][7]['type']
            min_occurs_9 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][8]['minOccurs']
            name_9 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][8]['name']
            type_9 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][8]['type']
            min_occurs_10 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][9]['minOccurs']
            name_10 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][9]['name']
            type_10 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][9]['type']
            name_11 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['complexType']['choice']['element']['name']
            name_12 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['name']
            use_current_locale = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['element']['UseCurrentLocale']
            curr_amt = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['CURRAMT']
            owner = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['OWNER']
            status = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['STATUS']
            arr_amt = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['ARRAMT']
            closing = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['CLOSING']
            house_no = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['HOUSENO']
            assesment_desc = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['ASSESMENT_DESC']
            mn_no = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['MNNO']
            city_name = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['CITY_NAME']
            dia_size = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['DIASIZE']
            id_1 = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['id']
            row_order = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['rowOrder']

            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {id}, {is_data_set},{min_occurs}, {max_occurs},{min_occurs_1},{name_1},{type_1},"
                f"{min_occurs_2},{name_2},{type_2},{min_occurs_3},{name_3},{type_3},{min_occurs_4},{name_4},{type_4},{min_occurs_5},{name_5},{type_5},"
                f"{min_occurs_6},{name_6},{type_6},{min_occurs_7},{name_7},{type_7},{min_occurs_8},{name_8},{type_8},{min_occurs_9},{name_9},{type_9},{min_occurs_10},{name_10},{type_10},"
                f"{name_11},{name_12},{use_current_locale},{curr_amt},{owner},{status},{arr_amt},{closing},{house_no},{assesment_desc},{mn_no},"
                f"{city_name},{dia_size},{id_1},{row_order}")
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
                expectedAPIValues1 = {"success": True, "id": "NewDataSet" , "is_data_set": "true" ,"min_occurs": "0" ,
                                      "max_occurs": "unbounded" ,"min_occurs_1": "0" ,"name_1": "MNNO" ,"type_1": "xs:decimal" ,
                                      "min_occurs_2": "0" ,"name_2": "HOUSENO" ,"type_2": "xs:string" ,"min_occurs_3": "0" ,
                                      "name_3": "CITY_NAME" ,"type_3": "xs:string" ,"min_occurs_4": "0" ,"name_4": "OWNER" ,
                                      "type_4": "xs:string" ,"min_occurs_5": "0" ,"name_5": "STATUS" ,"type_5": "xs:string" ,
                                      "min_occurs_6": "0" ,"name_6": "DIASIZE" ,"type_6": "xs:string" ,"min_occurs_7": "0" ,
                                      "name_7": "ASSESMENT_DESC" ,"type_7": "xs:string" ,"min_occurs_8": "0" ,"name_8": "ARRAMT" ,
                                      "type_8": "xs:decimal" ,"min_occurs_9": "0" ,"name_9": "CURRAMT" ,"type_9": "xs:decimal" ,
                                      "min_occurs_10": "0" ,"name_10": "CLOSING" ,"type_10": "xs:decimal" ,"name_11": "metertapview" ,
                                      "name_12": "NewDataSet" ,"use_current_locale": "true" ,"curr_amt": "2040" ,
                                      "owner": "GOPU VENNAMMA" ,"status": "NULL" ,"arr_amt": "3570" ,"closing": "5610" ,
                                      "house_no": "#1-7-985" ,"assesment_desc": "APARTMENTS" ,"mn_no": "674" ,
                                      "city_name": "ADVOCATE COLONY" ,"dia_size": "1.5" ,"id_1": "metertapview1" ,"row_order":"0"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "id": id , "is_data_set": is_data_set,"min_occurs":min_occurs,
                                      "max_occurs": max_occurs ,"min_occurs_1": min_occurs_1 ,"name_1": name_1 ,"type_1": type_1 ,
                                      "min_occurs_2": min_occurs_2 ,"name_2": name_2,"type_2": type_2,"min_occurs_3": min_occurs_3,
                                      "name_3":name_3 ,"type_3": type_3 ,"min_occurs_4": min_occurs_4,"name_4":name_4,
                                      "type_4": type_4 ,"min_occurs_5": min_occurs_5,"name_5": name_5 ,"type_5": type_5 ,
                                      "min_occurs_6":min_occurs_6,"name_6": name_6 ,"type_6": type_6 ,"min_occurs_7":min_occurs_7,
                                      "name_7": name_7 ,"type_7": type_7 ,"min_occurs_8":min_occurs_8 ,"name_8": name_8 ,
                                      "type_8": type_8 ,"min_occurs_9":min_occurs_9 ,"name_9": name_9 ,"type_9": type_9 ,
                                      "min_occurs_10":min_occurs_10 ,"name_10": name_10 ,"type_10": type_10 ,"name_11": name_11 ,
                                      "name_12": name_12 ,"use_current_locale":use_current_locale,"curr_amt": curr_amt ,
                                      "owner": owner ,"status": status ,"arr_amt": arr_amt ,"closing": closing ,
                                      "house_no": house_no,"assesment_desc": assesment_desc,"mn_no": mn_no ,
                                      "city_name": city_name,"dia_size": dia_size ,"id_1": id_1 ,"row_order":row_order}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"Body": {"metertapdemandResponse": {"metertapdemandResult": {"schema": {"id": "NewDataSet", "element": {"IsDataSet": "true", "complexType": {"choice": {"minOccurs": "0", "maxOccurs": "unbounded", "element": {"complexType": {"sequence": {"element": [{"minOccurs": "0", "name": "MNNO", "type": "xs:decimal"}, {"minOccurs": "0", "name": "HOUSENO", "type": "xs:string"}, {"minOccurs": "0", "name": "CITY_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "OWNER", "type": "xs:string"}, {"minOccurs": "0", "name": "STATUS", "type": "xs:string"}, {"minOccurs": "0", "name": "DIASIZE", "type": "xs:string"}, {"minOccurs": "0", "name": "ASSESMENT_DESC", "type": "xs:string"}, {"minOccurs": "0", "name": "ARRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CURRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CLOSING", "type": "xs:decimal"}]}}, "name": "metertapview"}}}, "name": "NewDataSet", "UseCurrentLocale": "true"}}, "diffgram": {"NewDataSet": {"metertapview": {"CURRAMT": "2040", "OWNER": "GOPU VENNAMMA", "STATUS": "NULL", "ARRAMT": "3570", "CLOSING": "5610", "HOUSENO": "#1-7-985", "ASSESMENT_DESC": "APARTMENTS", "MNNO": "674", "CITY_NAME": "ADVOCATE COLONY", "DIASIZE": "1.5", "id": "metertapview1", "rowOrder": "0"}}}}}}}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/YvTmTy/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'Meter_Charges_Tax_PullV2') and active = 1);"
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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
def test_common_300_303_003():
    """
        Sub Feature Code: NonUI_Common_Config_GWMC_fetch_Trade_Tax_PullV2
        Sub Feature Description: fetching details of GWMC Merchant having key "Trade_Tax_PullV2" via fetch/data API
        TC naming code description:
        300: Config
        303: GWMC
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
            api_details = DBProcessor.get_api_details('fetch_Trade_Tax_PullV2')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            id = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['id']
            is_data_set = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['IsDataSet']
            min_occurs = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['minOccurs']
            max_occurs = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['maxOccurs']
            min_occurs_1 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][0]['minOccurs']
            name_1 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][0]['name']
            type_1 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][0]['type']
            min_occurs_2 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][1]['minOccurs']
            name_2 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][1]['name']
            type_2 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][1]['type']
            min_occurs_3 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][2]['minOccurs']
            name_3 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][2]['name']
            type_3 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][2]['type']
            min_occurs_4 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][3]['minOccurs']
            name_4 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][3]['name']
            type_4 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][3]['type']
            min_occurs_5 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][4]['minOccurs']
            name_5 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][4]['name']
            type_5 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][4]['type']
            min_occurs_6 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][5]['minOccurs']
            name_6 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][5]['name']
            type_6 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][5]['type']
            min_occurs_7 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][6]['minOccurs']
            name_7 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][6]['name']
            type_7 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][6]['type']
            min_occurs_8 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][7]['minOccurs']
            name_8 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][7]['name']
            type_8 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][7]['type']
            min_occurs_9 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][8]['minOccurs']
            name_9 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][8]['name']
            type_9 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][8]['type']
            min_occurs_10 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][9]['minOccurs']
            name_10 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][9]['name']
            type_10 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][9]['type']
            min_occurs_11 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][10]['minOccurs']
            name_11 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][10]['name']
            type_11 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][10]['type']
            min_occurs_12 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][11]['minOccurs']
            name_12 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][11]['name']
            type_12 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][11]['type']
            min_occurs_13 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][12]['minOccurs']
            name_13 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][12]['name']
            type_13 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][12]['type']
            min_occurs_14 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][13]['minOccurs']
            name_14 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][13]['name']
            type_14 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][13]['type']
            min_occurs_15 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][14]['minOccurs']
            name_15 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][14]['name']
            type_15 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][14]['type']
            min_occurs_16 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][15]['minOccurs']
            name_16 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][15]['name']
            type_16 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][15]['type']
            min_occurs_17 =  response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][16]['minOccurs']
            name_17 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][16]['name']
            type_17 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][16]['type']
            min_occurs_18 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][17]['minOccurs']
            name_18 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][17]['name']
            type_18 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][17]['type']
            min_occurs_19 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][18]['minOccurs']
            name_19 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][18]['name']
            type_19 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][18]['type']
            min_occurs_20 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][19]['minOccurs']
            name_20 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][19]['name']
            type_20 =  response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][19]['type']
            min_occurs_21 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][20]['minOccurs']
            name_21 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][20]['name']
            type_21 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][20]['type']
            min_occurs_22 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][21]['minOccurs']
            name_22 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][21]['name']
            type_22 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['complexType']['sequence']['element'][21]['type']
            name_23 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['complexType']['choice']['element']['name']
            name_24 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['name']
            use_current_locale = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['element']['UseCurrentLocale']
            partner = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['PARTNER']
            curr_amt = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['CURRAMT']
            ofines = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['OFINES']
            closing = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['CLOSING']
            house_no = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['HOUSENO']
            fines = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['FINES']
            dyear = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['DYEAR']
            shop_name = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['SHOP_NAME']
            cfines = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['CFINES']
            block = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['BLOCK']
            hno = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['HNO']
            aadhar = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['AADHAR']
            row_order = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['rowOrder']
            shop_id = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['SHOPID']
            owner_of_the_shop = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['OWNEROFTHESHOP']
            status = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['STATUS']
            arr_amt = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['ARRAMT']
            ward = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['WARD']
            city_name = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['CITY_NAME']
            trade_code = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['TRADE_CODE']
            id_1 = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['id']
            trade_desc = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['TRADE_DESC']
            hno_id = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['HNOID']
            age = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['AGE']

            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {id}, {is_data_set},{min_occurs}, {max_occurs},{min_occurs_1},{name_1},{type_1},"
                f"{min_occurs_2},{name_2},{type_2},{min_occurs_3},{name_3},{type_3},{min_occurs_4},{name_4},{type_4},{min_occurs_5},{name_5},{type_5},"
                f"{min_occurs_6},{name_6},{type_6},{min_occurs_7},{name_7},{type_7},{min_occurs_8},{name_8},{type_8},{min_occurs_9},{name_9},{type_9},{min_occurs_10},{name_10},{type_10},"
                f"{min_occurs_11},{name_11},{type_11},{min_occurs_12},{name_12},{type_12},{min_occurs_13},{name_13},{type_13},{min_occurs_14},{name_14},{type_14},{min_occurs_15},{name_15},{type_15},"
                f"{min_occurs_16},{name_16},{type_16},{min_occurs_17},{name_17},{type_17},{min_occurs_18},{name_18},{type_18},{min_occurs_19},{name_19},{type_19},{min_occurs_20},{name_20},{type_20},"
                f"{min_occurs_21},{name_21},{type_21},{min_occurs_22},{name_22},{type_22},{name_23},{name_24},{use_current_locale},{partner},{curr_amt},{ofines},{closing},{house_no},{fines},{dyear},{shop_name},"
                f"{cfines},{block},{hno},{aadhar},{row_order},{shop_id},{owner_of_the_shop},{status},{arr_amt},{ward},{city_name},{trade_code},{id_1},{trade_desc},{hno_id},{age}")
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
                expectedAPIValues1 = {"success": True, "id": "NewDataSet" , "is_data_set": "true" ,"min_occurs": "0" ,
                                      "max_occurs": "unbounded" ,"min_occurs_1": "0" ,"name_1": "SHOPID" ,"type_1": "xs:double" ,
                                      "min_occurs_2": "0" ,"name_2": "SHOP_NAME" ,"type_2": "xs:string" ,"min_occurs_3": "0" ,"name_3": "CITY_NAME" ,
                                      "type_3": "xs:string" ,"min_occurs_4": "0" ,"name_4": "HNOID" ,"type_4": "xs:decimal" ,"min_occurs_5": "0" ,
                                      "name_5": "OWNEROFTHESHOP" ,"type_5": "xs:string" ,"min_occurs_6": "0" ,"name_6": "TRADE_DESC" ,
                                      "type_6": "xs:string" ,"min_occurs_7": "0" ,"name_7": "TRADE_CODE" ,"type_7": "xs:decimal" ,"min_occurs_8": "0" ,
                                      "name_8": "WARD" ,"type_8": "xs:decimal" ,"min_occurs_9": "0" ,"name_9": "BLOCK" ,"type_9": "xs:decimal" ,
                                      "min_occurs_10": "0" ,"name_10": "HNO" ,"type_10": "xs:string" ,"min_occurs_11": "0" ,"name_11": "HOUSENO" ,
                                      "type_11": "xs:string" ,"min_occurs_12": "0" ,"name_12": "AGE" ,"type_12": "xs:decimal" ,"min_occurs_13": "0" ,
                                      "name_13": "PARTNER" ,"type_13": "xs:string" ,"min_occurs_14": "0" ,"name_14": "AADHAR" ,"type_14": "xs:string" ,
                                      "min_occurs_15": "0" ,"name_15": "STATUS" ,"type_15": "xs:string" ,"min_occurs_16": "0" ,"name_16": "ARRAMT" ,
                                      "type_16": "xs:decimal" ,"min_occurs_17": "0" ,"name_17": "CURRAMT" ,"type_17": "xs:decimal" ,"min_occurs_18": "0" ,"name_18": "CLOSING" ,
                                      "type_18": "xs:decimal" ,"min_occurs_19": "0" ,"name_19": "OFINES" ,"type_19": "xs:decimal" ,"min_occurs_20": "0" ,"name_20": "FINES" ,
                                      "type_20": "xs:decimal" ,"min_occurs_21": "0" ,"name_21": "CFINES" ,"type_21": "xs:decimal" ,"min_occurs_22": "0" ,"name_22": "DYEAR" ,
                                      "type_22": "xs:string" ,"name_23": "TRADEDEMAND" ,"name_24": "NewDataSet" ,"use_current_locale": "true" ,
                                      "partner": "GAJULA RAJAMOULI" ,"curr_amt": "2000" ,"ofines": "0" ,"closing": "2000" ,"house_no": "1-1-227/20/1" ,"fines": "0" ,"dyear": "2022-23" ,
                                      "shop_name": "VARDHAN KIRANAM" ,"cfines": "0" ,"block": "1" ,"hno": "227/20/1" ,"aadhar":"880601356959",
                                      "row_order": "0" ,"shop_id": "45067" ,"owner_of_the_shop": "GAJULA VAMSHI" ,"status": "-" ,"arr_amt": "0" ,
                                      "ward": "1" ,"city_name": "PRASHANTI NAGAR" ,"trade_code": "2" ,"id_1": "TRADEDEMAND1" ,
                                      "trade_desc": "KIRANA SHOP" ,"hno_id": "139901" ,"age":"25"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "id": id, "is_data_set": is_data_set ,"min_occurs": min_occurs ,
                                      "max_occurs": max_occurs,"min_occurs_1": min_occurs_1 ,"name_1":name_1 ,"type_1": type_1,
                                      "min_occurs_2":min_occurs_2 ,"name_2": name_2 ,"type_2":type_2,"min_occurs_3": min_occurs_3 ,"name_3": name_3,
                                      "type_3": type_3 ,"min_occurs_4": min_occurs_4 ,"name_4": name_4 ,"type_4": type_4 ,"min_occurs_5": min_occurs_5 ,
                                      "name_5": name_5 ,"type_5": type_5,"min_occurs_6": min_occurs_6 ,"name_6": name_6 ,
                                      "type_6": type_6 ,"min_occurs_7":min_occurs_7 ,"name_7": name_7 ,"type_7": type_7 ,"min_occurs_8":min_occurs_8 ,
                                      "name_8": name_8,"type_8": type_8 ,"min_occurs_9": min_occurs_9 ,"name_9": name_9 ,"type_9": type_9 ,
                                      "min_occurs_10": min_occurs_10 ,"name_10": name_10 ,"type_10": type_10,"min_occurs_11":min_occurs_11,"name_11": name_11 ,
                                      "type_11": type_11 ,"min_occurs_12": min_occurs_12 ,"name_12":name_12,"type_12": type_12 ,"min_occurs_13": min_occurs_13 ,
                                      "name_13":name_13,"type_13": type_13 ,"min_occurs_14": min_occurs_14 ,"name_14": name_14 ,"type_14":type_14 ,
                                      "min_occurs_15": min_occurs_15 ,"name_15":name_15,"type_15": type_15,"min_occurs_16": min_occurs_16,"name_16":name_16 ,
                                      "type_16": type_16 ,"min_occurs_17":min_occurs_17,"name_17": name_17 ,"type_17": type_17 ,"min_occurs_18":min_occurs_18 ,"name_18": name_18,
                                      "type_18": type_18 ,"min_occurs_19": min_occurs_19 ,"name_19": name_19 ,"type_19":type_19 ,"min_occurs_20": min_occurs_20 ,"name_20":name_20,
                                      "type_20": type_20 ,"min_occurs_21": min_occurs_21 ,"name_21": name_21 ,"type_21": type_21 ,"min_occurs_22": min_occurs_22 ,"name_22": name_22,
                                      "type_22": type_22 ,"name_23":name_23 ,"name_24": name_24 ,"use_current_locale": use_current_locale ,
                                      "partner": partner,"curr_amt": curr_amt ,"ofines": ofines,"closing": closing ,"house_no": house_no,"fines": fines ,"dyear": dyear ,
                                      "shop_name": shop_name ,"cfines":cfines,"block": block,"hno": hno ,"aadhar":aadhar,
                                      "row_order": row_order ,"shop_id": shop_id ,"owner_of_the_shop": owner_of_the_shop ,"status": status ,"arr_amt": arr_amt ,
                                      "ward":ward,"city_name": city_name,"trade_code":trade_code ,"id_1": id_1,
                                      "trade_desc": trade_desc ,"hno_id": hno_id ,"age":age}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"Body": {"tradedemandResponse": {"tradedemandResult": {"schema": {"id": "NewDataSet", "element": {"IsDataSet": "true", "complexType": {"choice": {"minOccurs": "0", "maxOccurs": "unbounded", "element": {"complexType": {"sequence": {"element": [{"minOccurs": "0", "name": "SHOPID", "type": "xs:double"}, {"minOccurs": "0", "name": "SHOP_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "CITY_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "HNOID", "type": "xs:decimal"}, {"minOccurs": "0", "name": "OWNEROFTHESHOP", "type": "xs:string"}, {"minOccurs": "0", "name": "TRADE_DESC", "type": "xs:string"}, {"minOccurs": "0", "name": "TRADE_CODE", "type": "xs:decimal"}, {"minOccurs": "0", "name": "WARD", "type": "xs:decimal"}, {"minOccurs": "0", "name": "BLOCK", "type": "xs:decimal"}, {"minOccurs": "0", "name": "HNO", "type": "xs:string"}, {"minOccurs": "0", "name": "HOUSENO", "type": "xs:string"}, {"minOccurs": "0", "name": "AGE", "type": "xs:decimal"}, {"minOccurs": "0", "name": "PARTNER", "type": "xs:string"}, {"minOccurs": "0", "name": "AADHAR", "type": "xs:string"}, {"minOccurs": "0", "name": "STATUS", "type": "xs:string"}, {"minOccurs": "0", "name": "ARRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CURRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CLOSING", "type": "xs:decimal"}, {"minOccurs": "0", "name": "OFINES", "type": "xs:decimal"}, {"minOccurs": "0", "name": "FINES", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CFINES", "type": "xs:decimal"}, {"minOccurs": "0", "name": "DYEAR", "type": "xs:string"}]}}, "name": "TRADEDEMAND"}}}, "name": "NewDataSet", "UseCurrentLocale": "true"}}, "diffgram": {"NewDataSet": {"TRADEDEMAND": {"PARTNER": "GAJULA RAJAMOULI", "CURRAMT": "2000", "OFINES": "0", "CLOSING": "2000", "HOUSENO": "1-1-227/20/1", "FINES": "0", "DYEAR": "2022-23", "SHOP_NAME": "VARDHAN KIRANAM", "CFINES": "0", "BLOCK": "1", "HNO": "227/20/1", "AADHAR": "880601356959", "rowOrder": "0", "SHOPID": "45067", "OWNEROFTHESHOP": "GAJULA VAMSHI", "STATUS": "-", "ARRAMT": "0", "WARD": "1", "CITY_NAME": "PRASHANTI NAGAR", "TRADE_CODE": "2", "id": "TRADEDEMAND1", "TRADE_DESC": "KIRANA SHOP", "HNOID": "139901", "AGE": "25"}}}}}}}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/efZ1iC/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'Trade_Tax_PullV2') and active = 1);"
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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
def test_common_300_303_004():
    """
            Sub Feature Code: NonUI_Common_Config_GWMC_fetch_get_gwmc_tax_wcdemand
            Sub Feature Description: fetching details of GWMC Merchant having key "get_gwmc_tax_wcdemand" via fetch/data API
            TC naming code description:
            300: Config
            303: GWMC
            004: TC004

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
            api_details = DBProcessor.get_api_details('fetch_get_gwmc_tax_wcdemand')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            cons_no = response['data']['response'][0]['CONSNO']
            ofines = response['data']['response'][0]['OFINES']
            fines = response['data']['response'][0]['FINES']
            house_no = response['data']['response'][0]['HOUSENO']
            gtax = response['data']['response'][0]['GTAX']
            cell_no = response['data']['response'][0]['CELLNO']
            clgt = response['data']['response'][0]['CLGT']
            clwc = response['data']['response'][0]['CLWC']
            row_order = response['data']['response'][0]['rowOrder']
            wc = response['data']['response'][0]['WC']
            name = response['data']['response'][0]['NAME']
            clpt = response['data']['response'][0]['CLPT']
            arswc = response['data']['response'][0]['ARSWC']
            arsgt = response['data']['response'][0]['ARSGT']
            city_name = response['data']['response'][0]['CITY_NAME']
            id = response['data']['response'][0]['id']
            arspt = response['data']['response'][0]['ARSPT']
            idno = response['data']['response'][0]['IDNO']
            error_code = response['data']['response'][0]['errorcode']
            ptax = response['data']['response'][0]['PTAX']
            hno_id = response['data']['response'][0]['HNOID']

            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {cons_no}, {ofines},{fines},{house_no},{gtax},{cell_no},{clgt},"
                        f"{clwc},{row_order},{wc},{name},{clpt},{arswc},{arsgt},{city_name},{id},{arspt},{idno},{error_code},{ptax},{hno_id}")

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
                expectedAPIValues1 = {"success": True, "cons_no": "38122" , "ofines": "0" ,"fines": "0" ,"house_no": "16-10-1347" ,
                                      "gtax": "1440" ,"cell_no": "9296452832" ,"clgt": "1440" ,"clwc": "1800" ,"row_order": "0" ,"wc": "1800"
                                    ,"name": "AMARAVADHI VIJAYA SARADHI  AND A.SHESHA CHALA" ,"clpt": "3316" ,"arswc": "0" ,"arsgt": "0" ,
                                      "city_name": "SHIVA NAGAR" ,"id": "HouseMaster1" ,"arspt": "0" ,"idno": "0916101447" ,"error_code": "00" ,
                                      "ptax": "3316" ,"hno_id":"105821"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "cons_no": cons_no , "ofines": ofines,"fines":fines ,"house_no": house_no,
                                      "gtax": gtax,"cell_no": cell_no ,"clgt":clgt ,"clwc": clwc ,"row_order":row_order,"wc": wc
                                    ,"name": name,"clpt": clpt ,"arswc":arswc ,"arsgt": arsgt ,
                                      "city_name": city_name ,"id": id ,"arspt":arspt,"idno": idno ,"error_code": error_code ,
                                      "ptax": ptax ,"hno_id":hno_id}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"CONSNO": "38122", "OFINES": "0", "FINES": "0", "HOUSENO": "16-10-1347", "GTAX": "1440", "CELLNO": "9296452832", "CLGT": "1440", "CLWC": "1800", "rowOrder": "0", "WC": "1800", "NAME": "AMARAVADHI VIJAYA SARADHI  AND A.SHESHA CHALA", "CLPT": "3316", "ARSWC": "0", "ARSGT": "0", "CITY_NAME": "SHIVA NAGAR", "id": "HouseMaster1", "ARSPT": "0", "IDNO": "0916101447", "errorcode": "00", "PTAX": "3316", "HNOID": "105821"}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/1h7nkR/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_gwmc_tax_wcdemand') and active = 1);"
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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
def test_common_300_303_005():
    """
            Sub Feature Code: NonUI_Common_Config_GWMC_fetch_get_gwmc_tax_head
            Sub Feature Description: fetching details of GWMC Merchant having key "get_gwmc_tax_head" via fetch/data API
            TC naming code description:
            300: Config
            303: GWMC
            005: TC005

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
            api_details = DBProcessor.get_api_details('fetch_get_gwmc_tax_head')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            amt_1 = response['data']['response'][0]['keys'][0]['AMOUNT']
            head_code_1 = response['data']['response'][0]['keys'][0]['HEADCODE']
            head_name_1 = response['data']['response'][0]['keys'][0]['HEADNAME']
            amt_2 = response['data']['response'][0]['keys'][1]['AMOUNT']
            head_code_2 = response['data']['response'][0]['keys'][1]['HEADCODE']
            head_name_2 = response['data']['response'][0]['keys'][1]['HEADNAME']
            amt_3 = response['data']['response'][0]['keys'][2]['AMOUNT']
            head_code_3 = response['data']['response'][0]['keys'][2]['HEADCODE']
            head_name_3 = response['data']['response'][0]['keys'][2]['HEADNAME']
            amt_4 = response['data']['response'][0]['keys'][3]['AMOUNT']
            head_code_4 = response['data']['response'][0]['keys'][3]['HEADCODE']
            head_name_4 = response['data']['response'][0]['keys'][3]['HEADNAME']
            error_code = response['data']['response'][0]['errorcode']
            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {amt_1}, {head_code_1},{head_name_1},"
                        f"{amt_2}, {head_code_2},{head_name_2}, {amt_3}, {head_code_3},{head_name_3},"
                        f"{amt_4}, {head_code_4},{head_name_4},{error_code}")

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
                expectedAPIValues1 = {"success": True, "amt_1": "0" , "head_code_1": "253" ,"head_name_1": "COVID 19 FINES" ,
                                      "amt_2": "0" , "head_code_2": "229" ,"head_name_2": "FINES ON LITTERING" ,
                                      "amt_3": "0" , "head_code_3": "230" ,"head_name_3": "FINES ON PLASTIC" ,
                                      "amt_4": "0" ,"head_code_4": "195" ,"head_name_4": "SWM FINES" ,"error_code":"00"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success,"amt_1": amt_1, "head_code_1": head_code_1 ,"head_name_1": head_name_1 ,
                                      "amt_2": amt_2 , "head_code_2":head_code_2 ,"head_name_2": head_name_2,
                                      "amt_3": amt_3, "head_code_3": head_code_3,"head_name_3": head_name_3,
                                      "amt_4": amt_4,"head_code_4": head_code_4,"head_name_4": head_name_4 ,"error_code":error_code}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                # expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"keys": [{"AMOUNT": "0", "HEADCODE": "253", "HEADNAME": "COVID 19 FINES"}, {"AMOUNT": "0", "HEADCODE": "229", "HEADNAME": "FINES ON LITTERING"}, {"AMOUNT": "0", "HEADCODE": "230", "HEADNAME": "FINES ON PLASTIC"}, {"AMOUNT": "0", "HEADCODE": "195", "HEADNAME": "SWM FINES"}], "errorcode": "00"}]}}'}
                # logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                # actualAPIValues2 = {"Result": response_data}
                # logger.debug(f"actualAPIValues: {actualAPIValues2}")
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/POh9sU/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_gwmc_tax_head') and active = 1);"
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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
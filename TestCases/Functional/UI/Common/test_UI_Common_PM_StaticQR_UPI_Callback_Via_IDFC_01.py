import random
import sys
import requests
import pytest
from Configuration import testsuite_teardown, Configuration
from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_100_107_016():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Callback_Success_Autorefund_Enabled_Via_IDFC
    Sub Feature Description: Verifying UPI static QR Success callback when autorefund is enabled via IDFC
    TC naming code description:: 100: payment method, 107: UPI Static QR, 016: Testcase ID
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Enable auto refund
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund enabled is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Get vpa from upi_merchant_config table
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"

            result = DBProcessor.getValueFromDB(query)

            db_upi_config_id = result['id'].values[0]
            logger.info(f"fetched upi config id is : {db_upi_config_id}")

            db_upi_config_vpa = result['vpa'].values[0]
            logger.info(f"fetched vpa is : {db_upi_config_vpa}")

            db_upi_config_mid = result['mid'].values[0]
            logger.info(f"fetched mid is : {db_upi_config_mid}")

            db_upi_config_tid = result['tid'].values[0]
            logger.info(f"fetched tid is : {db_upi_config_tid}")

            testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username ,
                "qrCodeFormat" : "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")

            res_generateqr_success = response["success"]
            res_generateqr_username = response["username"]
            res_generateqr_publish_id = response["publishId"]
            res_generateqr_org_code = response["merchantCode"]
            res_generateqr_mid = response["mid"]
            res_generateqr_tid = response["tid"]

            # Generate HMAC and MerchCreds
            amount = random.randint(201, 300)
            logger.debug(f"generated random amount is : {amount}")

            # orig_cust_ref_id = str(random.randint(1000000, 999999)) + str(random.randint(1000000, 999999))
            orig_cust_ref_id = random.randint(11111110, 99999999)

            logger.debug(f"generated random org_cust_ref_id is : {orig_cust_ref_id}")

            ResCode = "000"
            req_merch_creds = "fCef5gQC8s861hBigj+NX7QTY7HuNjbRncLxYnphVJA="
            req_hmac = "8066ac67ef88ea969f0ca50a2c5f43b9ac298ab761b94e778e25d015faaf89b6"

            api_url = "http://192.168.3.80:8089/idfc/hmac_merchant_creds/generate"
            headers = {'Content-Type': 'application/json'}
            req_payload1 = {"MerchantCredential": req_merch_creds,
                    "ResCode": ResCode,
                    "PayerMobileNumber": "+919159362349",
                    "TxnType": "MerchantCREDIT",
                    "SubMerchantID": "-",
                    "statusUpdateRetryCount": "0",
                    "OperationName": "MerchantStatusUpdateReq",
                    "OrgTxnTimeStamp": "280622111525",
                    "HMAC": req_hmac,
                    "Amount": amount,
                    "PayeeMobileNumber": "+919159362350",
                    "PayerVirAddr": "divya.ezetap@idfb",
                    "PayeeVirAddr": db_upi_config_vpa,
                    "MerchantID": db_upi_config_mid,
                    "OrgCustRefId": orig_cust_ref_id,
                    "OrgTxnRefId": res_generateqr_publish_id,
                    "TimeStamp": "280622111524",
                    "TxnId": "IDFEZ3C11C084F3C54749926E0B852BBF32",
                    "Remarks": "test1",
                    "TerminalID": db_upi_config_tid,
                    "ResDesc": "NO ORIGINAL REQUEST FOUND DURING DEBIT/CREDIT",
                    "OrgTxnId": "IDFEZ3C11C084F3C54749926E0B852GBF32"}

            response1 = requests.post(url=api_url, json=req_payload1, headers=headers)
            response_merch_creds = response1.text.replace("\n","")

            logger.debug(f"First response received : {str(response_merch_creds)}")

            sub_string1 = "MerchantCreds="
            sub_string2 = "HMAC="

            index1 = response_merch_creds.index(sub_string1)
            index2 = response_merch_creds.index(sub_string2)
            generated_merch_creds = response_merch_creds[index1 + len(sub_string1): index2]
            logger.debug(f"Generated MerchCreds is : {generated_merch_creds}")

            req_payload2 = {"MerchantCredential": generated_merch_creds,
                           "ResCode": ResCode,
                           "PayerMobileNumber": "+919159362349",
                           "TxnType": "MerchantCREDIT",
                           "SubMerchantID": "-",
                           "statusUpdateRetryCount": "0",
                           "OperationName": "MerchantStatusUpdateReq",
                           "OrgTxnTimeStamp": "280622111525",
                           "HMAC": req_hmac,
                           "Amount": amount,
                           "PayeeMobileNumber": "+919159362350",
                           "PayerVirAddr": "divya.ezetap@idfb",
                           "PayeeVirAddr": db_upi_config_vpa,
                           "MerchantID": db_upi_config_mid,
                           "OrgCustRefId": orig_cust_ref_id,
                           "OrgTxnRefId": res_generateqr_publish_id,
                           "TimeStamp": "280622111524",
                           "TxnId": "IDFEZ3C11C084F3C54749926E0B852BBF32",
                           "Remarks": "test1",
                           "TerminalID": db_upi_config_tid,
                           "ResDesc": "NO ORIGINAL REQUEST FOUND DURING DEBIT/CREDIT",
                           "OrgTxnId": "IDFEZ3C11C084F3C54749926E0B852GBF32"}

            response2 = requests.post(url=api_url, json=req_payload2, headers=headers)
            response_hmac = response2.text

            res = response_hmac.split('HMAC=', 1)
            generated_hmac = res[1]

            logger.debug(f"Second response received : {str(response_hmac)}")
            logger.debug(f"Value of HMAC is : {generated_hmac}")

            req_payload3 = {"MerchantCredential": generated_merch_creds,
                           "ResCode": ResCode,
                           "PayerMobileNumber": "+919159362349",
                           "TxnType": "MerchantCREDIT",
                           "SubMerchantID": "-",
                           "statusUpdateRetryCount": "0",
                           "OperationName": "MerchantStatusUpdateReq",
                           "OrgTxnTimeStamp": "280622111525",
                           "HMAC": generated_hmac,
                           "Amount": amount,
                           "PayeeMobileNumber": "+919159362350",
                           "PayerVirAddr": "divya.ezetap@idfb",
                           "PayeeVirAddr": db_upi_config_vpa,
                           "MerchantID": db_upi_config_mid,
                           "OrgCustRefId": orig_cust_ref_id,
                           "OrgTxnRefId": res_generateqr_publish_id,
                           "TimeStamp": "280622111524",
                           "TxnId": "IDFEZ3C11C084F3C54749926E0B852BBF32",
                           "Remarks": "test1",
                           "TerminalID": db_upi_config_tid,
                           "ResDesc": "NO ORIGINAL REQUEST FOUND DURING DEBIT/CREDIT",
                           "OrgTxnId": "IDFEZ3C11C084F3C54749926E0B852GBF32"}

            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print(generated_merch_creds)
            print("###################################################################################")
            print("###################################################################################")
            print("###################################################################################")
            print("###################################################################################")
            print("###################################################################################")
            print("###################################################################################")
            print("###################################################################################")
            print("###################################################################################")
            print("###################################################################################")

            response3 = requests.post(url=api_url, json=req_payload3, headers=headers)
            response_final = response3.text

            logger.debug(f"Third response received : {str(response_final)}")

            # UPI Callback
            api_details = DBProcessor.get_api_details('staticQR_UPI_IDFC_callback', request_body=req_payload3)
            response = APIProcessor.send_request(api_details)

            logger.debug(f"Response received for staticQR_UPI_IDFC_callback api is : {response}")

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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_api_values = {"success": True,
                                       "username": portal_username,
                                       "tid": db_upi_config_tid,
                                       "mid": db_upi_config_mid,
                                       "merchantCode": org_code
                                       }

                actual_api_values = {"success": res_generateqr_success,
                                     "username": res_generateqr_username,
                                     "tid": res_generateqr_tid,
                                     "mid": res_generateqr_mid,
                                     "merchantCode": res_generateqr_org_code
                                    }
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "org_code" : org_code,
                    "vpa" :db_upi_config_vpa,
                    "user_mobile" :app_username,
                    "user_name" :app_username,
                    "mid" :db_upi_config_mid,
                    "tid" :db_upi_config_tid,
                    "qr_type" :"UPI",
                    "intent_type" :"STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from staticqr_intent where publish_id='" + str(res_generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")

                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                db_staticqrIntent_org_code = result["org_code"].iloc[0]
                db_staticqrIntent_vpa = result["vpa"].iloc[0]
                db_staticqrIntent_user_mobile = result["user_mobile"].iloc[0]
                db_staticqrIntent_user_name = result["user_name"].iloc[0]
                db_staticqrIntent_mid = result["mid"].iloc[0]
                db_staticqrIntent_tid = result["tid"].iloc[0]
                db_staticqrIntent_qrtype = result["qr_type"].iloc[0]
                db_staticqrIntent_intent_type = result["intent_type"].iloc[0]

                actual_db_values = {
                    "org_code" : db_staticqrIntent_org_code,
                    "vpa" :db_staticqrIntent_vpa,
                    "user_mobile" :db_staticqrIntent_user_mobile,
                    "user_name" :db_staticqrIntent_user_name,
                    "mid" :db_staticqrIntent_mid,
                    "tid" :db_staticqrIntent_tid,
                    "qr_type" :db_staticqrIntent_qrtype,
                    "intent_type" :db_staticqrIntent_intent_type
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)


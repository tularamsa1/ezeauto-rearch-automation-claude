import sys
import pytest
import random
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_421():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_UPG_AUTOREFUND_DISABLED_HDFC_MINTOAK and UI_Common_PM_BQRV4_UPG_AUTOREFUND_DISABLED_HDFC_MINTOAK_TID_Dep
    Sub Feature Description: Verification of a BQRv4 UPG txn when Auto refund is disabled via HDFC_MINTOAK and TID Dep - Verification of  a BQRv4 UPG txn when Auto refund is disabled via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 421: TC421
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
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = f"select org_code from org_employee where username = '{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                            portal_un=portal_username, portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Query result pgMerchantId : {pg_merchant_id}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(251, 300)
            logger.debug(f"Amount generated:{amount}")
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            logger.debug(f"upg_txn_id generated:{upg_txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"mtxn_id generated:{mtxn_id}")
            rrn = str(random.randint(10000000, 99999999))
            logger.debug(f"generated rrn value is:{rrn}")

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = rrn
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = upg_txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-UPI"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")

            logger.debug(f"performing callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from invalid_pg_request where request_id ='{upg_txn_id}';"
            logger.debug(f"query to fetch data from invalid_pg_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            ipr_txn_id = result['txn_id'].iloc[0]
            logger.debug(f"fetched txn_id is : {ipr_txn_id}")
            ipr_payment_mode = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode is : {ipr_payment_mode}")
            ipr_bank_code = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code is : {ipr_bank_code}")
            ipr_org_code = result["org_code"].iloc[0]
            logger.debug(f"fetched org_code is : {ipr_org_code}")
            ipr_amount = result["amount"].iloc[0]
            logger.debug(f"fetched amount is : {ipr_amount}")
            ipr_rrn = result["rrn"].iloc[0]
            logger.debug(f"fetched rrn is : {ipr_rrn}")
            ipr_auth_code = result["auth_code"].iloc[0]
            logger.debug(f"fetched auth_code is : {ipr_auth_code}")
            ipr_mid = result["mid"].iloc[0]
            logger.debug(f"fetched mid is : {ipr_mid}")
            ipr_tid = result["tid"].iloc[0]
            logger.debug(f"fetched tid is : {ipr_tid}")
            ipr_config_id = result["config_id"].iloc[0]
            logger.debug(f"fetched config_id is : {ipr_config_id}")
            ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
            logger.debug(f"fetched pg_merchant_id is : {ipr_pg_merchant_id}")

            query = f"select * from txn where id = '{ipr_txn_id}';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            status_db = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {status_db}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid from txn table is : {mid_db}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                                            "pmt_mode": "UPI",
                                            "pmt_status": "UPG_AUTHORIZED",
                                            "settle_status": "SETTLED",
                                            "txn_id": ipr_txn_id,
                                            "txn_amt": "{:.2f}".format(amount),
                                            "rrn": str(rrn),
                                            "pmt_msg": "PAYMENT SUCCESSFUL",
                                            "date": date_and_time
                                        }

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)

                loginPage = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.wait_for_home_page_load()
                homePage.check_home_page_logo()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(ipr_txn_id)

                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {ipr_txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {ipr_txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {ipr_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {ipr_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {ipr_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {ipr_txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {ipr_txn_id}, {app_rrn}")

                actual_app_values = {
                                        "pmt_status": app_payment_status.split(':')[1],
                                        "pmt_mode": app_payment_mode,
                                        "txn_id": app_txn_id,
                                        "txn_amt": str(app_amount).split(' ')[1],
                                        "rrn": str(app_rrn),
                                        "settle_status": app_settlement_status,
                                        "pmt_msg": app_payment_msg,
                                        "date": app_date_and_time
                                    }

                logger.debug(f"actualAppValues: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                                            "pmt_status": "UPG_AUTHORIZED",
                                            "txn_amt": amount,
                                            "pmt_mode": "UPI",
                                            "pmt_state": "UPG_AUTHORIZED",
                                            "rrn": str(rrn),
                                            "settle_status": "SETTLED",
                                            "acquirer_code": "HDFC",
                                            "issuer_code": "HDFC",
                                            "txn_type": txn_type,
                                            "mid": mid,
                                            "tid": tid,
                                            "org_code": org_code_txn,
                                            "date": date
                                        }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == ipr_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"fetched status from API response is : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"fetched amount from API response is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"fetched payment_mode from API response is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"fetched state from API response is : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"fetched rrn from API response is : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"fetched settlement_status from API response is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"fetched issuer_code from API response is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"fetched acquirer_code from API response is : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"fetched orgCode from API response is : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"fetched mid from API response is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"fetched tid from API response is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"fetched txn_type from API response is : {txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"fetched date from API response is : {date_api}")

                actual_api_values = {
                                        "pmt_status": status_api,
                                        "txn_amt": amount_api,
                                        "pmt_mode": payment_mode_api,
                                        "pmt_state": state_api,
                                        "rrn": str(rrn_api),
                                        "settle_status": settlement_status_api,
                                        "acquirer_code": acquirer_code_api,
                                        "issuer_code": issuer_code_api,
                                        "txn_type": txn_type_api,
                                        "mid": mid_api,
                                        "tid": tid_api,
                                        "org_code": org_code_api,
                                        "date": date_time_converter.from_api_to_datetime_format(date_api)
                                    }
                logger.debug(f"actual_api_values: {actual_api_values}")

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
                                        "pmt_status": "UPG_AUTHORIZED",
                                        "pmt_state": "UPG_AUTHORIZED",
                                        "pmt_mode": "UPI",
                                        "txn_amt": amount,
                                        "upi_txn_status": "UPG_AUTHORIZED",
                                        "settle_status": "SETTLED",
                                        "acquirer_code": "HDFC",
                                        "bank_code": "HDFC",
                                        "pmt_gateway": "MINTOAK",
                                        "upi_txn_type": "UNKNOWN",
                                        "upi_bank_code": "HDFC_MINTOAK",
                                        "upi_mc_id": upi_mc_id,
                                        "mid": mid,
                                        "tid": tid,
                                        "ipr_pmt_mode": "UPI",
                                        "ipr_bank_code": "HDFC",
                                        "ipr_org_code": org_code,
                                        "ipr_auth_code": auth_code,
                                        "ipr_rrn": str(rrn),
                                        "ipr_txn_amt": amount,
                                        "ipr_mid": mid,
                                        "ipr_tid": tid,
                                        "ipr_config_id": upi_mc_id,
                                        "ipr_pg_merchant_id": pg_merchant_id,
                                    }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{ipr_txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"fetched status from upi_txn table is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"fetched txn_type from upi_txn table is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"fetched bank_code from upi_txn table is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"fetched upi_mc_id from upi_txn table is : {upi_mc_id_db}")

                actual_db_values = {
                                        "pmt_status": status_db,
                                        "pmt_state": state_db,
                                        "pmt_mode": payment_mode_db,
                                        "txn_amt": amount_db,
                                        "upi_txn_status": upi_status_db,
                                        "settle_status": settlement_status_db,
                                        "acquirer_code": acquirer_code_db,
                                        "bank_code": bank_code_db,
                                        "pmt_gateway": payment_gateway_db,
                                        "upi_txn_type": upi_txn_type_db,
                                        "upi_bank_code": upi_bank_code_db,
                                        "upi_mc_id": upi_mc_id_db,
                                        "mid": mid_db,
                                        "tid": tid_db,
                                        "ipr_pmt_mode": ipr_payment_mode,
                                        "ipr_bank_code": ipr_bank_code,
                                        "ipr_org_code": ipr_org_code,
                                        "ipr_auth_code": ipr_auth_code,
                                        "ipr_rrn": str(ipr_rrn),
                                        "ipr_txn_amt": ipr_amount,
                                        "ipr_mid": ipr_mid,
                                        "ipr_tid": ipr_tid,
                                        "ipr_config_id": ipr_config_id,
                                        "ipr_pg_merchant_id": ipr_pg_merchant_id,
                                    }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                                            "date_time": date_and_time_portal,
                                            "pmt_state": "UPG_AUTHORIZED",
                                            "pmt_type": "UPI",
                                            "txn_amt": f"{str(amount)}.00",
                                            "username": "EZETAP",
                                            "txn_id": ipr_txn_id,
                                            "rrn": str(rrn),
                                            "auth_code": '-' if auth_code is None else auth_code
                                        }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"fetched Date & Time from portal is : {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"fetched Transaction ID from portal is : {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched Total Amount from portal is : {total_amount}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"fetched RR Number from portal is : {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"fetched Type from portal is : {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"fetched Status from portal is : {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"fetched Username from portal is : {username}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched Auth Code from portal is : {auth_code_portal}")

                actual_portal_values = {
                                            "date_time": date_time,
                                            "pmt_state": str(status),
                                            "pmt_type": transaction_type,
                                            "txn_amt": total_amount[1],
                                            "username": username,
                                            "txn_id": transaction_id,
                                            "rrn": rr_number,
                                            "auth_code": auth_code_portal
                                        }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
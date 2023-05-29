import sys
import random
import time
import pytest
from datetime import datetime
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from Utilities.execution_log_processor import EzeAutoLogger
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, date_time_converter

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
def test_common_100_102_352():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_StaticQR_Callback_Failed_AutoRefund_Disabled_Via_HDFC
    Sub Feature Description: TID Dep - Performing a pure bqrv4 1 upi success callback via AXIS_DIRECT and 1 bqr success callback via HDFC, after qr expiry when autorefund is enabled
    TC naming code description: 100: Payment Method, 102: BQRV4, 352: TC352
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code="AXIS_DIRECT", portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4', bank_code_bqr='HDFC')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for QR EXpiry of bharatQRExpiryTime and upiQRExpiryTime is: {response}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code ='AXIS' and payment_gateway='AXIS';"
        logger.info(f"Query to fetch data for updating status as active in terminal_dependency_config table : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        logger.info(f"Query to fetch data for updating status as inactive in bharatqr_merchant_config table : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating bharatqr_merchant_config table inactive: {result}")

        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC'"
        logger.info(f"Query to fetch data for updating status as active in bharatqr_merchant_config table : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating bharatqr_merchant_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        hdfc_mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : {hdfc_mid}")
        hdfc_tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : {hdfc_tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : {terminal_info_id}")
        bqr_merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table :  {bqr_merchant_config_id}")
        bqr_merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : {bqr_merchant_pan}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the upi_merchant_config table : {tid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from the upi_merchant_config table : {vpa}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Fetching pgMerchantId from the upi_merchant_config table : {pg_merchant_id}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch data from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of terminal_info table : {result}")
        device_serial = result['device_serial'].values[0]
        logger.debug(f"Fetching device_serial from the terminal_info table : {device_serial}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 49.65
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")

            logger.debug("waiting for the time till qr get expired...")
            time.sleep(60)

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {created_time}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Fetching status from the txn table : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment_mode from the txn table :{payment_mode_db}")
            amount_db = float(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from the txn table : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Fetching state from the txn table : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment_gateway from the txn table : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer_code from the txn table : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"Fetching bank_code from the txn table : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement_status from the txn table : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table : {mid_db}")
            order_id_db = result['external_ref'].values[0]
            logger.debug(f"Fetching external_ref from the txn table : {order_id_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from the txn table : {device_serial_db}")

            rrn_2 = random.randint(1111110, 9999999)
            logger.debug(f"Generated random rrn number for AXIS_DIRECT is: {rrn_2}")
            ref_id_2 = '211115084892E01' + str(rrn_2)
            logger.debug(f"Generated random ref_id for for AXIS_DIRECT is : {ref_id_2}")

            logger.debug(f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn_2} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',curl_data={
                'merchantTransactionId': txn_id,
                'transactionAmount': amount,
                'merchantId': str(pg_merchant_id),
                'creditVpa': vpa,
                'rrn': rrn_2,
                'gatewayTransactionId': ref_id_2
            })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data to updated curl_data for axis_direct_upi_success_curl is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT of data_buffer is : {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('confirm_axisdirect',request_body={
                "data": data_buffer
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response obtained from axis_direct is : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "' and orig_txn_id='" + str(txn_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table for bqrv4_upi : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result of txn table for bqrv4_upi : {result}")
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Value of txn_id obtained from txn table for bqrv4_upi : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table for bqrv4_upi : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table for bqrv4_upi : {payer_name_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Value of org_code obtained from txn table for bqrv4_upi : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table for bqrv4_upi : {txn_type_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table for bqrv4_upi : {auth_code_2}")
            txn_created_time_2 = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table for bqrv4_upi : {txn_created_time_2}")
            status_db_2 = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table for bqrv4_upi : {status_db_2}")
            payment_mode_db_2 = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table for bqrv4_upi : {payment_mode_db_2}")
            amount_db_2 = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table for bqrv4_upi : {amount_db_2}")
            state_db_2 = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table for bqrv4_upi : {state_db_2}")
            payment_gateway_db_2 = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table for bqrv4_upi : {payment_gateway_db_2}")
            acquirer_code_db_2 = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table for bqrv4_upi : {acquirer_code_db_2}")
            bank_code_db_2 = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table for bqrv4_upi : {bank_code_db_2}")
            settlement_status_db_2 = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table for bqrv4_upi : {settlement_status_db_2}")
            tid_db_2 = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table for bqrv4_upi : {tid_db_2}")
            mid_db_2 = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table for bqrv4_upi : {mid_db_2}")
            order_id_db_2 = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table for bqrv4_upi : {order_id_db_2}")
            rr_number_db_2 = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table for bqrv4_upi : {rr_number_db_2}")
            orig_txn_id_db_2 = result['orig_txn_id'].values[0]
            logger.debug(f"Value of orig_txn_id obtained from txn table for bqrv4_upi : {orig_txn_id_db_2}")
            device_serial_db_2 = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table for bqrv4_upi : {device_serial_db_2}")

            rrn_3 = "RE" + txn_id.split('E')[1]
            logger.debug(f"Generated random rrn number for HDFC Callback is : {rrn_3}")
            auth_code_3 = "AE" + txn_id.split('E')[1]
            logger.debug(f"Generated random auth_code for for HDFC Callback is : {auth_code_3}")

            logger.debug( f"Fetching Txn_id,Auth code,RRN from data base : Txn_id : {txn_id},"f" Auth code : {auth_code_3}, RRN : {rrn_3}")
            api_details = DBProcessor.get_api_details('callbackHDFC', request_body={
                "PRIMARY_ID": txn_id,
                "TXN_AMOUNT": str(amount),
                "TXN_ID": txn_id,
                "AUTH_CODE": auth_code_3,
                "RRN": rrn_3,
                "MERCHANT_PAN": bqr_merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for HDFC Callback is : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "' and orig_txn_id='" + str(txn_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table for bqrv4_bqr : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Result of txn table for bqrv4_bqr : {result}")
            txn_id_3 = result['id'].values[0]
            logger.debug(f"Value of txn_id obtained from txn table for bqrv4_bqr : {txn_id_3}")
            customer_name_3 = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table for bqrv4_bqr : {customer_name_3}")
            payer_name_3 = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table for bqrv4_bqr : {payer_name_3}")
            org_code_txn_3 = result['org_code'].values[0]
            logger.debug(f"Value of org_code obtained from txn table for bqrv4_bqr : {org_code_txn_3}")
            txn_type_3 = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table for bqrv4_bqr : {txn_type_3}")
            auth_code_3 = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table for bqrv4_bqr : {auth_code_3}")
            txn_created_time_3 = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table for bqrv4_bqr : {txn_created_time_3}")
            status_db_3 = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table for bqrv4_bqr : {status_db_3}")
            payment_mode_db_3 = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table for bqrv4_bqr : {payment_mode_db_3}")
            amount_db_3 = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table for bqrv4_bqr : {amount_db_3}")
            state_db_3 = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table for bqrv4_bqr : {state_db_3}")
            payment_gateway_db_3 = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table for bqrv4_bqr : {payment_gateway_db_3}")
            acquirer_code_db_3 = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table for bqrv4_bqr : {acquirer_code_db_3}")
            bank_code_db_3 = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table for bqrv4_bqr : {bank_code_db_3}")
            settlement_status_db_3 = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table for bqrv4_bqr : {settlement_status_db_3}")
            tid_db_3 = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table for bqrv4_bqr : {tid_db_3}")
            mid_db_3 = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table for bqrv4_bqr : {mid_db_3}")
            order_id_db_3 = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table for bqrv4_bqr : {order_id_db_3}")
            rr_number_db_3 = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table for bqrv4_bqr : {rr_number_db_3}")
            auth_code_db_3 = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table for bqrv4_bqr : {auth_code_db_3}")
            orig_txn_id_db_3 = result['orig_txn_id'].values[0]
            logger.debug(f"Value of orig_txn_id obtained from txn table for bqrv4_bqr : {orig_txn_id_db_3}")
            device_serial_db_3 = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table for bqrv4_bqr : {device_serial_db_3}")

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
                date_and_time_2 = date_time_converter.to_app_format(txn_created_time_2)
                date_and_time_3 = date_time_converter.to_app_format(txn_created_time_3)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "pmt_mode_3": "BHARAT QR",
                    "pmt_status_3": "REFUND_PENDING",
                    "txn_amt_3": "{:.2f}".format(amount),
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_3,
                    "order_id_3": order_id,
                    "payment_msg_3": "PAYMENT SUCCESSFUL",
                    "date_3": date_and_time_3,
                    "auth_code_3": auth_code_3,
                    "rrn_3": str(rrn_3)
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_2}, {payment_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_2}, {app_date_and_time_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_2}, {app_amount_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_2}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_2}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_3)
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_3}, {payment_status_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_3}, {app_date_and_time_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_3}, {app_auth_code_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_3}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_txn_id_3}")
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_3}, {app_amount_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_3}, {app_settlement_status_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_3}, {app_payment_msg_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_3}, {app_order_id_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_rrn_3}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "customer_name_2": app_customer_name_2,
                    "settle_status_2": app_settlement_status_2,
                    "payer_name_2": app_payer_name_2,
                    "order_id_2": app_order_id_2,
                    "payment_msg_2": app_payment_msg_2,
                    "date_2": app_date_and_time_3,
                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "txn_id_3": app_txn_id_3,
                    "rrn_3": str(app_rrn_3),
                    "settle_status_3": app_settlement_status_3,
                    "order_id_3": app_order_id_3,
                    "payment_msg_3": app_payment_msg_3,
                    "auth_code_3": app_auth_code_3,
                    "date_3": app_date_and_time_3
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

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
                date_2 = date_time_converter.db_datetime(txn_created_time_2)
                date_3 = date_time_converter.db_datetime(txn_created_time_3)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "order_id": order_id,
                    "txn_type": "CHARGE",
                    "mid": hdfc_mid,
                    "tid": hdfc_tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUND_PENDING",
                    "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "issuer_code_2": "AXIS",
                    "customer_name_2": customer_name_2,
                    "order_id_2": order_id,
                    "payer_name_2": payer_name_2,
                    "txn_type_2": "CHARGE",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_2,
                    "orig_txn_id_2": txn_id,
                    "pmt_status_3": "REFUND_PENDING",
                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "BHARATQR",
                    "pmt_state_3": "REFUND_PENDING",
                    "rrn_3": str(rrn_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "HDFC",
                    "issuer_code_3": "HDFC",
                    "order_id_3": order_id,
                    "txn_type_3": "CHARGE",
                    "mid_3": hdfc_mid,
                    "tid_3": hdfc_tid,
                    "org_code_3": org_code,
                    "date_3": date_3,
                    "orig_txn_id_3": txn_id,
                    "device_serial": str(device_serial),
                    "device_serial_2": str(device_serial),
                    "device_serial_3": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Value of status obtained from first txnlist api is : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Value of amount obtained from first txnlist api is : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from first txnlist api is : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Value of states obtained from first txnlist api is : {state_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from first txnlist api is : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from first txnlist api is : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from first txnlist api is : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from first txnlist api is : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Value of mid obtained from first txnlist api is : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Value of tid obtained from first txnlist api is : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from first txnlist api is : {txn_type_api}")
                date_api = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from first txnlist api is : {date_api}")
                order_id_api = response_1["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from first txnlist api is : {order_id_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from first txnlist api is : {device_serial_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of second txn api is : {response_2}")
                status_api_2 = response_2["status"]
                logger.debug(f"Value of status obtained from second txnlist api is : {status_api_2}")
                amount_api_2 = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from second txnlist api is : {amount_api_2}")
                payment_mode_api_2 = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from second txnlist api is : {payment_mode_api_2}")
                state_api_2 = response_2["states"][0]
                logger.debug(f"Value of states obtained from second txnlist api is : {state_api_2}")
                rrn_api_2 = response_2["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from second txnlist api is : {rrn_api_2}")
                settlement_status_api_2 = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from second txnlist api is : {settlement_status_api_2}")
                issuer_code_api_2 = response_2["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from second txnlist api is : {issuer_code_api_2}")
                customer_name_api_2 = response_2["customerName"]
                logger.debug(f"Value of customerName obtained from second txnlist api is : {customer_name_api_2}")
                payer_name_api_2 = response_2["payerName"]
                logger.debug(f"Value of payerName obtained from second txnlist api is : {payer_name_api_2}")
                acquirer_code_api_2 = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from second txnlist api is : {acquirer_code_api_2}")
                org_code_api_2 = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from second txnlist api is : {org_code_api_2}")
                mid_api_2 = response_2["mid"]
                logger.debug(f"Value of mid obtained from second txnlist api is : {mid_api_2}")
                tid_api_2= response_2["tid"]
                logger.debug(f"Value of tid obtained from second txnlist api is : {tid_api_2}")
                txn_type_api_2 = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from second txnlist api is : {txn_type_api_2}")
                date_api_2 = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from second txnlist api is : {date_api_2}")
                order_id_api_2 = response_2["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from second txnlist api is : {order_id_api_2}")
                device_serial_api_2 = response_2["deviceSerial"]
                logger.debug(f"Value of deviceSerial obtained from second txnlist api is : {device_serial_api_2}")
                orig_txn_id_api_2 = response_2["origTxnId"]
                logger.debug(f"Value of origTxnId obtained from second txnlist api is : {orig_txn_id_api_2}")

                response_3 = [x for x in response["txns"] if x["txnId"] == txn_id_3][0]
                logger.debug(f"Response after filtering data of third txn api is : {response_3}")
                status_api_3 = response_3["status"]
                logger.debug(f"Value of status obtained from third txnlist api is : {status_api_3}")
                amount_api_3 = float(response_3["amount"])
                logger.debug(f"Value of amount obtained from third txnlist api is : {amount_api_3}")
                payment_mode_api_3 = response_3["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from third txnlist api is : {payment_mode_api_3}")
                state_api_3 = response_3["states"][0]
                logger.debug(f"Value of states obtained from third txnlist api is : {state_api_3}")
                settlement_status_api_3 = response_3["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from third txnlist api is : {settlement_status_api_3}")
                acquirer_code_api_3 = response_3["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from third txnlist api is : {acquirer_code_api_3}")
                org_code_api_3 = response_3["orgCode"]
                logger.debug(f"Value of orgCode obtained from third txnlist api is : {org_code_api_3}")
                mid_api_3 = response_3["mid"]
                logger.debug(f"Value of mid obtained from third txnlist api is : {mid_api_3}")
                tid_api_3= response_3["tid"]
                logger.debug(f"Value of tid obtained from third txnlist api is : {tid_api_3}")
                txn_type_api_3 = response_3["txnType"]
                logger.debug(f"Value of txnType obtained from third txnlist api is : {txn_type_api_3}")
                date_api_3 = response_3["createdTime"]
                logger.debug(f"Value of createdTime obtained from third txnlist api is : {date_api_3}")
                order_id_api_3 = response_3["orderNumber"]
                logger.debug(f"Value of orderNumber obtained from third txnlist api is : {order_id_api_3}")
                device_serial_api_3 = response_3["deviceSerial"]
                logger.debug(f"Value of deviceSerial obtained from third txnlist api is : {device_serial_api_3}")
                rrn_api_3 = response_3["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from third txnlist api is : {rrn_api_3}")
                issuer_code_api_3 = response_3["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from third txnlist api is : {issuer_code_api_3}")
                orig_txn_id_api_3 = response_3["origTxnId"]
                logger.debug(f"Value of origTxnId obtained from third txnlist api is : {orig_txn_id_api_3}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "order_id": order_id_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2,
                    "txn_amt_2": float(amount_api_2),
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "customer_name_2": customer_name_api_2,
                    "order_id_2": order_id_api_2,
                    "payer_name_2": payer_name_api_2,
                    "txn_type_2": txn_type_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "orig_txn_id_2": orig_txn_id_api_2,
                    "pmt_status_3": status_api_3,
                    "txn_amt_3": float(amount_api_3),
                    "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_2,
                    "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "issuer_code_3": issuer_code_api_3,
                    "order_id_3": order_id_api_3,
                    "txn_type_3": txn_type_api_3,
                    "mid_3": mid_api_3,
                    "tid_3": tid_api_3,
                    "org_code_3": org_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_3),
                    "orig_txn_id_3": orig_txn_id_api_3,
                    "device_serial": device_serial_api,
                    "device_serial_2": device_serial_api_2,
                    "device_serial_3": device_serial_api_3
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
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "BHARATQR",
                    "txn_amt": float(amount),
                    "settle_status": "FAILED",
                    "order_id": order_id,
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "mid": hdfc_mid,
                    "tid": hdfc_tid,
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "HDFC",
                    "bqr_merchant_config_id": bqr_merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "REFUND_PENDING",
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_mode_2": "UPI",
                    "rr_number_2": str(rrn_2),
                    "txn_amt_2": float(amount),
                    "settle_status_2": "SETTLED",
                    "order_id_2": order_id,
                    "acquirer_code_2": "AXIS",
                    "bank_code_2": "AXIS",
                    "payment_gateway_2": "AXIS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "orig_txn_id_2": txn_id,
                    "upi_txn_status_2": "REFUND_PENDING",
                    "upi_txn_type_2": "PAY_BQR",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "pmt_status_3": "REFUND_PENDING",
                    "pmt_state_3": "REFUND_PENDING",
                    "pmt_mode_3": "BHARATQR",
                    "rr_number_3": str(rrn_3),
                    "auth_code_3": auth_code_3,
                    "txn_amt_3": float(amount),
                    "settle_status_3": "SETTLED",
                    "order_id_3": order_id,
                    "acquirer_code_3": "HDFC",
                    "bank_code_3": "HDFC",
                    "payment_gateway_3": "HDFC",
                    "mid_3": hdfc_mid,
                    "tid_3": hdfc_tid,
                    "orig_txn_id_3": txn_id,
                    "bqr_pmt_state_3": "REFUND_PENDING",
                    "bqr_txn_amt_3": float(amount),
                    "bqr_txn_type_3": "DYNAMIC_QR",
                    "bqr_terminal_info_id_3": terminal_info_id,
                    "bqr_bank_code_3": "HDFC",
                    "bqr_merchant_config_id_3": bqr_merchant_config_id,
                    "bqr_txn_primary_id_3": txn_id_3,
                    "bqr_org_code_3": org_code,
                    "device_serial": str(device_serial),
                    "device_serial_2": str(device_serial),
                    "device_serial_3": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table : {bqr_org_code_db}")

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table based on second txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table based on second txn_id : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table based on second txn_id : {upi_status_db_2}")
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table based on second txn_id : {upi_txn_type_db_2}")
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table based on second txn_id : {upi_bank_code_db_2}")
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table based on second txn_id : {upi_mc_id_db_2}")

                query = "select * from bharatqr_txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table based on third txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table based on third txn_id : {result}")
                bqr_status_db_3 = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from bharatqr_txn table based on third txn_id : {bqr_status_db_3}")
                bqr_state_db_3 = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table based on third txn_id : {bqr_state_db_3}")
                bqr_amount_db_3 = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table based on third txn_id : {bqr_amount_db_3}")
                bqr_txn_type_db_3 = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table based on third txn_id : {bqr_txn_type_db_3}")
                bqr_terminal_info_id_db_3 = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table based on third txn_id : {bqr_terminal_info_id_db_3}")
                bqr_bank_code_db_3 = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table based on third txn_id : {bqr_bank_code_db_3}")
                bqr_merchant_config_id_db_3 = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table based on third txn_id : {bqr_merchant_config_id_db_3}")
                bqr_txn_primary_id_db_3 = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table based on third txn_id : {bqr_txn_primary_id_db_3}")
                bqr_org_code_db_3 = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table based on third txn_id : {bqr_org_code_db_3}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "order_id": order_id_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "rr_number_2": str(rr_number_db_2),
                    "txn_amt_2": float(amount_db_2),
                    "settle_status_2": settlement_status_db_2,
                    "order_id_2": order_id_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "payment_gateway_2": payment_gateway_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "orig_txn_id_2": orig_txn_id_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "pmt_status_3": status_db_3,
                    "pmt_state_3": state_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "rr_number_3": str(rr_number_db_3),
                    "auth_code_3": auth_code_db_3,
                    "txn_amt_3": float(amount_db_3),
                    "settle_status_3": settlement_status_db_3,
                    "order_id_3": order_id_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "bank_code_3": bank_code_db_3,
                    "payment_gateway_3": payment_gateway_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "orig_txn_id_3": orig_txn_id_db_3,
                    "bqr_pmt_state_3": bqr_state_db_3,
                    "bqr_txn_amt_3": bqr_amount_db_3,
                    "bqr_txn_type_3": bqr_txn_type_db_3,
                    "bqr_terminal_info_id_3": bqr_terminal_info_id_db_3,
                    "bqr_bank_code_3": bqr_bank_code_db_3,
                    "bqr_merchant_config_id_3": bqr_merchant_config_id_db_3,
                    "bqr_txn_primary_id_3": bqr_txn_primary_id_db_3,
                    "bqr_org_code_3": bqr_org_code_db_3,
                    "device_serial": str(device_serial_db),
                    "device_serial_2": str(device_serial_db_2),
                    "device_serial_3": str(device_serial_db_3)
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
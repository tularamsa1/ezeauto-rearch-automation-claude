import random

class TestData:
    USER_NAME = "1076810769"
    PASSWORD = "A111111"
    AMOUNT  = random.randint(200, 1000)
    ORDER_NUMBER = random.randint(100, 5000)
    #CASH_AT_POS_AMOUNT = random.randrange(100, 2000, 100)


    DA_ALERT_MESSAGE  = 'Plese use any of the payments below all are working. Happy Shopping\n'

    API = 'txnList'
    #headers = {'Content-Type': 'application/json'}

    payload = {
        # "startDate": "2022-04-12",
        "username": USER_NAME,
        "password": PASSWORD,
        # "endDate": "2022-04-12",
    }
    #request_id = ''

    # start_payload = {
    #     "username": USER_NAME,
    #     "password": PASSWORD,
    #     "amount": AMOUNT,
    #     "paymentMode": "",
    #     "customerMobileNumber": "9731545096",
    #     "customerName": "Vineet",
    #     "customerEmail": "vineeth.b@ezetap.com",
    #     "externalRefNumber": "1201044",
    #     "externalRefNumber2": "HHHHHHH",
    #     "externalRefNumber3": "sfsdsd",
    #     "externalRefNumber4": "dfsdfs",
    #     "externalRefNumber5": "dddd",
    #     "externalRefNumber6": "kkkkk",
    #     "externalRefNumber7": "jjjjj",
    #     "additionalAmount": "1",
    #     "pushTo": {"deviceId": "0821045404|ezetap_android"},
    #     "externalRefNumbers": ["{\"offlinetxnID\":\"BAJAJ\"}"],
    #     "Description": "new txn"
    # }
    #
    # status_payload = {
    #     "username": USER_NAME,
    #     "password": PASSWORD,
    #     "origP2pRequestId": request_id
    # }
    #
    # cancel_payload = {
    #     "username": USER_NAME,
    #     "password": PASSWORD,
    #     "origP2pRequestId": request_id
    # }
    #


    #
    # START_URL = 'https://dev11.ezetap.com/api/3.0/p2p/start'
    # STATUS_URL = 'https://dev11.ezetap.com/api/3.0/p2p/status'
    # CANCEL_URL = 'https://dev11.ezetap.com/api/3.0/p2p/cancel'



    #TOTAL_TRANSACTIONS = 17
    #TRANSACTION_STATUS_LIST = ['AUTHORIZED', 'VOIDED', 'PENDING', 'EXPIRED', 'FAILED']



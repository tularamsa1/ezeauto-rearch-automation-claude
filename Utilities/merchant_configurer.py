import json
import random
import sqlite3

import requests

from DataProvider import GlobalConstants
from Utilities import DBProcessor, merchant_creator, ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


def configure_bqr_settings():
    """
    This method is used to configure the bqr settings for the merchants after creation.
    """
    api_details = merchant_creator.get_api_details_from_db("configureBqr")
    url = ConfigReader.read_config("APIs", "baseurl") + api_details["EndPoint"]
    headers = json.loads(api_details["Header"])
    lst_bqr_settings_api_body = generate_bqr_setting_api_for_all_merchants()
    lst_bqr_settings_api_body = [{'accountNumber': '3446182934', 'acquisitions': [
        {'acquirerCode': 'HDFC', 'apps': [], 'bankIdentifier': '0794589BI021078', 'microserviceCall': False,
         'offline': False, 'paymentGateway': 'HDFC', 'priority': 0, 'requestTime': 1653291856647, 'scheduler': False,
         'selfSignUp': False, 'settingVer': 0, 'settlementCycleDays': 0, 'status': 'ACTIVE', 'terminals': [
            {'apps': [], 'emiOnly': False, 'ignoreProperty': False, 'initialized': True, 'keyRotationReqd': True,
             'kxWithPg': True, 'loyaltyEnabled': False, 'microserviceCall': False, 'mid': 'MIDIS8921188816',
             'offline': False, 'requestTime': 1653291856648, 'scheduler': False, 'selfSignUp': False, 'sequenceId': 1,
             'settingVer': 0, 'status': 'ACTIVE', 'tid': '21188a21', 'tidPriority': 0, 'tleEnabled': True,
             'upgrade': True}], 'upgrade': True}], 'apps': [], 'bankCode': 'HDFC', 'bharatQrBankCode': 'HDFC',
                                  'categoryCode': '4112', 'city': 'Delhi', 'currencyCode': '356',
                                  'enableOrgSetting': True, 'ifscCode': 'KKBK0004589', 'mVisaId': '6435484104176227',
                                  'masterpassPan': '3535535087415157', 'microserviceCall': False,
                                  'mvisaPan': '6435484104176227', 'name': 'Auto_test_merch25', 'offline': False,
                                  'orgType': 'MERCHANT', 'pan': '21188A21', 'pinCode': '110024',
                                  'requestTime': 1653291856647, 'rupayPan': '2295831538928410', 'scheduler': False,
                                  'selfSignUp': False, 'settingVer': 0, 'setupType': 'BHARATQR', 'status': 'ACTIVE',
                                  'subscriptionPlan': 'BASIC', 'timeZone': 'Asia/Calcutta', 'upgrade': True,
                                  'username': '9886191638', 'password': 'A000000'}, {'accountNumber': '3446182934',
                                                                                     'acquisitions': [
                                                                                         {'acquirerCode': 'AXIS',
                                                                                          'apps': [],
                                                                                          'bankIdentifier': '0794589BI021078',
                                                                                          'microserviceCall': False,
                                                                                          'offline': False,
                                                                                          'paymentGateway': 'AXIS',
                                                                                          'priority': 0,
                                                                                          'requestTime': 1653291856647,
                                                                                          'scheduler': False,
                                                                                          'selfSignUp': False,
                                                                                          'settingVer': 0,
                                                                                          'settlementCycleDays': 0,
                                                                                          'status': 'ACTIVE',
                                                                                          'terminals': [{'apps': [],
                                                                                                         'emiOnly': False,
                                                                                                         'ignoreProperty': False,
                                                                                                         'initialized': True,
                                                                                                         'keyRotationReqd': True,
                                                                                                         'kxWithPg': True,
                                                                                                         'loyaltyEnabled': False,
                                                                                                         'microserviceCall': False,
                                                                                                         'mid': 'MIDIS8921188816',
                                                                                                         'offline': False,
                                                                                                         'requestTime': 1653291856648,
                                                                                                         'scheduler': False,
                                                                                                         'selfSignUp': False,
                                                                                                         'sequenceId': 1,
                                                                                                         'settingVer': 0,
                                                                                                         'status': 'ACTIVE',
                                                                                                         'tid': '21188a22',
                                                                                                         'tidPriority': 0,
                                                                                                         'tleEnabled': True,
                                                                                                         'upgrade': True}],
                                                                                          'upgrade': True}], 'apps': [],
                                                                                     'bankCode': 'AXIS_DIRECT',
                                                                                     'bharatQrBankCode': 'N/A',
                                                                                     'categoryCode': '4112',
                                                                                     'city': 'Delhi',
                                                                                     'currencyCode': '356',
                                                                                     'enableOrgSetting': True,
                                                                                     'ifscCode': 'KKBK0004589',
                                                                                     'mVisaId': '8074004665381721',
                                                                                     'masterpassPan': '7300940362854243',
                                                                                     'microserviceCall': False,
                                                                                     'mvisaPan': '8074004665381721',
                                                                                     'name': 'Auto_test_merch25',
                                                                                     'offline': False,
                                                                                     'orgType': 'MERCHANT',
                                                                                     'pan': '21188A22',
                                                                                     'pinCode': '110024',
                                                                                     'requestTime': 1653291856647,
                                                                                     'rupayPan': '9639357554264427',
                                                                                     'scheduler': False,
                                                                                     'selfSignUp': False,
                                                                                     'settingVer': 0,
                                                                                     'setupType': 'BHARATQR',
                                                                                     'status': 'ACTIVE',
                                                                                     'subscriptionPlan': 'BASIC',
                                                                                     'timeZone': 'Asia/Calcutta',
                                                                                     'upgrade': True,
                                                                                     'username': '9886191638',
                                                                                     'password': 'A000000'},
                                 {'accountNumber': '3446182934', 'acquisitions': [
                                     {'acquirerCode': 'YES', 'apps': [], 'bankIdentifier': '0794589BI021078',
                                      'microserviceCall': False, 'offline': False, 'paymentGateway': 'ATOS',
                                      'priority': 0, 'requestTime': 1653291856647, 'scheduler': False,
                                      'selfSignUp': False, 'settingVer': 0, 'settlementCycleDays': 0,
                                      'status': 'ACTIVE', 'terminals': [
                                         {'apps': [], 'emiOnly': False, 'ignoreProperty': False, 'initialized': True,
                                          'keyRotationReqd': True, 'kxWithPg': True, 'loyaltyEnabled': False,
                                          'microserviceCall': False, 'mid': 'MIDIS8921188816', 'offline': False,
                                          'requestTime': 1653291856648, 'scheduler': False, 'selfSignUp': False,
                                          'sequenceId': 1, 'settingVer': 0, 'status': 'ACTIVE', 'tid': '21188a23',
                                          'tidPriority': 0, 'tleEnabled': True, 'upgrade': True}], 'upgrade': True}],
                                  'apps': [], 'bankCode': 'YES', 'bharatQrBankCode': 'YES', 'categoryCode': '4112',
                                  'city': 'Delhi', 'currencyCode': '356', 'enableOrgSetting': True,
                                  'ifscCode': 'KKBK0004589', 'mVisaId': '8992938346353119',
                                  'masterpassPan': '5721597150355159', 'microserviceCall': False,
                                  'mvisaPan': '8992938346353119', 'name': 'Auto_test_merch25', 'offline': False,
                                  'orgType': 'MERCHANT', 'pan': '21188A23', 'pinCode': '110024',
                                  'requestTime': 1653291856647, 'rupayPan': '7302162342909710', 'scheduler': False,
                                  'selfSignUp': False, 'settingVer': 0, 'setupType': 'BHARATQR', 'status': 'ACTIVE',
                                  'subscriptionPlan': 'BASIC', 'timeZone': 'Asia/Calcutta', 'upgrade': True,
                                  'username': '9886191638', 'password': 'A000000'}, {'accountNumber': '3446182934',
                                                                                     'acquisitions': [
                                                                                         {'acquirerCode': 'ICICI',
                                                                                          'apps': [],
                                                                                          'bankIdentifier': '0794589BI021078',
                                                                                          'microserviceCall': False,
                                                                                          'offline': False,
                                                                                          'paymentGateway': 'FDC',
                                                                                          'priority': 0,
                                                                                          'requestTime': 1653291856647,
                                                                                          'scheduler': False,
                                                                                          'selfSignUp': False,
                                                                                          'settingVer': 0,
                                                                                          'settlementCycleDays': 0,
                                                                                          'status': 'ACTIVE',
                                                                                          'terminals': [{'apps': [],
                                                                                                         'emiOnly': False,
                                                                                                         'ignoreProperty': False,
                                                                                                         'initialized': True,
                                                                                                         'keyRotationReqd': True,
                                                                                                         'kxWithPg': True,
                                                                                                         'loyaltyEnabled': False,
                                                                                                         'microserviceCall': False,
                                                                                                         'mid': 'MIDIS8921188816',
                                                                                                         'offline': False,
                                                                                                         'requestTime': 1653291856648,
                                                                                                         'scheduler': False,
                                                                                                         'selfSignUp': False,
                                                                                                         'sequenceId': 1,
                                                                                                         'settingVer': 0,
                                                                                                         'status': 'ACTIVE',
                                                                                                         'tid': '21188a24',
                                                                                                         'tidPriority': 0,
                                                                                                         'tleEnabled': True,
                                                                                                         'upgrade': True}],
                                                                                          'upgrade': True}], 'apps': [],
                                                                                     'bankCode': 'ICICI',
                                                                                     'bharatQrBankCode': 'FDC_ICICI',
                                                                                     'categoryCode': '4112',
                                                                                     'city': 'Delhi',
                                                                                     'currencyCode': '356',
                                                                                     'enableOrgSetting': True,
                                                                                     'ifscCode': 'KKBK0004589',
                                                                                     'mVisaId': '7595106499001452',
                                                                                     'masterpassPan': '1433239107999857',
                                                                                     'microserviceCall': False,
                                                                                     'mvisaPan': '7595106499001452',
                                                                                     'name': 'Auto_test_merch25',
                                                                                     'offline': False,
                                                                                     'orgType': 'MERCHANT',
                                                                                     'pan': '21188A24',
                                                                                     'pinCode': '110024',
                                                                                     'requestTime': 1653291856647,
                                                                                     'rupayPan': '4166645103833591',
                                                                                     'scheduler': False,
                                                                                     'selfSignUp': False,
                                                                                     'settingVer': 0,
                                                                                     'setupType': 'BHARATQR',
                                                                                     'status': 'ACTIVE',
                                                                                     'subscriptionPlan': 'BASIC',
                                                                                     'timeZone': 'Asia/Calcutta',
                                                                                     'upgrade': True,
                                                                                     'username': '9886191638',
                                                                                     'password': 'A000000'},
                                 {'accountNumber': '3446182934', 'acquisitions': [
                                     {'acquirerCode': 'AXIS', 'apps': [], 'bankIdentifier': '0794589BI021078',
                                      'microserviceCall': False, 'offline': False, 'paymentGateway': 'ATOS_TLE',
                                      'priority': 0, 'requestTime': 1653291856647, 'scheduler': False,
                                      'selfSignUp': False, 'settingVer': 0, 'settlementCycleDays': 0,
                                      'status': 'ACTIVE', 'terminals': [
                                         {'apps': [], 'emiOnly': False, 'ignoreProperty': False, 'initialized': True,
                                          'keyRotationReqd': True, 'kxWithPg': True, 'loyaltyEnabled': False,
                                          'microserviceCall': False, 'mid': 'MIDIS8921188816', 'offline': False,
                                          'requestTime': 1653291856648, 'scheduler': False, 'selfSignUp': False,
                                          'sequenceId': 1, 'settingVer': 0, 'status': 'ACTIVE', 'tid': '21188a25',
                                          'tidPriority': 0, 'tleEnabled': True, 'upgrade': True}], 'upgrade': True}],
                                  'apps': [], 'bankCode': 'AXIS', 'bharatQrBankCode': 'AXIS_TLE',
                                  'categoryCode': '4112', 'city': 'Delhi', 'currencyCode': '356',
                                  'enableOrgSetting': True, 'ifscCode': 'KKBK0004589', 'mVisaId': '6640168353122204',
                                  'masterpassPan': '3138154724317528', 'microserviceCall': False,
                                  'mvisaPan': '6640168353122204', 'name': 'Auto_test_merch25', 'offline': False,
                                  'orgType': 'MERCHANT', 'pan': '21188A25', 'pinCode': '110024',
                                  'requestTime': 1653291856647, 'rupayPan': '4930110253994738', 'scheduler': False,
                                  'selfSignUp': False, 'settingVer': 0, 'setupType': 'BHARATQR', 'status': 'ACTIVE',
                                  'subscriptionPlan': 'BASIC', 'timeZone': 'Asia/Calcutta', 'upgrade': True,
                                  'username': '9886191638', 'password': 'A000000'}, {'accountNumber': '3446182934',
                                                                                     'acquisitions': [
                                                                                         {'acquirerCode': 'KOTAK',
                                                                                          'apps': [],
                                                                                          'bankIdentifier': '0794589BI021078',
                                                                                          'microserviceCall': False,
                                                                                          'offline': False,
                                                                                          'paymentGateway': 'KOTAK_ATOS',
                                                                                          'priority': 0,
                                                                                          'requestTime': 1653291856647,
                                                                                          'scheduler': False,
                                                                                          'selfSignUp': False,
                                                                                          'settingVer': 0,
                                                                                          'settlementCycleDays': 0,
                                                                                          'status': 'ACTIVE',
                                                                                          'terminals': [{'apps': [],
                                                                                                         'emiOnly': False,
                                                                                                         'ignoreProperty': False,
                                                                                                         'initialized': True,
                                                                                                         'keyRotationReqd': True,
                                                                                                         'kxWithPg': True,
                                                                                                         'loyaltyEnabled': False,
                                                                                                         'microserviceCall': False,
                                                                                                         'mid': 'MIDIS8921188816',
                                                                                                         'offline': False,
                                                                                                         'requestTime': 1653291856648,
                                                                                                         'scheduler': False,
                                                                                                         'selfSignUp': False,
                                                                                                         'sequenceId': 1,
                                                                                                         'settingVer': 0,
                                                                                                         'status': 'ACTIVE',
                                                                                                         'tid': '21188a26',
                                                                                                         'tidPriority': 0,
                                                                                                         'tleEnabled': True,
                                                                                                         'upgrade': True}],
                                                                                          'upgrade': True}], 'apps': [],
                                                                                     'bankCode': 'KOTAK',
                                                                                     'bharatQrBankCode': 'KOTAK_WL',
                                                                                     'categoryCode': '4112',
                                                                                     'city': 'Delhi',
                                                                                     'currencyCode': '356',
                                                                                     'enableOrgSetting': True,
                                                                                     'ifscCode': 'KKBK0004589',
                                                                                     'mVisaId': '9933238533445937',
                                                                                     'masterpassPan': '3029460040462346',
                                                                                     'microserviceCall': False,
                                                                                     'mvisaPan': '9933238533445937',
                                                                                     'name': 'Auto_test_merch25',
                                                                                     'offline': False,
                                                                                     'orgType': 'MERCHANT',
                                                                                     'pan': '21188A26',
                                                                                     'pinCode': '110024',
                                                                                     'requestTime': 1653291856647,
                                                                                     'rupayPan': '7672688564001183',
                                                                                     'scheduler': False,
                                                                                     'selfSignUp': False,
                                                                                     'settingVer': 0,
                                                                                     'setupType': 'BHARATQR',
                                                                                     'status': 'ACTIVE',
                                                                                     'subscriptionPlan': 'BASIC',
                                                                                     'timeZone': 'Asia/Calcutta',
                                                                                     'upgrade': True,
                                                                                     'username': '9886191638',
                                                                                     'password': 'A000000'},
                                 {'accountNumber': '3446182934', 'acquisitions': [
                                     {'acquirerCode': 'AIRP', 'apps': [], 'bankIdentifier': '0794589BI021078',
                                      'microserviceCall': False, 'offline': False, 'paymentGateway': 'APB',
                                      'priority': 0, 'requestTime': 1653291856647, 'scheduler': False,
                                      'selfSignUp': False, 'settingVer': 0, 'settlementCycleDays': 0,
                                      'status': 'ACTIVE', 'terminals': [
                                         {'apps': [], 'emiOnly': False, 'ignoreProperty': False, 'initialized': True,
                                          'keyRotationReqd': True, 'kxWithPg': True, 'loyaltyEnabled': False,
                                          'microserviceCall': False, 'mid': 'MIDIS8921188816', 'offline': False,
                                          'requestTime': 1653291856648, 'scheduler': False, 'selfSignUp': False,
                                          'sequenceId': 1, 'settingVer': 0, 'status': 'ACTIVE', 'tid': '21188a27',
                                          'tidPriority': 0, 'tleEnabled': True, 'upgrade': True}], 'upgrade': True}],
                                  'apps': [], 'bankCode': 'APB', 'bharatQrBankCode': 'N/A', 'categoryCode': '4112',
                                  'city': 'Delhi', 'currencyCode': '356', 'enableOrgSetting': True,
                                  'ifscCode': 'KKBK0004589', 'mVisaId': '2981590314540528',
                                  'masterpassPan': '1816109937895615', 'microserviceCall': False,
                                  'mvisaPan': '2981590314540528', 'name': 'Auto_test_merch25', 'offline': False,
                                  'orgType': 'MERCHANT', 'pan': '21188A27', 'pinCode': '110024',
                                  'requestTime': 1653291856647, 'rupayPan': '3617288595084078', 'scheduler': False,
                                  'selfSignUp': False, 'settingVer': 0, 'setupType': 'BHARATQR', 'status': 'ACTIVE',
                                  'subscriptionPlan': 'BASIC', 'timeZone': 'Asia/Calcutta', 'upgrade': True,
                                  'username': '9886191638', 'password': 'A000000'}, {'accountNumber': '3446182934',
                                                                                     'acquisitions': [
                                                                                         {'acquirerCode': 'AXIS',
                                                                                          'apps': [],
                                                                                          'bankIdentifier': '0794589BI021078',
                                                                                          'microserviceCall': False,
                                                                                          'offline': False,
                                                                                          'paymentGateway': 'ATOS',
                                                                                          'priority': 0,
                                                                                          'requestTime': 1653291856647,
                                                                                          'scheduler': False,
                                                                                          'selfSignUp': False,
                                                                                          'settingVer': 0,
                                                                                          'settlementCycleDays': 0,
                                                                                          'status': 'ACTIVE',
                                                                                          'terminals': [{'apps': [],
                                                                                                         'emiOnly': False,
                                                                                                         'ignoreProperty': False,
                                                                                                         'initialized': True,
                                                                                                         'keyRotationReqd': True,
                                                                                                         'kxWithPg': True,
                                                                                                         'loyaltyEnabled': False,
                                                                                                         'microserviceCall': False,
                                                                                                         'mid': 'MIDIS8921188816',
                                                                                                         'offline': False,
                                                                                                         'requestTime': 1653291856648,
                                                                                                         'scheduler': False,
                                                                                                         'selfSignUp': False,
                                                                                                         'sequenceId': 1,
                                                                                                         'settingVer': 0,
                                                                                                         'status': 'ACTIVE',
                                                                                                         'tid': '21188a28',
                                                                                                         'tidPriority': 0,
                                                                                                         'tleEnabled': True,
                                                                                                         'upgrade': True}],
                                                                                          'upgrade': True}], 'apps': [],
                                                                                     'bankCode': 'AXIS',
                                                                                     'bharatQrBankCode': 'AXIS',
                                                                                     'categoryCode': '4112',
                                                                                     'city': 'Delhi',
                                                                                     'currencyCode': '356',
                                                                                     'enableOrgSetting': True,
                                                                                     'ifscCode': 'KKBK0004589',
                                                                                     'mVisaId': '3950622822316809',
                                                                                     'masterpassPan': '1890050618008884',
                                                                                     'microserviceCall': False,
                                                                                     'mvisaPan': '3950622822316809',
                                                                                     'name': 'Auto_test_merch25',
                                                                                     'offline': False,
                                                                                     'orgType': 'MERCHANT',
                                                                                     'pan': '21188A28',
                                                                                     'pinCode': '110024',
                                                                                     'requestTime': 1653291856647,
                                                                                     'rupayPan': '6815619399257062',
                                                                                     'scheduler': False,
                                                                                     'selfSignUp': False,
                                                                                     'settingVer': 0,
                                                                                     'setupType': 'BHARATQR',
                                                                                     'status': 'ACTIVE',
                                                                                     'subscriptionPlan': 'BASIC',
                                                                                     'timeZone': 'Asia/Calcutta',
                                                                                     'upgrade': True,
                                                                                     'username': '9886191638',
                                                                                     'password': 'A000000'},
                                 {'accountNumber': '3446182934', 'acquisitions': [
                                     {'acquirerCode': 'HDFC', 'apps': [], 'bankIdentifier': '0794589BI021078',
                                      'microserviceCall': False, 'offline': False, 'paymentGateway': 'HDFC',
                                      'priority': 0, 'requestTime': 1653291856647, 'scheduler': False,
                                      'selfSignUp': False, 'settingVer': 0, 'settlementCycleDays': 0,
                                      'status': 'ACTIVE', 'terminals': [
                                         {'apps': [], 'emiOnly': False, 'ignoreProperty': False, 'initialized': True,
                                          'keyRotationReqd': True, 'kxWithPg': True, 'loyaltyEnabled': False,
                                          'microserviceCall': False, 'mid': 'MIDIS8921188916', 'offline': False,
                                          'requestTime': 1653291856648, 'scheduler': False, 'selfSignUp': False,
                                          'sequenceId': 1, 'settingVer': 0, 'status': 'ACTIVE', 'tid': '211889a0',
                                          'tidPriority': 0, 'tleEnabled': True, 'upgrade': True}], 'upgrade': True}],
                                  'apps': [], 'bankCode': 'HDFC', 'bharatQrBankCode': 'HDFC', 'categoryCode': '4112',
                                  'city': 'Delhi', 'currencyCode': '356', 'enableOrgSetting': True,
                                  'ifscCode': 'KKBK0004589', 'mVisaId': '6333017039045133',
                                  'masterpassPan': '5330484919772287', 'microserviceCall': False,
                                  'mvisaPan': '6333017039045133', 'name': 'Auto_test_merch26', 'offline': False,
                                  'orgType': 'MERCHANT', 'pan': '211889A0', 'pinCode': '110024',
                                  'requestTime': 1653291856647, 'rupayPan': '8464241291539925', 'scheduler': False,
                                  'selfSignUp': False, 'settingVer': 0, 'setupType': 'BHARATQR', 'status': 'ACTIVE',
                                  'subscriptionPlan': 'BASIC', 'timeZone': 'Asia/Calcutta', 'upgrade': True,
                                  'username': '9886191638', 'password': 'A000000'}, {'accountNumber': '3446182934',
                                                                                     'acquisitions': [
                                                                                         {'acquirerCode': 'AXIS',
                                                                                          'apps': [],
                                                                                          'bankIdentifier': '0794589BI021078',
                                                                                          'microserviceCall': False,
                                                                                          'offline': False,
                                                                                          'paymentGateway': 'AXIS',
                                                                                          'priority': 0,
                                                                                          'requestTime': 1653291856647,
                                                                                          'scheduler': False,
                                                                                          'selfSignUp': False,
                                                                                          'settingVer': 0,
                                                                                          'settlementCycleDays': 0,
                                                                                          'status': 'ACTIVE',
                                                                                          'terminals': [{'apps': [],
                                                                                                         'emiOnly': False,
                                                                                                         'ignoreProperty': False,
                                                                                                         'initialized': True,
                                                                                                         'keyRotationReqd': True,
                                                                                                         'kxWithPg': True,
                                                                                                         'loyaltyEnabled': False,
                                                                                                         'microserviceCall': False,
                                                                                                         'mid': 'MIDIS8921188916',
                                                                                                         'offline': False,
                                                                                                         'requestTime': 1653291856648,
                                                                                                         'scheduler': False,
                                                                                                         'selfSignUp': False,
                                                                                                         'sequenceId': 1,
                                                                                                         'settingVer': 0,
                                                                                                         'status': 'ACTIVE',
                                                                                                         'tid': '211889a1',
                                                                                                         'tidPriority': 0,
                                                                                                         'tleEnabled': True,
                                                                                                         'upgrade': True}],
                                                                                          'upgrade': True}], 'apps': [],
                                                                                     'bankCode': 'AXIS_DIRECT',
                                                                                     'bharatQrBankCode': 'N/A',
                                                                                     'categoryCode': '4112',
                                                                                     'city': 'Delhi',
                                                                                     'currencyCode': '356',
                                                                                     'enableOrgSetting': True,
                                                                                     'ifscCode': 'KKBK0004589',
                                                                                     'mVisaId': '1338122689098678',
                                                                                     'masterpassPan': '4754587841706574',
                                                                                     'microserviceCall': False,
                                                                                     'mvisaPan': '1338122689098678',
                                                                                     'name': 'Auto_test_merch26',
                                                                                     'offline': False,
                                                                                     'orgType': 'MERCHANT',
                                                                                     'pan': '211889A1',
                                                                                     'pinCode': '110024',
                                                                                     'requestTime': 1653291856647,
                                                                                     'rupayPan': '4831647953638383',
                                                                                     'scheduler': False,
                                                                                     'selfSignUp': False,
                                                                                     'settingVer': 0,
                                                                                     'setupType': 'BHARATQR',
                                                                                     'status': 'ACTIVE',
                                                                                     'subscriptionPlan': 'BASIC',
                                                                                     'timeZone': 'Asia/Calcutta',
                                                                                     'upgrade': True,
                                                                                     'username': '9886191638',
                                                                                     'password': 'A000000'},
                                 {'accountNumber': '3446182934', 'acquisitions': [
                                     {'acquirerCode': 'YES', 'apps': [], 'bankIdentifier': '0794589BI021078',
                                      'microserviceCall': False, 'offline': False, 'paymentGateway': 'ATOS',
                                      'priority': 0, 'requestTime': 1653291856647, 'scheduler': False,
                                      'selfSignUp': False, 'settingVer': 0, 'settlementCycleDays': 0,
                                      'status': 'ACTIVE', 'terminals': [
                                         {'apps': [], 'emiOnly': False, 'ignoreProperty': False, 'initialized': True,
                                          'keyRotationReqd': True, 'kxWithPg': True, 'loyaltyEnabled': False,
                                          'microserviceCall': False, 'mid': 'MIDIS8921188916', 'offline': False,
                                          'requestTime': 1653291856648, 'scheduler': False, 'selfSignUp': False,
                                          'sequenceId': 1, 'settingVer': 0, 'status': 'ACTIVE', 'tid': '211889a2',
                                          'tidPriority': 0, 'tleEnabled': True, 'upgrade': True}], 'upgrade': True}],
                                  'apps': [], 'bankCode': 'YES', 'bharatQrBankCode': 'YES', 'categoryCode': '4112',
                                  'city': 'Delhi', 'currencyCode': '356', 'enableOrgSetting': True,
                                  'ifscCode': 'KKBK0004589', 'mVisaId': '6132107508996969',
                                  'masterpassPan': '5504998595928361', 'microserviceCall': False,
                                  'mvisaPan': '6132107508996969', 'name': 'Auto_test_merch26', 'offline': False,
                                  'orgType': 'MERCHANT', 'pan': '211889A2', 'pinCode': '110024',
                                  'requestTime': 1653291856647, 'rupayPan': '7101577565129578', 'scheduler': False,
                                  'selfSignUp': False, 'settingVer': 0, 'setupType': 'BHARATQR', 'status': 'ACTIVE',
                                  'subscriptionPlan': 'BASIC', 'timeZone': 'Asia/Calcutta', 'upgrade': True,
                                  'username': '9886191638', 'password': 'A000000'}, {'accountNumber': '3446182934',
                                                                                     'acquisitions': [
                                                                                         {'acquirerCode': 'ICICI',
                                                                                          'apps': [],
                                                                                          'bankIdentifier': '0794589BI021078',
                                                                                          'microserviceCall': False,
                                                                                          'offline': False,
                                                                                          'paymentGateway': 'FDC',
                                                                                          'priority': 0,
                                                                                          'requestTime': 1653291856647,
                                                                                          'scheduler': False,
                                                                                          'selfSignUp': False,
                                                                                          'settingVer': 0,
                                                                                          'settlementCycleDays': 0,
                                                                                          'status': 'ACTIVE',
                                                                                          'terminals': [{'apps': [],
                                                                                                         'emiOnly': False,
                                                                                                         'ignoreProperty': False,
                                                                                                         'initialized': True,
                                                                                                         'keyRotationReqd': True,
                                                                                                         'kxWithPg': True,
                                                                                                         'loyaltyEnabled': False,
                                                                                                         'microserviceCall': False,
                                                                                                         'mid': 'MIDIS8921188916',
                                                                                                         'offline': False,
                                                                                                         'requestTime': 1653291856648,
                                                                                                         'scheduler': False,
                                                                                                         'selfSignUp': False,
                                                                                                         'sequenceId': 1,
                                                                                                         'settingVer': 0,
                                                                                                         'status': 'ACTIVE',
                                                                                                         'tid': '211889a3',
                                                                                                         'tidPriority': 0,
                                                                                                         'tleEnabled': True,
                                                                                                         'upgrade': True}],
                                                                                          'upgrade': True}], 'apps': [],
                                                                                     'bankCode': 'ICICI',
                                                                                     'bharatQrBankCode': 'FDC_ICICI',
                                                                                     'categoryCode': '4112',
                                                                                     'city': 'Delhi',
                                                                                     'currencyCode': '356',
                                                                                     'enableOrgSetting': True,
                                                                                     'ifscCode': 'KKBK0004589',
                                                                                     'mVisaId': '1477200510400617',
                                                                                     'masterpassPan': '6645509814300494',
                                                                                     'microserviceCall': False,
                                                                                     'mvisaPan': '1477200510400617',
                                                                                     'name': 'Auto_test_merch26',
                                                                                     'offline': False,
                                                                                     'orgType': 'MERCHANT',
                                                                                     'pan': '211889A3',
                                                                                     'pinCode': '110024',
                                                                                     'requestTime': 1653291856647,
                                                                                     'rupayPan': '4984905238513480',
                                                                                     'scheduler': False,
                                                                                     'selfSignUp': False,
                                                                                     'settingVer': 0,
                                                                                     'setupType': 'BHARATQR',
                                                                                     'status': 'ACTIVE',
                                                                                     'subscriptionPlan': 'BASIC',
                                                                                     'timeZone': 'Asia/Calcutta',
                                                                                     'upgrade': True,
                                                                                     'username': '9886191638',
                                                                                     'password': 'A000000'},
                                 {'accountNumber': '3446182934', 'acquisitions': [
                                     {'acquirerCode': 'AXIS', 'apps': [], 'bankIdentifier': '0794589BI021078',
                                      'microserviceCall': False, 'offline': False, 'paymentGateway': 'ATOS_TLE',
                                      'priority': 0, 'requestTime': 1653291856647, 'scheduler': False,
                                      'selfSignUp': False, 'settingVer': 0, 'settlementCycleDays': 0,
                                      'status': 'ACTIVE', 'terminals': [
                                         {'apps': [], 'emiOnly': False, 'ignoreProperty': False, 'initialized': True,
                                          'keyRotationReqd': True, 'kxWithPg': True, 'loyaltyEnabled': False,
                                          'microserviceCall': False, 'mid': 'MIDIS8921188916', 'offline': False,
                                          'requestTime': 1653291856648, 'scheduler': False, 'selfSignUp': False,
                                          'sequenceId': 1, 'settingVer': 0, 'status': 'ACTIVE', 'tid': '211889a4',
                                          'tidPriority': 0, 'tleEnabled': True, 'upgrade': True}], 'upgrade': True}],
                                  'apps': [], 'bankCode': 'AXIS', 'bharatQrBankCode': 'AXIS_TLE',
                                  'categoryCode': '4112', 'city': 'Delhi', 'currencyCode': '356',
                                  'enableOrgSetting': True, 'ifscCode': 'KKBK0004589', 'mVisaId': '5497490238710760',
                                  'masterpassPan': '7717093555327590', 'microserviceCall': False,
                                  'mvisaPan': '5497490238710760', 'name': 'Auto_test_merch26', 'offline': False,
                                  'orgType': 'MERCHANT', 'pan': '211889A4', 'pinCode': '110024',
                                  'requestTime': 1653291856647, 'rupayPan': '3644735740944124', 'scheduler': False,
                                  'selfSignUp': False, 'settingVer': 0, 'setupType': 'BHARATQR', 'status': 'ACTIVE',
                                  'subscriptionPlan': 'BASIC', 'timeZone': 'Asia/Calcutta', 'upgrade': True,
                                  'username': '9886191638', 'password': 'A000000'}, {'accountNumber': '3446182934',
                                                                                     'acquisitions': [
                                                                                         {'acquirerCode': 'KOTAK',
                                                                                          'apps': [],
                                                                                          'bankIdentifier': '0794589BI021078',
                                                                                          'microserviceCall': False,
                                                                                          'offline': False,
                                                                                          'paymentGateway': 'KOTAK_ATOS',
                                                                                          'priority': 0,
                                                                                          'requestTime': 1653291856647,
                                                                                          'scheduler': False,
                                                                                          'selfSignUp': False,
                                                                                          'settingVer': 0,
                                                                                          'settlementCycleDays': 0,
                                                                                          'status': 'ACTIVE',
                                                                                          'terminals': [{'apps': [],
                                                                                                         'emiOnly': False,
                                                                                                         'ignoreProperty': False,
                                                                                                         'initialized': True,
                                                                                                         'keyRotationReqd': True,
                                                                                                         'kxWithPg': True,
                                                                                                         'loyaltyEnabled': False,
                                                                                                         'microserviceCall': False,
                                                                                                         'mid': 'MIDIS8921188916',
                                                                                                         'offline': False,
                                                                                                         'requestTime': 1653291856648,
                                                                                                         'scheduler': False,
                                                                                                         'selfSignUp': False,
                                                                                                         'sequenceId': 1,
                                                                                                         'settingVer': 0,
                                                                                                         'status': 'ACTIVE',
                                                                                                         'tid': '211889a5',
                                                                                                         'tidPriority': 0,
                                                                                                         'tleEnabled': True,
                                                                                                         'upgrade': True}],
                                                                                          'upgrade': True}], 'apps': [],
                                                                                     'bankCode': 'KOTAK',
                                                                                     'bharatQrBankCode': 'KOTAK_WL',
                                                                                     'categoryCode': '4112',
                                                                                     'city': 'Delhi',
                                                                                     'currencyCode': '356',
                                                                                     'enableOrgSetting': True,
                                                                                     'ifscCode': 'KKBK0004589',
                                                                                     'mVisaId': '7110319482090391',
                                                                                     'masterpassPan': '7065353619472279',
                                                                                     'microserviceCall': False,
                                                                                     'mvisaPan': '7110319482090391',
                                                                                     'name': 'Auto_test_merch26',
                                                                                     'offline': False,
                                                                                     'orgType': 'MERCHANT',
                                                                                     'pan': '211889A5',
                                                                                     'pinCode': '110024',
                                                                                     'requestTime': 1653291856647,
                                                                                     'rupayPan': '3548985816227401',
                                                                                     'scheduler': False,
                                                                                     'selfSignUp': False,
                                                                                     'settingVer': 0,
                                                                                     'setupType': 'BHARATQR',
                                                                                     'status': 'ACTIVE',
                                                                                     'subscriptionPlan': 'BASIC',
                                                                                     'timeZone': 'Asia/Calcutta',
                                                                                     'upgrade': True,
                                                                                     'username': '9886191638',
                                                                                     'password': 'A000000'},
                                 {'accountNumber': '3446182934', 'acquisitions': [
                                     {'acquirerCode': 'AIRP', 'apps': [], 'bankIdentifier': '0794589BI021078',
                                      'microserviceCall': False, 'offline': False, 'paymentGateway': 'APB',
                                      'priority': 0, 'requestTime': 1653291856647, 'scheduler': False,
                                      'selfSignUp': False, 'settingVer': 0, 'settlementCycleDays': 0,
                                      'status': 'ACTIVE', 'terminals': [
                                         {'apps': [], 'emiOnly': False, 'ignoreProperty': False, 'initialized': True,
                                          'keyRotationReqd': True, 'kxWithPg': True, 'loyaltyEnabled': False,
                                          'microserviceCall': False, 'mid': 'MIDIS8921188916', 'offline': False,
                                          'requestTime': 1653291856648, 'scheduler': False, 'selfSignUp': False,
                                          'sequenceId': 1, 'settingVer': 0, 'status': 'ACTIVE', 'tid': '211889a6',
                                          'tidPriority': 0, 'tleEnabled': True, 'upgrade': True}], 'upgrade': True}],
                                  'apps': [], 'bankCode': 'APB', 'bharatQrBankCode': 'N/A', 'categoryCode': '4112',
                                  'city': 'Delhi', 'currencyCode': '356', 'enableOrgSetting': True,
                                  'ifscCode': 'KKBK0004589', 'mVisaId': '8906828693208232',
                                  'masterpassPan': '7959492960692972', 'microserviceCall': False,
                                  'mvisaPan': '8906828693208232', 'name': 'Auto_test_merch26', 'offline': False,
                                  'orgType': 'MERCHANT', 'pan': '211889A6', 'pinCode': '110024',
                                  'requestTime': 1653291856647, 'rupayPan': '7432435799102184', 'scheduler': False,
                                  'selfSignUp': False, 'settingVer': 0, 'setupType': 'BHARATQR', 'status': 'ACTIVE',
                                  'subscriptionPlan': 'BASIC', 'timeZone': 'Asia/Calcutta', 'upgrade': True,
                                  'username': '9886191638', 'password': 'A000000'}, {'accountNumber': '3446182934',
                                                                                     'acquisitions': [
                                                                                         {'acquirerCode': 'AXIS',
                                                                                          'apps': [],
                                                                                          'bankIdentifier': '0794589BI021078',
                                                                                          'microserviceCall': False,
                                                                                          'offline': False,
                                                                                          'paymentGateway': 'ATOS',
                                                                                          'priority': 0,
                                                                                          'requestTime': 1653291856647,
                                                                                          'scheduler': False,
                                                                                          'selfSignUp': False,
                                                                                          'settingVer': 0,
                                                                                          'settlementCycleDays': 0,
                                                                                          'status': 'ACTIVE',
                                                                                          'terminals': [{'apps': [],
                                                                                                         'emiOnly': False,
                                                                                                         'ignoreProperty': False,
                                                                                                         'initialized': True,
                                                                                                         'keyRotationReqd': True,
                                                                                                         'kxWithPg': True,
                                                                                                         'loyaltyEnabled': False,
                                                                                                         'microserviceCall': False,
                                                                                                         'mid': 'MIDIS8921188916',
                                                                                                         'offline': False,
                                                                                                         'requestTime': 1653291856648,
                                                                                                         'scheduler': False,
                                                                                                         'selfSignUp': False,
                                                                                                         'sequenceId': 1,
                                                                                                         'settingVer': 0,
                                                                                                         'status': 'ACTIVE',
                                                                                                         'tid': '211889a7',
                                                                                                         'tidPriority': 0,
                                                                                                         'tleEnabled': True,
                                                                                                         'upgrade': True}],
                                                                                          'upgrade': True}], 'apps': [],
                                                                                     'bankCode': 'AXIS',
                                                                                     'bharatQrBankCode': 'AXIS',
                                                                                     'categoryCode': '4112',
                                                                                     'city': 'Delhi',
                                                                                     'currencyCode': '356',
                                                                                     'enableOrgSetting': True,
                                                                                     'ifscCode': 'KKBK0004589',
                                                                                     'mVisaId': '4952117256055276',
                                                                                     'masterpassPan': '9756112952374690',
                                                                                     'microserviceCall': False,
                                                                                     'mvisaPan': '4952117256055276',
                                                                                     'name': 'Auto_test_merch26',
                                                                                     'offline': False,
                                                                                     'orgType': 'MERCHANT',
                                                                                     'pan': '211889A7',
                                                                                     'pinCode': '110024',
                                                                                     'requestTime': 1653291856647,
                                                                                     'rupayPan': '1712286706987057',
                                                                                     'scheduler': False,
                                                                                     'selfSignUp': False,
                                                                                     'settingVer': 0,
                                                                                     'setupType': 'BHARATQR',
                                                                                     'status': 'ACTIVE',
                                                                                     'subscriptionPlan': 'BASIC',
                                                                                     'timeZone': 'Asia/Calcutta',
                                                                                     'upgrade': True,
                                                                                     'username': '9886191638',
                                                                                     'password': 'A000000'}]
    if lst_bqr_settings_api_body:
        for bqr_setting_api_body in lst_bqr_settings_api_body:
            merchant_code = get_merchant_code_using_mid(bqr_setting_api_body['acquisitions'][0]['terminals'][0]['mid'])
            acquirer_code = bqr_setting_api_body['acquisitions'][0]['acquirerCode']
            payment_gateway = bqr_setting_api_body['acquisitions'][0]['paymentGateway']
            visa_pan = bqr_setting_api_body['mvisaPan']
            master_pan = bqr_setting_api_body['masterpassPan']
            rupay_pan = bqr_setting_api_body['rupayPan']
            payload = json.dumps(bqr_setting_api_body)
            logger.debug(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            logger.debug(response.text)
            result = json.loads(response.text)
            if result["success"]:
                logger.debug(f"BQR setting through api done successfully for {acquirer_code} with {payment_gateway} "
                             f"of {merchant_code}.")
                update_config_result(merchant_code, acquirer_code, payment_gateway, "BQR", "API")
                update_setting_generated_values(merchant_code, acquirer_code, payment_gateway, visa_pan, master_pan,
                                                rupay_pan)
            else:
                logger.debug(f"BQR setting  through api failed for {acquirer_code} with {payment_gateway} "
                             f"of {merchant_code}.")
                update_config_result(merchant_code, acquirer_code, payment_gateway, "BQR", "FAILED")
    else:
        logger.debug(f"There are no merchants available for performing bqr settings.")


def generate_bqr_setting_api_for_all_merchants() -> list or None:
    """
    This method is used to generate the bqr setting api body for all the available merchants
    :return: list
    """
    conn = ""
    cursor = ""
    lst_bqr_settings = []
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MerchantCode FROM merchants WHERE CreationStatus IN ('Created','Existed');")
        merchant_details = cursor.fetchall()
        lst_merchants_code = []
        for merchant_details in merchant_details:
            lst_merchants_code.append(merchant_details[0])
        cursor.execute("SELECT AcquirerCode, PaymentGateway FROM acquisitions;")
        acquisition_details = cursor.fetchall()
        lst_acquisition_details = []
        for acquisition_detail in acquisition_details:
            lst_acquisition_details.append([acquisition_detail[0], acquisition_detail[1]])
        for merchant_code in lst_merchants_code:
            for acquisition in lst_acquisition_details:
                lst_bqr_settings.append(generate_bqr_setting_api_body(merchant_code, acquisition[0], acquisition[1]))
    except Exception as e:
        logger.error(f"Unable to brq setting api list due to error {str(e)}")
        lst_bqr_settings = None
    cursor.close()
    conn.close()
    return lst_bqr_settings


def generate_bqr_setting_api_body(merchant_code: str, acquirer_code: str, payment_gateway: str) -> dict or None:
    """
    This method is used to generate the bqr setting api body for a specific acquirer code and payment
    gateway of a merchant.
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :return: dict (merchant config api body)
    """
    try:
        merchant_configuration_api = json.loads(merchant_creator.get_api_details_from_db("configureBqr")['RequestBody'])
        settings = get_setting_details(merchant_code, acquirer_code, payment_gateway)
        merchant_configuration_api["username"] = ConfigReader.read_config("SuperUserCredentials", "username")
        merchant_configuration_api["password"] = ConfigReader.read_config("SuperUserCredentials", "password")
        merchant_configuration_api['bankCode'] = settings['bank_code']
        merchant_configuration_api['bharatQrBankCode'] = settings['bqr_bank_code']
        merchant_configuration_api['categoryCode'] = settings['category_code']
        merchant_configuration_api['name'] = settings['merchant_name']
        merchant_configuration_api['mvisaPan'] = get_brand_pan_number(merchant_code, acquirer_code, payment_gateway)[
            'visa_pan']
        merchant_configuration_api['masterpassPan'] = \
        get_brand_pan_number(merchant_code, acquirer_code, payment_gateway)['master_pan']
        merchant_configuration_api['rupayPan'] = get_brand_pan_number(merchant_code, acquirer_code, payment_gateway)[
            'rupay_pan']
        merchant_configuration_api['mVisaId'] = merchant_configuration_api['mvisaPan']
        merchant_configuration_api['pan'] = str(settings['tid']).upper()
        merchant_configuration_api['acquisitions'][0]['acquirerCode'] = settings['acquirer_code']
        merchant_configuration_api['acquisitions'][0]['paymentGateway'] = settings['payment_gateway']
        merchant_configuration_api['acquisitions'][0]['terminals'][0]['mid'] = settings['mid']
        merchant_configuration_api['acquisitions'][0]['terminals'][0]['tid'] = settings['tid']
        if check_if_virtual_mid_required_for_bqr(acquirer_code, payment_gateway) == "True":
            merchant_configuration_api['virtualMid'] = 'V' + settings['mid']
        logger.debug(merchant_configuration_api)
        return merchant_configuration_api
    except Exception as e:
        logger.error(f"Unable to generate the merchant config api due to error {str(e)}")
        return None


def check_if_pan_exists(pan_number: str) -> bool or None:
    """
    This method is used to check if the pan number exists in the environment.
    :param pan_number str
    :return: bool or None
    """
    try:
        query = "SELECT visa_merchant_id_primary, mastercard_merchant_id_primary, npci_merchant_id_primary, " \
                "visa_merchant_id_secondary, mastercard_merchant_id_secondary, npci_merchant_id_secondary, " \
                "merchant_pan FROM bharatqr_merchant_config;"
        result = DBProcessor.getValueFromDB(query)
        column_names = result.columns
        for i in range(0, len(result)):
            for j in range(0, len(column_names)):
                if result[column_names[j]][i] == pan_number:
                    logger.debug(f"Pan number {pan_number} is available in the environment")
                    return True
        logger.debug(f"Pan number {pan_number} is not available in the environment")
        return False
    except Exception as e:
        logger.error(f"Unable to check if the pan number exists in the environment due to error {str(e)}")
        return None


def configure_terminal_dependency(merchant_code: str, acquirer_code: str, payment_gateway: str, payment_mode: str):
    """
    This method is used to configure the terminal dependency for a merchant.
    :param merchant_code str
    :param acquirer_code
    :param payment_gateway
    :param payment_mode
    """
    try:
        if payment_mode.lower() == 'upi':
            payment_mode = "UPI"
        else:
            payment_mode = "BHARATQR"
        query = f"SELECT * from terminal_dependency_config where org_code = '{merchant_code}' and " \
                f"payment_mode = '{payment_mode}' and acquirer_code = '{acquirer_code}' and " \
                f"payment_gateway = '{payment_gateway}';"
        result = DBProcessor.getValueFromDB(query)
        if len(result) > 0:
            logger.debug(f"Terminal dependency is already configured for {acquirer_code} of {merchant_code}")
        else:
            query = f"INSERT INTO terminal_dependency_config(org_code, payment_mode, acquirer_code, payment_gateway, " \
                    f"terminal_dependent_enabled, created_by, created_time, modified_by, modified_time) VALUES " \
                    f"('{merchant_code}', '{payment_mode}',  '{acquirer_code}', '{payment_gateway}',  1,  'ezetap', " \
                    f"now(), 'ezetap', now());"
            result = DBProcessor.setValueToDB(query)
            if DBProcessor.set_value_to_db_query_passed(result):
                logger.debug(f"Terminal dependency successfully configured for {acquirer_code} of {merchant_code}")
            else:
                logger.debug(f"Terminal dependency configuration failed for {acquirer_code} of {merchant_code}")

    except Exception as e:
        logger.error(f"Unable to configure the terminal dependency for {merchant_code} due to error {str(e)}")


def generate_random_number(number_of_digits: int) -> int:
    """
    This method is used to generate the random of a specific length in digits.
    :param number_of_digits int
    :return int
    """
    try:
        length_string = ""
        for i in range(0, number_of_digits):
            length_string = length_string + '9'
        lower_limit = int(length_string[:-1])
        upper_limit = int(length_string)
        return random.randint(lower_limit, upper_limit)
    except Exception as e:
        logger.error(f"Unable to generate the random number due to error {str(e)}")


def add_key_to_upi_setting_api_body(merchant_configuration_api_body: dict) -> dict:
    """
    This method is used to add key to the merchant configuration api body if needed.
    :param merchant_configuration_api_body dict
    :return: dict
    """
    try:
        acquirer = merchant_configuration_api_body['acquisitions'][0]['acquirerCode']
        payment_gateway = merchant_configuration_api_body['acquisitions'][0]['paymentGateway']
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT KeyForUpi FROM acquisitions WHERE AcquirerCode = '{acquirer}' and "
                       f"PaymentGateway = '{payment_gateway}';")
        key = cursor.fetchone()
        if key[0] != 'N/A':
            merchant_configuration_api_body['key'] = key[0]
    except Exception as e:
        logger.error(f"Unable to add key to the merchant configuration request body due to error {str(e)}")
    return merchant_configuration_api_body


def get_setting_details(merchant_code: str, acquirer_code: str, payment_gateway: str) -> dict:
    """
    This method is used to retrieve all the setting related details from the db
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :return: dict
    """
    setting_details = {}
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM acquisitions WHERE AcquirerCode = '{acquirer_code}' AND "
                       f"PaymentGateway = '{payment_gateway}';")
        acquisition_details = cursor.fetchone()
        setting_details['acquirer_code'] = acquisition_details[0]
        setting_details['payment_gateway'] = acquisition_details[1]
        setting_details['number_of_terminals'] = acquisition_details[2]
        setting_details['hsm_name'] = acquisition_details[3]
        setting_details['bank_code'] = acquisition_details[4]
        setting_details['bqr_bank_code'] = acquisition_details[5]
        setting_details['upi_bank_code'] = acquisition_details[6]
        setting_details['bqr_terminal_dependant'] = acquisition_details[7]
        setting_details['upi_terminal_dependant'] = acquisition_details[8]
        setting_details['key_for_upi'] = acquisition_details[9]
        cursor.execute(f"SELECT TID, DeviceSerial, CategoryCode, MID, MerchantCode, MerchantName FROM terminal_details "
                       f"WHERE MerchantCode = '{merchant_code}' AND AcquirerCode = '{acquirer_code}' AND "
                       f"PaymentGateway = '{payment_gateway}';")
        terminal_details = cursor.fetchone()
        setting_details['tid'] = terminal_details[0]
        setting_details['device_serial'] = terminal_details[1]
        setting_details['category_code'] = terminal_details[2]
        setting_details['mid'] = terminal_details[3]
        setting_details['merchant_code'] = terminal_details[4]
        setting_details['merchant_name'] = terminal_details[5]
    except Exception as e:
        logger.error(f"Unable to get the setting details due to error {str(e)}")
    cursor.close()
    conn.close()
    return setting_details


def get_brand_pan_number(merchant_code: str, acquirer_code: str, payment_gateway: str) -> dict or None:
    """
    This method is used to get the pan number of the specified branch.
    This will either return the available pan or a newly generated one.
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :return: str or None
    """
    conn = ""
    cursor = ""
    brands_pan = {}
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT VisaPrimaryPan, MasterPrimaryPan, RupayPrimaryPan FROM settings_generated_values"
                       f" WHERE MerchantCode = '{merchant_code}' AND AcquirerCode = '{acquirer_code}' AND "
                       f"PaymentGateway = '{payment_gateway}';")
        entries = cursor.fetchone()
        if entries:
            logger.debug("Picking the available pan numbers...")
            brands_pan['visa_pan'] = entries[0]
            brands_pan['master_pan'] = entries[1]
            brands_pan['rupay_pan'] = entries[2]
        else:
            logger.debug("Generating unique number for brand pan numbers...")
            brands_pan['visa_pan'] = get_unique_pan_for_bqr_settings(16)
            brands_pan['master_pan'] = get_unique_pan_for_bqr_settings(16)
            brands_pan['rupay_pan'] = get_unique_pan_for_bqr_settings(16)
    except Exception as e:
        logger.error(f"Unable to get the brand pan number due to error {str(e)}")
        brands_pan = None
    cursor.close()
    conn.close()
    return brands_pan


def get_unique_pan_for_bqr_settings(digits: int) -> str or None:
    """
    This method is used to generate the unique pan for bqr settings
    :param digits int
    :return str
    """
    try:
        pan_number = generate_random_number(digits)
        while check_if_pan_exists(str(pan_number)):
            pan_number = generate_random_number(digits)
        return str(pan_number)
    except Exception as e:
        logger.error(f"Unable to get unique pan number due to error {str(e)}")
        return None


def get_merchant_code_using_mid(mid: str) -> str or None:
    """
    This method is used to get the merchant code associated with a mid.
    """
    merchant_code = None
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"select DISTINCT(MerchantCode) from terminal_details where MID = '{mid}';")
        merchant_code = cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Unable to get the merchant code for mid {mid} due to error {str(e)}.")
    return merchant_code


def update_setting_generated_values(merchant_code: str, acquirer_code: str, payment_gateway: str, visa_pan: str,
                                    master_pan: str, rupay_pan: str):
    """
    This method is used to update the setting generated values in the table.
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :param visa_pan str
    :param master_pan str
    :param rupay_pan str
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM settings_generated_values WHERE MerchantCode = '{merchant_code}' AND "
                       f"AcquirerCode = '{acquirer_code}' AND PaymentGateway = '{payment_gateway}';")
        result = cursor.fetchone()
        if result:
            cursor.execute(f"UPDATE settings_generated_values SET VisaPrimaryPan = '{visa_pan}', "
                           f"MasterPrimaryPan = '{master_pan}', RupayPrimaryPan = '{rupay_pan}' WHERE "
                           f"MerchantCode = '{merchant_code}' AND AcquirerCode = '{acquirer_code}' AND "
                           f"PaymentGateway = '{payment_gateway}';")
            conn.commit()
        else:
            cursor.execute(f"INSERT INTO settings_generated_values(MerchantCode, AcquirerCode, PaymentGateway, "
                           f"VisaPrimaryPan, MasterPrimaryPan, RupayPrimaryPan)VALUES('{merchant_code}',"
                           f"'{acquirer_code}','{payment_gateway}','{visa_pan}','{master_pan}','{rupay_pan}');")
            conn.commit()
    except Exception as e:
        logger.error(f"Unable to update the setting generated values due to error {str(e)}")


def update_config_result(merchant_code: str, acquirer_code: str, payment_gateway: str, setting_type: str,
                         set_through: str):
    """
    This method is used to update the configuration results table.
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM configuration_results WHERE MerchantCode = '{merchant_code}' AND "
                       f"AcquirerCode = '{acquirer_code}' AND PaymentGateway = '{payment_gateway}' AND "
                       f"SettingType = '{setting_type}';")
        if len(cursor.fetchall()) > 0:
            cursor.execute(f"UPDATE configuration_results SET SetThrough = '{set_through}' WHERE "
                           f"MerchantCode = '{merchant_code}' AND AcquirerCode = '{acquirer_code}' AND "
                           f"PaymentGateway = '{payment_gateway}' AND SettingType = '{setting_type}'; ")
            conn.commit()
            logger.debug(f"BQR setting result updated for {acquirer_code} with {payment_gateway} of {merchant_code}.")
        else:
            cursor.execute(f"INSERT INTO configuration_results(MerchantCode, AcquirerCode, PaymentGateway, "
                           f"SettingType, SetThrough)VALUES('{merchant_code}','{acquirer_code}',"
                           f"'{payment_gateway}','{setting_type}','{set_through}');")
            logger.debug(f"New entry added for {acquirer_code} with {payment_gateway} of {merchant_code}.")
            conn.commit()
    except Exception as e:
        logger.error(f"Unable update the config results due to error {str(e)}")
    cursor.close()
    conn.close()


def clear_merchant_config_related_tables():
    """
    This method is used to clear the tables that hosts the values of merchant configuration
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MerchantCode FROM merchants WHERE CreationStatus IN ('Created','Existed');")
        lst_merchants = [x[0] for x in cursor.fetchall()]
        cursor.execute("Select DISTINCT(MerchantCode) from settings_generated_values;")
        lst_merchants_to_be_removed = []
        for merchant_to_remove in [x[0] for x in cursor.fetchall()]:
            if not merchant_to_remove in lst_merchants:
                lst_merchants_to_be_removed.append(merchant_to_remove)
        for remove_merchant in lst_merchants_to_be_removed:
            cursor.execute(f"DELETE FROM settings_generated_values where MerchantCode = '{remove_merchant}';")
            conn.commit()
            logger.debug(f"Merchant {remove_merchant} has been removed from settings_generated_values table.")
        cursor.execute("Select DISTINCT(MerchantCode) from configuration_results;")
        lst_merchants_to_be_removed = []
        for merchant_to_remove in [x[0] for x in cursor.fetchall()]:
            if not merchant_to_remove in lst_merchants:
                lst_merchants_to_be_removed.append(merchant_to_remove)
        for remove_merchant in lst_merchants_to_be_removed:
            cursor.execute(f"DELETE FROM configuration_results where MerchantCode = '{remove_merchant}';")
            conn.commit()
            logger.debug(f"Merchant {remove_merchant} has been removed from configuration_results table.")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Unable to clear the merchant config related tables due to error {str(e)}")


def check_if_virtual_mid_required_for_bqr(acquirer_code: str, payment_gateway: str) -> bool:
    """
    This method is used to check if virtual mid is required in the merchant configuration api body.
    :param acquirer_code str
    :param payment_gateway str
    :return: bool
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT VirtualMidRequired FROM acquisitions WHERE AcquirerCode = '{acquirer_code}' AND "
                       f"PaymentGateway = '{payment_gateway}';")
        result = cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Unable to check if virtual mid is required, due to error {str(e)}")
        result = None
    cursor.close()
    conn.close()
    return result


print(configure_bqr_settings())

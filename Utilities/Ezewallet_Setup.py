from Utilities import DBProcessor
from DataProvider import GlobalConstants

# Rename func DBReset
def db_reset():
    delete_wallet_txn_leg = "delete from wallet_txn_leg where wallet_txn_id in (select wallet_txn_id from wallet_txn where merchant_id = '" + GlobalConstants.ORG + "');"
    delete_wallet_txn = "delete from wallet_txn where merchant_id = '" + GlobalConstants.ORG + "';"
    update_agency_account = "update account set balance = '0.00' where entity_id = '" + GlobalConstants.ORG + "';"
    update_admin_account = "update account set balance = '0.00' where entity_id = '" + GlobalConstants.ADMIN_USER + "';"
    update_agent_account = "update account set balance = '0.00' where entity_id = '" + GlobalConstants.AGENT_USER + "';"
    querylist = [delete_wallet_txn_leg, delete_wallet_txn, update_agency_account, update_admin_account, update_agent_account]
    print(querylist)
    print("==========Data setting on ClosedLoop DB "+GlobalConstants.ORG+"===============")
    try:
        for li in querylist:
            DBProcessor.setValueToDB(li, "closedloop_demo")
        print("==========Data setting is successfull=========")
    except:
        print("=========Data Setting failed=======")


def setup_ezewallet():
    db_reset()
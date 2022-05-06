import pandas as pd


def create_csv_file_with_data(self, fileName):
    # list of name, degree, score
    nme = ["aparna"]
    usrname = ["7812540980"]
    mobNum = ["7812540980"]
    email = ["aparna@gmail"]
    pwd = ["D1234567"]
    ext_ref1 = ["extRef1"]
    ext_ref2 = ["extRef2"]
    auth_token = ["12123"]
    p2p = ["true"]
    roles = ["Admin"]
    org = ["AUTO_PYTHON_TRIAL"]
    force_chnge_pwd = ["false"]
    wallet = ["false"]
    labels = ["aparna"]
    tag = ["aparna"]
    status = ["ACTIVE"]
    auth_mob = ["7812540980"]
    processFlow = ["true"]

    # dictionary of lists
    dict = {'Name*': nme, 'UserName*': usrname, 'Mobile Number*': mobNum,'EmailID':email,'Password*':pwd,'External ref 1':ext_ref1,'External ref 2':ext_ref2,'AUTHENTICATION TOKEN':auth_token,
    'P2P(true/false)':p2p,'Roles':roles,'Org_code*':org,'ForcePasswordChange':force_chnge_pwd,'walletEnable(true/false)':wallet,'Labels':labels,'Tag':tag,'Status':status,
    'AuthMobileNumber':auth_mob,'ProcessFlow':processFlow}

    df = pd.DataFrame(dict)

    # saving the dataframe
    df.to_csv(fileName+'.csv', header=True, index=False)

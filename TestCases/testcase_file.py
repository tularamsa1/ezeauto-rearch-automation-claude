from Utilities import DBProcessor


query = "select * from org where org_code = 'Auto_test_merch49';"

result = DBProcessor.getValueFromDB(query)

print(result)


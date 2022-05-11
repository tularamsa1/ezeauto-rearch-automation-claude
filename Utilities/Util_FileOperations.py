# # import openpyxl
# # import xlsxwriter
# # import csv
# #
# # # workbook_read = openpyxl.load_workbook("/home/ezetap/PycharmProjects/PortalAutomation/TestData/myexcel_read.xlsx")
# # # workbook_write = openpyxl.load_workbook("/home/ezetap/PycharmProjects/PortalAutomation/TestData/myexcel_write.xlsx")
# # from self import self
# #
# #
# # def createExcelWithHeaders(fileName):
# #
# #     path = '/home/ezetap/PycharmProjects/PortalAutomation/TestData/'+fileName+'.xlsx'
# #     print(path)
# #     workbook = xlsxwriter.Workbook(path)
# #     worksheet = workbook.add_worksheet('First')
# #     worksheet.write('A1', 'TestCases')
# #     worksheet.write('B1', 'TC Execution')
# #     worksheet.write('C1', 'API|DB Val')
# #     worksheet.write('D1', 'DB Val')
# #     worksheet.write('E1', 'Portal Val')
# #     worksheet.write('F1', 'App Val')
# #     worksheet.write('G1', 'UI Val')
# #     worksheet.write('H1', 'Execution Time')
# #     worksheet.write('I1', 'Validation Time')
# #     worksheet.write('J1', 'Log Coll Time')
# #     worksheet.write('K1', 'Total Time')
# #     workbook.close()
# #     return path
# #
# #
# # def getRowCount(self, path, sheetName):
# #     workbook = openpyxl.load_workbook(path)
# #     sheet = workbook[sheetName]
# #     return sheet.max_row
# #
# #
# # def getColCount(self, path, sheetName):
# #     print("path is : ",path)
# #     workbook = openpyxl.load_workbook(path)
# #     sheet = workbook[sheetName]
# #     return sheet.max_column
# #
# #
# # def getCellData(self, path, sheetName, rowNum, colNum):
# #     workbook = openpyxl.load_workbook(path)
# #     sheet = workbook[sheetName]
# #     return sheet.cell(row=rowNum, column=colNum).value
# #
# #
# # def setCellData(self, path, sheetName, rowNum, colNum, data):
# #     workbook = openpyxl.load_workbook(path)
# #     sheet = workbook[sheetName]
# #     sheet.cell(row=rowNum, column=colNum).value = data
# #     workbook.save(path)
# #
# #
# # def werty():
# #     print("Entered")
# #     path = "/home/ezetap/PycharmProjects/PortalAutomation/TestData/myexcel_read.xlsx"
# #     sheetName = "First"
# #     rows = getRowCount(self, path, sheetName)
# #     cols = getColCount(self, path, sheetName)
# #     print(rows, "===============", cols)
# #     print(getCellData(self, path, sheetName, 2, 1))
# #     setCellData(self, path, sheetName, 5, 5, "DOB")
# #
#
#
#
# import openpyxl
# import xlsxwriter
# import csv
#
# # workbook_read = openpyxl.load_workbook("/home/ezetap/PycharmProjects/PortalAutomation/TestData/myexcel_read.xlsx")
# # workbook_write = openpyxl.load_workbook("/home/ezetap/PycharmProjects/PortalAutomation/TestData/myexcel_write.xlsx")
# from self import self
#
#
# def createExcelWithHeaders(fileName):
#
#     path = '/home/ezetap/PycharmProjects/PortalAutomation/TestData/'+fileName+'.xlsx'
#     workbook = xlsxwriter.Workbook(path)
#     worksheet = workbook.add_worksheet('First')
#     worksheet.write('A1', 'TestCases')
#     worksheet.write('B1', 'TC Execution')
#     worksheet.write('C1', 'API|DB Val')
#     worksheet.write('D1', 'DB Val')
#     worksheet.write('E1', 'Portal Val')
#     worksheet.write('F1', 'App Val')
#     worksheet.write('G1', 'UI Val')
#     worksheet.write('H1', 'Execution Time')
#     worksheet.write('I1', 'Validation Time')
#     worksheet.write('J1', 'Log Coll Time')
#     worksheet.write('K1', 'Total Time')
#     workbook.close()
#     return path
#
#
# def getRowCount(self, path, sheetName):
#     workbook = openpyxl.load_workbook(path)
#     sheet = workbook[sheetName]
#     return sheet.max_row
#
#
# def getColCount(self, path, sheetName):
#     print("path is : ",path)
#     workbook = openpyxl.load_workbook(path)
#     sheet = workbook[sheetName]
#     return sheet.max_column
#
#
# def getCellData(self, path, sheetName, rowNum, colNum):
#     workbook = openpyxl.load_workbook(path)
#     sheet = workbook[sheetName]
#     return sheet.cell(row=rowNum, column=colNum).value
#
#
# def setCellData(self, workbook, path, sheetName, rowNum, colNum, data):
#     sheet = workbook[sheetName]
#     sheet.cell(row=rowNum, column=1).value = data["TC_Name"]
#     sheet.cell(row=rowNum, column=2).value = data["TC_Execution"]
#     sheet.cell(row=rowNum, column=3).value = data["API_Val"]
#     sheet.cell(row=rowNum, column=4).value = data["DB_Val"]
#     sheet.cell(row=rowNum, column=5).value = data["Portal_Val"]
#     sheet.cell(row=rowNum, column=6).value = data["App_Val"]
#     sheet.cell(row=rowNum, column=7).value = data["UI_Val"]
#     sheet.cell(row=rowNum, column=8).value = data["Execution_Time"]
#     sheet.cell(row=rowNum, column=9).value = data["Val_time"]
#     sheet.cell(row=rowNum, column=10).value = data["LogCollTime"]
#     sheet.cell(row=rowNum, column=11).value = data["Tot_Time"]
#
#     workbook.save(path)
#
#
# ExcelData = {"TC_Name":"test_OneTestCase",
#        "TC_Execution":"Pass",
#        "API_Val":"Pass",
#        "DB_Val":"Fail",
#        "Portal_Val":"Pass",
#        "App_Val":"Fail",
#        "UI_Val":"NA",
#        "Execution_Time":"134 ms",
#        "Val_time":"212",
#        "LogCollTime":"12",
#        "Tot_Time":"123"}
#
#
#
#
#
#
#
#
#
# rowNumber = 2
# FileName = createExcelWithHeaders("Details")
# workbook = openpyxl.load_workbook(FileName)
# setCellData(self, workbook,FileName, "First", rowNumber, 11, ExcelData)

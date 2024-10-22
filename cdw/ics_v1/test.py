# import openpyxl
# import pandas as pd
#
# # Create a new Excel workbook
# wb = openpyxl.Workbook()
#
# # Create a worksheet
# ws = wb.active
#
# # Create a MultiIndex object with the parent header name and the calories and duration column names
# columns = pd.MultiIndex.from_tuples([('main_data', 'calories'), ('main_data', 'duration')])
#
# # Create a table
# table = ws.create_table(ref='A1:B3')
#
# # Set the table columns
# table.columns = columns
#
# # Set the table data
# table.cell(row=2, column=1).value = 420
# table.cell(row=2, column=2).value = 50
# table.cell(row=3, column=1).value = 380
# table.cell(row=3, column=2).value = 40
# table.cell(row=4, column=1).value = 390
# table.cell(row=4, column=2).value = 45
#
# # Format the table
# table.autofit()
# table.style = 'TableStyleLight9'
#
# # Save the Excel workbook
# wb.save('data.xlsx')
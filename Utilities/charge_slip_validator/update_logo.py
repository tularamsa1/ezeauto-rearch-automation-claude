import charge_slip_validator
from pathlib import Path

manual_logo_dir = Path("/home/ezetap/Pictures/Screenshots/")

# updating logos
#
# FISERV
reference_url = "https://dev11.ezetap.com/r/o/iwmi3jLF/"
reference_logo_path = manual_logo_dir / "Screenshot from 2023-04-03 12-31-01.png"
bank_or_company = 'fiserv.ezetap'
charge_slip_validator.add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True
)
# #
# # # EZETAP
# reference_url = "https://dev11.ezetap.com/r/o/SjAsWEYr/"  # axis and ezetap logos
# reference_logo_path = manual_logo_dir / "Screenshot from 2023-03-30 15-20-55.png"
# bank_or_company = 'ezetap'
# charge_slip_validator.add_or_update_logo(
#     bank_or_company,
#     reference_url,
#     reference_logo_path,
#     verbose = True
# )
# #
# # # AXIS
# reference_url = "https://dev11.ezetap.com/r/o/SjAsWEYr/"  # axis and ezetap logos
# reference_logo_path = manual_logo_dir / "Screenshot from 2023-03-15 11-45-41.png"
# bank_or_company = "AXIS"
# charge_slip_validator.add_or_update_logo(
#     bank_or_company,
#     reference_url,
#     reference_logo_path,
#     verbose = True
# )
#
# HDFC
# reference_url = "https://dev11.ezetap.com/r/o/H2ma5l3w//"  # axis and ezetap logos
# reference_logo_path = manual_logo_dir / "Screenshot from 2023-02-17 13-30-37.png"
#
# bank_or_company = "HDFC"
# charge_slip_validator.add_or_update_logo(
#     bank_or_company,
#     reference_url,
#     reference_logo_path,
#     verbose = True
# )
# #
# # # YES
# bank_or_company = "YES"
# reference_url = "https://dev11.ezetap.com/r/o/TkOVtk9v/"
# reference_logo_path = manual_logo_dir / "Screenshot from 2023-03-30 15-07-19.png"
# charge_slip_validator.add_or_update_logo(
#     bank_or_company,
#     reference_url,
#     reference_logo_path,
#     verbose = True
# )
# #
# # # iCICI
# reference_url = "https://dev11.ezetap.com/r/o/JB1WaynT/"
# reference_logo_path = manual_logo_dir / "Screenshot from 2023-03-30 15-12-12.png"
# bank_or_company = 'ICICI'
# charge_slip_validator.add_or_update_logo(
#     bank_or_company,
#     reference_url,
#     reference_logo_path,
#     verbose = True
# )
# #
# # # KOTAK
# reference_url = "https://dev11.ezetap.com/r/o/FcxpbCBt/"
# reference_logo_path = manual_logo_dir / "Screenshot from 2023-03-30 15-18-22.png"
# bank_or_company = 'KOTAK'
# charge_slip_validator.add_or_update_logo(
#     bank_or_company,
#     reference_url,
#     reference_logo_path,
#     verbose = True
# )
# #
# #
# # # # IDFC
# reference_url = "https://dev11.ezetap.com/r/o/TYlyHnno/"
# reference_logo_path = manual_logo_dir / "cs_bank_idfc.png"
# bank_or_company = 'IDFC'
# charge_slip_validator.add_or_update_logo(
#     bank_or_company,
#     reference_url,
#     reference_logo_path,
#     verbose = True
# )
# #
# # # AIRP  - Airtel Payments Bank
# reference_url = "https://dev11.ezetap.com/r/o/k5WNwhbk/"
# reference_logo_path = manual_logo_dir / "Screenshot from 2023-03-30 15-19-53.png"
# bank_or_company = 'AIRP'
# charge_slip_validator.add_or_update_logo(
#     bank_or_company,
#     reference_url,
#     reference_logo_path,
#     verbose = True
# )
# #
# from datetime import datetime
# from datetime import timedelta
# # Given timestamp in string
# time_str = '23/2/2020 11:12:22.234513'
# date_format_str = '%d/%m/%Y %H:%M:%S.%f'
# # create datetime object from timestamp string
# given_time = datetime.strptime(time_str, date_format_str)
# print('Given timestamp: ', given_time)
# n = 15
# # Add 15 minutes to datetime object
# final_time = given_time + timedelta(minutes=n)
# print('Final Time (15 minutes after given time ): ', final_time)
# # Convert datetime object to string in specific format
# final_time_str = final_time.strftime('%d/%m/%Y %H:%M:%S.%f')
# print('Final Time as string object: ', final_time_str)
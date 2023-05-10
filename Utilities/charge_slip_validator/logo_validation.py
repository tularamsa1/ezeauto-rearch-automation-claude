
bank = 'HDFC'
# bank = "IDFC"
# company = 'fiserv.ezetap'
company = 'ezetap'
visualize=False
# April 10, 2023
# url = "https://dev11.ezetap.com/r/o/w4Gyihwh"  # ICICI test 1
# url = "https://dev11.ezetap.com/r/o/fA4J0C1U"  # ICICI test 2
# url = "https://dev11.ezetap.com/r/o/nH8K9JOH"  # ICICI test 3
# url = "https://dev11.ezetap.com/r/o/nfK1Vmvt"  # ICICI test 4
# url = "https://dev11.ezetap.com/r/o/eQaDSmBr"  # ICICI test 5
# url = "https://dev11.ezetap.com/r/o/OsA4Bc8F"  # IDFC test 1
# url = "https://dev11.ezetap.com/r/o/VLO3pvZF"  # IDFC test 2
# url = "https://dev11.ezetap.com/r/o/V8UBUMDh"  # IDFC test 3
# url = "https://dev11.ezetap.com/r/o/0Urxfbrn"  # IDFC test 4
# url = "https://dev11.ezetap.com/r/o/PBmUrU0p"  # IDFC test 5
# url = "https://dev11.ezetap.com/r/o/GoOEYtYg"  # KOTAK test 1

# url = "https://demo1.ezetap.com/r/o/J4FC43o2/"  # kotak
# url = "https://dev11.ezetap.com/r/o/iwmi3jLF/"  # idfc

# url = "https://dev11.ezetap.com/r/o/TkOVtk9v/"  # yes bank
# url = "https://demo1.ezetap.com/r/o/Thvh8e3h/"  # original axis
# url = "https://dev11.ezetap.com/r/o/SjAsWEYr/" # test axis
url = 'https://dev11.ezetap.com/r/o/H2ma5l3w/'  # original hdfc
# url = 'https://dev11.ezetap.com/r/o/H2ma5l3w/'  # test hdfc
# url = 'https://dev11.ezetap.com/r/o/JB1WaynT/'  # icici

import charge_slip_validator

company_logo_valid, bank_logo_valid = charge_slip_validator.validate_chargeslip_image_logos_from_url(url, bank, company, visualize=True)

print(f"{company_logo_valid=}\n{bank_logo_valid=}")

# ezetap logo from axis url is used to create golden master
# AXIS + ezetap working - fine
# HDFC + ezetap working - fine

# fiserv logo from icci url is used to create golden master
# ICICI + fiserve working - fine
# IDFC + fiserv working - ?





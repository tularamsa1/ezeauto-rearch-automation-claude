bank = None
company = 'fiserv.ezetap'
# company = 'ezetap'
visualize=True

# url = "https://demo1.ezetap.com/r/o/J4FC43o2/"  # kotak
# url = "https://dev11.ezetap.com/r/o/iwmi3jLF/"  # idfc
# url = "https://demo1.ezetap.com/r/o/OOvarhdH/"  # yes bank
# url = "https://demo1.ezetap.com/r/o/Thvh8e3h/"  # original axis
# url = "https://demo1.ezetap.com/r/o/RVpfCy1z/" # test axis
url = "https://dev11.ezetap.com/r/o/JB1WaynT/" # test ICICI
# url = 'http://demo1.ezetap.com/r/o/xdJxBfiz/'  # original hdfc
# url = 'https://demo1.ezetap.com/r/o/RT5EP72j/'  # test hdfc

import charge_slip_validator

company_logo_valid, bank_logo_valid = charge_slip_validator.validate_chargeslip_image_logos_from_url(url, bank, company, visualize=True)
print("Name company_logo_valid", company_logo_valid)
print("Name Bank Logo", bank_logo_valid)

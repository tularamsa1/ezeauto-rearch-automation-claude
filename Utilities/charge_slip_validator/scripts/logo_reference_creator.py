

# create a yaml file and add these data to it and then read yaml to dict and run creation in loop

import charge_slip_validator

# HDFC  + EZETAP
bank_or_company = "hdfc"
reference_url = "https://www.ezetap.com/r/o/zit95O7A/"
reference_logo_path = "/home/santokalayil/Pictures/Screenshots/Screenshot from 2022-11-10 16-36-01.png"

# AXIS
bank_or_company = "axis"
reference_url = "http://eze.cc/r/o/NcRYNDC4/"  # axis old does not work.. but looks similar
reference_logo_path = "/home/santokalayil/Pictures/Screenshots/Screenshot from 2022-11-10 16-49-47.png"

# ICICI + FISERV EZETAP
bank_or_company = "icici"
reference_url = "https://www.ezetap.com/r/o/qem8b5ML/"  # icici was not exisiting
reference_logo_path = "/home/santokalayil/Pictures/Screenshots/Screenshot from 2022-11-10 17-41-49.png"

# FISERV EZETAP
bank_or_company = "fiserv.ezetap"
reference_url = "https://www.ezetap.com/r/o/qem8b5ML/"
reference_logo_path = "/home/santokalayil/Pictures/Screenshots/Screenshot from 2022-11-10 17-52-00.png"



# reference_logo_path = f'charge_slip_validator/assets/media/logos/manual_references/{bank_or_company}.png'
charge_slip_validator.add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True
)
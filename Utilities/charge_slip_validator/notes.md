
# Install instructions:
Currently in two ways you can install this library

1. Cloning or copying directory and installing 
```
git clone https://github.com/santokalayil/charge_slip_validator.git
cd charge_slip_validator

# to install or upgrade
pip3 install --no-cache-dir --upgrade ./

```

2. pip install directly from git dev branch
```
pip3 install git+https://github.com/santokalayil/charge_slip_validator.git@dev
```

## Script to get the so far available logos
```
import charge_slip_validator

bank_or_company = "kotak"
reference_url = "https://demo1.ezetap.com/r/o/J4FC43o2/"
reference_logo_path = f'/home/ezetap/Documents/work/workroom/logos_manually_taken/{bank_or_company}.png'
charge_slip_validator.add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True
)

bank_or_company = "fiserv.ezetap"
reference_url = "https://demo1.ezetap.com/r/o/nKxs1qDS/"
reference_logo_path = f'/home/ezetap/Documents/work/workroom/logos_manually_taken/{bank_or_company}.png'
charge_slip_validator.add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True
)

bank_or_company = "idfc"
reference_url = "https://demo1.ezetap.com/r/o/nKxs1qDS/"
reference_logo_path = f'/home/ezetap/Documents/work/workroom/logos_manually_taken/{bank_or_company}.png'
charge_slip_validator.add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True
)

bank_or_company = "yes"
reference_url = "https://demo1.ezetap.com/r/o/OOvarhdH/"
reference_logo_path = f'/home/ezetap/Documents/work/workroom/logos_manually_taken/{bank_or_company}.png'
charge_slip_validator.add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True
)

bank_or_company = "axis"
reference_url = "http://demo1.ezetap.com/r/o/Thvh8e3h/"
reference_logo_path = f'/home/ezetap/Documents/work/workroom/logos_manually_taken/{bank_or_company}.png'
charge_slip_validator.add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True
)


bank_or_company = 'hdfc'
reference_url = 'http://demo1.ezetap.com/r/o/xdJxBfiz/'
reference_logo_path = f'/home/ezetap/Documents/work/workroom/logos_manually_taken/{bank_or_company}.png'

charge_slip_validator.add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True
)

bank_or_company = 'ezetap'
reference_url = 'http://demo1.ezetap.com/r/o/xdJxBfiz/'
reference_logo_path = '/home/ezetap/Documents/work/workroom/logos_manually_taken/ezetap.png'

charge_slip_validator.add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True
)
```
## How to validate?

```
bank = 'axis'
# company = 'fiserv.ezetap'
company = 'ezetap'
visualize=False

# url = "https://demo1.ezetap.com/r/o/J4FC43o2/"  # kotak
# url = "https://demo1.ezetap.com/r/o/nKxs1qDS/"  # idfc
# url = "https://demo1.ezetap.com/r/o/OOvarhdH/"  # yes bank
# url = "https://demo1.ezetap.com/r/o/Thvh8e3h/"  # original axis
url = "https://demo1.ezetap.com/r/o/RVpfCy1z/" # test axis
# url = 'http://demo1.ezetap.com/r/o/xdJxBfiz/'  # original hdfc
# url = 'https://demo1.ezetap.com/r/o/RT5EP72j/'  # test hdfc

import charge_slip_validator

company_logo_valid, bank_logo_valid = charge_slip_validator.validate_chargeslip_image_logos_from_url(url, bank, company, visualize=True)



```

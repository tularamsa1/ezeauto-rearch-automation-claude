# charge_slip_validator
---

[![N|Solid](https://www.python.org/static/community_logos/python-powered-w-70x28.png)](https://www.python.org/)
<!-- [![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat)](https://github.com/santokalayil/) -->
---

charge_slip_validator - an charge slip validation library for Python
=====================================================================
**charge_slip_validator** is a Python libarary used to validate chargeslips. The library is developed by Santo K Thomas for Ezetap by Razorpay.
Charge slip screenshot images are analysed and validated with more accuracy.
Additionally, it uses computer vision to identify the logo locations and 
identify and compare with the original logo images based on threshold values. 

Main Features
-------------
Here are just a few of the things that charge slip validator does well:
  - Logos in Screenshots taken from selenium brower will be located, saved 
  as separate images and validated.
  - Uses openCV to detect the location of logos



## Install instructions:

### Install external dependencies

Ubuntu based linux distributions:
```
sudo apt-get update

# required for opencv to work
sudo apt-get install ffmpeg libsm6 libxext6  -y

# firefox required for gecko-driver installation
sudo apt install snapd  # restart might be required to start snap services
# systemctl start snapd.service
sudo snap install firefox

```
Fedora based distributions
```
sudo dnf update

# required for opencv to work
sudo dnf install ffmpeg gtk2 gtk2-devel -y # libsm6 libxext6  -y

# firefox required for gecko-driver installation
sudo apt install snapd  # restart might be required to start snap services
# systemctl start snapd.service
sudo snap install firefox

```
Visit: https://fedoramagazine.org/automate-web-browser-selenium/ for alternate ways


Currently in two ways you can install this library

1. pip install directly from git dev branch
```
pip3 install git+https://github.com/ezetap-user/charge_slip_validator.git@dev
```

2. Cloning or copying directory and installing 
```
git clone https://github.com/ezetap-user/charge_slip_validator.git
cd charge_slip_validator

# to install or upgrade
pip3 install --no-cache-dir --upgrade ./

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

 if issues while running program similar to `OpenCV(4.5.4) /tmp/pip-req-build-khv2fx3p/opencv/modules/highgui/src/window.cpp:1274:`, then you might have a headless version installed. please do the follwing

```
pip uninstall opencv-python-headless -y 
pip install opencv-python --upgrade
```

from __future__ import annotations

__docformat__ = "restructuredtext"

# Let users know if they're missing any of our hard dependencies
_hard_dependencies = ('numpy', )  # ("numpy", "pytz", "dateutil")
_missing_dependencies = []

for _dependency in _hard_dependencies:
    try:
        __import__(_dependency)
    except ImportError as _e:
        _missing_dependencies.append(f"{_dependency}: {_e}")

if _missing_dependencies:
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join(_missing_dependencies)
    )
del _hard_dependencies, _dependency, _missing_dependencies

__version__  = "0.01"



def __dir__() -> list[str]:
    return list(globals().keys())



# module level doc-string
__doc__ = """
charge_slip_validator - a charge slip validation library for Python
=====================================================================
**charge_slip_validator** is a Python libarary used to validate chargeslips.
Charge slip screenshot images are analysed and validated with more accuracy.
Additionally, it uses computer vision to identify the logo locations and 
identify and compare with the original logo images based on threshold values. 

Main Features
-------------
Here are just a few of the things that charge slip validator does well:
  - Logos in Screenshots taken from selenium brower will be located, saved 
  as separate images and validated.
  - Uses openCV to detect the location of logos
"""


from . import errors, config, cv_tools, core

from .core.screenshot_processor import add_or_update_logo, validate_chargeslip_image_logos_from_url
from .config import reset_configuration
from .core.logo_detector import does_both_logos_exist_in_screenshot


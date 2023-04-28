import os
from typing import Optional
import cv2

from ..cv_tools.template_detection import detect_template_and_get_coordinates
from .. import errors
from ..config import path

from ..config.utilities import load_configuration, save_configuration


def get_threshold(logo:str):
    config_info = load_configuration()
    if logo == 'ezetap':
        if "EZETAP_LOGO_THRESHOLD" in config_info.keys():
            return config_info['EZETAP_LOGO_THRESHOLD']
        else:
            raise Exception("The 'EZETAP_LOGO_THRESHOLD' key is not found in configuration yaml file") 
    elif logo == 'bank':
        if "BANK_LOGO_THRESHOLD" in config_info.keys():
            return config_info['BANK_LOGO_THRESHOLD']
        else:
            raise Exception("The 'BANK_LOGO_THRESHOLD' key is not found in configuration yaml file") 
    else:
        raise Exception(f"unknown logo '{logo}' is found. Options are 'ezetap' or 'bank'")



def set_threshold(threshold, logo: Optional[str]=None):
    config_info = load_configuration()
    if logo is None:
        config_info['EZETAP_LOGO_THRESHOLD'] = threshold
        config_info['BANK_LOGO_THRESHOLD'] = threshold
    elif logo == 'ezetap':
        config_info['EZETAP_LOGO_THRESHOLD'] = threshold
    elif logo == 'bank':
        config_info['BANK_LOGO_THRESHOLD'] = threshold
    else:
        raise Exception(f"unknown logo '{logo}' is found. Options are 'ezetap' or 'bank'")
    
    save_configuration(config_info)



def detect_logos_from_screenshot(img_path, ezetap_logo_path, bank_logo_path, save_location: Optional[str]=None):
    '''This function detects ezetap logo and bank if exists and returns result as tuple (ezetap_logo_found: bool, bank_logo_found: bool)'''

    # check ezetap_logo 
    ezetap_logo_found = None
    try:
        ezetap_logo_coordinates = detect_template_and_get_coordinates(img_path, ezetap_logo_path, threshold=get_threshold('ezetap'))
        ezetap_logo_found = True
    except errors.opencv.TemplateNotDetectedError as _:  # change this to corresponding Not found error
        ezetap_logo_found = False

    # check bank_logo 
    bank_logo_found = None
    try:
        bank_logo_coordinates = detect_template_and_get_coordinates(img_path, bank_logo_path, threshold=get_threshold('bank'))
        bank_logo_found = True
    except errors.opencv.TemplateNotDetectedError as _:  # change this to corresponding Not found error
        bank_logo_found = False
    
    # drawing and saving
    if ezetap_logo_found is True or bank_logo_found is True:
        img = cv2.imread(img_path)

        if ezetap_logo_found is True:
            top_left_loc, bottom_right_loc = ezetap_logo_coordinates
            cv2.rectangle(img, top_left_loc, bottom_right_loc, (255, 255, 0), 2)

        if bank_logo_found is True:
            top_left_loc, bottom_right_loc = bank_logo_coordinates
            cv2.rectangle(img, top_left_loc, bottom_right_loc, (0, 255, 255), 2)

        if save_location:
            cv2.imwrite(save_location, img)

    return ezetap_logo_found, bank_logo_found


def does_both_logos_exist_in_screenshot(sceenshot_path, bank, save_location: Optional[str]=None):
    ezetap_logo_path = path.EZETAP_LOGO_PATH
    if not os.path.isfile(ezetap_logo_path):
        raise Exception(f"Ezetap Logo is not found in location '{ezetap_logo_path}'")

    bank_logo_path = os.path.join(path.BANK_LOGOS_DIR, f"{bank.strip().lower() if bank.strip() else 'empty'}.png")
    if not os.path.isfile(bank_logo_path):
        raise Exception(f"Ezetap Logo is not found in location '{ezetap_logo_path}'")
    
    ezetap_log_exists, bank_logo_exists = detect_logos_from_screenshot(sceenshot_path, ezetap_logo_path, bank_logo_path, save_location)
    return all((ezetap_log_exists, bank_logo_exists))


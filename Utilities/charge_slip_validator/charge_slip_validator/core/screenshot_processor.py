import os
import json
import pathlib
import numpy as np
import cv2

import geckodriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
# from Screenshot import Screenshot
# import Screenshot


from ..config import utilities as config_utils
from .. import cv_tools
from ..config import path

driver_path = geckodriver_autoinstaller.install()

# SCREENSHOTS_DIR = pathlib.Path("screenshots").resolve()
# SCREENSHOTS_DIR.mkdir(exist_ok=True)

# ORIGINAL_SCREENSHOTS_DIR = SCREENSHOTS_DIR / 'original'
# ORIGINAL_SCREENSHOTS_DIR.mkdir(exist_ok=True)

# IDENTIFIED_WIDTH, BROWSER_HEIGHT = 400, 500

def cv2_show(img):
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def take_screenshot_of_webpage(url, output_filepath):

    configuration = config_utils.load_configuration()

    BROWSER_WIDTH = configuration['BROWSER_WIDTH']
    BROWSER_HEIGHT = configuration['BROWSER_HEIGHT']

    

    opts = Options()
    if configuration['BROWSER_HEADLESS_MODE'] is True:
        opts.add_argument("--headless")

    # opts.add_argument(f"--window-size={BROWSER_WIDTH}x{BROWSER_HEIGHT}")
    DRIVER = webdriver.Firefox(options=opts)
    # DRIVER = webdriver.Firefox()
    
    DRIVER.set_window_size(width=BROWSER_WIDTH, height=BROWSER_HEIGHT)
    DRIVER.get(url)

    # save_path, image_name = os.path.split(output_filepath)

    # # saving screenshot
    # ob = Screenshot.Screenshot()
    # img=ob.full_Screenshot(DRIVER, save_path=save_path, image_name=image_name)
    
    # screenshot_image_path = str(ORIGINAL_SCREENSHOTS_DIR / output_filename)
    w = DRIVER.execute_script('return document.body.parentNode.scrollWidth')
    h = DRIVER.execute_script('return document.body.parentNode.scrollHeight')
    DRIVER.set_window_size(w, h)

    DRIVER.get_full_page_screenshot_as_file(output_filepath)
    # DRIVER.find_element_by_tag_name('body').screenshot(output_filepath)

    # DRIVER.get_screenshot_as_file(output_filepath)

    # we might need to take global driver from ezeauto . Then driver closing is not needed
    DRIVER.close()
    DRIVER.quit()


def crop_the_screenshot(img: np.ndarray):
    '''Takes the input array of BGR color image (read via cv2.imread) and returns a cropped image of the chargeslip box
    '''
    avg = np.mean(img, axis=2)  # img (3 dim) is converted to 2 dim (with height and width) so that filtering with 255 is easy
    threshold = 125

    # LEFT RIGHT WHITE SPACE CUTTING
    # any or all (all preferred if an)  # variabl name ends with non_255 bcz initially it was avg != 255
    locatons_in_y_axis_with_non_255 = np.where(np.any(avg < threshold, axis=0))  # axis 0 will check for only y axis section

    locatons_in_y_axis_with_non_255 = locatons_in_y_axis_with_non_255[0]  # since previous line created a tuple
    # start_n_end_in_width_axis = locatons_in_y_axis_with_non_255[[0, -1]]  # taking first and last element 
    # (they will be indices in width pixel to start and end to avoid left and right white spaces)

    start_pxl_in_width_axis = locatons_in_y_axis_with_non_255[0]
    end_pxl_in_width_axis = locatons_in_y_axis_with_non_255[-1] + 1  # +1 to add the end point also
    left_right_cropped_img = img[:, start_pxl_in_width_axis:end_pxl_in_width_axis:, :]

    # TOP BOTTOM WHITE SPACE CUTTING
    left_half_of_avg = avg[:, :int(avg.shape[1]/2)+1] # since print button can interfere in calculating

    locatons_in_x_axis_with_non_255 = np.where(np.any(left_half_of_avg < threshold, axis=1))
    locatons_in_x_axis_with_non_255 = locatons_in_x_axis_with_non_255[0]

    start_pxl_in_height_axis = locatons_in_x_axis_with_non_255[0]
    end_pxl_in_height_axis = locatons_in_x_axis_with_non_255[-1] + 1  # +1 to add the end point also

    # CROPPING HAPPENS HERE FROM LEFT, RIGHT, TOP and BOTTOM
    cropped_img = img[start_pxl_in_height_axis:end_pxl_in_height_axis, start_pxl_in_width_axis:end_pxl_in_width_axis, :]
    return cropped_img


def add_padding_to_image(img, padding_width=10):
    # adding padding to the top-bottom
    padding_above_n_below = np.full((padding_width, *img.shape[1:]), 255)  # 255 * 3 dim for adding white padding
    top_bottom_padding_added_img = np.vstack([padding_above_n_below, img, padding_above_n_below])

    # adding padding to sides              original height                     padding          original_3_dim (BGR dim)
    padding_left_n_right = np.full((top_bottom_padding_added_img.shape[0], padding_width, top_bottom_padding_added_img.shape[-1]), 255)
    right_left_top_bottom_padding_added_img = np.hstack([padding_left_n_right, top_bottom_padding_added_img, padding_left_n_right])
    return right_left_top_bottom_padding_added_img


def create_reference_logo_image_from_receipt_image(
    bank_or_company,
    img_path, 
    manual_reference_logo_path, 
    ideal_reference_logo_save_dir_path,
    threshold=0.8,
    visualize=True, 
    color= (0, 255, 255),
):
    '''

    Example here:
    -----------
    import pathlib

    bank = 'hdfc'\n
    img_path = "screenshots/cropped/screenshot_4.png"  #


    logos_ideal_references_dir = pathlib.Path("logos_ideal_reference").resolve()
    logos_ideal_references_dir.mkdir(exist_ok=True)

    template_img_path = f"logos_manually_taken/{bank}.png"

    create_reference_logo_image_from_receipt_image(
        bank,
        img_path, 
        manual_reference_logo_path=template_img_path, 
        ideal_reference_logo_save_dir_path=logos_ideal_references_dir,
        threshold=0.8,
        visualize=True, 
        color= (0, 255, 255),
    )


    company = 'ezetap'
    img_path = "screenshots/cropped/screenshot_4.png"  #

    logos_ideal_references_dir = pathlib.Path("logos_ideal_reference").resolve()
    logos_ideal_references_dir.mkdir(exist_ok=True)

    template_img_path = f"logos_manually_taken/{company}.png"

    create_reference_logo_image_from_receipt_image(
        company,
        img_path, 
        manual_reference_logo_path=template_img_path, 
        ideal_reference_logo_save_dir_path=logos_ideal_references_dir,
        threshold=0.8,
        visualize=True, 
        color= (0, 255, 255),
    )
    
    '''
    lower_section_logos = config_utils.load_configuration()['LOWER_SECTION_LOGOS']
    
    found_top_left_loc, found_bottom_right_loc = cv_tools.template_detection.detect_template_and_get_coordinates(
        img_path=img_path, 
        template_img_path=manual_reference_logo_path,
        threshold=threshold, 
        visualize=visualize, 
        color= color, 
        verbose=True,
    )

    
    img = cv2.imread(img_path)

    # crop logo from image coordinates
    cropped_img = img[found_top_left_loc[-1]:found_bottom_right_loc[-1], found_top_left_loc[0]:found_bottom_right_loc[0]]

    reference_logo_path = os.path.join(ideal_reference_logo_save_dir_path, f'{bank_or_company}.png')
    cv2.imwrite(reference_logo_path, cropped_img)

    bank_or_company_referece_logo_coordinates_json = os.path.join(ideal_reference_logo_save_dir_path, f'{bank_or_company}.json')
    
    if bank_or_company in lower_section_logos:
        reference_receipt_height, reference_receipt_width, _ = img.shape

        print("REFERENCE HEIGHT AND WIDTH: ", reference_receipt_height, reference_receipt_width)

        save_dict = dict(
            reference_receipt_height = reference_receipt_height,
            reference_receipt_width = reference_receipt_width,
            found_top_left_loc = found_top_left_loc,
            found_bottom_right_loc = found_bottom_right_loc,
        )
        

    else:
        save_dict = dict(
            found_top_left_loc = found_top_left_loc,
            found_bottom_right_loc = found_bottom_right_loc
        )

    with open(bank_or_company_referece_logo_coordinates_json, 'w') as f:
        json.dump(save_dict, f)

    if visualize is True:
        cv2_show(cropped_img)
        # plt.imshow(cropped_img[::,::,::-1]);


def create_reference_logo_image_from_ideal_receipt_url(url, bank_or_company):

    output_filename = f"{bank_or_company}.png"
    ORIGINAL_SCREENSHOTS_DIR = pathlib.Path(path.ORIGINAL_SCREENSHOTS_DIR)
    ORIGINAL_SCREENSHOTS_DIR.mkdir(exist_ok=True)

    CROPPED_SCREENSHOTS_DIR = pathlib.Path(path.CROPPED_SCREENSHOTS_DIR)
    CROPPED_SCREENSHOTS_DIR.mkdir(exist_ok=True)

    PADDED_SCREENSHOTS_DIR = pathlib.Path(path.PADDED_SCREENSHOTS_DIR)
    PADDED_SCREENSHOTS_DIR.mkdir(exist_ok=True)

    img_path = ORIGINAL_SCREENSHOTS_DIR / output_filename

    take_screenshot_of_webpage(url, str(img_path))
    img = cv2.imread(str(img_path))

    img = crop_the_screenshot(img)
    cropped_img_path = CROPPED_SCREENSHOTS_DIR / img_path.name
    cv2.imwrite(str(cropped_img_path), img)

    img = add_padding_to_image(img)
    padded_img_path = PADDED_SCREENSHOTS_DIR / img_path.name
    cv2.imwrite(str(padded_img_path), img)

    manual_reference_logo_path = os.path.join(path.MANUAL_REFERECES_DIR, f"{bank_or_company}.png")

    create_reference_logo_image_from_receipt_image(
        bank_or_company=bank_or_company,
        img_path=str(cropped_img_path),
        manual_reference_logo_path=manual_reference_logo_path,
        ideal_reference_logo_save_dir_path=path.IDEAL_REFERECES_DIR,
        threshold=0.8,
        visualize=False,
    )
    print("Created new ideal reference logo image fromthe ideal receipt")


def add_or_update_logo(
    bank_or_company,
    reference_url,
    reference_logo_path,
    verbose = True

):
    '''
    Usage:
    ------
    First, Manually cut the logo for referencing. and get the path as reference_logo_path
    
    ---
    ```\n
    bank_or_company = 'hdfc'\n
    reference_url = 'http://demo1.ezetap.com/r/o/xdJxBfiz/'\n
    reference_logo_path = './hdfc.png'

    add_or_update_logo(
        bank_or_company,
        reference_url,
        reference_logo_path,
        verbose = True
    )
    ```
    ---
    Whenever a logo or entity is added or changed, we need to run this function for each of them

    '''


    # copy reference image (manually cut) and update the reference url info on configuration.yaml file
    if not os.path.isdir(path.MANUAL_REFERECES_DIR):
        os.mkdir(path.MANUAL_REFERECES_DIR)

    cv2.imwrite(
        os.path.join(path.MANUAL_REFERECES_DIR, f'{bank_or_company}.png'), 
        cv2.imread(str(reference_logo_path))
    )

    if verbose is True:
        print(f"Reference logo is stored for further process and extraction")


    configuration = config_utils.load_configuration()
    # reference_urls = configuration['REFERENCE_URLS']
    # reference_urls[bank_or_company] = reference_url
    config_utils.save_configuration(configuration)

    if verbose is True:
        print(f"Configuration file updated with new entity info: {bank_or_company}")

    create_reference_logo_image_from_ideal_receipt_url(
        url=reference_url, 
        bank_or_company=bank_or_company
    )
    if verbose is True:
        print("Done")



def validate_chargeslip_image_logos(img_path, bank, company, visualize=False): 
    
    logos_ideal_references_dir = path.IDEAL_REFERECES_DIR
    if not os.path.isdir(logos_ideal_references_dir):
        os.mkdir(logos_ideal_references_dir)
    
    logos_ideal_references_dir = pathlib.Path(logos_ideal_references_dir)

    # loading the new screenshot image
    img = cv2.imread(str(img_path))

    # initializing variables 
    BANK_LOGO_MATCH = None
    COMPANY_LOGO_MATCH = None

    # BANK LOGO COMPARISON
    if bank is not None:
        bank_reference_logo_path = logos_ideal_references_dir / f'{bank}.png'

        bank_reference_logo_coordinates_json = logos_ideal_references_dir / f'{bank}.json'
        
        # raises exception if not found the co-ordinates
        if not os.path.isfile(bank_reference_logo_coordinates_json):
            raise Exception(f"Json file with coordinates is not found for bank :{bank}.\
                \nPlease make sure if you have added logo for {bank}")


        with open(str(bank_reference_logo_coordinates_json), 'r') as f:
            bank_reference_logo_coordinates = json.load(f)

        bank_reference_logo = cv2.imread(str(bank_reference_logo_path))


        cropped_from_screenshot_to_compare_with_bank_reference_logo = img[\
            bank_reference_logo_coordinates['found_top_left_loc'][-1]\
                :bank_reference_logo_coordinates['found_bottom_right_loc'][-1], \
                    bank_reference_logo_coordinates['found_top_left_loc'][0]\
                        :bank_reference_logo_coordinates['found_bottom_right_loc'][0]]

        # if np.sum(bank_reference_logo != cropped_from_screenshot_to_compare_with_bank_reference_logo) == 0:
        #     print("MATCH")

        if np.all(bank_reference_logo == cropped_from_screenshot_to_compare_with_bank_reference_logo):
            BANK_LOGO_MATCH = True
        else:
            BANK_LOGO_MATCH = False


    # COMPANY LOGO COMPARISON
    company_reference_logo_path = logos_ideal_references_dir / f'{company}.png'
    company_reference_logo_coordinates_json = logos_ideal_references_dir / f'{company}.json'

    if not os.path.isfile(company_reference_logo_coordinates_json):
        raise Exception(f"Json file with coordinates is not found for company :{company}.\
            \nPlease make sure if you have added logo for {company}")

    with open(str(company_reference_logo_coordinates_json), 'r') as f:
        company_reference_logo_coordinates = json.load(f)

    company_reference_logo = cv2.imread(str(company_reference_logo_path))

    # relative calculations start
    current_image_height, current_image_width, _ = img.shape

    calc_relative_top = company_reference_logo_coordinates["found_top_left_loc"][-1] - company_reference_logo_coordinates['reference_receipt_height']
    calc_top = current_image_height + calc_relative_top

    calc_relative_bottom = company_reference_logo_coordinates["found_bottom_right_loc"][-1] - company_reference_logo_coordinates['reference_receipt_height']
    calc_bottom = current_image_height + calc_relative_bottom

    calc_top_left_loc = (company_reference_logo_coordinates['found_top_left_loc'][0], calc_top)
    calc_bottom_right_loc = (company_reference_logo_coordinates['found_bottom_right_loc'][0], calc_bottom)
    # relative calculations end

    cropped_from_screenshot_to_compare_with_company_reference_logo = img[\
        calc_top_left_loc[-1]\
            :calc_bottom_right_loc[-1], \
                calc_top_left_loc[0]\
                    :calc_bottom_right_loc[0]]

    if np.all(company_reference_logo == cropped_from_screenshot_to_compare_with_company_reference_logo):
        COMPANY_LOGO_MATCH = True
    else:
        COMPANY_LOGO_MATCH = False


    # DRAWING IMAGE FOR VIEW PURPOSE
    if visualize is True:
        img_drawn = img.copy()

        if BANK_LOGO_MATCH is True:
            cv2.rectangle(
                img_drawn, 
                bank_reference_logo_coordinates['found_top_left_loc'],
                bank_reference_logo_coordinates['found_bottom_right_loc'],
                color=(0, 255, 255),
                thickness=2
            )
        if COMPANY_LOGO_MATCH is True:
            cv2.rectangle(img_drawn, calc_top_left_loc, calc_bottom_right_loc, color=(0, 255, 0), thickness=2)
        
        cv2_show(img_drawn)
        # plt.imshow(img_drawn[::,::,::-1])

    return COMPANY_LOGO_MATCH, BANK_LOGO_MATCH



def validate_chargeslip_image_logos_from_url(url, bank, company='ezetap', visualize=False):
    '''This function returns a tuple of boolean (COMPANY_LOGO_MATCH, BANK_LOGO_MATCH)\n
    Usage:
    -----
    ```
    bank = "hdfc"
    company = 'ezetap'
    visualize=False
    
    url = 'http://demo1.ezetap.com/r/o/xdJxBfiz/'

    company_logo_match, bank_logo_match = validate_chargeslip_image_logos_from_url(url, bank, company, visualize=True)

    if all([company_logo_match, bank_logo_match]):
        print("Full Pass!")

    ```

    '''
    image_path = os.path.join(path.TEMP_DIR, f"screenshot_original.png")
    take_screenshot_of_webpage(url, image_path)

    img = cv2.imread(image_path)

    img = crop_the_screenshot(img)
    cropped_img_path = os.path.join(path.TEMP_DIR, f"screenshot_cropped.png")
    cv2.imwrite(cropped_img_path, img)

    img = add_padding_to_image(img)
    padded_img_path = os.path.join(path.TEMP_DIR, f"screenshot_padded.png")
    cv2.imwrite(str(padded_img_path), img)
    
    COMPANY_LOGO_MATCH, BANK_LOGO_MATCH = validate_chargeslip_image_logos(cropped_img_path, bank, company, visualize=visualize)
    
    # The following if else condition may be rewritten again with a better logic

    # assuming here is both logos are to expected
    if COMPANY_LOGO_MATCH and BANK_LOGO_MATCH:
        print("Both Company and Bank logo matches!")
    
    # if the above condition fails
    elif COMPANY_LOGO_MATCH or BANK_LOGO_MATCH:

        # checking if both bank and company logos are expected, if so they will be of boolean type
        if isinstance(BANK_LOGO_MATCH, bool) and isinstance(COMPANY_LOGO_MATCH, bool):
            print(f"Partial Match! {'Company logo' if COMPANY_LOGO_MATCH is not True else 'Bank logo' if BANK_LOGO_MATCH is not True else 'Something'} does not match")
        # checking if anyone of them is none
        elif bank is None and isinstance(COMPANY_LOGO_MATCH, bool):
            print(f"Only Company logo is expected and It is {'' if COMPANY_LOGO_MATCH is True else 'not'} matching")
        elif company is None and isinstance(BANK_LOGO_MATCH, bool):
            print(f"Only Bank logo is expected and It is {'' if BANK_LOGO_MATCH is True else 'not'} matching")
        else:
            raise Exception("Unknown Error: [it seems both of them are None] CHECK screenshot_processor.py line no. 469")
        
    else:
        print("No Match!")

    return COMPANY_LOGO_MATCH, BANK_LOGO_MATCH




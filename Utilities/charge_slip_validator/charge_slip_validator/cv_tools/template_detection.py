import cv2
import matplotlib.pyplot as plt
import numpy as np
import imutils

from .. import errors


def cv2_show(img):
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



def detect_template_and_get_coordinates(img_path, template_img_path, threshold=0.8, visualize=False, color= (0, 255, 255), verbose=False):
    img = cv2.imread(img_path)
    # convert this image as grayscale to do match templating
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # read as gray scale since template image is not used anymore afterwards
    template_img = cv2.imread(template_img_path, cv2.IMREAD_GRAYSCALE)
    template_height, template_width = template_img.shape

    found = None
    number_of_scales = 20

    for scale_percentage in np.linspace(1.0, 0.2, number_of_scales):
        width = int(grey_img.shape[1] * scale_percentage)  # if width only is provided it will keep aspect ratio
        
        resized = imutils.resize(grey_img, width)
        ratio = grey_img.shape[1] / float(resized.shape[1])
        # print('ratio:', ratio, "| width:", width)

        # if the resized image is smaller than the template, then break from the loop
        if resized.shape[0] < template_height or resized.shape[1] < template_width:
            break

        # detect edges in the resized, grayscale image and apply template
        # matching to find the template in the image
        edged = resized.copy()  #cv2.Canny(resized, 50, 200)  # edge detection is not working. so disabled
        result = cv2.matchTemplate(edged, template_img, cv2.TM_CCOEFF_NORMED)
        (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(result)  # min loc is good for cv2.TM_SQDIFF or similar ..
        
        # check to see if the iteration should be visualized
        if visualize is True:
            # draw a bounding box around the detected region
            clone = np.dstack([edged, edged, edged])
            cv2.rectangle(clone, (max_loc[0], max_loc[1]),
                (max_loc[0] + template_width, max_loc[1] + template_height), (0, 255, 255), 2)
            cv2_show(clone)
            del clone

        # if we have found a new maximum correlation value, then update
        # the bookkeeping variable
        if found is None or max_val > found[0]:
            found = (max_val, max_loc, ratio)
            if verbose is True:
                print('ratio:', ratio, "| width:", width)
                print(found)


    if found is None:
        raise errors.opencv.TemplateNotDetectedError(f'No matching locations for the template image.')

    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (max_val, max_loc, ratio) = found

    if max_val < threshold:
        raise errors.opencv.TemplateNotDetectedError(f"Matching locations found but they were of below threshold")
    
    (start_x, start_y) = (int(max_loc[0] * ratio), int(max_loc[1] * ratio))
    (end_x, end_y) = (int((max_loc[0] + template_width) * ratio), int((max_loc[1] + template_height) * ratio))

    found_top_left_loc = start_x, start_y
    found_bottom_right_loc = end_x, end_y
    
    if visualize is True:
        # draw a bounding box around the detected result and display the image
        cv2.rectangle(img, found_top_left_loc, found_bottom_right_loc, color, 2)

        cv2_show(img)
    
    return found_top_left_loc, found_bottom_right_loc



# SIMPLE DETECTOR =======> Incase if we want a backup
'''
import cv2
import numpy as np
import imutils


class TemplateNotDetectedError(Exception):
    pass


# params
threshold = 0.7


img = cv2.imread(img_path)

# convert this image as grayscale to do match templating
grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# read as gray scale since template image is not used anymore afterwards
template_img = cv2.imread(template_img_path, cv2.IMREAD_GRAYSCALE)
# grey_img = cv2.Canny(grey_img, 50, 200)

result = cv2.matchTemplate(grey_img, template_img, cv2.TM_CCOEFF_NORMED)  # last param can be changed

template_height, template_width = template_img.shape
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

if max_val < threshold:
    raise TemplateNotDetectedError(f'No matching locations while considering the threshold value {threshold}.')

top_left_loc = max_loc
bottom_right_loc = (max_loc[0] + template_width), (max_loc[1] + template_height)

color = (0, 255, 255)
outline_width = 2
cv2.rectangle(img, top_left_loc, bottom_right_loc, color, outline_width)

cv2.imshow("Location Drawn Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()


'''


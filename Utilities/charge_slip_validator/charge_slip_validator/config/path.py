import os


# DIRECTORY LOCATIONS
MAIN_DIR = os.path.dirname(os.path.dirname(__file__))
# CONFIG_DIR = os.path.join(MAIN_DIR, 'config')

ASSETS_DIR = os.path.join(MAIN_DIR, 'assets')
CONFIGURATION_YAML_FILE_PATH = os.path.join(ASSETS_DIR, 'configuration.yaml')

MEDIA_DIR = os.path.join(ASSETS_DIR, 'media')
if not os.path.isdir(MEDIA_DIR):
    os.mkdir(MEDIA_DIR)

LOGOS_DIR = os.path.join(MEDIA_DIR, "logos")
if not os.path.isdir(LOGOS_DIR):
    os.mkdir(LOGOS_DIR)

EZETAP_LOGO_PATH = os.path.join(LOGOS_DIR, 'ezetap.png')
BANK_LOGOS_DIR = os.path.join(LOGOS_DIR, 'banks')

SCREENSHOTS_DIR = os.path.join(MEDIA_DIR, 'screenshots')
if not os.path.isdir(SCREENSHOTS_DIR):
    os.mkdir(SCREENSHOTS_DIR)

ORIGINAL_SCREENSHOTS_DIR = os.path.join(SCREENSHOTS_DIR, 'original')
CROPPED_SCREENSHOTS_DIR = os.path.join(SCREENSHOTS_DIR, 'cropped')
PADDED_SCREENSHOTS_DIR = os.path.join(SCREENSHOTS_DIR, 'padded')

MANUAL_REFERECES_DIR = os.path.join(LOGOS_DIR, 'manual_references')
IDEAL_REFERECES_DIR = os.path.join(LOGOS_DIR, 'ideal_references')

TEMP_DIR = os.path.join(MAIN_DIR, '.TEMP')
if not os.path.isdir(TEMP_DIR):
    os.mkdir(TEMP_DIR)

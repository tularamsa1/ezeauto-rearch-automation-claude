from . import path, utilities

reset_yaml_text = '''
EZETAP_LOGO_THRESHOLD: 0.39
BANK_LOGO_THRESHOLD: 0.8
BROWSER_HEADLESS_MODE: true
BROWSER_WIDTH: 400
BROWSER_HEIGHT: 500
REFERENCE_URLS:
  ezetap: http://demo1.ezetap.com/r/o/xdJxBfiz/
  hdfc: http://demo1.ezetap.com/r/o/xdJxBfiz/
LOGOS:
  EZETAP_LOGO_PATH: null
  HDFC_LOGO_PATH: null
  AXIS_LOGO_PATH: null
  ICICI_LOGO_PATH: null
LOWER_SECTION_LOGOS:
- ezetap
- fiserv.ezetap
'''

def reset_configuration():
    '''This is used in case of error due to yaml configuration file corruption'''
    global reset_yaml_text
    with open(path.CONFIGURATION_YAML_FILE_PATH, 'w') as f:
        f.write(reset_yaml_text)
    print("Resetting configuration file is successful.\nHere is the configuration text")
    print(reset_yaml_text)

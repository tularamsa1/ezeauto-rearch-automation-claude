import os
from subprocess import Popen, PIPE

from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


'''To undestand why use of Popen and proc.communicate() in the current scenario of netcat commands,
please see https://stackoverflow.com/questions/22250893/capture-segmentation-\
fault-message-for-a-crashed-subprocess-no-out-and-err-af/22253472#22253472
'''
def run_shell_command_n_get_output_in_list_of_lines(cmd):
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    out_lines = [] if err else out.decode().strip().splitlines()
    if err: 
        logger.critical(f'The command execution for "{cmd}" returns error code: {err}')
    return out_lines


def get_adb_devices():  # adb_device_id looks like 'emulator-5556'
    logger.debug("Getting all running ADB devices")
    cmd = f'''adb devices'''
    out_lines = run_shell_command_n_get_output_in_list_of_lines(cmd)
    adb_devices = [line.rstrip('\tdevice').strip() for line in out_lines if line.endswith('\tdevice')]
    logger.debug(f"Found {len(adb_devices)} ADB devices. They are {', '.join(adb_devices)}")
    return adb_devices


def get_avd_name_from_adb_device_id(adb_device_id):
    port_number = adb_device_id.split('-')[-1]  # eg: emulator-5556
    cmd = f'''echo "avd name" | nc -w 1 localhost {port_number}'''

    out_lines = run_shell_command_n_get_output_in_list_of_lines(cmd)
    avd_name = out_lines[-2] if (out_lines[-1] == "OK") and (out_lines[-3] == "OK") else None
    return avd_name


def get_adb_devices_n_corresponding_avd_names() -> dict:
    """returns something like this '{'emulator-5556': 'Nexus_6_API_31'}'"""
    logger.debug("Getting ADB devices and their corresponding AVD names by netcating into ADB devices")
    emulators = [adb_device for adb_device in get_adb_devices() if adb_device.startswith('emulator')] # to avoid devices other than emulators
    adb_devices_to_avd_name_map = {adb_device_id: get_avd_name_from_adb_device_id(adb_device_id) for adb_device_id in emulators}
    logger.info(f"ADB devices and their AVD names: {adb_devices_to_avd_name_map}")
    
    for adb_device_id in adb_devices_to_avd_name_map:
        if adb_devices_to_avd_name_map[adb_device_id] is None:
            # logger.error(f"AVD name for ADB device id '{adb_device_id}' is None. Please debug the issue!")
            raise Exception(f"AVD name for ADB device id '{adb_device_id}' is None. Please debug the issue!")
            # this might not be good for later purposes. Deal this later
    
    return adb_devices_to_avd_name_map


def get_emulator_bin_path():  # this can be set as global constant as well
    sdk_dir = os.getenv('ANDROID_HOME')
    emulator_dir = os.path.join(sdk_dir, 'emulator')
    emulator_path = os.path.join(emulator_dir, 'emulator')
    return emulator_path


def get_list_avds():
    """"returns a list like this: ['Nexus_6_API_31', ]"""
    logger.debug("Finding list of all AVD devices [running or not running]")
    emulator_bin_path = get_emulator_bin_path()
    cmd = f'''{emulator_bin_path} -list-avds'''
    list_avds = run_shell_command_n_get_output_in_list_of_lines(cmd)
    logger.debug(f"Found {len(list_avds)} AVDs. They are {', '.join(list_avds)}")
    return list_avds


def get_the_list_of_currently_not_started_avds():
    try:
        mapping = get_adb_devices_n_corresponding_avd_names()
        currently_not_started_avds = [avd_name for avd_name in get_list_avds() if avd_name not in mapping.values()]
        logger.info(f"Found {len(currently_not_started_avds)} currently-not-running devices. They are {', '.join(currently_not_started_avds)}")
    except Exception as e:
        logger.error(f"{e}")
        currently_not_started_avds = []   # this might not be a good idea
        logger.warning("Therefore emptying 'currently_not_started_avds' list [CAUTION]")

    return currently_not_started_avds


def start_emulator(avd_name):
    logger.info(f"Starting emulator with AVD name: {avd_name}")
    cmd = f"{get_emulator_bin_path()} -avd {avd_name} &"
    logger.debug(f"Running the command in shell: '{cmd}'")
    return os.system(cmd)



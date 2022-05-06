import logging

def log():
    logging.basicConfig(filename="\\Logfile.log",
    format='%(asctime)s: %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
    logger=logging.getLogger()
    return logger
logger=log()
logger.info("This is new log")
logger.error("This is error log")
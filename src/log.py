import logging

logger = logging.getLogger()
# Set the output standard of the log
logger.setLevel(logging.INFO)
# log output format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# log output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

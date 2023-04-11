import logging
import os

from .constants import BASE_DIRECTORY

log_file_path = os.path.join(BASE_DIRECTORY, "std.log")
logging.basicConfig(filename=log_file_path, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

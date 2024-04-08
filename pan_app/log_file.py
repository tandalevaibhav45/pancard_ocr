import logging
import os
from pan_car.settings import BASE_DIR


# Creating logger file and folder
folder_path = os.path.join(BASE_DIR,'pan_app','log')
log_file_path = os.path.join(folder_path,'pan_logger_file.log')

if not os.path.exists(folder_path):
    os.makedirs(folder_path,exist_ok=True)

if not os.path.exists(log_file_path):
    with open(log_file_path,'w'):
        pass

logger3 = logging.getLogger('log_file3')

file_handler = logging.FileHandler(log_file_path,mode='a')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s: An error occured: %(message)s in funtion %(funcName)s in module %(module)s')
file_handler.setFormatter(formatter)

logger3.addHandler(file_handler)
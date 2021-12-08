#!python

# This script is used to rename mp4 files by adding the datetime-hour-minute
# to the filename. This is necessary because some camera manufacturers
# do not add a timestamp and simply name files in sequence (001, 002, ...)
# so you can end up with multiple identically named files when the sequence restarts

import os
from datetime import datetime as dt
import re
import logging

def rename_mp4_timestamp(dir):

    for root, dirs, files in os.walk(dir):     
        for name in files:
            logging.info(f'processing {name}')
            full_name = os.path.abspath(root + os.sep + name)
            file = full_name[:-4]
            file_type = full_name[-4:].lower()

            if file_type.lower() == '.mp4':        
                mtime = os.path.getmtime(full_name)
                suffix = dt.fromtimestamp(mtime).strftime('_%Y%m%d_%H%M')
                
                if not bool(re.match("(^[0-9]{8})([_])([0-9]{4}$)",file[-13:])):
                    new_name = file + suffix + file_type 
                    logging.info(new_name)
                    # os.rename(full_name, new_name)
                    
                else:
                    logging.info(f'already renamed as {name}')
            else:
                logging.info(f'{name} is not an mp4')

if __name__ == '__main__':
    logging.basicConfig(
        # filename='hdo_upload.log',
        encoding='utf-8',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    dir = 'project/temp/downloads'
    rename_mp4_timestamp(dir)

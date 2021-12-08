#!python

# This module is used to create and remove a lock file
# typically used to ensure cron does not launch an already-running script

import os
import logging

def lock_file_exists(filename):
    if os.path.exists(filename):
        logging.warning('lock file exists, indicating script is alredy running')
        return True
    else:
        logging.info('lock file does not exit, proceeding...') 
        return False

def make_lock_file(filename, infotext):
    f = open(filename,'w')
    f.write(infotext)
    f.close()
    logging.info(f'created lock file: {filename}')

def release_lock_file(filename):
    try:
        os.remove(filename)
    except Exception as ex:
        logging.error(ex)
    logging.info(f'removed lock file: {filename}')
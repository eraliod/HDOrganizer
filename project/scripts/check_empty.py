#!python

import os
import shutil
import logging
from hdo_import import hdo_import_file

src = 'project/temp/downloads'
dest = 'project/temp/hd_videos'

# Normalize source and destination pathc
src = os.path.abspath(src)
dest = os.path.abspath(dest)

bucket = 'hdorganizer'

def empty_check(src):    
    empty = False

    if not os.listdir(src):
        logging.info('Source directory is empty... Terminating')
        empty = True
    else:
        logging.info('contents in the source: '+ ', '.join(os.listdir(src)))
    
    return empty

def process4kfiles(src, dest):
    # Seek files in the source directory and process them individually
    for root, dirs, files in os.walk(src):
        for name in files:
            
            # Set the file name being processed
            f = os.path.join(root, name)
            
            # Determine if the file is a 4K (mp4) video
            if name.lower().endswith('.mp4'):
                # Try to send 4K videos through the HDO app
                try:
                    logging.info(f'Uploading to S3: {f.removeprefix(src)}')
                    hdo_import_file(name, root, bucket)
                except:
                    logging.warning(f'There was an error sending the file to S3, skipping {f}')
                    continue #continue will push to the next file in the loop
            
            # Check if the destination directory exists
            dir_dest = dest + os.sep + root.lstrip(src)
            if not os.path.exists(dir_dest):
                os.makedirs(dir_dest)
            
            # Set the destination path for this file
            f_dest = dest + os.sep + f.lstrip(src)
            
            # Move the file to its new location
            logging.info(f'Moving {f.removeprefix(src)}')
            shutil.move(f, f_dest)
    
    # Seek directories in the source folder and process them individually, bottom-up
    for root, dirs, files in os.walk(src, topdown=False):
        
        # Do not delete the source directory
        if root == src:
            break
        
        # Delete directories that are empty
        if not os.listdir(root):
            try:
                os.rmdir(root)
                logging.info(f'deleting empty directory: {root}')
            except OSError as ex:
                logging.error(ex)
        else:
            logging.warning('contents in directory: ' + ' ,'.join(os.listdir(root)))

def main():
    logging.basicConfig(
        # filename='check_empty.log',
        encoding='utf-8',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('----- BEGIN PROCESS -----')
    if not empty_check(src):
        process4kfiles(src, dest)
    logging.info('----- END PROCESS -----')

if __name__ == '__main__':
    main()

# TODO - remove empty directories
# TODO - logging and errors
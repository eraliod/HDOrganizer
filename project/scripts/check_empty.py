#!python

import os
import shutil

src = 'project/temp/downloads'
dest = 'project/temp/hd_videos'

# Normalize source and destination pathc
src = os.path.abspath(src)
dest = os.path.abspath(dest)
print(src)
print(dest)

# Check if source is empty
print(os.listdir(src))

if not os.listdir(src):
    print('Source directory is empty')
else:
    pass
# print(list(os.walk(src))[2:3])

# exit()
# Seek files in the source directory
for root, dirs, files in os.walk(src):
    for name in files:
        # State the file name being processed
        f = os.path.join(root, name)
        print(f)
        # Determine if the file is a 4K (mp4) video
        if name.lower().endswith('.mp4'):
            # Try to send 4K videos through the HDO app
            try:
                print(f'This file would get sent to S3: {f}')
            except:
                print(f'There was an error sending the file to S3, skipping {f}')
                continue #continue will push to the next file in the loop
        # Check if the destination directory exists
        dir_dest = dest + os.sep + root.lstrip(src)
        if not os.path.exists(dir_dest):
            os.makedirs(dir_dest)
        # Set the destination path for this file
        f_dest = dest + os.sep + f.lstrip(src)
        # Move the file to its new location
        shutil.move(f, f_dest)

# TODO - remove empty directories
# TODO - logging and errors
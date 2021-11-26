#!/usr/bin/env bash

inotifywait -mq -r -e create -e modify -e delete -e move /data/hd_videos |
    while read path action file; do
        echo "The file '$file' appeared in directory '$path' via '$action'" >> log.txt
    done
#!/bin/bash
# https://askubuntu.com/questions/610903/how-can-i-create-a-video-file-from-a-set-of-jpg-images

ffmpeg -framerate 25 -pattern_type glob -i 'world_day*_step*.png' -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p output_$1.mp4

# testmedia

This repository contains various scripts to generate test media.

## Requirements

* OSX - The scripts use "say" on OSX to generate synthesised speach.
* ffmpeg - has been tested with ffmpeg 3.2.4. YMMV
* python 2.7

## generate_multichannel_video.py

This script generates an mp4 video at 25 fps with a rolling timecode
starting at 00:00:00:00 with a user-specified number of stereo
tracks. The video will flash white every second except every 5 seconds
where it flashes red. Each audio track will give a beep at 1kHz every
second, except every even 5 seconds where it gives a beep at 2kHz
instead. Each channel is identified by a voice saying "track NUMBER,
right/left

The purpose of this video is to test accuracy between video and audio
and to test accuracy betwen different audio tracks when playing more
than one at a time.
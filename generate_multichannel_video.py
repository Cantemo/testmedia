#! /usr/bin/python

from __future__ import print_function

import argparse
import subprocess
import os

# Video generation functions

def gen_1_sec_color_video(color):
    "Generates a 1 second long video with all black frames, except for the last which is of the specified color"

    cmd = ["ffmpeg", "-y"]

    filter_complex = ""

    filter_complex += "color=c={color}:s=640x480:r=25:d=1[color]; ".format(color=color)
    filter_complex += "color=c=black:s=640x480:r=25:d=10[black]; "
    filter_complex += "[color]trim=start_frame=0:end_frame=1[color_1f] ;"
    filter_complex += "[black]trim=start_frame=0:end_frame=24[black_24f] ;"
    filter_complex += "[black_24f][color_1f]concat=n=2:v=1:a=0[out]"

    cmd.extend(["-filter_complex", filter_complex])

    cmd.extend(["-map", "[out]"])

    cmd.append("tmp/1sec_{color}.ts".format(color=color))

    subprocess.call(cmd)

def gen_video(duration):
    output_fn = "tmp/video.mp4"

    "Generates a video of the specified duration, with a white flashing frame every second except for every 5th second which flashes red"
    with open("tmp/concat.txt", "w") as f:
        for nr in range(0, duration*60/5):
            for i in range(0, 4): # 4 seconds of white
                print("file '{fn}'".format(fn="1sec_white.ts"), file=f)
            print("file '{fn}'".format(fn="1sec_red.ts"), file=f) # 1 second of red

    cmd = ["ffmpeg", "-y"]
    cmd.extend(["-f", "concat"])
    cmd.extend(["-i", "tmp/concat.txt"])

    # Add timecode
    filter_complex = "[0:v] drawtext=fontfile=font/RobotoMono-Medium.ttf:timecode=00\\\:00\\\:00\\\:00:r=25:x=(w-tw)/2:y=h-(2*lh):box=1:boxcolor=0xffffff:boxborderw=5:fontcolor=black:fontsize=16 [out]"

    cmd.extend(["-filter_complex", filter_complex])

    cmd.extend(["-map", "[out]"])
    cmd.append(output_fn)

    subprocess.call(cmd)

    return output_fn

# Audio generation functions

def gen_5sec_audio(track, channel):
    """Generates a 5 second audio loop in 5sec.aiff"""

    track_filename = "tmp/track{nr}{channel}.aiff".format(nr=track, channel=channel)

    cmd = ["ffmpeg"]
    cmd.append("-y")
    cmd.append("-i")
    cmd.append("tmp/low_beep.aiff")
    cmd.append("-i")
    cmd.append("tmp/low_beep.aiff")
    cmd.append("-i")
    cmd.append("tmp/low_beep.aiff")
    cmd.append("-i")
    cmd.append("tmp/low_beep.aiff")
    cmd.append("-i")
    cmd.append("tmp/high_beep.aiff")
    cmd.append("-i")
    cmd.append(track_filename)

    cmd.append("-filter_complex")


    filterstr = """
    [0]adelay=960[0out];
    [1]adelay=1960[1out];
    [2]adelay=2960[2out];
    [3]adelay=3960[3out];
    [4]adelay=4960[4out];
    [5]adelay=300[5out];
    [0out][1out][2out][3out][4out][5out]amix=inputs=6[out]
    """

    cmd.append(filterstr)
    cmd.append("-map")
    cmd.append("[out]")
    cmd.append("tmp/5sec_track{nr}{channel}.aiff".format(nr=track, channel=channel))
    subprocess.call(cmd)


def gen_audio_channel(track, channel, duration):
    """Generates an audio track of a specified duration for a track and channel"""
    filename_5sec = "tmp/5sec_track{nr}{channel}.aiff".format(nr=track, channel=channel)

    repeats = duration*60/5

    # Create a file concat.txt which repeats filename_5sec enough times for the given duration
    with open("tmp/concat.txt", "w") as f:
        for i in range(0, repeats):
            print("file '{fn}'".format(fn=os.path.basename(filename_5sec)), file=f)

    cmd = ["ffmpeg", "-y"]

    # cmd.extend(["-i", filename_5sec])
    cmd.extend(["-f", "concat"])
    cmd.extend(["-i", "tmp/concat.txt"])

    filter_complex = ""
    outputs = ""

    # For each minute, create a filter with a nullsrc which is 1 min
    # long and the correct minute read-out, shifted to 57 seconds. Then mix these together into [{nr}out]
    for nr in range(1, duration+1):
        cmd.extend(["-i", "tmp/{nr}min.aiff".format(nr=nr)])
        # delay is in ms so it should be 1000*60*(nr-1)+57*1000 for a nice round number

        # add a null src of 1 min duration
        filter_complex += "aevalsrc=0:d=60[{nr}null];".format(nr=nr)
        filter_complex += "[{nr}]adelay={delay}[{nr}delay];".format(nr=nr, delay=57*1000)
        filter_complex += "[{nr}delay][{nr}null]amix=inputs=2[{nr}out];".format(nr=nr)
        outputs += "[{nr}out]".format(nr=nr)

    # Concatinate all the individual minutes into one output
    filter_complex += "{outputs}concat=n={nroutputs}:v=0:a=1[minutes];".format(outputs=outputs, nroutputs=duration)

    # Mix together the second beeps with the minute readouts
    filter_complex += "[0][minutes]amix=inputs=2[out]".format(outputs=outputs, nrinputs=duration+1)

    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(["-map", "[out]"])
    cmd.append("tmp/track{nr}{channel}.mp4".format(nr=track, channel=channel))

    subprocess.call(cmd)

#    print("\n   ".join(cmd))

def gen_stereo_track(track):

    output_fn = "tmp/track{nr}.mp4".format(nr=track)

    cmd = ["ffmpeg", "-y"]

    cmd.extend(["-i", "tmp/track{nr}left.mp4".format(nr=track)])
    cmd.extend(["-i", "tmp/track{nr}right.mp4".format(nr=track)])

    filter_complex = """
    [0:a][1:a]amerge=inputs=2[out]
    """

    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(["-map", "[out]"])
    cmd.append(output_fn)

    subprocess.call(cmd)

    return output_fn

def gen_audio_track(track, duration):

    gen_5sec_audio(track, "left")
    gen_5sec_audio(track, "right")

    gen_audio_channel(track=track, channel="left", duration=duration)
    gen_audio_channel(track=track, channel="right", duration=duration)

    return gen_stereo_track(track=track)

def say(filename, text):
    """This uses the say command of OSX to output an aiff file with spoken text"""
    if not os.path.exists("{filename}.aiff".format(filename=filename)):
        os.system("say -o {filename} -v Alex {text}".format(
            filename=filename,
            text=text
        ))

def gen_say_fragments(tracks, duration):
    say("tmp/1min", "1 minute")

    for nr in range(2,duration+1):
        say("tmp/{nr}min".format(nr=nr), "{nr} minutes".format(nr=nr))

    for nr in range(1,tracks+1):
        say("tmp/track{nr}right".format(nr=nr), "Track {nr} right".format(nr=nr))
        say("tmp/track{nr}left".format(nr=nr), "Track {nr} left".format(nr=nr))



def gen_beeps():
    "Generate two beeps to distinguish 1 and and 5 second marks"
    os.system('ffmpeg -y -f lavfi -i "sine=frequency=1000:sample_rate=48000:duration=0.04" tmp/low_beep.aiff')
    os.system('ffmpeg -y -f lavfi -i "sine=frequency=2000:sample_rate=48000:duration=0.04" tmp/high_beep.aiff')


def gen_audio_tracks(number, duration):
    gen_say_fragments(number, duration)
    gen_beeps()

    files = []

    for i in range(1, number+1):
        files.append(gen_audio_track(i, duration))

    return files

def mux_file(files):
    cmd = ["ffmpeg", "-y"]

    for i, f in enumerate(files):
        cmd.extend(["-i", f])

    for i, f in enumerate(files):
        cmd.extend(["-map", "{nr}:0.{nr}".format(nr=i)])

    cmd.extend(["-acodec", "copy"])
    cmd.extend(["-vcodec", "copy"])

    cmd.append("out.mp4")

    print(cmd)

    subprocess.call(cmd)
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generates a video with a specified number of audio tracks')
    parser.add_argument('tracks', type=int, help='Number of tracks')
    parser.add_argument('duration', type=int, help='The duration in minutes')

    args = parser.parse_args()


    try:
        os.mkdir("tmp")
    except OSError:
        # Dir already exists
        pass


    

    # Create the individual 1 second long clips
    gen_1_sec_color_video("red")
    gen_1_sec_color_video("white")

    vid_fn = gen_video(args.duration)

    files = [vid_fn]

    files.extend(gen_audio_tracks(args.tracks, args.duration))

    mux_file(files)

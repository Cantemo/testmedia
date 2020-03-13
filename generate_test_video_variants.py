import subprocess
import glob
import os

VOICE="Daniel"
#DATA_FORMAT=aac@48000
# Big-Endian signed 16bit 48KHz
DATA_FORMAT="BEI16@48000"

EXT="aiff"

MAX_TRACKS=8
MAX_CHANNELS=8

def run(cmd, force=False):
    if not force and os.path.exists(cmd[-1]):
        return

    print(f"Running: {cmd}" )
    subprocess.run(cmd, check=True)
    


def gen_voices(track_num):
    cmd = ["say", "-v", VOICE, "--data-format", DATA_FORMAT, f"Track {track_num}", "-o", f"voice_{track_num}.{EXT}"]
    run(cmd)
    
    cmd = ["say", "-v",  VOICE, "--data-format", DATA_FORMAT, f"Track {track_num}. Mono.", "-o", f"voice_{track_num}_mono.{EXT}"]
    run(cmd)

    for ch in range(1, MAX_CHANNELS+1):
        cmd = ["say", "-v", VOICE, "--data-format", DATA_FORMAT, f"Track {track_num}. Channel {ch}.", "-o", f"voice_{track_num}_ch{ch}.{EXT}"]
        run(cmd)

    for side in ["left", "right"]:
        side_titled=side.title()
        cmd = ["say", "-v", VOICE, "--data-format", DATA_FORMAT, f"Track {track_num}. Stereo. {side_titled}.", "-o", f"voice_{track_num}_stereo_{side}.{EXT}"]
        run(cmd)


def gen_long_tracks(track_num):

    for layout in ["mono", "stereo_left", "stereo_right"] + [f"ch{x}" for x in range(1, MAX_CHANNELS+1)]:
        fn = f"voice_{track_num}_{layout}.{EXT}"

        fn_10s=f"10s_track_{track_num}_{layout}.{EXT}"
        fn_60s=f"60s_track_{track_num}_{layout}.{EXT}"

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=48000:cl=mono",
            "-i", fn,
            "-f", "lavfi",
            "-i", "anullsrc=r=48000:cl=mono",
            "-filter_complex",
            '[0]atrim=end=1[lead]; [2]atrim=end=10[trail]; [lead] [1] [trail] concat=n=3:v=0:a=1 [concated]; [concated]atrim=end=10[out]',
            "-map", '[out]',
            fn_10s
        ]

        run(cmd)

        # generate 60s long files
        with open("list.txt", 'w') as f:
            for i in range(6):
                f.write(f"file '{fn_10s}'\n")

        cmd = ["ffmpeg", "-y", "-f", "concat", "-i", "list.txt", "-acodec", "copy", fn_60s]
        run(cmd)


def gen_audio_tracks(track_num):
    # Now combine the individual files into differnt combinations
    # Mono
    cmd = [
        "ffmpeg",
        "-y",
        "-i", f"60s_track_{track_num}_mono.{EXT}",
        "-channel_layout", "mono",
        f"60s_track_{track_num}_mono.mov"
    ]
    run(cmd)

    # Stereo
    cmd = [
        "ffmpeg",
        "-y",
        "-i", f"60s_track_{track_num}_stereo_left.{EXT}",
        "-i", f"60s_track_{track_num}_stereo_right.{EXT}",
        "-filter_complex", "[0:a][1:a]join=inputs=2:channel_layout=stereo[a]",
        "-map", "[a]",
        "-channel_layout", "stereo",
        f"60s_track_{track_num}_stereo.mov"
    ]
    run(cmd)
    
    # Quad
    cmd = [
        "ffmpeg", "-y",
        "-i", f"60s_track_{track_num}_ch1.{EXT}",
        "-i", f"60s_track_{track_num}_ch2.{EXT}",
        "-i", f"60s_track_{track_num}_ch3.{EXT}",
        "-i", f"60s_track_{track_num}_ch4.{EXT}",
        "-filter_complex", "[0:a][1:a][2:a][3:a]join=inputs=4:channel_layout=quad[a]",
        "-map", "[a]",
        f"60s_track_{track_num}_quad.mov"
    ]
    run(cmd)

    # 5.1
    cmd = [
        "ffmpeg", "-y",
        "-i", f"60s_track_{track_num}_ch1.{EXT}",
        "-i", f"60s_track_{track_num}_ch2.{EXT}",
        "-i", f"60s_track_{track_num}_ch3.{EXT}",
        "-i", f"60s_track_{track_num}_ch4.{EXT}",
        "-i", f"60s_track_{track_num}_ch5.{EXT}",
        "-i", f"60s_track_{track_num}_ch6.{EXT}",
        "-filter_complex", "[0:a][1:a][2:a][3:a][4:a][5:a]join=inputs=6:channel_layout=5.1[a]",
        "-map", "[a]",
        f"60s_track_{track_num}_5.1.mov"
    ]
    run(cmd)

    # 7.1
    cmd = [
        "ffmpeg", "-y",
        "-i", f"60s_track_{track_num}_ch1.{EXT}",
        "-i", f"60s_track_{track_num}_ch2.{EXT}",
        "-i", f"60s_track_{track_num}_ch3.{EXT}",
        "-i", f"60s_track_{track_num}_ch4.{EXT}",
        "-i", f"60s_track_{track_num}_ch5.{EXT}",
        "-i", f"60s_track_{track_num}_ch6.{EXT}",
        "-i", f"60s_track_{track_num}_ch7.{EXT}",
        "-i", f"60s_track_{track_num}_ch8.{EXT}",
        "-filter_complex", "[0:a][1:a][2:a][3:a][4:a][5:a][6:a][7:a]join=inputs=8:channel_layout=7.1[a]",
        "-map", "[a]",
        f"60s_track_{track_num}_7.1.mov"
    ]
    run(cmd)

    # octagonal
    cmd = [
        "ffmpeg", "-y",
           "-i", f"60s_track_{track_num}_ch1.{EXT}", \
           "-i", f"60s_track_{track_num}_ch2.{EXT}", \
           "-i", f"60s_track_{track_num}_ch3.{EXT}", \
           "-i", f"60s_track_{track_num}_ch4.{EXT}", \
           "-i", f"60s_track_{track_num}_ch5.{EXT}", \
           "-i", f"60s_track_{track_num}_ch6.{EXT}", \
           "-i", f"60s_track_{track_num}_ch7.{EXT}", \
           "-i", f"60s_track_{track_num}_ch8.{EXT}", \
        "-filter_complex", "[0:a][1:a][2:a][3:a][4:a][5:a][6:a][7:a]join=inputs=8:channel_layout=octagonal[a]",
        "-map", "[a]",
        f"60s_track_{track_num}_octagonal.mov"
    ]
    run(cmd)


def gen_video(audios, frame_rate, df=False):

    text = "Video: {frame_rate} fps {df}\n".format(
        frame_rate=frame_rate,
        df="DF" if df else "NDF"
    )

    output_fn = f"output/test_video_{frame_rate}"
    
    if df:
        timecode=r'00\\:00\\:00\\\;00'
        output_fn += "_df"
    else:
        timecode=r'00\\:00\\:00\\:00'
        output_fn += "_ndf"

    for i, audio in enumerate(audios):
        track_num = i + 1
        text += f"Track {track_num} {audio}\n"

    output_fn += f"_{len(audios)}tr"
        
    if len(set(audios)) == 1:
        output_fn += f"_{audio}"
    else:
        output_fn += f"_mixed"
        for i, audio in enumerate(audios):
            track_num = i + 1
            output_fn += f"_tr{track_num}_{audio}"

    output_fn += ".mov"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"testsrc=duration=60:size=hd720:rate={frame_rate}:decimals=2",
    ]

    for audio in audios:
        cmd += [
            "-i", f"60s_track_{track_num}_{audio}.mov"
        ]
    
    cmd += [
        "-filter_complex", f'[0]drawtext=text={text}:fontcolor=black:box=1:boxcolor=0x000000:boxborderw=5:fontcolor=white:fontsize=32:x=0:y=0,drawtext=timecode={timecode}:fontcolor=white:rate={frame_rate}:x=(w-tw)/2:y=(2*lh):box=1:boxcolor=0xffffff:boxborderw=5:fontcolor=black:fontsize=100[vout]',
        "-pix_fmt", "yuv420p",
        "-t", "60",
        "-r", frame_rate,
        '-map', '[vout]'
    ]

    for i in range(1, len(audios)+1):
        cmd += ["-map", f'{i}:a']

    cmd += [output_fn]

    run(cmd)


def gen_videos_by_framerate(frame_rate, df=False):
    

    gen_video(["mono"], frame_rate, df)
    gen_video(["stereo"], frame_rate, df)
    gen_video(["quad"], frame_rate, df)
        
    gen_video(["mono"]*4, frame_rate, df)
    gen_video(["stereo"]*4, frame_rate, df)
    gen_video(["stereo"]*8, frame_rate, df)
    gen_video(["mono", "stereo"], frame_rate, df)
    gen_video(["stereo", "mono", "5.1"], frame_rate, df)


def main():
    
    # This script generates a set of audio files for test purposes
    for track_num in range(1, MAX_TRACKS+1):
        gen_voices(track_num)
        gen_long_tracks(track_num)
        gen_audio_tracks(track_num)

    for frame_rate in ["23.98", "24", "25", "29.97", "30", "50", "59.94", "60", "120"]:
        gen_videos_by_framerate(frame_rate)

        if frame_rate in ["29.97", "59.94"]:
            gen_videos_by_framerate(frame_rate, True)
        
if __name__ == '__main__':
    main()
    

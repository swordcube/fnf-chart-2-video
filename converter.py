# imports
import os
import json

import numpy as np
from PIL import Image

from moviepy import VideoClip, AudioFileClip, CompositeAudioClip
import game.game as game

is_verbose_raw = False
is_verbose = False

force_song_name = "comacopian"
force_song_mix = "default"
force_difficulty = "hard"

last_total_time = 0.0

if __name__ == "__main__":
    # lil note on startup
    print("swordcube fnf -> mp4 converter\nplease note that this only supports garfie baby charts!\n")

    # basic config
    song_name = force_song_name if len(force_song_name) > 0 else input("Song: ").strip()
    song_mix = force_song_mix if len(force_song_mix) > 0 else input("Mix/Variant (optional): ").strip()

    if len(song_mix) == 0:
        print("No mix specified, using default instead!\n")
        song_mix = "default"
    
    difficulty = force_difficulty if len(force_difficulty) > 0 else input("Difficulty (optional, default=normal): ").strip()

    if len(difficulty) == 0:
        print("No difficulty specified, using normal instead!\n")
        difficulty = "normal"

    video_fps_raw = input("Video FPS (optional, default=60): ").strip()

    if len(video_fps_raw) == 0:
        video_fps_raw = "60"

    video_duration_raw = input("Video Duration (in seconds) (optional, default=full): ").strip()

    yes_list = ["true", "t", "yes", "absolutely", "positively", "no no", "false false", "f f", "ff", "nn", "n n", "y", "hell yeah", "hell yes", "hy", "dude, fuck. yes.", "dfy"]
    
    is_downscroll_raw = input("Downscroll? (optional, yes/no, default=false): ")
    is_downscroll = is_downscroll_raw.lower() in yes_list

    is_verbose_raw = input("Verbose Output? (optional, yes/no): ")
    is_verbose = is_verbose_raw.lower() in yes_list

    # the converting!
    if is_verbose:
        print("\nLoading audio...")

    audio_dir = f"songs/{song_name}/{song_mix}/music"
    audio_types = [".ogg", ".wav", ".mp3"]
    audio_files = []

    for file_path in os.listdir(audio_dir):
        file_name = file_path
        file_path = os.path.join(audio_dir, file_path)
        _, file_ext = os.path.splitext(file_path)

        if os.path.isdir(file_path):
            # this is a directory, fuck off!
            continue
        
        if not file_ext in audio_types:
            # not a valid audio file, fuck off!
            continue
        
        if is_verbose:
            print(f"Loading {file_name}")
        
        audio_files.append(file_path)

    audio_clips = []

    for file_path in audio_files:
        audio_clips.append(AudioFileClip(file_path))

    audio = CompositeAudioClip(audio_clips)
    video_fps = int(video_fps_raw)
    video_duration = float(video_duration_raw) if len(video_duration_raw) > 0 else audio.duration

    if video_duration < audio.duration:
        audio = audio.with_duration(video_duration)

    if is_verbose:
        print(f"Loaded {len(audio_clips)} audio file{'' if len(audio_clips) == 1 else 's'}...")

    print("\nConverting...this might take a while, so be patient!\n")
    game = game.Game()

    if is_verbose:
        print("Loading chart...")
    
    game.chart = json.load(open(f"songs/{song_name}/{song_mix}/chart.json"))
    
    meta = json.load(open(f"songs/{song_name}/{song_mix}/metadata.json"))
    game.chart["meta"] = meta
    
    game.song_name = meta["song"]["title"]
    game.song_mix = song_mix
    game.difficulty = difficulty
    
    game.downscroll = is_downscroll

    if is_verbose:
        print("Starting gameplay...")
    
    game.create()

    def make_frame(total_time: float):
        game.update_dt(total_time)
        game.update(game.tracked_dt)

        frame = game.draw()
        return np.array(frame)
    
    if not os.path.exists("output"):
        os.mkdir("output")

    video = VideoClip(make_frame, duration=video_duration).with_fps(video_fps).with_audio(audio)
    video.write_videofile(f"output/{song_name}-{song_mix}-{difficulty}.mp4", codec="libx264", audio_codec="aac", threads=4)
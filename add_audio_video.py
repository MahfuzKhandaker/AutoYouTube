from moviepy.editor import *


audioDir = "./songs/outputs/luxuryaudio.mp3"
videoDir = "./videos/outputs/luxuriousvideos/luxurylivingroom.mp4"

video = VideoFileClip(videoDir)
audio_clip = AudioFileClip(audioDir)
audio_new = afx.audio_loop(audio_clip, duration = video.duration)
video.audio = audio_new

video.write_videofile('./videos/outputs/yt_video/luxurylivingroom.mp4', fps=24, audio=True, audio_fps=44100,
                        audio_nbytes=4, audio_bufsize=2000,
                        temp_audiofile=None,
                        rewrite_audio=True, remove_temp=True,
                        write_logfile=False, verbose=True,
				)
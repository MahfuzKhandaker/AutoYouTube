from moviepy.editor import *
import os

# audio clips

audio_dir = './songs/'
audio_files = [audio_dir+'/'+img for img in os.listdir(audio_dir) if img.endswith('.mp3')] 

print(audio_files)

audios = []

for audio in audio_files:
	audios.append(AudioFileClip(audio))

audioClips = concatenate_audioclips([audio for audio in audios])
audioClips.write_audiofile(f"{audio_dir}outputs/luxuryaudio.mp3")
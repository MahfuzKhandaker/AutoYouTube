from moviepy.editor import *


videoDir = './videos/scrap_videos/'
files = os.listdir(videoDir)

print(files)

videos = []

for file in files:
    full_path = videoDir+file
    try:
        clip = VideoFileClip(full_path)
        clip = clip.fx(vfx.resize, width=1920)

    except Exception as e:
        print(e, ' video failed to load')

    videos.append(clip)

final_clip = concatenate_videoclips(videos, method='compose')
final_clip.write_videofile('./videos/outputs/luxuriousvideos/luxurylivingroom.mp4', 
                        fps=24, codec='libx264', audio=False
                    )
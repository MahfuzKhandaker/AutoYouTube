from moviepy.editor import *
import os


def CutIntoPieces(route, OutputRoute):
	video = VideoFileClip(route, audio=False)
	length = video.duration
	print(length)

	PieceLen = 300

	i = 0
	while 1:
		if (i + 1) * PieceLen < length:
			piece = video.subclip(i * PieceLen,(i + 1) * PieceLen)
			i = i + 1
			result = CompositeVideoClip([piece])
			result.write_videofile(OutputRoute[0:len(OutputRoute) - 4] + '_' + str(i) + '.mp4')
		else:
			break


CutIntoPieces('./videos/outputs/luxuriousvideos/luxuryracecar.mp4','./videos/stitch_video/luxuryracecar.mp4')

'''
Make stitch video
'''

#Videos directory
videos = []

path="./videos/stitch_video/"
RouteList = []
RouteName = []
for a, b, c in os.walk(path):
	for name in c:
		fname = os.path.join(a, name)
		if fname.endswith(".mp4"):
			RouteList.append(fname)
			RouteName.append(name)
 #Location
pos = []
for i in range(3):
	pos.append([i*1920/3, 0])
for i in range(3):
	pos.append([i*1920/3, 1080/2])
 #Length
length = 300
 #Size
size = (1920/3, 1080/2)
 #Setting
for i in range(6):
	video = VideoFileClip(RouteList[i]).subclip(0, length).resize(size).margin(1, color=(36, 36, 36)).set_position(pos[i])
	print(video)


	# add audio to video
	audio_dir = './songs/outputs/luxuryaudio.mp3'
	audioClip = AudioFileClip(audio_dir)
	audio_new = afx.audio_loop(audioClip, duration= video.duration)
	video.audio = audio_new


	videos.append(video)


#Output
result = CompositeVideoClip(videos, size=(1920, 1080))
result.write_videofile('./videos/outputs/yt_video/luxuryracecar.mp4', fps=24, audio=True, audio_fps=44100,
                        audio_nbytes=4, audio_bufsize=2000,
                        temp_audiofile=None,
                        rewrite_audio=True, remove_temp=True,
                        write_logfile=False, verbose=True,
				)

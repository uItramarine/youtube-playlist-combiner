# import argparse
import yt_dlp
import ffmpeg
import os


MUSIC_DIR = "../music"
TEMP_DIR = "./music/.temp"



def links_collector():
    # Collect links from playlist
    pass

def download_audio(audio_urls: list, output_path=TEMP_DIR, format='opus') -> list:

    #TODO: Check params for future 
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{output_path}/%(title)s.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(audio_urls)
    
    return [f"{TEMP_DIR}/{name}" for name in os.listdir(TEMP_DIR)]
        
def mix_audio(input_files, output_file='./music/out.opus'):
    audios = [ffmpeg.input(file).audio for file in input_files]

    concatenated = ffmpeg.concat(*audios, v=0, a=1).node
    
    output = ffmpeg.output(concatenated[0], output_file, format="opus", acodec="libopus")

    ffmpeg.run(output, overwrite_output=True)

    return output_file

def convert_to_mp3(input_file, output_file='./music/out.mp3'):
    try:
        (
            ffmpeg.input(input_file)
            .output(output_file, format="mp3", acodec="libmp3lame", audio_bitrate="192k")
            .run(overwrite_output=True)
        )
        print(f"Conversion successful: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: {e.stderr.decode()}")


audio_urls = [
'https://www.youtube.com/watch?v=DCbvbCbB0fE',
'https://www.youtube.com/watch?v=dRhY7J1SSXg',
'https://www.youtube.com/watch?v=7FgEvZu_GcQ',
'https://www.youtube.com/watch?v=jlEkr-wxLUA',
'https://www.youtube.com/watch?v=Wlffl6ZVgog',
'https://www.youtube.com/watch?v=raDJTzGybj4',
'https://www.youtube.com/watch?v=uOJSE6mqkQI',
'https://www.youtube.com/watch?v=jL-GDY2sECA',
'https://www.youtube.com/watch?v=9TdWXq7MfHw',
'https://www.youtube.com/watch?v=MIySgVOzdto',
'https://www.youtube.com/watch?v=PhtrSxNmbKI'
]

tracks = download_audio(audio_urls)

mix = mix_audio(tracks)

convert_to_mp3(mix)



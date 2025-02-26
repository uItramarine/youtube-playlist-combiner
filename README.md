# youtube-playlist-combiner
Combine all tracks from public playlist into one. 

# Plan
- Add error chatching for downloader process
- Add abbility to send music in chanal

# Problems
Function `yt_dlp.YoutubeDL.download(url)` can take a list with links to audio,
or playlist and inside create list whith traks from playlist.
But if sth went wrong with track in a middle of list,
for example track will not be avilable, it will cause an error,
and all subsequent tracks will not be downloaded. 
I can not handle this error in tipical way Try Except becouse 
i dont have access to inside of the logic (`yt_dlp.YoutubeDL.download(url)`).
Probably there is hook mechanism that will help me, which i dont know.

For now I have dirty hack in code which work like this:
1. Use `yt_dlp.YoutubeDL.extract_info(url)` to extract list of audio from playlist.
2. Parse links and tracks name to dict value.
3. Use `yt_dlp.YoutubeDL.download(url)` to download tracks by link.





# Info
Might be need to install ffmpeg package `pip install yt-dlp`


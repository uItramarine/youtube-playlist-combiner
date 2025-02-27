import json
import os
import re

import telebot
import yt_dlp
from dotenv import load_dotenv


class LoggerOutputs:
    def __init__(self, bot, message):
        self.bot = bot
        self.message = message

    # TODO: Add abbility to send name of audio in chat
    # TODO: Add logger and make logs nice and collectable
    # TODO: Refactor

    def error(self, msg):
        notification = f"Аудіо з айді {msg.split(' ')[2]} недоступне."
        self.bot.send_message(self.message.chat.id, notification)
        print(msg)

    def warning(self, msg):
        print(msg)

    def debug(self, msg):
        print(msg)


class AudioManager:
    def __init__(self, filepath, temp_files, mode="rb"):
        self.filepath = filepath
        self.mode = mode
        self.temp_files = temp_files
        self.file = None

        self.temp_files["filepath"] = filepath

    def __enter__(self):
        # TODO: Logging
        # TODO: Error Catching
        self.file = open(self.filepath, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file:
            self.file.close()

        for key, filepath in self.temp_files.items():
            # TODO: Logging
            if os.path.exists(filepath):
                os.remove(filepath)


class CollectorBot:
    TEMP_DIR = ".temp-audio/"

    def __init__(self):
        self.bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
        self.playlist_pattern = r"^(https?\:\/\/)?(www\.)?(youtube\.com|music\.youtube\.com)\/playlist\?list=.+$"
        self.track_pattern = (
            r"^(https?\:\/\/)?(www\.)?(youtube\.com|music\.youtube\.com)\/watch\?v=.+$"
        )

        self.user_dir = None
        self.message = None
        self.id = None

        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            # TODO: Change intro text

            self.bot.send_message(
                message.chat.id,
                "Встав посилання на плейлист або на музику яку хочеш скачати з Youtube.",
            )

        @self.bot.message_handler(regexp=self.track_pattern, func=self.__is_alloved)
        def scrapp_track(message):
            self.message = message
            self.user_dir = os.path.join(self.TEMP_DIR, str(message.chat.id))
            self.id = message.chat.id

            self.bot.send_message(message.chat.id, "Качаю трек... 💓")

            self.__track_processing(message.text)

        @self.bot.message_handler(regexp=self.playlist_pattern, func=self.__is_alloved)
        def scrapp_playlist(message):
            self.message = message
            self.user_dir = os.path.join(self.TEMP_DIR, str(message.chat.id))
            self.id = message.chat.id

            self.bot.send_message(message.chat.id, "Качаю плейлист. 💓")
            self.bot.send_message(message.chat.id, "Займе кілька секунд.")


            self.__playlist_processing(message.text)

        @self.bot.message_handler(func=self.__is_alloved, commands=["save"])
        def scrapp_to_channel(message):
            link = message.text[6:]

            if self.__is_valid_link(message.text, self.track_pattern):
                self.__process_link(message, link, self.__track_processing)
            elif self.__is_valid_link(message.text, self.playlist_pattern):
                self.__process_link(message, link, self.__playlist_processing, "Качаю плейлист. 💓", "Займе кілька секунд.")
            else:
                self.bot.send_message(message.chat.id, "не можу прочитати посилання :(")

    #TODO Rename
    def __process_link(self, message, link, processing_method, *extra_messages):
        self.message = message
        self.user_dir = os.path.join(self.TEMP_DIR, str(message.chat.id))
        self.id = os.getenv("CHAT_ID")

        for msg in extra_messages:
            self.bot.send_message(message.chat.id, msg)
        
        processing_method(link)

    #TODO Rename
    def __is_valid_link(self, message, pattern):
        args = message.split(maxsplit=1)
        if len(args) < 2:
            return False
        
        return bool(re.search(pattern, args[1]))
    
    def __is_alloved(self, message):
        alloved_users = json.loads(os.getenv("WHITE_LIST"))

        # TODO Logging save user ids
        if message.from_user.id in alloved_users:
            return True
        
        print(message.chat.id)
        self.bot.send_message(message.chat.id, "Ви не в вайт-лісті.")
        return False
            
    def run(self):
        # TODO: Change text
        print("Бот запущений...")
        self.bot.infinity_polling()

    def __send_hook(self, meta_data):
        if meta_data["_default_template"] == "MoveFiles finished":
            audio_path = meta_data["info_dict"]["filepath"]
            temp_files = {"stage": meta_data["info_dict"]["filename"]}

            with AudioManager(audio_path, temp_files) as a:
                self.bot.send_audio(self.id, a)

    # TODO: Refactoring
    def __track_processing(self, url: str):
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                track_meta = ydl.extract_info(url, download=False)
        except Exception as e:
            print("Track unavailable.")
            return

        ydl_opts = {
            "logger": LoggerOutputs(self.bot, self.message),
            # "ignoreerrors": True,
            "outtmpl": f"{self.user_dir}/%(title)s.%(ext)s",
            "postprocessor_hooks": [self.__send_hook],
            "extract_audio": True,
            "format": "bestaudio",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([track_meta["webpage_url"]])
        except:
            print("Track unavailable.")
            return

    # TODO: Refactoring
    def __playlist_processing(self, url: str):
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_meta = ydl.extract_info(url, download=False)
        except Exception as e:
            print("---------------ERROR-----------------")
            return

        ydl_opts = {
            "logger": LoggerOutputs(self.bot, self.message),
            # "ignoreerrors": True,
            "outtmpl": f"{self.user_dir}/%(title)s.%(ext)s",
            "postprocessor_hooks": [self.__send_hook],
            "extract_audio": True,
            "format": "bestaudio",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        for el in playlist_meta["entries"]:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([el["url"]])
            except:
                pass


def main():
    load_dotenv(override=True)

    bot = CollectorBot()
    bot.run()


if __name__ == "__main__":
    main()


# 'https://www.youtube.com/watch?v=tLhY1l_dfU4',
# 'https://www.youtube.com/watch?v=riWtG3NQZ9o',
# 'https://www.youtube.com/watch?v=b7X2_Sbo4S8',
# https://www.youtube.com/playlist?list=PLmvWwY_qHYFXVL6zzbSqhcuoH_iLNkcDy


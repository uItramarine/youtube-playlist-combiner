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
    def error(self, msg):
        notification = f"Аудіо з айді {msg.split(' ')[2]} недоступне."
        self.bot.send_message(self.message.chat.id, notification)
        print(msg)

    def warning(self, msg):
        print(msg)

    def debug(self, msg):
        print(msg)


class CollectorBot:
    def __init__(self, bot_token, temp_dir="./music"):
        self.bot = telebot.TeleBot(bot_token)
        self.temp_dir = temp_dir
        self.message = None

        @self.bot.message_handler(commands=["start"])
        def start(message):
            # TODO: Change intro text
            self.bot.send_message(
                message.chat.id,
                "Встав посилання на плейлист або на музику яку хочеш скачати з Youtube.",
            )

        @self.bot.message_handler(func=lambda message: True)
        def echo(message):
            if self.__check_msg(message.text):
                self.message = message
                self.__send_audio(message.text)
                self.bot.send_message(message.chat.id, "Скачано. 💓")

            else:
                self.bot.send_message(message.chat.id, "Невірний формат посилання.")

    def run(self):
        print("Бот запущений...")
        self.bot.infinity_polling()

    def __post_process_hook(self, d):

        # TODO: Rewrite in context manager
        # TODO: Add try except
        if d["postprocessor"] == "MoveFiles" and d["status"] == "finished":
            audio_name = os.listdir(self.temp_dir)[0]
            audio_path = os.path.join(self.temp_dir, audio_name)

            with open(audio_path, "rb") as audio:
                self.bot.send_audio(self.message.chat.id, audio)

            os.remove(audio_path)

    def __progress_hook(self, d): ...

    def __send_audio(self, url: list):
        ydl_opts = {
            "logger": LoggerOutputs(self.bot, self.message),
            "ignoreerrors": True,
            "outtmpl": f"{self.temp_dir}/%(title)s.%(ext)s",
            "postprocessor_hooks": [self.__post_process_hook],
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)

    def __check_msg(self, url):
        pattern = r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$"
        return bool(re.fullmatch(pattern, url))


def main():
    load_dotenv()
    bot = CollectorBot(os.getenv("BOT_TOKEN"))

    bot.run()


if __name__ == "__main__":
    main()


# 'https://www.youtube.com/watch?v=tLhY1l_dfU4',
# 'https://www.youtube.com/watch?v=riWtG3NQZ9o',
# 'https://www.youtube.com/watch?v=b7X2_Sbo4S8',

# https://www.youtube.com/playlist?list=PLmvWwY_qHYFXVL6zzbSqhcuoH_iLNkcDy

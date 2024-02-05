import uuid
import asyncio

from files import *
from config import *
from tqdm import tqdm
from db import Database
from termcolor import colored
from prettytable import PrettyTable
from telethon import TelegramClient, events, sync

VERBOSE = get_verbose()

if VERBOSE:
    import logging

    logging.basicConfig(level=logging.DEBUG)


class Telegram:
    def __init__(self):
        self._api_id = get_telegram_api_id()
        self._api_hash = get_telegram_api_hash()
        self._client = TelegramClient("anon", self.api_id, self.api_hash)
        self._client.start()
        self._db = Database("files.db")

    @property
    def api_id(self):
        return self._api_id

    @property
    def api_hash(self):
        return self._api_hash

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db

    def list_files(self):
        # List all files
        files = self.db.fetch()
        table = PrettyTable()
        table.field_names = [
            "ID 🌟",
            "File Name 📁",
            "File Path 📂",
            "File Size 📌",
            "Chunks 🔗",
        ]
        for file in files:
            table.add_row(
                [
                    file[0],
                    colored(file[1], "magenta"),
                    colored(file[2], "cyan"),
                    colored(parse_bytes(file[3]), "blue"),
                    colored(len(json.loads(file[4])), "green"),
                ]
            )

        print(table)

    def download_file(self, file_query: str):
        # Download a file
        print(colored(f'[*] Searching for "{file_query}"...', "blue"))
        file = self.db.find_file_by_name_or_path_or_id(file_query)

        if not file:
            print(colored(f"[-] File {file_query} not found.", "red"))
            return

        file = file[0]
        chunks = json.loads(file[4])
        file_name = file[1]
        file_path = file[2]
        file_size = file[3]

        print(colored(f"\n[+] Downloading {len(chunks)} chunk(s).", "magenta"))

        # Download each chunk
        with self.client.start() as client:
            for chunk_num, chunk_path in enumerate(chunks):
                caption = f"{file[0]}:::::{file[2]}:::::{str(chunk_num)}"
                messages = client.get_messages("me", search=caption)

                for message in messages:
                    if message.message.split(":::::")[0] == file[0]:
                        client.download_media(message, file=chunk_path)

                        with open(chunk_path, "rb") as chunk_file:
                            chunk = chunk_file.read()

                            with open(file_path, "ab") as file:
                                # Append the chunk to the file
                                file.write(chunk)

        # Merge the chunks
        print(colored(f"[*] Merging chunks...", "magenta"))

        print(colored(f"[+] Downloaded file {file_name}.", "green"))

    def remove_file(self, file_query: str):
        # Remove a file
        print(colored(f"[+] Removing file {file_query}...", "green"))
        file = self.db.find_file_by_name_or_path_or_id(file_query)

        if not file:
            print(colored(f"[-] File {file_query} not found.", "red"))
            return

        with self.client.start() as client:
            # Get all messages
            messages = client.get_messages("me")

            # Find the message with the absolute path in the caption
            for message in messages:
                if message.caption:
                    if file[0][1] in message.caption:
                        print(colored(f"[+] Deleting message {message.id}...", "green"))
                        client.delete_messages("me", message.id)

        self.db.remove(file[0][0])
        print(colored(f"[+] Removed file {file_query}.", "green"))

    def upload_file(
        self,
        current_dir: str,
        file_path: str,
        file_name: str,
    ) -> str:
        print(colored(f"[*] Uploading {file_name} to Telegram...", "magenta"))
        # Upload file to Telegram and get the file URL
        absolute_path = os.path.abspath(os.path.join(current_dir, file_path))

        # Split the file into chunks
        chunks = split_file_into_chunks(absolute_path)

        id = uuid.uuid4().__str__().replace("-", "")
        print(colored(f"\n[+] Split {file_name} into {len(chunks)} chunk(s).", "cyan"))

        # Upload each chunk to Telegram
        with self.client.start() as client:
            print()
            progress = tqdm(total=len(chunks))

            for chunk_num, chunk_path in enumerate(chunks):
                caption = f"{id}::::::{absolute_path}::::::{str(chunk_num)}"
                result = client.send_file(
                    "me",
                    chunk_path,
                    caption=caption,
                    progress_callback=lambda current, total: progress.update(1),
                )

        self.db.insert(
            id, file_name, absolute_path, os.path.getsize(absolute_path), chunks
        )

        # Return the file URL
        return file_name

        print(colored(f"[+] Uploaded {file_name} to Telegram.", "green"))

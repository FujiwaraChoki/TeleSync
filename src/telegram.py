import os
import uuid

from files import *
from config import *
from tqdm import tqdm
from db import Database
from termcolor import colored
from prettytable import PrettyTable
from telethon import TelegramClient, events, sync

VERBOSE = get_verbose()
DB_FILE = get_db_file()
PHONE = get_phone()
db_type = get_db_type()
neon_db = get_neon_db()

if VERBOSE:
    import logging

    logging.basicConfig(level=logging.DEBUG)


class Telegram:
    def __init__(self):
        self._api_id = get_telegram_api_id()
        self._api_hash = get_telegram_api_hash()
        if VERBOSE:
            print(colored("[INFO] Initializing Telegram Client...", "magenta"))
        self._client = TelegramClient("anon", self.api_id, self.api_hash)
        if VERBOSE:
            print(colored(f"[INFO] Connecting to Telegram via \"{PHONE}\""))
        self._client.start(phone=PHONE)
        
        db1 = None
        db2 = None

        if db_type == 1 or db_type == 3:
            if not DB_FILE:
                db1 = db.Database("files.db")
            else:
                if VERBOSE:
                    print(colored(f"[INFO] Using \"{DB_FILE}\" as database location..."))
                db1 = db.Database(DB_FILE)

        if db_type == 2 or db_type == 3:
            db2 = db.Database2(neon_db)

        self._db = db.DynamicDatabase(db_type, db1, db2)

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
        if VERBOSE:
            print(colored("[INFO] Fetching files..."))
        files = self.db.fetch()
        if VERBOSE:
            print(colored(f"[SUC] Found {len(list(files))} files."))
        table = PrettyTable()
        table.field_names = [
            "ID 🌟",
            "File Name 📁",
            "File Path 📂",
            "File Size 📌",
            "Chunks 🔗",
            "Type 📝",
            "Uploaded 📅",
        ]
        for file in files:
            table.add_row(
                [
                    file[0],
                    colored(file[1], "magenta"),
                    colored(file[2], "cyan"),
                    colored(parse_bytes(file[3]), "blue"),
                    colored(len(json.loads(file[4])), "green"),
                    colored(file[5], "yellow"),
                    colored(file[6], "magenta"),
                ]
            )

        print(table)

    def download_file(self, file_query: str):
        # Download a file
        print(colored(f'[*] Searching for "{file_query}"...', "blue"))
        file = self.db.find_file_by_name_or_path_or_id(file_query)

        if file[0][-2] == "dir":
            self.download_directory(file_query)
            return

        if not file:
            print(colored(f"[-] File {file_query} not found.", "red"))
            return

        file = file[0]
        chunks = json.loads(file[4])
        file_name = file[1]
        file_path = file[2]

        print(colored(f"\n[+] Downloading {len(chunks)} chunk(s).", "magenta"))

        # Download each chunk
        with self.client.start() as client:
            # Loop through each chunk
            for chunk_num, chunk_path in enumerate(chunks):
                # Build the caption, to search for the message
                # that contains the chunk we need.
                caption = f"{file[0]}:::::{file[2]}:::::{str(chunk_num)}:::::file"
                messages = client.get_messages("me", search=caption)

                # Loop through each message
                for message in messages:
                    # Check if message contains the chunk we need
                    if message.message.split(":::::")[0] == file[0]:
                        # Download the chunk in temp directory
                        client.download_media(message, file=chunk_path)

                        # Read the chunk
                        with open(chunk_path, "rb") as chunk_file:
                            chunk = chunk_file.read()

                            # Append the chunk to the file
                            with open(file_path, "ab") as file:
                                file.write(chunk)

        print(colored(f"[+] Downloaded file \"{file_name}\" to \"{file_path}\".", "green"))

    def remove_file(self, file_query: str):
        # Remove a file
        print(colored(f"[+] Removing file {file_query}...", "green"))
        file = self.db.find_file_by_name_or_path_or_id(file_query)

        if not file:
            print(colored(f"[-] File/Directory {file_query} not found.", "red"))
            return
        
        if file[0][-2] == "file":
            with self.client.start() as client:
                # Get all messages
                messages = client.get_messages("me")

                # Find the message with the absolute path in the caption
                for message in messages:
                    if message.message:
                        if file[0][1]:
                            print(colored(f"[+] Deleting message {message.id}...", "magenta"))
                            client.delete_messages("me", message.id)

            self.db.remove(file[0][0])
            print(colored(f"[+] Removed file {file_query}.", "green"))
        else:
            with self.client.start() as client:
                # Get all messages
                messages = client.get_messages("me")

                # Find the message with the absolute path in the caption
                for message in messages:
                    if message.message:
                        if file[0][1]:
                            print(colored(f"[+] Deleting message {message.id}...", "magenta"))
                            client.delete_messages("me", message.id)

            self.db.remove(file[0][0])
            print(colored(f"[+] Removed directory {file_query}.", "green"))

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
                caption = f"{id}::::::{absolute_path}::::::{str(chunk_num)}:::::file"
                client.send_file(
                    "me",
                    chunk_path,
                    caption=caption,
                    progress_callback=lambda current, total: progress.update(1),
                )

        self.db.insert(
            id, file_name, absolute_path, os.path.getsize(absolute_path), chunks, "file"
        )

    def upload_directory(self, current_dir: str, dir_path: str, dir_name: str):
        print(colored(f"[*] Uploading {dir_path} to Telegram...", "magenta"))

        # Upload directory to Telegram and get the file URL
        absolute_path = os.path.abspath(os.path.join(current_dir, dir_path))

        # List all files in the directory
        files = os.listdir(absolute_path)
        
        progress = tqdm(total=len(files))

        for file in files:
            file_path = os.path.join(absolute_path, file)
            if os.path.isfile(file_path):
                # Split the file into chunks
                chunks = split_file_into_chunks(file_path)

                id = uuid.uuid4().__str__().replace("-", "")
                if VERBOSE:
                    print(colored(f"\n\t[+] Split {file} into {len(chunks)} chunk(s).", "cyan"))

                # Upload each chunk to Telegram
                with self.client.start() as client:
                    print()

                    for chunk_num, chunk_path in enumerate(chunks):
                        if VERBOSE:
                            print(colored(
                                f"\t[+] Uploading chunk {chunk_num} of {file} to Telegram...", "magenta"
                            ))
                        caption = f"{id}::::::{file_path}::::::{str(chunk_num)}:::::dir"
                        client.send_file(
                            "me",
                            chunk_path,
                            caption=caption,
                            progress_callback=lambda current, total: progress.update(1 if current == total else 0),
                        )

                self.db.insert(
                    id, file, file_path, os.path.getsize(file_path), chunks, "dir"
                )

        print(colored(f"\n[+] Uploaded {dir_name} to Telegram.", "green"))


    def download_directory(self, dir_query: str):
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))

        # Download a directory
        files = self.db.find_file_by_name_or_path_or_id("dir")

        dir_path = os.path.dirname(files[0][2])

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        if not dir:
            print(colored(f"[-] Directory {dir_query} not found.", "red"))
            return

        if VERBOSE:
            print(f"[INFO] Downloading {len(files)} files from {dir_path}.")

        # Loop through each file in the directory, and see if it's part of the directory
        for file in files:
            if VERBOSE:
                print(f"[INFO] Downloading {file[1]}, with ID \"{file[0]}\".")

            if dir_query in file[2]:
                chunks = json.loads(file[4])
                file_name = file[1]
                file_path = file[2]

                print(colored(f"[+] Downloading {len(chunks)} chunk(s) to \"{file_name}\".", "magenta"))

                # Download each chunk
                with self.client.start() as client:
                    for chunk_num, chunk_path in enumerate(chunks):
                        caption = f"{file[0]}:::::{file[2]}:::::{str(chunk_num)}:::::dir"
                        messages = client.get_messages("me", search=caption)

                        for message in messages:
                            if message.message.split(":::::")[0] == file[0]:
                                temp_chunk_path = os.path.join(ROOT_DIR, "temp", f"{file_name}.part{chunk_num}")
                                if VERBOSE:
                                    print(colored(f"\t[INFO] Downloading chunk {chunk_num} to {temp_chunk_path}.", "yellow"))
                                client.download_media(message, file=temp_chunk_path)

                                with open(temp_chunk_path, "rb") as chunk_file:
                                    chunk = chunk_file.read()

                                    print(colored(f"\t[INFO] Appending chunk {chunk_num} to {file_path}.", "green"))
                                    with open(file_path, "ab") as file:
                                        # Append the chunk to the file
                                        file.write(chunk)

        print(colored(f"[+] Downloaded directory \"{dir_query}\"", "green"))

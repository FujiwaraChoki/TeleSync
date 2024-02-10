"""
By using `TeleSync`, you agree to the following terms and conditions:
- No warranty is provided. Use at your own risk.
- You will not use this tool for any illegal activities.
- You will not use this tool to upload or download any illegal content.

If you do not agree to these terms, do not use this tool.

This tool is provided as is, and is not affiliated with Telegram in any way.

Author: @FujiwaraChoki
Date: 08.02.2024
Version: 1.0.4
GitHub: https://github.com/FujiwaraChoki/TeleSync

Licensed under the GNU General Public License v3.0.
See the LICENSE file for more information.
"""

import os
import sys

from telegram import Telegram
from termcolor import colored


def main():
    # Main function
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))

    # See if `temp` directory exists
    temp_dir = os.path.join(ROOT_DIR, "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    else:
        # Clean
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))

    # Check if `config.json` exists
    config_file = os.path.join(ROOT_DIR, "config.json")

    if not os.path.exists(config_file):
        print(colored("[-] Couldn't not find your config file.", "red"))
        sys.exit(1)

    telegram = Telegram()

    # See args
    args = sys.argv[1:]

    command = args[0]

    if len(args) == 0:
        print(colored("[-] No arguments provided.", "red"))
        sys.exit(1)

    if command == "upload":
        if len(args) < 2:
            print(colored("[-] Not enough arguments provided.", "red"))
            sys.exit(1)

        current_dir = os.getcwd()
        file_path = args[1]
        file_name = os.path.basename(file_path)

        if not os.path.exists(file_path):
            print(colored(f"[-] File {file_path} does not exist.", "red"))
            sys.exit(1)

        # Check if directory
        if os.path.isdir(file_path):
            telegram.upload_directory(current_dir, file_path, file_name)
            sys.exit(0)
        else:
            telegram.upload_file(current_dir, file_path, file_name)
            sys.exit(0)

    if command == "download":
        if len(args) < 2:
            print(colored("[-] Not enough arguments provided.", "red"))
            sys.exit(1)

        file_query = args[1]
        telegram.download_file(file_query)

        sys.exit(0)

    if args[0] == "list":
        telegram.list_files()

        sys.exit(0)

    if command == "remove":
        if len(args) < 2:
            print(colored("[-] Not enough arguments provided.", "red"))
            sys.exit(1)

        file_query = args[1]
        telegram.remove_file(file_query)

        sys.exit(0)

    print(colored(f"[-] Invalid action {args[0]}.", "red"))
    sys.exit(1)


if __name__ == "__main__":
    main()

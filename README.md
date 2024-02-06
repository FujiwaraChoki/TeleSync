# TeleSync

An application to store your local files on Telegram.

## Features

- Infinite storage (No limit)
- Easy to use
- Fast and secure
- Free

## Prerequisites

You need a Telegram API ID and API Hash.
You can create a new App [here](https://my.telegram.org/apps).

## Installation

```bash
git clone https://github.com/FujiwaraChoki/TeleSync.git
cd TeleSync
pip install -r requirements.txt

# Copy the example.config.json to config.json
cp example.config.json config.json # Edit the config.json file with your own settings

# Give run.sh execution permission
chmod +x run.sh
```

## Configuration

| Option         | Description                                                                |
| -------------- | -------------------------------------------------------------------------- |
| `api_id`       | Your Telegram API ID.                                                      |
| `api_hash`     | Your Telegram API Hash.                                                    |
| `phone_number` | Your phone number, which you use for Telegram.                             |
| `db_file`      | The name of the database file. (Default: `files.db`)                       |
| `verbose`      | If `true`, the application will print more information. (Default: `false`) |

## Usage

```bash
./run.sh [COMMAND] [ARGUMENTS]
```

### Commands

| Command                 | Description                            |
| ----------------------- | -------------------------------------- |
| `upload [FILE_QUERY]`   | Upload a file to Telegram              |
| `download [FILE_QUERY]` | Download a file from Telegram          |
| `remove [FILE_QUERY]`   | Delete a file from Telegram            |
| `list`                  | List all files in the Telegram Channel |

`FILE_QUERY` can be the file name, file path, the ID of the file, or a part of the file name.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Authors

- [FujiwaraChoki](https://github.com/FujiwaraChoki)

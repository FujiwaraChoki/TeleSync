import os
import sys


def parse_bytes(bytes: int):
    # Parse bytes to human-readable format
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024


def split_file_into_chunks(absolute_path: str):
    # Splits the file into chunks
    # so Telegram can handle it (2GB max)
    chunks = []

    file_size = os.path.getsize(absolute_path)

    # 2GB max file size
    if file_size > 2000000000:
        # Split the file into chunks
        with open(absolute_path, "rb") as file:
            print(f"Splitting {absolute_path} into chunks...")
            chunk_num = 0
            while True:
                chunk = file.read(50 * 1024 * 1024)
                if not chunk:
                    break

                root_dir = os.path.dirname(sys.argv[0])
                temp_dir = os.path.join(root_dir, "temp")

                # Write the chunk to a file in `temp`
                chunk_file_path = os.path.join(
                    temp_dir,
                    f"{absolute_path}-{chunk_num}.chunk",
                )
                print(f"Writing chunk to {chunk_file_path}...")

                with open(chunk_file_path, "wb") as chunk_file:
                    chunk_file.write(chunk)

                chunks.append(chunk_file_path)
                chunk_num += 1

        return chunks

    else:
        # No need to split the file
        with open(absolute_path, "rb") as file:
            chunks.append(file.read())

        root_dir = os.path.dirname(os.path.dirname(sys.argv[0]))
        temp_dir = os.path.abspath(os.path.join(root_dir, "temp"))
        file_name = os.path.basename(absolute_path)

        chunk_file_path = os.path.join(temp_dir, f"{file_name}.chunk")

        with open(chunk_file_path, "wb") as chunk_file:
            chunk_file.write(chunks[0])

        chunks = [chunk_file_path]

        return chunks

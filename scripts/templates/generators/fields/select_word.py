import os
import random
from pathlib import Path


def select_random_word_from_nested_directory(directory):
    """
    Scouts a directory (including subdirectories), selects a random file,
    selects a random line from that file, and returns the line and file path.

    Args:
        directory: Path to the directory to search (string or Path object)

    Returns:
        tuple: (word, file_path) where word is the selected line and 
               file_path is the path to the file it came from

    Raises:
        ValueError: If directory is empty or contains no readable files
        FileNotFoundError: If directory does not exist
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    all_files = [f for f in directory.rglob('*') if f.is_file()]

    if not all_files:
        raise ValueError(f"No files found in directory: {directory}")

    selected_file = random.choice(all_files)

    try:
        with open(selected_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except (IOError, UnicodeDecodeError) as e:
        raise ValueError(f"Could not read file {selected_file}: {e}")

    if not lines:
        raise ValueError(f"Selected file is empty: {selected_file}")

    selected_word = random.choice(lines)
    raw_path = os.path.abspath(str(selected_file))

    source = raw_path.replace(
        str(directory.absolute()),
        ""
    ).replace(os.sep, "/")

    return selected_word, source

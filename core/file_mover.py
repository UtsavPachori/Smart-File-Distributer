from pathlib import Path
import shutil

from core.file_types import (
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    MUSIC_EXTENSIONS
)

from utils.path_manager import get_windows_folders


def get_destination(extension, base_folder):
    base = Path(base_folder)

    if extension in DOCUMENT_EXTENSIONS:
        return base / "Documents"

    elif extension in IMAGE_EXTENSIONS:
        return base / "Images"

    elif extension in VIDEO_EXTENSIONS:
        return base / "Videos"

    elif extension in MUSIC_EXTENSIONS:
        return base / "Music"

    return None


def generate_new_name(destination, file_name):
    destination_path = Path(destination) / file_name

    if not destination_path.exists():
        return destination_path

    stem = destination_path.stem
    suffix = destination_path.suffix

    counter = 1

    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = Path(destination) / new_name

        if not new_path.exists():
            return new_path

        counter += 1


def move_file(file_path, base_folder):
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    destination_folder = get_destination(extension, base_folder)

    if not destination_folder:
        return "Skipped (unsupported type)"
    
    destination_folder.mkdir(exist_ok=True)
    
    new_path = generate_new_name(destination_folder, file_path.name)
    shutil.move(str(file_path), str(new_path))
    
    return f"Moved → {new_path}", new_path
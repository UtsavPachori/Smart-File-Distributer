from pathlib import Path

def scan_folder(folder_path, recursive = False):
    folder = Path(folder_path)
    files = []

    if recursive:
        for item in folder.rglob("*"):
            if item.is_file():
                files.append(item)
    else:
        for item in folder.iterdir():
            if item.is_file():
                files.append(item)

    return files
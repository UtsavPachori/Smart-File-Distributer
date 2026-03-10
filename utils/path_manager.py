from pathlib import Path

def get_windows_folders():
    home = Path.home()

    folders = {
        "documents": home / "Documents", 
        "pictures": home / "Pictures", 
        "music": home / "Music", 
        "videos": home / "Videos"
    }

    return folders
import os

def scan_folder_with_data(folder_path, recursive=True):
    files_data = []

    if recursive:
        # Walk through all subfolders
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)

                try:
                    size = os.path.getsize(full_path)
                    extension = os.path.splitext(file)[1].lower()

                    files_data.append({
                        "name": file,
                        "path": full_path,
                        "size": size,
                        "extension": extension
                    })

                except Exception:
                    pass

    else:
        # Scan only the top-level folder
        try:
            for file in os.listdir(folder_path):
                full_path = os.path.join(folder_path, file)

                if os.path.isfile(full_path):
                    try:
                        size = os.path.getsize(full_path)
                        extension = os.path.splitext(file)[1].lower()

                        files_data.append({
                            "name": file,
                            "path": full_path,
                            "size": size,
                            "extension": extension
                        })

                    except Exception:
                        pass
        except Exception:
            pass

    return files_data
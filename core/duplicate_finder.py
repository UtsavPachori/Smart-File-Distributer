import hashlib
from collections import defaultdict

def get_file_hash(file_path):
    hasher = hashlib.md5()

    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()

    except Exception:
        return None

def find_duplicates(files_data, progress_callback=None):
    size_map = defaultdict(list)

    for file in files_data:
        size_map[file["size"]].append(file)

    duplicate_groups = []
    space_wasted = 0

    processed = 0

    for size, files in size_map.items():
        if len(files) < 2:
            for _ in files:
                processed += 1
                if progress_callback:
                    progress_callback(processed)
            continue

        hash_map = defaultdict(list)

        for file in files:
            path = file["path"]
            file_hash = get_file_hash(path)

            processed += 1
            if progress_callback:
                progress_callback(processed)

            if not file_hash:
                continue

            hash_map[file_hash].append(path)

        for hash_value, paths in hash_map.items():
            if len(paths) > 1:
                duplicate_groups.append(paths)
                space_wasted += size * (len(paths) - 1)

    return duplicate_groups, space_wasted
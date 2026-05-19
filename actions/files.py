"""
actions/files.py — file and folder operations
"""
import os
import shutil
import glob
import zipfile
import hashlib
import datetime


def _stdout(text):
    return type("R", (), {"stdout": str(text)})()


def _file_hash(path: str, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


ACTIONS = {
    "os_create_file": {
        "description": "Create empty file, args = [filepath]",
        "execute": lambda a: open(a[0], "w", encoding="utf-8").close() or _stdout(f"created {a[0]}"),
    },
    "os_write_file": {
        "description": "Write content to file, args = [filepath, content]",
        "execute": lambda a: (
            open(a[0], "w", encoding="utf-8").write(a[1] if len(a) > 1 else ""),
            _stdout(f"written {a[0]}"),
        )[-1],
    },
    "os_append_file": {
        "description": "Append content to file, args = [filepath, content]",
        "execute": lambda a: _stdout(open(a[0], "a", encoding="utf-8").write("\n" + a[1]) or f"appended {a[0]}"),
    },
    "os_read_file": {
        "description": "Read a file, args = [filepath]",
        "execute": lambda a: _stdout(open(a[0], "r", encoding="utf-8").read()),
    },
    "os_read_file_lines": {
        "description": "Read first N lines of file, args = [filepath, N]",
        "execute": lambda a: _stdout("".join(open(a[0], "r", encoding="utf-8").readlines()[:int(a[1])])),
    },
    "os_delete_file": {
        "description": "Delete a file, args = [filepath]",
        "execute": lambda a: [os.remove(a[0]), _stdout(f"deleted {a[0]}")][-1],
    },
    "os_rename_file": {
        "description": "Rename a file, args = [old, new]",
        "execute": lambda a: [os.rename(a[0], a[1]), _stdout(f"renamed {a[0]} -> {a[1]}")][-1],
    },
    "os_copy_file": {
        "description": "Copy a file, args = [source, destination]",
        "execute": lambda a: _stdout(shutil.copy2(a[0], a[1])),
    },
    "os_move_file": {
        "description": "Move a file, args = [source, destination]",
        "execute": lambda a: _stdout(shutil.move(a[0], a[1])),
    },
    "os_list_files": {
        "description": "List files in folder, args = [path] or []",
        "execute": lambda a: _stdout("\n".join(os.listdir(a[0] if a else "."))),
    },
    "os_list_files_detail": {
        "description": "List files with details, args = [path]",
        "execute": lambda a: _stdout("\n".join(
            f"{e.name:<40} {e.stat().st_size:>10} B  {datetime.datetime.fromtimestamp(e.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}"
            for e in sorted(os.scandir(a[0] if a else "."), key=lambda x: x.name)
        )),
    },
    "os_create_folder": {
        "description": "Create folder, args = [path]",
        "execute": lambda a: [os.makedirs(a[0], exist_ok=True), _stdout(f"created {a[0]}")][-1],
    },
    "os_delete_folder": {
        "description": "Delete empty folder, args = [path]",
        "execute": lambda a: [os.rmdir(a[0]), _stdout(f"deleted {a[0]}")][-1],
    },
    "os_delete_folder_recursive": {
        "description": "Delete folder and all contents, args = [path]",
        "execute": lambda a: [shutil.rmtree(a[0]), _stdout(f"deleted {a[0]}")][-1],
    },
    "os_copy_folder": {
        "description": "Copy entire folder, args = [source, destination]",
        "execute": lambda a: _stdout(shutil.copytree(a[0], a[1])),
    },
    "os_file_exists": {
        "description": "Check if file/folder exists, args = [path]",
        "execute": lambda a: _stdout(f"{a[0]} -> {'EXISTS' if os.path.exists(a[0]) else 'NOT FOUND'}"),
    },
    "os_file_size": {
        "description": "Get file size, args = [filepath]",
        "execute": lambda a: _stdout(f"{a[0]} -> {os.path.getsize(a[0]) / 1024:.2f} KB"),
    },
    "os_file_hash": {
        "description": "Get SHA256 hash of a file, args = [filepath]",
        "execute": lambda a: _stdout(f"SHA256: {_file_hash(a[0])}"),
    },
    "os_file_hash_md5": {
        "description": "Get MD5 hash of a file, args = [filepath]",
        "execute": lambda a: _stdout(f"MD5: {_file_hash(a[0], 'md5')}"),
    },
    "os_file_modified": {
        "description": "Get last modified date, args = [filepath]",
        "execute": lambda a: _stdout(f"Modified: {datetime.datetime.fromtimestamp(os.path.getmtime(a[0]))}"),
    },
    "os_zip_folder": {
        "description": "Zip a folder, args = [folder_path, output_zip_name]",
        "execute": lambda a: _stdout(shutil.make_archive(a[1], "zip", a[0])),
    },
    "os_zip_file": {
        "description": "Zip a single file, args = [filepath, output_zip]",
        "execute": lambda a: [
            zipfile.ZipFile(a[1], "w").write(a[0], os.path.basename(a[0])),
            _stdout(f"Zipped to {a[1]}")
        ][-1],
    },
    "os_unzip": {
        "description": "Unzip a file, args = [zip_path, destination_folder]",
        "execute": lambda a: [shutil.unpack_archive(a[0], a[1]), _stdout(f"Unzipped to {a[1]}")][-1],
    },
    "os_count_files": {
        "description": "Count files in folder, args = [path]",
        "execute": lambda a: _stdout(f"{len(os.listdir(a[0]))} items in {a[0]}"),
    },
    "os_search_files": {
        "description": "Search files by name pattern, args = [folder, pattern]",
        "execute": lambda a: _stdout("\n".join(
            os.path.join(r, f)
            for r, _, files in os.walk(a[0])
            for f in files if a[1].lower() in f.lower()
        ) or "No files found"),
    },
    "os_get_cwd": {
        "description": "Get current working directory",
        "execute": lambda a: _stdout(os.getcwd()),
    },
    "os_change_dir": {
        "description": "Change working directory, args = [path]",
        "execute": lambda a: [os.chdir(a[0]), _stdout(f"Changed to {os.getcwd()}")][-1],
    },
    "os_tree": {
        "description": "Show folder tree, args = [path]",
        "execute": lambda a: _stdout(_build_tree(a[0] if a else ".")),
    },
    "os_find_duplicates": {
        "description": "Find duplicate files by size, args = [folder]",
        "execute": lambda a: _stdout(_find_dupes(a[0])),
    },
    "os_get_extension": {
        "description": "Get file extension, args = [filepath]",
        "execute": lambda a: _stdout(f"Extension: {os.path.splitext(a[0])[1]}"),
    },
    "os_get_filename": {
        "description": "Get filename from path, args = [filepath]",
        "execute": lambda a: _stdout(f"Filename: {os.path.basename(a[0])}"),
    },
    "os_get_folder": {
        "description": "Get parent folder, args = [filepath]",
        "execute": lambda a: _stdout(f"Folder: {os.path.dirname(a[0])}"),
    },
}


def _build_tree(path: str, prefix: str = "", max_depth: int = 4, depth: int = 0) -> str:
    if depth > max_depth or not os.path.isdir(path):
        return ""
    lines = [os.path.basename(path) + "/"]
    entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name))
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        if entry.is_dir():
            sub = _build_tree(entry.path, prefix + ("    " if i == len(entries) - 1 else "│   "), max_depth, depth + 1)
            lines.append(prefix + connector + sub)
        else:
            lines.append(prefix + connector + entry.name)
    return "\n".join(lines)


def _find_dupes(folder: str) -> str:
    sizes: dict = {}
    for r, _, files in os.walk(folder):
        for f in files:
            p = os.path.join(r, f)
            s = os.path.getsize(p)
            sizes.setdefault(s, []).append(p)
    dupes = {s: v for s, v in sizes.items() if len(v) > 1}
    if not dupes:
        return "No duplicates found"
    lines = []
    for size, paths in dupes.items():
        lines.append(f"[{size} B]")
        lines.extend(f"  {p}" for p in paths)
    return "\n".join(lines)

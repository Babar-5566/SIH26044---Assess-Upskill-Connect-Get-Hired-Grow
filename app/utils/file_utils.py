from pathlib import Path
def safe_path(path, root):
    return Path(path).resolve().is_relative_to(Path(root).resolve())

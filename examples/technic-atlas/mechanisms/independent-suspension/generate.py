"""Rebuild the placement from this exported source and plan."""
from pathlib import Path
import sys

if __name__ == '__main__':
    folder = Path(__file__).resolve().parent
    for parent in folder.parents:
        if (parent / 'ldraw_tools').is_dir():
            sys.path.insert(0, str(parent))
            break
    from ldraw_tools.manuals import regenerate_placement
    print(regenerate_placement(folder))

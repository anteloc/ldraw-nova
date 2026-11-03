from pathlib import Path
import sys
sys.path.insert(0,str(next(p for p in Path(__file__).resolve().parents if (p / 'ldraw_tools').is_dir())))
from ldraw_tools.reference_recipes import generate_recipe

if __name__ == '__main__':
    raise SystemExit(generate_recipe('street-lantern',Path(__file__).resolve().parent))

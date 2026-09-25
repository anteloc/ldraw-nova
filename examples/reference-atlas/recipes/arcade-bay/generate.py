from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from ldraw_tools.reference_recipes import generate_recipe

if __name__ == '__main__':
    raise SystemExit(generate_recipe('arcade-bay',Path(__file__).resolve().parent))

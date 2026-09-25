"""Rebuild this structural example and its evidence from the shared recipe."""
from pathlib import Path
import runpy
if __name__ == "__main__":
    api = runpy.run_path(str(Path(__file__).resolve().parents[1]/"generate.py"))
    api["generate"](Path(__file__).resolve().parents[1], names=['frame-tower'], levels=2, colour=71, accent=14)

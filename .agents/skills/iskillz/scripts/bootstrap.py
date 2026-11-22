"""Make the script's dependencies importable with nothing but Python.

If they are already importable (e.g. you run it inside your own virtualenv),
nothing happens. Otherwise the first run creates a private virtualenv with
the standard `python -m venv`, installs requirements.txt into it with pip,
and re-runs the script with that virtualenv's Python. Later runs reuse it;
it is rebuilt when requirements.txt changes.

The virtualenv lives in $ISKILLZ_VENV, default ~/.cache/iskillz/venv
(or $XDG_CACHE_HOME/iskillz/venv).
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 11)
REQUIREMENTS = Path(__file__).with_name("requirements.txt")
MODULES = ("yaml", "markdown_it", "skills_ref", "bs4", "pypandoc")


def venv_dir() -> Path:
    if env := os.environ.get("ISKILLZ_VENV"):
        return Path(env).expanduser()
    cache = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return cache / "iskillz" / "venv"


def fail(msg: str) -> None:
    print(f"skilltree: {msg}", file=sys.stderr)
    sys.exit(1)


def ensure() -> None:
    if sys.version_info < MIN_PYTHON:
        fail(f"needs Python {'.'.join(map(str, MIN_PYTHON))} or newer "
             f"(this is {sys.version.split()[0]})")
    if all(importlib.util.find_spec(m) for m in MODULES):
        return
    if os.environ.get("ISKILLZ_BOOTSTRAPPED"):
        fail(f"dependencies still missing in {sys.prefix}; delete it and retry")

    venv = venv_dir()
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    stamp = venv / "requirements.txt"
    wanted = REQUIREMENTS.read_text()
    if not python.exists() or not stamp.is_file() or stamp.read_text() != wanted:
        print(f"skilltree: first run: installing dependencies into {venv} "
              "(once, about a minute)...", file=sys.stderr)
        try:
            subprocess.run([sys.executable, "-m", "venv", "--clear", str(venv)], check=True,
                           stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            fail("could not create a virtualenv. On Debian/Ubuntu: sudo apt install python3-venv")
        try:
            subprocess.run([str(python), "-m", "pip", "install", "--quiet",
                            "--disable-pip-version-check", "-r", str(REQUIREMENTS)], check=True)
        except subprocess.CalledProcessError:
            fail(f"pip could not install {REQUIREMENTS} (offline?)")
        stamp.write_text(wanted)

    env = os.environ | {"ISKILLZ_BOOTSTRAPPED": "1"}
    args = [str(python), os.path.abspath(sys.argv[0]), *sys.argv[1:]]
    if os.name == "nt":  # no real exec on Windows
        sys.exit(subprocess.run(args, env=env).returncode)
    os.execve(str(python), args, env)

"""The generated command reference must match the executable parser."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_command_reference_is_current():
    result = subprocess.run([sys.executable, 'scripts/cli_reference.py', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_specialist_commands_are_hidden_from_help_but_still_run():
    help_text = subprocess.run([sys.executable, '-m', 'ldraw_tools.cli', '--help'], cwd=ROOT, capture_output=True, text=True).stdout
    listed = help_text.split('options:')[0]
    assert '    build ' in listed and '    review ' in listed and '    matrix ' not in listed
    result = subprocess.run([sys.executable, '-m', 'ldraw_tools.cli', 'matrix', 'y', '90'], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0


def test_technic_parts_reference_is_current():
    result = subprocess.run([sys.executable, 'scripts/technic_parts_reference.py', '--check'], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr

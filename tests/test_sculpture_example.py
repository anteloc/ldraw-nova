import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('sculpture_example', Path(__file__).parents[1] / 'examples/sculpture/generate.py')
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


def test_import_recovers_colours_rotations_and_integer_layers():
    text = '1 14 20 -24 60 0 0 1 0 1 0 -1 0 0 2456.DAT\n0 STEP\n'
    rows = example.export_cells(text)
    assert rows == [[x,y,1,14] for x in range(2) for y in range(6)]
    turned = '1 4 60 -48 20 -1 0 0 0 1 0 0 0 -1 2456.dat'
    assert example.export_cells(turned) == [[x,y,2,4] for x in range(6) for y in range(2)]


@pytest.mark.parametrize('text',[
    '', '1 14 10 0 10 1 0 0 0 1 0 0 0 1 3005.dat',
    '1 16 10 0 10 0 0 1 0 1 0 -1 0 0 3005.dat',
    '1 14 11 0 10 0 0 1 0 1 0 -1 0 0 3005.dat',
    '1 14 nan 0 10 0 0 1 0 1 0 -1 0 0 3005.dat',
    '1 14 10 0 10 0 0 1 0 1 0 -1 0 0 unsafe.ldr',
    '2 14 0 0 0 0 0 0',
    '1 14 10 0 10 0 0 1 0 1 0 -1 0 0 3005.dat\n' * 2,
])
def test_import_rejects_unsupported_misaligned_and_overlapping_exports(text):
    with pytest.raises(ValueError): example.export_cells(text)

from pathlib import Path
from types import SimpleNamespace

from ldraw_tools.external import render, render_steps


def test_long_snapshot_includes_all_placements_without_changing_instructions(tmp_path, parts, monkeypatch):
    source = tmp_path / "long.mpd"
    placements = [f"1 14 {i * 80} 0 0 1 0 0 0 1 0 0 0 1 3001.dat" for i in range(300)]
    body = "\r\n0 STEP\r\n".join(placements)
    original = ("0 FILE main.ldr\r\n0 Example STEP comment\r\n" + body +
                "\r\n0 ROTSTEP 0 90 0 REL\r\n0 NOFILE\r\n").encode()
    source.write_bytes(original)
    observed = []

    def cad(command, **kwargs):
        # Snapshots use a complete disposable scene; BOM uses original source.
        path = Path(command[command.index("--no-fade-steps") + 1]) if "-i" in command else Path(command[-1])
        text = path.read_text()
        observed.append(text)
        assert all(placement in text for placement in placements)
        if "-i" in command:
            assert not any(line.split()[:2] in (["0", "STEP"], ["0", "ROTSTEP"]) for line in text.splitlines())
            assert "0 Example STEP comment" in text
            Path(command[command.index("-i") + 1]).write_bytes(b"complete scene")
        else:
            assert path == source
            Path(command[command.index("-csv") + 1]).write_text("Part ID,Color Code,Quantity\n3001,14,300\n")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("ldraw_tools.external.subprocess.run", cad)
    render(source, parts.path.parent, tmp_path / "renders", views=["home"])
    assert source.read_bytes() == original
    assert len(observed) == 2


def test_instruction_renderer_keeps_long_sequence_step_boundaries(tmp_path, parts, monkeypatch):
    source = tmp_path / "steps.mpd"
    body = "\n0 STEP\n".join(f"1 14 {i * 80} 0 0 1 0 0 0 1 0 0 0 1 3001.dat" for i in range(300))
    source.write_text("0 FILE main.ldr\n" + body + "\n0 NOFILE\n")

    def cad(command, **kwargs):
        assert Path(command[-1]) == source
        assert Path(command[-1]).read_text().count("0 STEP") == 299
        assert command[command.index("--from") + 1] == "300"
        assert command[command.index("--to") + 1] == "300"
        Path(command[command.index("-i") + 1]).write_bytes(b"final step")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("ldraw_tools.external.subprocess.run", cad)
    render_steps(source, parts.path.parent, tmp_path / "steps", steps=[300], views=["home"])

"""`finalize` adds the delivery metadata the plan cannot carry, once, and checks the rest."""
from ldraw_tools.finalize import COMMENT, KEYWORDS, LICENCE, finalize, finalize_text

HEADER = ['0 Name: {name}', '0 Author: Claude Code 2.1 (agent); Claude Opus 5.5 (claude-opus-5-5)', '0 !LDRAW_ORG Model', LICENCE]


def mpd(*sections):
    lines = []
    for name, title, header in sections:
        lines += [f'0 FILE {name}', f'0 {title}', *(h.format(name=name) for h in header), '1 4 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat']
    return '\r\n'.join(lines) + '\r\n'


def test_generated_sections_get_the_comment_and_keywords_once_and_keep_crlf(tmp_path):
    imported = ['0 Name: {name}', '0 Author: Jane Builder', '0 !LICENSE Licensed under CC BY 4.0 : see CAreadme.txt']
    text = mpd(('main.ldr', '[AI-GENERATED] Crane', HEADER), ('arm.ldr', 'Arm', HEADER), ('wheel.ldr', 'Wheel', imported))
    done, problems = finalize_text(text)
    assert not problems and '\n' not in done.replace('\r\n', '')
    lines = done.split('\r\n')
    assert [lines[i + 1:i + 3] for i, line in enumerate(lines) if line == LICENCE] == [[COMMENT, KEYWORDS]] * 2
    assert lines.count(COMMENT) == 2 and 'Jane Builder' in done and done.count(KEYWORDS) == 2
    assert finalize_text(done) == (done, [])
    path = tmp_path / 'ai-generated.mpd'
    path.write_bytes(text.encode())
    assert finalize(path)['written'] and path.read_bytes().decode() == done


def test_problems_are_named_and_nothing_is_written(tmp_path):
    path = tmp_path / 'ai-generated.mpd'
    path.write_bytes(mpd(('main.ldr', 'Crane', HEADER)).encode())
    report = finalize(path)
    assert not report['written'] and any('[AI-GENERATED] ' in p for p in report['problems'])
    assert path.read_bytes().decode() == mpd(('main.ldr', 'Crane', HEADER))
    unlicensed = [h for h in HEADER if h != LICENCE]
    _, problems = finalize_text(mpd(('main.ldr', '[AI-GENERATED] Crane', unlicensed)))
    assert any('"license": "CC-BY-NC"' in p for p in problems)
    anonymous = [h for h in HEADER if not h.startswith('0 Author:')]
    _, problems = finalize_text(mpd(('main.ldr', '[AI-GENERATED] Crane', anonymous)))
    assert any("'0 Author:'" in p for p in problems)

"""Use the installed CAD renderers with argument lists, timeouts and unique files."""
from __future__ import annotations

import subprocess
import math
import csv
import hashlib
import re
from pathlib import Path
from tempfile import TemporaryDirectory


def view_camera(bounds, view):
    """Frame the complete assembly with a stable margin in every build step."""
    low, high = bounds.min, bounds.max
    center = [(getattr(low, axis) + getattr(high, axis)) / 2 for axis in 'xyz']
    radius = max(1.0, math.sqrt(sum((getattr(high, axis)-getattr(low, axis))**2 for axis in 'xyz')) / 2)
    direction = {'home':(1,-1,-1), 'front':(0,0,-1), 'back':(0,0,1),
                 'left':(-1,0,0), 'right':(1,0,0), 'top':(0,-1,0), 'bottom':(0,1,0)}[view]
    distance = radius / math.sin(math.radians(15)) * 1.15
    norm = math.sqrt(sum(v*v for v in direction))
    camera = [c + v / norm * distance for c,v in zip(center,direction)]
    up = (0,0,1) if view == 'top' else (0,0,-1) if view == 'bottom' else (0,-1,0)
    return ['--fov', '30', '--camera-position-ldraw', *map(str, (*camera, *center, *up))]


def render_steps(path, library, outdir, *, steps, views=("home", "back"), timeout=90, bounds=None):
    """Render actual nonempty source steps, including a final unterminated step.

    Uses the same LeoCAD switches as ldraw-render-steps.sh, with argument lists,
    fresh output files and the embedded-DAT adapter used by normal rendering.
    """
    if not steps or steps != sorted(set(steps)) or any(n < 1 for n in steps):
        raise ValueError('Step numbers must be distinct positive numbers in order')
    if not views or len(set(views)) != len(views) or any(v not in
            {'home', 'front', 'back', 'left', 'right', 'top', 'bottom'} for v in views):
        raise ValueError('Choose distinct supported viewpoints')
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    images = []
    with TemporaryDirectory(prefix='.steps-', dir=outdir) as temp:
        prepared, lib, _ = cad_source(path, library, temp)
        for view in views:
            target = Path(temp)/f'{view}.png'
            camera = view_camera(bounds, view) if bounds is not None else ['--viewpoint',view]
            result = subprocess.run(['leocad', '-l', str(lib), '-i', str(target),
                '--from', str(min(steps)), '--to', str(max(steps)), *camera,
                '-w', '1000', '-h', '750', '--aa-samples', '4', '--shading', 'full',
                '--highlight', '--no-fade-steps', '--line-width', '1', str(prepared)],
                capture_output=True, text=True, timeout=timeout)
            if result.returncode:
                raise ValueError(f'LeoCAD step rendering failed: {result.stdout}\n{result.stderr}')
            found = {}
            for candidate in Path(temp).glob(view+'*.png'):
                match = re.fullmatch(re.escape(view)+r'(\d+)\.png', candidate.name)
                if match:
                    found[int(match[1])] = candidate
                elif candidate == target and len(steps) == 1:
                    found[steps[0]] = candidate
            if any(n not in found for n in steps):
                raise ValueError(f'LeoCAD did not render every requested {view} step')
            for number in steps:
                name = f'step-{number:03}-{view}.png'
                found[number].replace(outdir/name)
                images.append(dict(step=number, view=view, file=name))
    return images


def cad_source(path, library, temp):
    """Materialize embedded DAT definitions for LeoCAD without modifying source.

    LeoCAD's MPD loader treats inline DAT geometry as model contents and can omit
    those parts in snapshots/CSV. Give it a minimal ordinary library instead.
    """
    from .document import parse_source, section_table, is_part, source_blocks
    from .common import get_parts, normalized, atomic_write
    from ldraw import Piece
    path,library,temp=Path(path).resolve(),Path(library).resolve(),Path(temp)
    if path.suffix.casefold() not in {".mpd",".ldr"}:
        return path,library,{}
    model=parse_source(path)
    table=section_table(model)
    embedded=[s for s in table.values() if is_part(s)]
    if not embedded:
        return path,library,{}
    digest=hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    renames={normalized(s.name):f"nova-{digest}-{i:03d}.dat" for i,s in enumerate(embedded)}
    parts=get_parts(library)
    mini=temp/'library';mini.mkdir()
    (mini/'parts').mkdir();(mini/'p').mkdir()
    config=next(p for p in library.iterdir() if p.name.casefold()=='ldconfig.ldr')
    (mini/'LDConfig.ldr').symlink_to(config)
    seen=set();index={}

    def include(code):
        code=normalized(code).removesuffix('.dat')
        if code in seen or code+'.dat' in table:
            return
        seen.add(code)
        part=parts.find_part(code=code)
        if part is None:
            raise ValueError(f"Cannot render: unresolved library dependency {code}.dat")
        source=part.path.resolve()
        relative=source.relative_to(library)
        destination=mini/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        if not destination.exists():destination.symlink_to(source)
        if relative.parent==Path('parts'):
            index[relative.name]=part.description
        for obj in part.objects:
            if isinstance(obj,Piece):include(obj.reference)

    for sub in table.values():
        for p in sub.pieces:
            if normalized(p.reference) not in table:include(p.reference)
    blocks=source_blocks(path)
    if not blocks:
        raise ValueError("Embedded DAT rendering requires MPD FILE blocks")

    def rewritten(sub):
        result=[]
        for _,line in blocks[normalized(sub.name)]:
            tokens=line.split(None,14)
            if tokens[:2]==['0','Name:'] and is_part(sub):
                line='0 Name: '+renames[normalized(sub.name)]
            elif tokens[:1]==['1'] and len(tokens)==15 and normalized(tokens[14]) in renames:
                line=' '.join(tokens[:14])+' '+renames[normalized(tokens[14])]
            result.append(line)
        return result
    lines=[]
    if is_part(model):
        wrapper='nova-cad-root.ldr'
        while normalized(wrapper) in table:wrapper='_'+wrapper
        lines.extend(['0 FILE '+wrapper,'0 Embedded part preview',
                      '1 7 0 0 0 1 0 0 0 1 0 0 0 1 '+renames[normalized(model.name)]])
    for sub in table.values():
        body=rewritten(sub)
        if is_part(sub):
            filename=renames[normalized(sub.name)]
            atomic_write(mini/'parts'/filename,'\r\n'.join(body)+'\r\n')
            index[filename]=sub.description or sub.name
        else:
            lines.extend(['0 FILE '+sub.name,*body])
    lines.append('0 NOFILE')
    prepared=temp/'leocad-source.mpd'
    atomic_write(prepared,'\r\n'.join(lines)+'\r\n')
    atomic_write(mini/'parts.lst','\n'.join(f'{name} {title}' for name,title in sorted(index.items()))+'\n')
    return prepared,mini,{new:table[old].name for old,new in renames.items()}


def restore_bom_names(path, names):
    if not names:return
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    for row in rows:
        row['Part ID']=names.get(row['Part ID'],row['Part ID'])
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def compare_bom(model,parts,csv_path):
    from collections import Counter
    from .common import normalized
    from .document import physical_context
    model,parts=physical_context(model,parts)
    expected=Counter()
    for row in model.bill_of_materials(parts=parts):
        expected[(normalized(row.part).removesuffix('.dat'),row.colour_code)]+=row.quantity
    actual=Counter()
    with Path(csv_path).open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not {'Part ID','Color Code','Quantity'}.issubset(reader.fieldnames or []):
            raise ValueError('CSV must be a LeoCAD BOM with Part ID, Color Code, Quantity columns')
        for row in reader:
            quantity=int(row['Quantity'])
            if quantity<0:raise ValueError('BOM quantities must be nonnegative')
            actual[(normalized(row['Part ID']).removesuffix('.dat'),int(row['Color Code']))]+=quantity
    differences=[dict(part=part+'.dat',colour=colour,python=expected[(part,colour)],leocad=actual[(part,colour)])
                 for part,colour in sorted(expected.keys()|actual.keys()) if expected[(part,colour)]!=actual[(part,colour)]]
    return dict(matches=not differences,physical_placements=sum(expected.values()),leocad_placements=sum(actual.values()),differences=differences)


def cad_check(path, library, *, timeout=90):
    with TemporaryDirectory(prefix="ldraw-check-") as temp:
        render(path, library, temp, views=("home",), timeout=timeout)
        return dict(tool="LeoCAD", passed=True, snapshot_created=True, bom_created=True,
                    note="Import/export smoke test; Python diagnostics provide syntax/reference checks. Temporary artifacts removed after checking.")


def prepare_glb(path, library, output, parts, *, timeout=180):
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".glb-", dir=output.parent) as temp:
        descriptions = Path(temp) / "descriptions.tsv"
        descriptions.write_text("".join(f"{code}.dat\t{description}\n" for code, description in parts.by_code.items()), encoding="utf-8")
        target = Path(temp) / output.name
        command = ["mpd2glb.sh", "-l", str(library), "-c", "draco", "--descriptions", str(descriptions),
                   "--map-color", "16,Pearl_Dark_Grey", "-o", str(target), str(Path(path).resolve())]
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode or not target.exists():
            raise ValueError(f"GLB conversion failed: {result.stdout}\n{result.stderr}")
        target.replace(output)
    return dict(output=str(output), log=(result.stdout + "\n" + result.stderr)[-8000:],
                note="Preview maps unresolved colour 16 to Pearl Dark Grey. In source, 16 means inherited current colour. MPD remains authoritative.")


def render(path, library, outdir, *, views=("home", "top", "front"), timeout=90, bounds=None):
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    results = []
    # Unique temporary outputs ensure an old artifact cannot make a failed run pass.
    with TemporaryDirectory(prefix=".render-", dir=outdir) as temp:
        path,library,embedded_names=cad_source(path,library,temp)
        for view in views:
            if view not in {"home", "front", "back", "left", "right", "top", "bottom"}:
                raise ValueError(f"Unknown view {view}")
            target = Path(temp) / f"{view}.png"
            command = ["leocad", "-l", str(library), "-i", str(target), "-w", "1000", "-h", "800",
                       "--aa-samples", "4", "--shading", "full", "--line-width", "1",
                       "--no-highlight", "--no-fade-steps", str(Path(path).resolve())]
            if bounds is None:
                command += ["--viewpoint", view]
            if bounds is not None:
                command += view_camera(bounds, view)
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            if result.returncode or not target.exists():
                raise ValueError(f"LeoCAD render failed: {result.stdout}\n{result.stderr}")
            destination = outdir / target.name
            target.replace(destination)
            results.append(str(destination))
        bom = Path(temp) / "leocad-bom.csv"
        result = subprocess.run(["leocad", "-l", str(library), "-csv", str(bom), str(Path(path).resolve())], capture_output=True, text=True, timeout=timeout)
        if result.returncode or not bom.exists():
            raise ValueError(f"LeoCAD BOM failed: {result.stdout}\n{result.stderr}")
        restore_bom_names(bom,embedded_names)
        bom.replace(outdir / bom.name)
    return dict(images=results, bom=str(outdir / "leocad-bom.csv"), embedded_definitions_materialized=len(embedded_names),
                visual_review="required: open and inspect the images")

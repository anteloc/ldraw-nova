"""Read the supplied generated categories as metadata, without importing py4bricks.

The source tree and its author/licence notices remain untouched. Current library
records determine availability and colours; cached dimensions are search hints.
"""
from __future__ import annotations

import ast
import copy
import math
import os
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

from .common import RESOURCE_DATA, jsonable


def category_path():
    path = Path(os.environ.get('LDRAW_CATEGORIES', RESOURCE_DATA / 'categories')).expanduser().resolve()
    if not (path / 'parts').is_dir():
        raise ValueError(f'Categories missing at {path}; set LDRAW_CATEGORIES or use numeric part references')
    return path


def assignments(path):
    for node in ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path)).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            yield node.targets[0].id, node.value, node.lineno


def signature(root):
    return tuple((str(p.relative_to(root)),p.stat().st_mtime_ns,p.stat().st_size)
                 for p in sorted(root.rglob('*.py')))


@lru_cache(maxsize=2)
def _load(root, stamp):
    root = Path(root)
    entries = {}
    for path in sorted((root/'parts').rglob('*.py')):
        if path.name == '__init__.py':
            continue
        category = '.'.join(path.relative_to(root/'parts').with_suffix('').parts)
        for name,value,line in assignments(path):
            if isinstance(value,ast.Constant) and isinstance(value.value,str):
                symbol = category+'.'+name
                entries[symbol] = dict(symbol=symbol,category=category,code=value.value.casefold().removesuffix('.dat'),
                                       source=str(path),line=line,internal_hint=name.startswith('_'))
    colours = {}
    for name,node,line in assignments(root/'colours.py'):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='Colour':
            fields={k.arg:ast.literal_eval(k.value) for k in node.keywords}
            colours[name] = dict(symbol='colours.'+name,code=fields['code'],snapshot=fields,
                                  source=str(root/'colours.py'),line=line)
    dimensions = next((ast.literal_eval(v) for n,v,_ in assignments(root/'dimensions.py') if n=='PartsDimensions'),{})
    return entries,colours,dimensions


def catalog_data():
    root=category_path()
    return _load(str(root),signature(root))


def resolve_part(symbol, parts):
    key=symbol.removeprefix('@')
    entry=catalog_data()[0].get(key)
    if entry is None:
        raise ValueError(f'Unknown category symbol {symbol}; use catalog parts to find an exact name')
    code=entry['code']
    if parts.find_part(code=code) is None:
        raise ValueError(f'{symbol} resolves to {code}.dat, which is absent from the installed library')
    return code+'.dat'


def resolve_colour(symbol, parts):
    key=symbol.removeprefix('@').removeprefix('colours.')
    entry=catalog_data()[1].get(key)
    if entry is None or entry['code'] not in parts.colours_by_code:
        raise ValueError(f'Unknown/unavailable category colour {symbol}')
    return entry['code']


def resolve_plan(plan, parts):
    """Leave the editable symbolic plan intact; resolve only the build copy."""
    result=copy.deepcopy(plan)
    references, colours = {}, {}
    for section in result['sections']:
        for step in section['steps']:
            for p in step:
                if p['ref'].startswith('@'):
                    symbol=p['ref']
                    if symbol not in references:
                        references[symbol] = resolve_part(symbol,parts)
                    p['ref']=references[symbol]
                    p.setdefault('purpose',symbol)
                if isinstance(p['colour'],str):
                    symbol=p['colour']
                    if symbol not in colours:
                        colours[symbol] = resolve_colour(symbol,parts)
                    p['colour']=colours[symbol]
    return result


def search_catalog(parts, kind, query='', *, category=None, limit=12, include_unavailable=False, max_size=None, measure=False):
    if kind not in {'categories', 'parts', 'colours'}:
        raise ValueError('Choose categories, parts, or colours')
    if limit < 1:
        raise ValueError('Result limit must be positive')
    if kind != 'parts' and (category or max_size is not None or measure):
        raise ValueError('--category, --max-size and --measure apply to catalog parts')
    if max_size is not None and (len(max_size) != 3 or any(not math.isfinite(v) or v <= 0 for v in max_size)):
        raise ValueError('Maximum dimensions must be three finite positive LDU values')
    entries,colours,dimensions=catalog_data()
    if kind=='categories':
        return dict(source=str(category_path()),categories=dict(sorted(Counter(e['category'] for e in entries.values()).items())),
                    note='Counts are category symbols, including legacy entries; search results check the installed library.')
    rows=[]
    terms=query.casefold().split()
    if kind=='colours':
        for entry in colours.values():
            current=parts.colours_by_code.get(entry['code'])
            if not all(t in (entry['symbol']+' '+str(entry['code'])).casefold() for t in terms):continue
            if current is None and not include_unavailable:continue
            rows.append(dict(symbol='@'+entry['symbol'],code=entry['code'],available=current is not None,
                             current=jsonable(current) if current else None,source=entry['source'],line=entry['line']))
    else:
        categories={e['category'] for e in entries.values()}
        if category and category not in categories:raise ValueError(f'Unknown category {category}; run catalog categories')
        for symbol,entry in entries.items():
            if category and entry['category']!=category:continue
            code=entry['code']
            title=parts.by_code.get(code,'')
            words=re.sub(r'([a-z])([A-Z])',r'\1 \2',symbol).replace('_',' ')
            haystack=(symbol+' '+words+' '+title+' '+code).casefold()
            if not all(re.search(r'(?<![0-9])'+re.escape(t)+r'(?![0-9])',haystack) if t.isdigit() else t in haystack for t in terms):continue
            available=code in parts.by_code
            legacy=entry['internal_hint'] or title.startswith(('~','=')) or entry['category'] in {'obsoletes','helpers'}
            if not include_unavailable and (not available or legacy):continue
            dims=dimensions.get(code)
            if max_size and (not dims or any(dims.get('ldu_'+axis,float('inf'))>bound for axis,bound in zip('xyz',max_size))):continue
            rows.append(dict(ref='@'+symbol,filename=code+'.dat',description=title or words,
                             category=entry['category'],available=available,legacy_or_internal=legacy,
                             dimensions_hint=dims,source=entry['source'],line=entry['line']))
        rows.sort(key=lambda r:(r['legacy_or_internal'],not r['available'],len(r['description']),r['ref']))
    selected=rows[:limit]
    if measure and kind=='parts':
        for row in selected:
            if not row['available']:continue
            g=parts.geometry(row['filename'].removesuffix('.dat'))
            row['geometry_complete']=g.complete
            row['measured_size_ldu']=jsonable(g.bounds.size) if g.bounds else None
            hint=row['dimensions_hint']
            row['dimensions_disagree']=bool(hint and g.bounds and any(abs(hint['ldu_'+axis]-getattr(g.bounds.size,axis))>0.05 for axis in 'xyz'))
    return dict(total=len(rows),results=selected,truncated=len(rows)>limit,
                note='Source categories are discovery metadata. Dimensions include studs/decorations and are not stacking heights or connection frames. Inspect selected parts; colour/part manufacture combinations are not known.')

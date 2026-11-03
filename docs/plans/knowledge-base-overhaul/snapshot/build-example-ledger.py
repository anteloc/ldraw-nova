"""Planning inventory. Does not move sources or generate models."""
import hashlib,json,re,subprocess
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path.cwd(); OUT=ROOT/'output/kb-visual-audit'
read=lambda name:json.loads((OUT/name).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def relative(p):
 p=Path(p)
 try:return str(p.relative_to(ROOT))
 except ValueError:return str(p)
def findings(collection,key,item):
 if item.get('findings'):return ' '.join(item['findings'])
 if item.get('finding'):return item['finding']
 if item.get('decision'):return item['decision']
 text=(OUT/(collection+'-findings.md')).read_text()
 m=re.search(r'^## '+re.escape(key)+r'(?:\s*[:—].*)?\n(.*?)(?=^## |\Z)',text,re.M|re.S)
 if m:return m.group(1).strip().split('\n\n')[0].replace('\n',' ')
 return item.get('visual_observation') or item.get('disposition') or 'Apply the linked per-section findings and preserve all existing check limitations.'
rows=[]
def add(collection,item,owner,destination,*,anchor=None,action='retain scoped lesson; package and correct',scope='construction',alias_family=None,pointer=None,work=None):
 key=item.get('id','titan');audit=collection+'-audit.json'
 source=item.get('source',item.get('constraints'))
 if isinstance(source,dict):source=source.get('source')
 hashes=[]
 if source:
  expected=item.get('source_sha256',item.get('constraints_sha256'))
  if isinstance(item.get('source'),dict):expected=item['source'].get('source_sha256')
  if expected:hashes.append({'path':relative(source),'sha256':expected,'role':'upstream_original' if collection=='reference' and '/models-annotated/' in source else 'audited_source'})
 for evidence in item.get('evidence',[]):
  if isinstance(evidence,dict) and evidence.get('source_sha256') and evidence.get('source'):
   hashes.append({'path':relative(evidence['source']),'sha256':evidence['source_sha256']})
 if item.get('synthesis_sha256'):hashes.append({'path':item['synthesis'],'sha256':item['synthesis_sha256']})
 frozen=[]
 if collection=='reference' and (ROOT/owner/'card.json').exists():
  card=json.loads((ROOT/owner/'card.json').read_text())
  for name,expected in card.get('artifact_hashes',{}).items():
   artifact=ROOT/owner/name
   frozen.append(dict(path=relative(artifact),sha256=expected,current_match=artifact.is_file() and sha(artifact)==expected))
 for h in hashes:
  p=Path(h['path']);h['current_match']=p.is_file() and sha(p)==h['sha256']
 rows.append(dict(id=f'{collection}:{key}',collection=collection,legacy_key=key,source_owner=owner,proposed_destination=destination,lesson_anchor=anchor,action=action,search_scope=scope,admission='conditional on linked corrections, fresh evidence and existing export gates' if scope in ['construction','tutorial'] else 'excluded from default construction recommendations',aliases=[f'{alias_family}:{key}'] if alias_family else [],audit=f'output/kb-visual-audit/{audit}',audit_pointer=pointer,findings=f'output/kb-visual-audit/{collection}-findings.md',required_work=work or findings(collection,key,item),source_hash_checks=hashes,frozen_artifact_checks=frozen))
subnames=['8081-front-axle','42075-differential-axle','42050-v8-engine','42078-headlight-cluster','10269-primary-drive-cover','10283-oms-pod','75060-pivoting-cockpit','7784-bat-grille','10182-roof-tower','10298-vespa-leg-shield','21307-engine-exhaust','21319-patterned-floor','21309-radial-hub','41627-yoda','10278-vine-column','10272-glazed-wall','10267-christmas-tree','10258-rounded-roof','21046-recessed-entrance','10226-striped-rudder','40412-buckbeak-head','21303-walle-eye','10183-inverted-underbody','30050-micro-shuttle','10294-hull-panels','10294-hull-panels','75276-mouth-grille','31031-chameleon','21325-tree-trunk','10030-micro-tantive']
for idx,(item,name) in enumerate(zip(read('submodel-audit.json')['items'],subnames)):
 add('submodel',item,str(Path(item['guide']).parent),'examples/'+name,anchor=item['id'] if name=='10294-hull-panels' else None,scope='inspiration' if item['current_use']=='inspiration' else 'construction',alias_family='submodel',pointer=f'/items/{idx}')
refnames={'classic-truck-cab':'6594-tractor-unit','mini-truck-cab':'4915-tractor-unit','rounded-cockpit-shell':'10212-rounded-side-covers','spacecraft-wheel-module':'5980-buggy-chassis','classical-arch-bay':'classical-arch-bay','arcade-bay':'classical-arch-bay'}
d=read('reference-audit.json')
for group in ['items','recipes']:
 for idx,item in enumerate(d[group]):
  key=item['id'];owner='examples/reference-atlas/'+('recipes/' if group=='recipes' else '')+key
  add('reference',item,owner,'examples/'+refnames.get(key,key),anchor='adjustable-recipe' if key=='arcade-bay' else ('source-study' if key=='classical-arch-bay' else None),alias_family='reference',pointer=f'/{group}/{idx}')
for idx,item in enumerate(read('mechanical-audit.json')['items']):
 name={'independent-suspension':'paired-suspension-axles'}.get(item['id'],item['id'])
 add('mechanical',item,item['package'],'examples/'+name,alias_family='mechanism' if '/mechanism-atlas/' in item['package'] else 'technic',pointer=f'/items/{idx}')
structowners={'workshop-machine':'examples/workshop/workshop','mounted-frame-named':'examples/workshop/mounted-frame','retained-chain-drive':'examples/workshop/chain-drive'}
for idx,item in enumerate(read('structural-audit.json')['items']):
 key=item['id'];dest='mounted-service-frame' if key in ['mounted-frame-named','service-platform'] else key
 add('structural',item,structowners.get(key,'examples/technic-atlas/'+key),'examples/'+dest,action='merge identical geometry; named plan is canonical' if key=='service-platform' else 'retain scoped lesson; package and correct',alias_family='technic',pointer=f'/items/{idx}')
for idx,item in enumerate(read('vehicle-audit.json')['items']):
 key=item['id'];small=idx>=3
 source=Path(item['source']);owner=str(source.parent)
 add('vehicle',item,owner,'examples/vehicle-fittings' if small else 'examples/'+key,anchor=key if small else None,alias_family='vehicle',pointer=f'/items/{idx}')
for idx,item in enumerate(read('building-audit.json')['items']):
 key=item['id'];source=Path(item['source']);small=key not in ['cottage','conservatory','skyline','dormer-roof']
 dest={'cottage':'cottage','conservatory':'glasshouse-walls','skyline':'microscale-skyline','dormer-roof':'cottage'}.get(key,'building-fittings')
 add('building',item,str(source.parent),'examples/'+dest,anchor=key if small or key=='dormer-roof' else None,action='extract reviewed wall shell and its dependency closure; retire whole-scene recommendation' if key=='conservatory' else ('improve cottage and nested weak tree/bench before promotion' if key=='cottage' else 'retain scoped lesson; consolidate fitting variants'),alias_family='building',pointer=f'/items/{idx}')
for idx,item in enumerate(read('snot-audit.json')['items']):
 add('snot',item,'examples/snot/'+item['id'],'examples/'+item['id'],pointer=f'/items/{idx}')
for c,parent in [('f40','ferrari-f40'),('bwing6208','b-wing-6208')]:
 for idx,item in enumerate(read(c+'-audit.json')['items']):
  add(c,item,'examples/snot/'+parent+'/studies/'+item['id'],'examples/'+parent,anchor=item['id'],pointer=f'/items/{idx}',action='retain study within parent package; distinguish child, callout and cutaway')
for idx,item in enumerate(read('spaceship-audit.json')['items']):
 key=item['id'];dest={'b-wing':'75050-b-wing','star-destroyer-study':'10030-star-destroyer','ucs-y-wing-study':'75181-y-wing'}.get(key,key)
 add('spaceship',item,'examples/spaceship-atlas/'+key,'examples/'+dest,scope='inspiration' if key in ['star-destroyer-study','ucs-y-wing-study'] else 'construction',alias_family='spaceship',pointer=f'/items/{idx}')
standowners={'copper-lane':'examples/modular-street','copper-bean':'examples/copper-bean','sakura-garden':'examples/sakura-garden','cathedral-window':'examples/cathedral/window-fit.mpd','cathedral-rose':'examples/cathedral/rose-fit.mpd','gear-drive':'examples/technic-studies/gear-drive','bridge-tutorial':'examples/bridge.plan.json','python-api':'examples/python_api.py','shadow-snap':'examples/shadow-snap.plan.json'}
for idx,item in enumerate(read('standalone-audit.json')['items']):
 key=item['id'];dest='cathedral-glazing' if key.startswith('cathedral-') else ('plan-basics' if key in ['bridge-tutorial','python-api','shadow-snap'] else key)
 add('standalone',item,standowners[key],'examples/'+dest,anchor=key if dest in ['cathedral-glazing','plan-basics'] else None,scope='tutorial' if dest=='plan-basics' else 'construction',pointer=f'/items/{idx}')
for idx,item in enumerate(read('remaining-standalone-audit.json')['entries']):
 key=item['id'];scope='hold' if key=='atlas-root' else ('diagnostic' if key=='turntable' else 'construction')
 dest='examples/archive/atlas-crane-2026-11-03' if key=='atlas-root' else ('tests/fixtures/turntable-seating' if key=='turntable' else 'examples/atlas-crane-studies')
 add('remaining-standalone',item,'examples/turntable-frame' if key=='turntable' else 'examples/atlas-crane',dest,anchor=None if key in ['atlas-root','turntable'] else key,pointer=f'/entries/{idx}',scope=scope,action='hold whole source; extract only named selected sections' if key.startswith('atlas-') else 'retain known-failure fixture')
for idx,item in enumerate(read('lsynth-legacy-audit.json')['items']):
 add('lsynth-legacy',item,item['constraints'],'lsynth-examples',anchor=item['id'],scope='research',action='retain raw source/synthesis and provenance; exclude default',pointer=f'/items/{idx}')
for idx,item in enumerate(read('constraint-lab-audit.json')['items']):
 add('constraint-lab',item,'examples/flex/constraint-lab','tests/fixtures/flex-constraints',anchor=item['id'],scope='diagnostic',action='retain executable fixture and expected failure classification',pointer=f'/items/{idx}')
d=read('mounted-flex-audit.json');add('mounted-flex',d['press'],'examples/flex/pneumatic-press','examples/pneumatic-press',pointer='/press',work='Use named.plan.json and named-review evidence as canonical. Preserve original-source compatibility/evidence separately. Correct C-frame to portal frame; keep three distinct hoses, actual fitting interfaces and static-only scope.')
for idx,item in enumerate(d['minimal_examples']):
 add('mounted-flex',item,item['source'],'examples/flex-basics',anchor=item['id'],scope='tutorial',pointer=f'/minimal_examples/{idx}')
d=read('replacement-audit.json')
for idx,item in enumerate(d['admitted_candidates']):
 add('replacement',item,'output/an225-mriya' if item['id']=='an225' else 'output/boombox','examples/an225-mriya' if item['id']=='an225' else 'examples/boombox',pointer=f'/admitted_candidates/{idx}')
add('replacement',dict(d['held_root_only'],id='titan'),'output/titan','output/titan',scope='hold',action='retain research in place; no submodel admission',pointer='/held_root_only')
assert len(rows)==187,len(rows)
assert len({r['id'] for r in rows})==187
for row in rows:
 upstream_stale=any(not h['current_match'] and h.get('role')=='upstream_original' for h in row['source_hash_checks'])
 row['export_blocker']='Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.' if upstream_stale else None
 if upstream_stale:row['required_work']+=' Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.'
# Existing catalog aliases: deduplicate examples/details rows, never infer admission.
by_alias={alias:r for r in rows for alias in r['aliases']}
catalogs=[];retired=[]
for p in sorted((ROOT/'examples').glob('*-atlas/catalog.json')):
 family=p.parent.name.removesuffix('-atlas');seen=set()
 for group in ['examples','details']:
  for item in json.loads(p.read_text()).get(group,[]):
   alias=family+':'+item['key']
   if alias in seen:continue
   seen.add(alias)
   if alias not in by_alias:
    owner=relative(p.parent/item['key'])
    model=item.get('model')
    if model:owner=relative((p.parent/model).parent)
    rec=dict(alias=alias,source_owner=owner,proposed_destination='examples/archive/'+family+'/'+item['key'],action='retire from default; preserve legacy source pending any explicit reselection',search_scope='archive',visual_status='no new visual acceptance; not selected for retention',model=relative(p.parent/model) if model else None)
    retired.append(rec)
   catalogs.append(dict(alias=alias,catalog=relative(p),row_group=group,resolution=by_alias[alias]['id'] if alias in by_alias else 'retired',destination=by_alias[alias]['proposed_destination'] if alias in by_alias else retired[-1]['proposed_destination']))
# Explicitly held/unselected sources outside the catalog system.
extra=[
 dict(source_owner='examples/stadium',proposed_destination='examples/archive/stadium',search_scope='hold',action='Reconcile authoritative plan/generator and delivered model before any admission.'),
 dict(source_owner='output/goliath',proposed_destination='output/goliath',search_scope='research',action='Unfinished circuit/integration; process only, no model admission.'),
 dict(source_owner='output/jaguar-e-type',proposed_destination='output/jaguar-e-type',search_scope='hold',action='Reconcile source-specific reconstruction, attribution/restriction and completion before selection.'),
 dict(source_owner='examples/construction-studies',proposed_destination='docs/reports/construction-studies',search_scope='research',action='Preserve analysis/source evidence; deduplicate Copper Lane lessons against its one example package.'),
 dict(source_owner='examples/archive',proposed_destination='examples/archive',search_scope='archive',action='Keep archive excluded; no automatic resurrection or deletion.'),
 dict(source_owner='examples/technic-studies',proposed_destination='docs/reports/technic-studies',search_scope='research',action='Keep transferred historical source notes/images; gear-drive is the separately admitted child package.'),
]
extra.extend([
 dict(source_owner='examples/snot/ferrari-f40',proposed_destination='examples/ferrari-f40',search_scope='source-context',action='Preserve attributed source and selected-study evidence; unselected callouts and whole car remain source context, not admitted lessons.'),
 dict(source_owner='examples/snot/b-wing-6208',proposed_destination='examples/b-wing-6208',search_scope='source-context',action='Keep parent source, route dependency and study metadata; no automatic admission of other set objects.'),
 dict(source_owner='examples/cathedral',proposed_destination='examples/archive/cathedral',search_scope='archive',action='Retain whole scene and history outside default; move only the two reviewed glazing fittings and their plan/evidence companions.'),
 dict(source_owner='lsynth-examples',proposed_destination='lsynth-examples',search_scope='research',action='Retain synthesis companions, credits and previews with the raw corpus.'),
 dict(source_owner='examples/bridge.mpd',proposed_destination='examples/plan-basics',search_scope='tutorial',action='Move the reviewed MPD with bridge.plan.json; keep its section names.'),
])
for stem in ['window-fit','rose-fit']:
 for file in sorted((ROOT/'examples/cathedral').glob(stem+'.*')):
  extra.append(dict(source_owner=relative(file),proposed_destination='examples/cathedral-glazing',search_scope='evidence',action='Keep fitting plan, source and exact check report together; not whole-cathedral acceptance.'))
for row in rows:
 if row['collection']=='submodel':
  recipe=ROOT/'examples/submodel-atlas/recipes'/(row['legacy_key']+'.json')
  if recipe.exists():extra.append(dict(source_owner=relative(recipe),proposed_destination=row['proposed_destination'],search_scope='evidence',action='Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest.'))
# Per-file routing inventory. Prefix rules route dependencies with their package;
# many-to-one decisions remain explicit reconciliation, not destructive overwrites.
index=subprocess.check_output(['git','ls-files','-s','examples','lsynth-examples'],text=True).splitlines()
file_rows=[]
for line in index:
 head,path=line.split('\t',1); blob=head.split()[1]
 matches=[]
 for row in rows:
  prefix=row['source_owner'].rstrip('/')
  if path==prefix or path.startswith(prefix+'/'):matches.append((len(prefix),row['id'],row['proposed_destination']))
 for row in retired+extra:
  prefix=row['source_owner'].rstrip('/')
  if path==prefix or path.startswith(prefix+'/'):matches.append((len(prefix),row.get('alias',prefix),row['proposed_destination']))
 if matches:
  size=max(x[0] for x in matches);chosen=[x for x in matches if x[0]==size]
  assignment=sorted(set(x[1] for x in chosen));dest=sorted(set(x[2] for x in chosen));action='route with owner; reconcile shared/selected content before copying'
 else:
  assignment=['shared:'+path.split('/')[1]];dest=[str(Path(path).parent)];action='retain shared infrastructure during compatibility migration; replace generated catalogs/galleries, migrate reusable generators and preserve historical manifests outside default search'
 extraction_targets=[]
 if path.startswith('examples/atlas-crane/'):
  assignment=['remaining-standalone:atlas-root'];dest=['examples/archive/atlas-crane-2026-11-03'];action='archive original; selected sections are derived extractions, not a recursive copy into the study package'
  extraction_targets=['remaining-standalone:atlas-frame','remaining-standalone:atlas-outrigger','remaining-standalone:atlas-boom'] if path.endswith('atlas-crane.mpd') else []
 file_rows.append(dict(path=path,index_blob_oid=blob,owners=assignment,package_destinations=dest,action=action,selected_derivative_targets=extraction_targets))
# Original evidence is linked, not duplicated and not rewritten to simulate freshness.
result=dict(date='2026-11-03',status='planning_only',reviewed_entries=rows,legacy_catalog_aliases=catalogs,retired_catalog_entries=retired,additional_dispositions=extra,tracked_file_routes=file_rows,file_hash_scope='index_blob_oid identifies the git-index snapshot, not a hash of the current working file. Audited primary sources have independent current SHA-256 comparisons. Image freshness remains in the linked audits.',admission_rule='No visual or numeric pass is created by relocation. Linked visual findings and existing export checks remain binding; all construction destinations are conditional until corrections and migration checks pass.')
(OUT/'example-migration-ledger.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# Example package migration ledger','', 'Planning only, 2026-11-03. This maps all **187 visually audited candidate entries** to concrete package destinations, preserving their existing qualifications. It adds no visual acceptance. [Machine-readable ledger](example-migration-ledger.json) includes every catalog alias, current primary-source hash comparison and tracked-file routing inventory.','', 'Repeated colour variants, child models and visibility cutaways can share one package. The actual LDraw FILE names and provenance remain intact; a package rename does not rename its geometry. `lesson_anchor` identifies a README lesson, not an invented model section. Construction destinations remain conditional on the linked corrections and check scopes.','', '## Per-candidate decisions','']
for collection in dict.fromkeys(r['collection'] for r in rows):
 lines+=['### '+collection,'', '| Current candidate / owner | Proposed destination | Scope and action |','|---|---|---|']
 for row in rows:
  if row['collection']!=collection:continue
  target=row['proposed_destination']+('#'+row['lesson_anchor'] if row['lesson_anchor'] else '')
  lines.append(f"| `{row['legacy_key']}`<br/>`{row['source_owner']}` | `{target}` | **{row['search_scope']}** — {row['action']}. {row['required_work'].replace('|','/')} |")
 lines+=['',f"Per-section observations, parents and limits: [{collection} findings]({collection}-findings.md).",'']
lines+=['## Existing catalog entries not admitted','', 'Preserve their source for compatibility/history; remove their default recommendation and replacement fallback. These are not newly visually accepted. Re-selection would require the same visual/evidence gate.','', '| Legacy alias | Source | Proposed archive destination |','|---|---|---|']
for r in retired:lines.append(f"| `{r['alias']}` | `{r['source_owner']}` | `{r['proposed_destination']}` |")
lines+=['','## Other retained research and holds','','| Source | Destination | Decision |','|---|---|---|']
for r in extra:lines.append(f"| `{r['source_owner']}` | `{r['proposed_destination']}` | {r['action']} |")
lines+=['', '## File ownership and shared infrastructure','',f'The JSON inventories **{len(file_rows)} tracked files** under examples and lsynth-examples. Files with an owner travel with that package, subject to selective extraction and metadata consolidation; shared files remain at their existing location until their consumers are reconciled. No automatic recursive copy or deletion is authorized by this inventory.','', 'Parent source packages such as F40/B-wing retain their provenance and dependencies as a unit; only selected lessons enter search. The whole F40 source is not admitted by five reviewed studies. Atlas source travels as held provenance while only three named construction studies are extracted. The conservatory roof/whole scene is excluded even though its glazing selection is useful. Old test fixtures may retain their original paths until tests are migrated.','', 'Grouped fitting packages retain independent source files below their lesson IDs; do not concatenate unrelated snippets into an artificial model. Keep one README with scoped sections and generate index entries for those sections. Distinct imported source assemblies can keep distinct packages even when their subject names overlap.','', 'Shared atlas catalog/gallery generators, selections/manifests, reproduction helpers and root READMEs are infrastructure, not newly accepted examples. Replace authored catalog summaries with generated views of package metadata. Keep shared runtime geometry helpers in ldraw_tools; move or retire only the atlas orchestration layer after its consumers migrate.','', 'See [catalog and export compatibility plan](catalog-export-migration.md) for aliases, generator/export contracts, evidence relocation and acceptance checks.','']
(OUT/'example-migration-ledger.md').write_text('\n'.join(lines))
print(json.dumps(dict(audited_entries=len(rows),catalog_aliases=len(catalogs),retired_aliases=len(retired),tracked_files=len(file_rows),shared_or_ancillary_files=sum(r['owners'][0].startswith('shared:') for r in file_rows),source_hash_mismatches=sum(not h['current_match'] for r in rows for h in r['source_hash_checks']),frozen_artifact_mismatches=sum(not h['current_match'] for r in rows for h in r['frozen_artifact_checks']),scopes=dict(Counter(r['search_scope'] for r in rows))),indent=2))

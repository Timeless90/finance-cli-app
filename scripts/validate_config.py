from pathlib import Path
import ast
import json
import re
import tomllib
import yaml
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','hooks','.venv','node_modules','.local','vscode-development-setup','__pycache__','coverage','dist','playwright-report','test-results'}

def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError(f'Duplicate JSON key: {key}')
        result[key]=value
    return result

class UniqueLoader(yaml.SafeLoader): pass
def mapping(loader,node,deep=False):
    result={}
    for key_node,value_node in node.value:
        key=loader.construct_object(key_node,deep=deep)
        if key in result: raise ValueError(f'Duplicate YAML key: {key}')
        result[key]=loader.construct_object(value_node,deep=deep)
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
counts={'json':0,'toml':0,'yaml':0,'python':0,'frontmatter':0}
for path in ROOT.rglob('*'):
    if not path.is_file() or any(part in EXCLUDED for part in path.relative_to(ROOT).parts): continue
    if path.name.startswith('.env') or path.suffix in {'.key','.pem'}: continue
    if path.suffix=='.json': json.loads(path.read_text(),object_pairs_hook=unique);counts['json']+=1
    elif path.suffix=='.toml': tomllib.loads(path.read_text());counts['toml']+=1
    elif path.suffix in {'.yml','.yaml'}: yaml.load(path.read_text(),Loader=UniqueLoader);counts['yaml']+=1
    elif path.suffix=='.py': ast.parse(path.read_text());counts['python']+=1
    elif path.suffix=='.md' and path.read_text().startswith('---\n'):
        yaml.load(path.read_text().split('---\n',2)[1],Loader=UniqueLoader);counts['frontmatter']+=1
makefile=(ROOT/'Makefile').read_text()
labels=set()
for task in json.loads((ROOT/'.vscode/tasks.json').read_text())['tasks']:
    assert task['label'] not in labels
    labels.add(task['label'])
    assert task['runOptions']['runOn']=='default'
    assert re.search(r'^'+re.escape(task['args'][-1])+r':',makefile,re.M),task['label']
for name in ['compose.yml','compose.app.yml','compose.observability.yml']:
    services=yaml.safe_load((ROOT/name).read_text())['services']
    for service in services.values():
        for port in service.get('ports',[]): assert str(port).startswith('127.0.0.1:'),port
assert 'retain-on-failure' in (ROOT/'frontend/playwright.config.ts').read_text()
assert 'source.fixAll.ruff' in (ROOT/'.vscode/settings.json').read_text()
print('PASS config validation:',json.dumps(counts),';',len(labels),'task/Make mappings')

# The wizard's runtime copies must describe the same project.
project=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
backend_project=json.loads((ROOT/'backend/app/shared/project.json').read_text(encoding='utf-8'))
frontend_project=json.loads((ROOT/'frontend/src/app/project.json').read_text(encoding='utf-8'))
assert backend_project == {'name':project['name'],'service_name':project['id']+'-backend'}
assert frontend_project == {'name':project['name'],'description':project['description']}
assert tomllib.loads((ROOT/'backend/pyproject.toml').read_text())['project']['name'] == project['id']+'-backend'
assert json.loads((ROOT/'frontend/package.json').read_text())['name'] == project['id']+'-frontend'
print('PASS project identity consistency')
assert json.loads((ROOT/'.devcontainer/devcontainer.json').read_text(encoding='utf-8'))['name'] == project['name']
local_packages=[p for p in tomllib.loads((ROOT/'backend/uv.lock').read_text())['package'] if p.get('source') == {'editable':'.'}]
assert len(local_packages) == 1 and local_packages[0]['name'] == project['id']+'-backend'

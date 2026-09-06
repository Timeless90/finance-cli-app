"""Generate the path adapter for existing feature queries from Orval operations.

Orval owns transport, request URLs and model types. This adapter preserves feature
query keys and injectable fetch used by contract tests while migrating callers.
"""
from pathlib import Path
import json
import re
ROOT = Path(__file__).resolve().parents[1]
schema = json.loads((ROOT / 'backend/openapi.json').read_text())
source = (ROOT / 'frontend/src/generated/api.ts').read_text()
functions = dict(re.findall(r'export const (\w+) = async \((.*?)\): Promise<', source, re.S))
def camel(s):
    parts = re.split(r'[^a-zA-Z0-9]+',s)
    return parts[0] + ''.join(p[:1].upper()+p[1:] for p in parts[1:])
lines = ["// Generated from OpenAPI and Orval. Do not edit.", "import * as operations from './api';", "import type { ClientOptions } from '../shared/api/client';", 'export const dispatch = {']
types = []
for path,methods in schema['paths'].items():
 for method,op in methods.items():
  if method not in ['get','post','put','patch','delete']:continue
  name = camel(op['operationId']);signature=functions[name];args=[]
  path_params={camel(p['name']):p['name'] for p in op.get('parameters',[]) if p['in']=='path'}
  for i,param in enumerate(signature.split(',')):
   variable=param.strip().split(':')[0].rstrip('?').strip()
   if variable=='options':args.append('options.request')
   elif variable=='params':args.append(f'options.params?.query as Parameters<typeof operations.{name}>[{i}]')
   elif variable in path_params:args.append(f'String(options.params?.path?.[{json.dumps(path_params[variable])}]) as Parameters<typeof operations.{name}>[{i}]')
   else:args.append(f'options.body as Parameters<typeof operations.{name}>[{i}]')
  key=method.upper()+' '+path
  lines.append(f'{json.dumps(key)}: (options: ClientOptions) => operations.{name}({", ".join(args)}),')
  types.append(f'{json.dumps(key)}: Extract<Awaited<ReturnType<typeof operations.{name}>>, {{ status: 200 | 201 | 202 | 204 }}>["data"];')
lines+=['};', 'export type ResponseData = {',*types,'};']
(ROOT/'frontend/src/generated/dispatch.ts').write_text('\n'.join(lines)+'\n')

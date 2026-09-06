"""Run the complete local acceptance and leave an honest machine-readable result."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/'.local/acceptance.json'
PROJECT=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
BASE_ENV={**os.environ,'CFO_GOVERNANCE_DATABASE_URL':'postgresql://template:template-local@127.0.0.1:15432/template','APP_DB_PORT':'15432','CFO_TELEMETRY_ENABLED':'false','CFO_NAME':PROJECT['name'],'CFO_SERVICE_NAME':PROJECT['id']+'-backend'}
results=[]
def run(name,args,env=None):
    print('\n== '+name+' ==',flush=True)
    result=subprocess.run(args,cwd=ROOT,env=env or BASE_ENV)
    results.append({'check':name,'passed':result.returncode==0})
    if result.returncode: raise RuntimeError(name+' failed')
def request(url):
    with urllib.request.urlopen(url,timeout=5) as response:
        return json.load(response)
def wait(name,url,predicate):
    for _ in range(30):
        try:
            if predicate(request(url)):
                results.append({'check':name,'passed':True});return
        except (OSError,ValueError):pass
        time.sleep(1)
    results.append({'check':name,'passed':False})
    raise RuntimeError(name+' did not become ready')
def main():
    try:
        run('prerequisites',['make','doctor'])
        run('configuration',['make','compose-check'])
        run('quality and coverage',['make','check'])
        run('PostgreSQL',['make','infra-up'])
        run('persistence initialization',['make','backend-migrate'])
        run('persistence schema check',['make','backend-migration-check'])
        run('browser flow and accessibility',['make','e2e'])
        run('live finance workflows',['make','e2e-live'])
        env={**BASE_ENV,'CFO_TELEMETRY_ENABLED':'true'}
        run('Docker builds and all services',['docker','compose','--env-file','/dev/null','-f','compose.yml','-f','compose.app.yml','-f','compose.observability.yml','up','-d','--build','--wait'],env)
        wait('container API/database','http://127.0.0.1:8000/health/ready',lambda d:d.get('status')=='ready')
        wait('container frontend proxy','http://127.0.0.1:5173/health/ready',lambda d:d.get('status')=='ready')
        wait('Grafana','http://127.0.0.1:3000/api/health',lambda d:d.get('database')=='ok')
        wait('metrics scrape','http://127.0.0.1:9090/api/v1/query?'+urllib.parse.urlencode({'query':'up{job="backend-otel"}'}),lambda d:any(row['value'][1]=='1' for row in d.get('data',{}).get('result',[])))
        wait('traces','http://127.0.0.1:3200/api/search',lambda d:bool(d.get('traces')))
        wait('correlated logs','http://127.0.0.1:3100/loki/api/v1/query_range?'+urllib.parse.urlencode({'query':'{service_name='+json.dumps(PROJECT['id']+'-backend')+'}'}),lambda d:bool(d.get('data',{}).get('result')))
    except (RuntimeError,OSError) as error:
        print(str(error),file=sys.stderr)
        if not results or results[-1]['passed']: results.append({'check':'execution','passed':False,'error':str(error)})
    finally:
        RESULT.parent.mkdir(parents=True,exist_ok=True)
        RESULT.write_text(json.dumps({'complete':bool(results) and all(x['passed'] for x in results),'checks':results},indent=2)+'\n')
        print('Result:',RESULT)
        print('Services and volumes retained. Stop with make containers-down and make observability-down.')
    return 0 if results and all(x['passed'] for x in results) else 1
if __name__=='__main__':sys.exit(main())

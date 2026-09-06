"""Run local services; terminate both child process groups on failure or Ctrl+C."""
from pathlib import Path
import os
import signal
import subprocess
import sys
import time
ROOT = Path(__file__).resolve().parents[1]

def main():
    if os.environ.get('TEMPLATE_INFRA_MANAGED') != '1':
        subprocess.run(['make', 'infra-up'], cwd=ROOT, check=True)
    if '--full' in sys.argv:
        if os.environ.get('TEMPLATE_INFRA_MANAGED') == '1':
            raise SystemExit('dev-full is a host command. Use make dev inside the Dev Container.')
        subprocess.run(['make', 'observability-up'], cwd=ROOT, check=True)
        os.environ['CFO_TELEMETRY_ENABLED'] = 'true'
    os.environ.setdefault('CFO_GOVERNANCE_DATABASE_URL', 'postgresql://template:template-local@127.0.0.1:15432/template')
    os.environ.setdefault('CFO_IMPORT_STORAGE_PATH', str(ROOT / '.local/migrated/imports'))
    os.environ.setdefault('CFO_LOCAL_GATEWAY', 'true')
    children = []
    def stop(_signal=None, _frame=None):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        for target in ['backend-dev', 'frontend-local']:
            children.append(subprocess.Popen(['make', target], cwd=ROOT, start_new_session=True))
        while all(child.poll() is None for child in children):
            time.sleep(0.25)
        raise SystemExit(next((child.returncode or 1 for child in children if child.poll() is not None), 1))
    except KeyboardInterrupt:
        pass
    finally:
        for child in children:
            if child.poll() is None:
                try: os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError: pass
        for child in children:
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try: os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                child.wait()
        print('App processes stopped. PostgreSQL data retained; use make infra-down to stop infrastructure.')
if __name__ == '__main__': main()

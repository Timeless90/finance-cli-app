"""Install the agreed toolchain dependencies and generate the API client."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]

def run(args, cwd=ROOT):
    subprocess.run(args, cwd=cwd, check=True)

def main():
    version = subprocess.check_output(['node', '-p', 'process.versions.node'], text=True).strip()
    if sys.version_info[:2] != (3, 13) or version.split('.')[0] != '24':
        raise SystemExit('Use mise install, then mise exec -- make install (Python 3.13 / Node 24).')
    backend, frontend = ROOT/'backend', ROOT/'frontend'
    if not (backend/'uv.lock').exists():
        print('Initial dependency resolution: generating backend/uv.lock.', flush=True)
        run(['uv', 'lock'], backend)
    run(['uv', 'sync', '--locked'], backend)
    if not (frontend/'pnpm-lock.yaml').exists():
        print('Initial dependency resolution: generating frontend/pnpm-lock.yaml.', flush=True)
        run(['pnpm', 'install', '--lockfile-only'], frontend)
    run(['pnpm', 'install', '--frozen-lockfile'], frontend)
    run(['make', 'api-generate'])
    # Personalized HTML titles may exceed Prettier's line width. Format only
    # the frontend fields owned by initialization, after tools are installed.
    run(['pnpm', 'exec', 'prettier', '--write', 'index.html',
         'src/app/project.json', 'package.json'], frontend)
    run(['pnpm', 'exec', 'playwright', 'install', 'chromium'], frontend)
    print('Dependencies installed. Keep both lockfiles and generated contract/client in Git.')
if __name__ == '__main__': main()

"""Compare regenerated artifacts to current files, including before the first commit."""
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
def snapshot():
    files = [ROOT/'backend/openapi.json', *(ROOT/'frontend/src/generated').rglob('*')]
    return {str(p.relative_to(ROOT)): p.read_bytes() for p in files if p.is_file()}
before = snapshot()
subprocess.run(['make', 'api-generate'], cwd=ROOT, check=True)
if before != snapshot():
    raise SystemExit('API drift detected. Review regenerated OpenAPI/client files and keep them in Git.')
print('PASS: API contract and generated client are current.')

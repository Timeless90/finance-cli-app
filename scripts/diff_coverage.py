"""Normalize both stack reports to Git-root paths and report changed-line coverage."""
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def normalize(report: Path, stack: str) -> Path:
    tree = ET.parse(report)
    sources = tree.getroot().find('sources')
    raw_sources = [element.text or '' for element in sources] if sources is not None else []
    for node in tree.findall('.//class'):
        filename = node.attrib['filename']
        candidates = []
        for source in raw_sources:
            base = Path(source)
            candidates.append((base if base.is_absolute() else ROOT / stack / base) / filename)
        candidates += [ROOT / stack / filename, ROOT / filename]
        match = next((p.resolve() for p in candidates if p.is_file() and p.resolve().is_relative_to(ROOT)), None)
        if match is None:
            raise RuntimeError(f'Coverage source could not be matched: {stack}/{filename}')
        node.attrib['filename'] = str(match.relative_to(ROOT))
    if sources is None:
        sources = ET.SubElement(tree.getroot(), 'sources')
    sources.clear()
    ET.SubElement(sources, 'source').text = str(ROOT)
    destination = ROOT / '.local/coverage' / (stack + '.xml')
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(destination, encoding='utf-8', xml_declaration=True)
    return destination


def main():
    base = os.environ.get('DIFF_BASE', 'HEAD')
    if subprocess.run(['git', 'rev-parse', '--verify', base], cwd=ROOT, capture_output=True).returncode:
        print('Diff coverage not available before the initial commit. Global 80% gates still apply.')
        return
    for stack, report in [('backend', 'backend/coverage.xml'), ('frontend', 'frontend/coverage/cobertura-coverage.xml')]:
        normalized = normalize(ROOT / report, stack)
        cmd = ['uv', 'run', '--project', 'backend', '--locked', 'diff-cover', str(normalized), '--compare-branch', base]
        if os.environ.get('DIFF_COVERAGE_MIN'):
            cmd += ['--fail-under', os.environ['DIFF_COVERAGE_MIN']]
        subprocess.run(cmd, cwd=ROOT, check=True)
    if not os.environ.get('DIFF_COVERAGE_MIN'):
        print('Diff coverage reported without a threshold: no percentage was agreed in the original decisions.')

if __name__ == '__main__':
    main()

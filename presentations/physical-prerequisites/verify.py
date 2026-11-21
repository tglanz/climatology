#!/usr/bin/env python3
"""Check PDF navigation and equation presence; optionally render every page for QA.

Requires pypdf; --render additionally requires Pillow and Poppler's pdftoppm.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--render', action='store_true')
args = parser.parse_args()
reader = PdfReader(HERE / 'physical-prerequisites.pdf')
text = '\n'.join(page.extract_text() for page in reader.pages)
manuscript = (HERE / 'physical-prerequisites.md').read_text()
missing = [tag for tag in re.findall(r'\\tag\{([^}]+)\}', manuscript)
           if '(' + tag + ')' not in text]
assert not missing, f'Missing numbered equations: {missing}'
assert '[@' not in text, 'Unprocessed citation'
assert reader.outline, 'Missing PDF bookmarks'
names = reader.named_destinations
links = 0
for page_number, page in enumerate(reader.pages, 1):
    lines = page.extract_text().splitlines()
    assert len(lines) >= 3, f'Missing content/header on page {page_number}'
    for ref in page.get('/Annots', []):
        annotation = ref.get_object()
        action = annotation.get('/A', {})
        if action.get('/S') == '/GoTo':
            destination = action.get('/D')
            if isinstance(destination, str):
                assert destination in names, f'Broken destination {destination}'
            links += 1
        elif '/Dest' in annotation:
            destination = annotation['/Dest']
            if isinstance(destination, str):
                assert destination in names, f'Broken destination {destination}'
            links += 1
assert links >= 60, f'Too few internal links: {links}'
report = {'pages': len(reader.pages), 'internal_links': links,
          'named_destinations': len(names), 'numbered_equations': len(re.findall(r'\\tag\{', manuscript)),
          'headers': [{'pdf_page': i + 1, 'lines': p.extract_text().splitlines()[:2]}
                      for i, p in enumerate(reader.pages)]}
qa = HERE / 'qa'
qa.mkdir(exist_ok=True)
(qa / 'pdf-checks.json').write_text(json.dumps(report, indent=2) + '\n')
if args.render:
    from PIL import Image, ImageDraw
    for pattern in ('page-*.png', 'sheet-*.png'):
        for generated in qa.glob(pattern):
            generated.unlink()
    subprocess.run(['pdftoppm', '-r', '90', '-png',
                    str(HERE / 'physical-prerequisites.pdf'), str(qa / 'page')], check=True)
    paths = sorted(qa.glob('page-*.png'))
    assert len(paths) == len(reader.pages)
    for start in range(0, len(paths), 4):
        cells = []
        for path in paths[start:start + 4]:
            with Image.open(path) as source:
                page = source.convert('RGB')
                page.thumbnail((740, 1050))
                cells.append(page.copy())
        sheet = Image.new('RGB', (1520, 2180), '#cccccc')
        draw = ImageDraw.Draw(sheet)
        for offset, page in enumerate(cells):
            x, y = (offset % 2) * 760 + 10, (offset // 2) * 1090 + 25
            sheet.paste(page, (x, y))
            draw.text((x, y - 18), f'PDF page {start + offset + 1}', fill='black')
        sheet.save(qa / f'sheet-{start // 4 + 1:02d}.png')
print(json.dumps({k: v for k, v in report.items() if k != 'headers'}, indent=2))

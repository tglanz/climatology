#!/usr/bin/env python3
"""Assemble the shared Markdown chapters and render the mathematical guide."""
from pathlib import Path
import argparse
import re
import subprocess
import hashlib
import json
from sync_book import sync

ROOT = Path(__file__).resolve().parent
CHAPTERS = sorted((ROOT / 'chapters').glob('*.md'))
SOURCE = ROOT / 'mathematical-prerequisites.md'


def assemble(check=False):
    chapters = [p.read_text() for p in CHAPTERS]
    toc = ['<nav aria-label="Contents">', '<ul>']
    for text in chapters:
        title, anchor = re.match(r'# (.*?) \{#(.*?)\}', text).groups()
        toc.append(f'<li><a href="#{anchor}">{title}</a></li>')
    toc += ['<li><a href="#answers">Self-test answers</a></li>',
            '<li><a href="#references">References</a></li>', '</ul>', '</nav>']
    metadata = '''---
title: "Mathematical prerequisites"
subtitle: "From fields and conservation to spherical analysis and operator maps"
date: "21 November 2026"
lang: en-US
documentclass: report
classoption: [oneside, openany]
fontsize: 11pt
papersize: a4
geometry: [left=23mm, right=23mm, top=26mm, bottom=24mm]
mainfont: texgyrepagella-regular.otf
mainfontoptions: [BoldFont=texgyrepagella-bold.otf, ItalicFont=texgyrepagella-italic.otf, BoldItalicFont=texgyrepagella-bolditalic.otf]
mathfont: texgyrepagella-math.otf
monofont: texgyrecursor-regular.otf
colorlinks: true
linkcolor: MidnightBlue
urlcolor: MidnightBlue
citecolor: MidnightBlue
toc-depth: 2
numbersections: true
bibliography: ../../book/references.bib
link-citations: true
header-includes:
  - \\usepackage[dvipsnames]{xcolor}
---

'''
    references = '\n# References {.unnumbered #references}\n\n::: {#refs}\n:::\n'
    assembled = (metadata + '\n'.join(toc) + '\n\n' +
                      (ROOT / 'preface.md').read_text() + '\n' +
                      '\n'.join(chapters) + '\n' +
                      (ROOT / 'answers.md').read_text() + '\n' +
                      (ROOT / 'repository-map.md').read_text() + references)
    if check:
        assert SOURCE.read_text() == assembled, 'Assembled Markdown is out of sync'
    else:
        SOURCE.write_text(assembled)
    return SOURCE


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--sync-book', action='store_true', help='Synchronize general mathematical chapters without building PDF')
    parser.add_argument('--check', action='store_true', help='Check source structure and book parity without writing')
    args = parser.parse_args()
    if args.check:
        for path in CHAPTERS:
            text = path.read_text()
            assert text.isascii(), path
            assert text.count('$$') % 2 == 0, path
            for heading, body in re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', text, re.M | re.S):
                if heading != 'Chapter summary and self-test':
                    assert body.lstrip().startswith('**Result and motivation.**'), (path, heading)
            assert '## Chapter summary and self-test' in text, path
        tags = re.findall(r'\\tag\{([^}]+)\}', '\n'.join(p.read_text() for p in CHAPTERS))
        assert len(tags) == len(set(tags)), 'Duplicate equation tags'
        for number, path in enumerate(CHAPTERS, 1):
            actual = re.findall(r'\\tag\{([^}]+)\}', path.read_text())
            assert actual == [f'{number}.{i}' for i in range(1, len(actual)+1)], path
        sync(check=True)
        assemble(check=True)
        print(f'Checked {len(CHAPTERS)} chapters, {len(tags)} unique sequential equations, and book source parity.')
        return
    source = assemble()
    if args.sync_book:
        sync()
        return
    if not args.source_only:
        tex = ROOT / '.build' / 'guide.tex'
        tex.parent.mkdir(exist_ok=True)
        pdf_input = re.sub(r'<nav.*?</nav>', '', source.read_text(), flags=re.S)
        subprocess.run(['pandoc', '-', '--from=markdown', '--standalone', '--citeproc',
                        '--number-sections', '--toc', '--top-level-division=chapter',
                        '--include-in-header=header.tex', '--lua-filter=headers.lua', '--to=latex',
                        '--output=' + str(tex)], cwd=ROOT, check=True, input=pdf_input, text=True)
        tex.write_text(tex.read_text().replace(r'\maketitle', r'\maketitle' + '\n' + r'\setcounter{page}{2}'))
        for _ in range(3):
            subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error',
                            '-output-directory=' + str(tex.parent), str(tex)],
                           cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        log = tex.with_suffix('.log').read_text()
        if 'Overfull' in log or 'Missing character' in log:
            raise SystemExit('PDF layout or glyph defect; inspect .build/guide.log')
        (ROOT / 'mathematical-prerequisites.pdf').write_bytes(
            tex.with_suffix('.pdf').read_bytes())
        repo = ROOT.parents[1]
        inputs = [SOURCE, ROOT/'header.tex', ROOT/'headers.lua', Path(__file__), repo/'book/references.bib']
        evidence = [repo/'papers'/name for name in (
            'methods-of-mathemacial-for-physicists.pdf',
            'atmospheric-and-oceanic-fluid-dymamics.pdf', 'fno.pdf', 'sfno.pdf')]
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        record = {'date': '2026-11-21',
                  'input_sha256': {str(p.relative_to(repo)): digest(p) for p in inputs},
                  'evidence_sha256': {str(p.relative_to(repo)): digest(p) for p in evidence},
                  'pdf_sha256': digest(ROOT/'mathematical-prerequisites.pdf'),
                  'repository_revision_at_build': subprocess.check_output(['git','rev-parse','HEAD'], cwd=repo, text=True).strip(),
                  'pandoc': subprocess.check_output(['pandoc','--version'], text=True).splitlines()[0],
                  'engine': 'XeLaTeX; three passes; report; A4; 11pt',
                  'book_equations': 'M prefix, source chapter numbering; physical companion owns fluid sequence'}
        (ROOT/'build-record.json').write_text(json.dumps(record, indent=2)+'\n')
        print(ROOT / 'mathematical-prerequisites.pdf')


if __name__ == '__main__':
    main()

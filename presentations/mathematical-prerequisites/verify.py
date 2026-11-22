#!/usr/bin/env python3
"""Verify equations, PDF navigation, and small analytic/numerical examples."""
from pathlib import Path
import argparse
import json
import hashlib
import re
import subprocess
import numpy as np
from numpy.polynomial import legendre as leg
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent


def math_checks():
    checks = []
    def close(name, value, expected, tol=2e-12):
        assert np.allclose(value, expected, rtol=tol, atol=tol), name
        checks.append(name)
    # Polynomial orthogonality, quadrature limits, and the guide's worked fields.
    mu, w = leg.leggauss(8)
    B = leg.legvander(mu, 7) * np.sqrt(2*np.arange(8)+1)
    close('normalized Legendre orthogonality', B.T @ (w[:, None]*B/2), np.eye(8))
    close('constant spherical area', 2*np.pi*w.sum(), 4*np.pi)
    for p in range(16):
        close(f'Gaussian polynomial degree {p}', w @ mu**p, 0 if p % 2 else 2/(p+1))
    mu2, w2 = leg.leggauss(2)
    close('two-node mu squared mean', w2 @ mu2**2/2, 1/3)
    close('two-node fourth power deliberately inexact', w2 @ mu2**4/2, 1/9)
    close('diffusion example initial mean square', w @ (mu**2-1/3)**2/2, 4/45)
    close('spherical harmonic mu squared Parseval', (4*np.pi)/9 + (4/9)*(4*np.pi/5), 4*np.pi/5)
    # Sampling conditions: exact linear recovery and quadratic projection.
    for L in (2, 3, 5):
        n = (3*L+2)//2
        x, wg = leg.leggauss(n)
        pL = leg.Legendre.basis(L)
        p2L = pL*pL
        for j in range(L+1):
            product = p2L*leg.Legendre.basis(j)
            close(f'quadratic Legendre projection L={L},j={j}',
                  wg @ product(x), product.integ()(1)-product.integ()(-1))
    x = 2*np.pi*np.arange(8)/8
    close('DFT alias 6 equals minus 2', np.exp(6j*x), np.exp(-2j*x))
    close('Fourier cosine mean square', np.mean((3*np.cos(2*x))**2), 9/2)
    # Exact covariance count versus the lag-count formula.
    N, r = 20, .8
    C = r**np.abs(np.arange(N)[:, None]-np.arange(N)[None, :])
    lag_variance = (1+2*sum((1-k/N)*r**k for k in range(1, N)))/N
    close('serial sample-mean variance', C.sum()/N**2, lag_variance)
    close('long-series effective count', 900*(1-r)/(1+r), 100)
    close('Rossby beta-plane residual', (-.4/(.4**2+.3**2))*(.4**2+.3**2)+.4, 0)
    close('spherical Rossby residual', (-2*.3*2/(3*4))*(3*4)+2*.3*2, 0)
    close('spectral enstrophy energy ratio change', (4*5)/(2*3), 10/3)
    return checks


def pdf_checks():
    record = json.loads((ROOT/'build-record.json').read_text())
    for name, expected in record['input_sha256'].items():
        assert hashlib.sha256((ROOT.parents[1]/name).read_bytes()).hexdigest() == expected, f'PDF is stale: {name}'
    assert hashlib.sha256((ROOT/'mathematical-prerequisites.pdf').read_bytes()).hexdigest() == record['pdf_sha256']
    assert hashlib.sha256((ROOT/'instructor-solutions.md').read_bytes()).hexdigest() == record['instructor_key_sha256']
    reader = PdfReader(ROOT/'mathematical-prerequisites.pdf')
    pages = [page.extract_text() or '' for page in reader.pages]
    text = '\n'.join(pages)
    source = (ROOT/'mathematical-prerequisites.md').read_text()
    tags = re.findall(r'\\tag\{([^}]+)\}', source)
    for tag in tags:
        assert len(re.findall(r'\('+re.escape(tag)+r'\)', text)) >= 1, f'Missing PDF equation {tag}'
    assert all(page.strip() for page in pages), 'Empty page'
    assert '\ufffd' not in text, 'Replacement glyph'
    assert '[@' not in text, 'Unresolved citation'
    assert 'Solution to Exercise' not in text, 'Instructor solutions leaked into student PDF'
    flat = re.sub(r'\s+', ' ', text)
    objects = re.findall(r'^\*\*((?:Definition|Assumption|Model|Law|Postulate|Result|Example|Counterexample|Remark|Exercise) \d+\.\d+) - ', source, re.M)
    for label in objects:
        assert label in flat, f'Missing teaching object in PDF: {label}'

    destinations = reader.named_destinations
    for number in range(1, 13):
        assert f'chapter.{number}' in destinations, f'Missing chapter destination {number}'
    internal = 0
    for page in reader.pages:
        for ref in page.get('/Annots', []):
            annotation = ref.get_object()
            action = annotation.get('/A', {})
            target = annotation.get('/Dest')
            if action.get('/S') == '/GoTo':
                target = action.get('/D')
            if isinstance(target, str):
                assert target in destinations, f'Broken PDF destination {target}'
                internal += 1
    assert internal >= 60, 'Expected linked chapter and subsection TOC'
    log = (ROOT/'.build/guide.log').read_text()
    assert 'Overfull' not in log, 'Layout overflow in LaTeX log'
    assert 'Missing character' not in log, 'Missing font glyph'
    assert 'undefined references' not in log, 'Unresolved references'
    headers = []
    for i, page in enumerate(pages, 1):
        assert page.splitlines()[-1].strip() == str(i), f'Page number mismatch {i}'
        first = page.splitlines()[:2]
        if re.match(r'^\d+\.', first[0]):
            assert re.match(r'^\d+\.\d+\.', first[1]), f'Missing subsection header on page {i}'
        headers.append({'page': i, 'header': first})
    return {'pages': len(pages), 'numbered_equations': len(tags),
            'internal_links_checked': internal, 'named_destinations': len(destinations),
            'teaching_objects_and_exercises': len(objects),
            'page_headers': headers}


def render():
    from PIL import Image, ImageDraw
    folder = ROOT/'.build/qa'
    folder.mkdir(parents=True, exist_ok=True)
    for pattern in ('page-*.png', 'sheet-*.png'):
        for previous in folder.glob(pattern):
            previous.unlink()
    subprocess.run(['pdftoppm', '-r', '90', '-png',
                    str(ROOT/'mathematical-prerequisites.pdf'), str(folder/'page')], check=True)
    paths = sorted(folder.glob('page-*.png'))[:len(PdfReader(ROOT/'mathematical-prerequisites.pdf').pages)]
    for first in range(0, len(paths), 4):
        images = [Image.open(p).convert('RGB') for p in paths[first:first+4]]
        width, height = images[0].size
        sheet = Image.new('RGB', (2*width, 2*(height+24)), '#dddddd')
        draw = ImageDraw.Draw(sheet)
        for j, image in enumerate(images):
            x, y = (j % 2)*width, (j//2)*(height+24)
            sheet.paste(image, (x, y+24))
            draw.text((x+12, y+5), f'PDF page {first+j+1}', fill='black')
        sheet.save(folder/f'sheet-{first//4+1:02}.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    results = {'mathematical_checks': math_checks(), 'pdf': pdf_checks()}
    (ROOT/'.build/verification.json').write_text(json.dumps(results, indent=2)+'\n')
    if args.render:
        render()
    print(f"Verified {len(results['mathematical_checks'])} mathematical probes; "
          f"{results['pdf']['pages']} pages; {results['pdf']['numbered_equations']} equations; "
          f"{results['pdf']['internal_links_checked']} internal links.")


if __name__ == '__main__':
    main()

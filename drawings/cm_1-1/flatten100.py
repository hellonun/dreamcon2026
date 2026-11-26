# bake the ×100 scale into every coordinate so Illustrator imports the middle table with no transform at all
import re, sys
p = sys.argv[1]; s = open(p).read(); F = 100
num = lambda m: f'{float(m.group(0)) * F:.4f}'.rstrip('0').rstrip('.')
s = s.replace('<g transform="scale(100)">', '').replace('</g>\n</svg>', '</svg>').replace('</g></svg>', '</svg>')
s = re.sub(r' d="([^"]*)"', lambda m: ' d="' + re.sub(r'-?\d+(?:\.\d+)?', num, m.group(1)) + '"', s)
for a in ('cx', 'cy', 'r', 'x', 'y', 'font-size', 'stroke-width'):
    s = re.sub(rf' {a}="(-?\d+(?:\.\d+)?)"', lambda m, a=a: f' {a}="{float(m.group(1)) * F:.4f}"', s)
s = re.sub(r'(<rect) width="(\d+)" height="(\d+)"', lambda m: f'{m.group(1)} width="{int(m.group(2)) * F}" height="{int(m.group(3)) * F}"', s)
s = re.sub(r'rotate\((-?[\d.]+) (-?[\d.]+) (-?[\d.]+)\)', lambda m: f'rotate({m.group(1)} {float(m.group(2)) * F:.4f} {float(m.group(3)) * F:.4f})', s)
open(p, 'w').write(s)

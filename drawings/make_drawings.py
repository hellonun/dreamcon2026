import math
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white

OUT = '/home/claude/drawings/DreamCon2026_Brick-Table_Top-Panel_Drawings.pdf'
PW, PH = landscape(A3)
R = 3500.0          # disc radius, mm
SCALE = 40          # 1:40 at A3
SHEET = (2440, 1220)
INK = black
GREY = Color(0.45, 0.47, 0.52)
LIGHT = Color(0.78, 0.80, 0.85)
ACCENT = Color(0.20, 0.29, 0.80)   # royal, used sparingly
FILL = Color(0.93, 0.89, 0.81)

# Hole set-out, measured from the agreed screenshots, scaled to a 7000 mm disc.
# X = east of centre, Y = north of centre (top of sheet), Ø rounded to 50 mm, centres to 10 mm.
OPTIONS = [
    ('1', 'One hole',      [('H1', 542, 93, 5200)]),
    ('2', 'Two holes',     [('H1', -2214, 523, 1750), ('H2', 1455, 603, 3150)]),
    ('3', 'Three holes',   [('H1', -761, 2144, 1750), ('H2', 2033, 526, 2100), ('H3', -1206, -1013, 3150)]),
]

def clearances(holes):
    rim = min(R - (math.hypot(x, y) + d / 2) for _, x, y, d in holes)
    between = None
    for i in range(len(holes)):
        for j in range(i + 1, len(holes)):
            _, x1, y1, d1 = holes[i]; _, x2, y2, d2 = holes[j]
            g = math.hypot(x1 - x2, y1 - y2) - d1 / 2 - d2 / 2
            between = g if between is None else min(between, g)
    return rim, between

def title_block(c, code, title, scale_txt, sheet_no, sheets):
    x0, y0, w, h = PW - 12 * mm - 120 * mm, 12 * mm, 120 * mm, 46 * mm
    c.setLineWidth(0.6); c.setStrokeColor(INK); c.rect(x0, y0, w, h)
    rows = [(x0, y0 + 30 * mm, w, 16 * mm), (x0, y0 + 15 * mm, w, 15 * mm)]
    c.line(x0, y0 + 30 * mm, x0 + w, y0 + 30 * mm); c.line(x0, y0 + 15 * mm, x0 + w, y0 + 15 * mm)
    c.line(x0 + 60 * mm, y0, x0 + 60 * mm, y0 + 15 * mm); c.line(x0 + 90 * mm, y0, x0 + 90 * mm, y0 + 15 * mm)
    c.setFillColor(INK)
    c.setFont('Helvetica-Bold', 11); c.drawString(x0 + 4 * mm, y0 + 39 * mm, 'Dream Con Fair 2026')
    c.setFont('Helvetica', 8); c.drawString(x0 + 4 * mm, y0 + 33.5 * mm, 'BACC Level L foyer, Bangkok  ·  1–6 Dec 2026  ·  Brick table')
    c.setFont('Helvetica-Bold', 10.5); c.drawString(x0 + 4 * mm, y0 + 23 * mm, title)
    c.setFont('Helvetica', 8); c.drawString(x0 + 4 * mm, y0 + 18 * mm, 'Top panel for scaffold table, CNC cut')
    lab = lambda x, t, v: (c.setFont('Helvetica', 6.5), c.setFillColor(GREY), c.drawString(x + 3 * mm, y0 + 10.5 * mm, t), c.setFont('Helvetica-Bold', 9), c.setFillColor(INK), c.drawString(x + 3 * mm, y0 + 4 * mm, v))
    lab(x0, 'DRAWING', f'DC26-BT-{sheet_no:02d}  ({sheet_no} of {sheets})')
    lab(x0 + 60 * mm, 'SCALE', scale_txt)
    lab(x0 + 90 * mm, 'DATE / REV', '11.11.2026 / A')
    c.setFont('Helvetica', 6.5); c.setFillColor(GREY)
    c.drawString(x0, y0 - 5 * mm, 'All dimensions in millimetres. Do not scale from this drawing. Check before cutting.')

def frame(c):
    c.setStrokeColor(INK); c.setLineWidth(1.0); c.rect(8 * mm, 8 * mm, PW - 16 * mm, PH - 16 * mm)

def arrow(c, x, y, ang, size=2.2 * mm):
    a1, a2 = ang + math.radians(160), ang - math.radians(160)
    p = c.beginPath(); p.moveTo(x, y); p.lineTo(x + size * math.cos(a1), y + size * math.sin(a1)); p.lineTo(x + size * math.cos(a2), y + size * math.sin(a2)); p.close()
    c.drawPath(p, fill=1, stroke=0)

def dim_line(c, x1, y1, x2, y2, text, off=0, ext=True, size=7.5):
    """aligned dimension between two points (page units), text centred above"""
    ang = math.atan2(y2 - y1, x2 - x1); nx, ny = -math.sin(ang), math.cos(ang)
    a = (x1 + nx * off, y1 + ny * off); b = (x2 + nx * off, y2 + ny * off)
    c.setStrokeColor(INK); c.setFillColor(INK); c.setLineWidth(0.35)
    if ext and off:
        for (px, py), (qx, qy) in [((x1, y1), a), ((x2, y2), b)]:
            s = 1.5 * mm * (1 if off > 0 else -1)
            c.line(px + nx * s * 0.6, py + ny * s * 0.6, qx + nx * s, qy + ny * s)
    c.line(*a, *b); arrow(c, a[0], a[1], ang + math.pi); arrow(c, b[0], b[1], ang)
    c.saveState(); c.translate((a[0] + b[0]) / 2 + nx * 1.4 * mm, (a[1] + b[1]) / 2 + ny * 1.4 * mm)
    deg = math.degrees(ang)
    if deg > 90 or deg < -90: deg += 180
    c.rotate(deg); c.setFont('Helvetica', size); c.drawCentredString(0, 0, text); c.restoreState()

def centre_mark(c, x, y, s=4 * mm):
    c.setStrokeColor(INK); c.setLineWidth(0.3); c.setDash([6, 2, 1, 2])
    c.line(x - s, y, x + s, y); c.line(x, y - s, x, y + s); c.setDash()

def plan_sheet(c, code, name, holes, sheet_no, sheets):
    frame(c)
    k = mm / SCALE * 1.0           # mm on the ground -> page points
    cx, cy = 34 * mm + R * k, PH / 2 + 2 * mm
    P = lambda x, y: (cx + x * k, cy + y * k)
    # panel with holes
    c.setLineWidth(1.1); c.setStrokeColor(INK); c.setFillColor(FILL)
    p = c.beginPath(); p.circle(cx, cy, R * k)
    for _, x, y, d in holes: p.circle(*P(x, y), d / 2 * k)
    c.drawPath(p, fill=1, stroke=1, fillMode=0)
    # indicative sheet layout (bottom layer), light
    c.saveState(); p = c.beginPath(); p.circle(cx, cy, R * k)
    for _, x, y, d in holes: p.circle(*P(x, y), d / 2 * k)
    c.clipPath(p, stroke=0, fillMode=1)
    c.setStrokeColor(LIGHT); c.setLineWidth(0.3); c.setDash(3, 2)
    for i in range(-3, 4):
        y = i * SHEET[1] + SHEET[1] / 2 - 0 if False else i * SHEET[1] - SHEET[1] / 2 + 610
        c.line(*P(-R, y), *P(R, y))
    for j, yb in enumerate(range(-3, 4)):
        ystart = yb * SHEET[1] - SHEET[1] / 2 + 610
        offs = 0 if j % 2 == 0 else SHEET[0] / 2
        x = -R - offs
        while x < R:
            c.line(*P(x, ystart), *P(x, ystart + SHEET[1])); x += SHEET[0]
    c.restoreState(); c.setDash()
    # centre lines
    c.setStrokeColor(INK); c.setLineWidth(0.3); c.setDash([10, 3, 2, 3])
    c.line(*P(-R - 300, 0), *P(R + 300, 0)); c.line(*P(0, -R - 300), *P(0, R + 300)); c.setDash()
    c.setFont('Helvetica', 7); c.setFillColor(INK); c.drawString(*(lambda q: (q[0] + 1 * mm, q[1] + 1 * mm))(P(R + 300, 0)), 'X'); c.drawString(*(lambda q: (q[0] + 1 * mm, q[1] + 1 * mm))(P(0, R + 300)), 'Y')
    c.setFont('Helvetica-Bold', 7); c.drawString(*(lambda q: (q[0] + 1.2 * mm, q[1] - 3.2 * mm))(P(0, 0)), 'DATUM 0,0')
    # overall diameter, horizontal, below disc
    dim_line(c, *P(-R, -R), *P(R, -R), 'Ø 7000', off=-10 * mm)
    for xx in (-R, R):
        c.setLineWidth(0.35); c.line(*P(xx, 0), *(lambda q: (q[0], q[1] - 11 * mm))(P(xx, -R)))
    # holes: centre marks, diameters, labels
    for hid, x, y, d in holes:
        hx, hy = P(x, y); centre_mark(c, hx, hy)
        a = math.radians(35)
        dim_line(c, hx - math.cos(a) * d / 2 * k, hy - math.sin(a) * d / 2 * k, hx + math.cos(a) * d / 2 * k, hy + math.sin(a) * d / 2 * k, f'Ø {d}', off=0, ext=False)
        c.setFillColor(ACCENT); c.circle(hx, hy - 7 * mm, 3.2 * mm, fill=1, stroke=0)
        c.setFillColor(white); c.setFont('Helvetica-Bold', 7.5); c.drawCentredString(hx, hy - 7 * mm - 2.6, hid)
    # rim width at the narrowest point of each hole
    for hid, x, y, d in holes:
        ang = math.atan2(y, x); dc = math.hypot(x, y); rim = R - dc - d / 2
        p1 = P((dc + d / 2) * math.cos(ang), (dc + d / 2) * math.sin(ang)); p2 = P(R * math.cos(ang), R * math.sin(ang))
        c.setFillColor(INK); c.setStrokeColor(INK); c.setLineWidth(0.35); c.line(*p1, *p2); arrow(c, *p1, ang + math.pi, 1.6 * mm); arrow(c, *p2, ang, 1.6 * mm)
        tx, ty = P((R + 260) * math.cos(ang), (R + 260) * math.sin(ang)); c.setFont('Helvetica-Bold', 7.5)
        c.drawCentredString(tx, ty - 2.5, f'{round(rim)}')
    # ordinate dimensions to hole centres (X along top, Y along left)
    top = cy + R * k + 14 * mm; left = cx - R * k - 12 * mm
    c.setLineWidth(0.3); c.setStrokeColor(GREY); c.setFillColor(INK)
    xs = sorted(set([0] + [x for _, x, _, _ in holes])); ys = sorted(set([0] + [y for _, _, y, _ in holes]))
    c.setStrokeColor(INK); c.line(cx - R * k, top, cx + R * k, top); c.line(left, cy - R * k, left, cy + R * k)
    for x in xs:
        px = P(x, 0)[0]; c.setStrokeColor(LIGHT); c.setDash(2, 2); c.line(px, top - 2 * mm, px, P(0, max([y for _, xx, y, _ in holes if xx == x] or [0]))[1] if x else cy + R * k + 4 * mm); c.setDash()
        c.setStrokeColor(INK); c.line(px, top - 1.2 * mm, px, top + 1.2 * mm); c.circle(px, top, 0.6 * mm, fill=1, stroke=0)
        c.saveState(); c.translate(px + 1.2 * mm, top + 2 * mm); c.rotate(60); c.setFont('Helvetica', 7.5); c.drawString(0, 0, f'{x:+d}' if x else '0'); c.restoreState()
    lastpy = None
    for y in ys:
        py = P(0, y)[1]; tpy = py if lastpy is None else max(py, lastpy + 4.4 * mm); lastpy = tpy; c.setStrokeColor(LIGHT); c.setDash(2, 2); c.line(left + 2 * mm, py, P(min([x for _, x, yy, _ in holes if yy == y] or [0]), 0)[0] if y else cx - R * k, py); c.setDash()
        c.setStrokeColor(INK); c.line(left - 1.2 * mm, py, left + 1.2 * mm, py); c.circle(left, py, 0.6 * mm, fill=1, stroke=0)
        c.setFont('Helvetica', 7.5); c.drawRightString(left - 2 * mm, tpy - 2.5, f'{y:+d}' if y else '0')
    c.setFont('Helvetica', 6.5); c.setFillColor(GREY)
    c.drawString(cx - R * k, top + 12 * mm, 'X set-out of hole centres from datum (east +)')
    c.saveState(); c.translate(left - 10 * mm, cy - R * k); c.rotate(90); c.drawString(0, 0, 'Y set-out of hole centres from datum (north +)'); c.restoreState()
    # north arrow
    nx, ny = cx + R * k + 8 * mm, cy + R * k - 2 * mm
    c.setFillColor(INK); p = c.beginPath(); p.moveTo(nx, ny + 7 * mm); p.lineTo(nx - 3 * mm, ny); p.lineTo(nx, ny + 2 * mm); p.lineTo(nx + 3 * mm, ny); p.close(); c.drawPath(p, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 8); c.drawCentredString(nx, ny - 4 * mm, 'N')

    # right column: title, table, notes
    rx = cx + R * k + 22 * mm; rw = PW - 12 * mm - rx
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 16); c.drawString(rx, PH - 26 * mm, f'Option {code} · {name}')
    c.setFont('Helvetica', 9); c.setFillColor(GREY); c.drawString(rx, PH - 32 * mm, 'Top panel, plan view, 1:40 at A3')
    # table
    ty = PH - 44 * mm; cols = [0, 18, 42, 66, 90]; hdr = ['Hole', 'X', 'Y', 'Ø', 'Radius']
    c.setFont('Helvetica-Bold', 8); c.setFillColor(INK)
    c.drawString(rx, ty + 2 * mm, 'Cut-out schedule (mm, from datum at disc centre)')
    ty -= 5 * mm
    for i, h in enumerate(hdr): c.drawString(rx + cols[i] * mm, ty, h)
    c.setLineWidth(0.4); c.line(rx, ty - 2 * mm, rx + 110 * mm, ty - 2 * mm)
    rows = [('Disc', 0, 0, 7000)] + [(h, x, y, d) for h, x, y, d in holes]
    c.setFont('Helvetica', 8.5)
    for r_ in rows:
        ty -= 6 * mm
        vals = [r_[0], f'{r_[1]:+d}' if r_[1] else '0', f'{r_[2]:+d}' if r_[2] else '0', f'{r_[3]}', f'{r_[3] // 2}']
        for i, v in enumerate(vals):
            (c.drawString if i == 0 else c.drawRightString)(rx + (cols[i] if i == 0 else cols[i] + 16) * mm, ty, v)
        c.setStrokeColor(LIGHT); c.setLineWidth(0.3); c.line(rx, ty - 2 * mm, rx + 110 * mm, ty - 2 * mm); c.setStrokeColor(INK)
    title_block(c, code, f'Top panel · Option {code} · {name}', '1:40 @ A3', sheet_no, sheets)
    # scale bar
    sx, sy = 26 * mm, 18 * mm
    c.setFont('Helvetica', 7); c.setFillColor(INK); c.setStrokeColor(INK); c.setLineWidth(0.5)
    for i in range(5):
        c.setFillColor(INK if i % 2 == 0 else white); c.rect(sx + i * 1000 * k, sy, 1000 * k, 1.6 * mm, fill=1, stroke=1)
    c.setFillColor(INK)
    for i in range(6): c.drawCentredString(sx + i * 1000 * k, sy - 3.5 * mm, f'{i}')
    c.drawString(sx + 5000 * k + 2 * mm, sy - 3.5 * mm, 'm')

# ---------------- isometric ----------------
def scaffold_parts(holes, step=900, ring=150):
    posts, ledgers = [], []
    def ringp(cx, cy, rad):
        n = max(4, math.ceil(2 * math.pi * rad / step)); pts = [(cx + rad * math.cos(i / n * 2 * math.pi), cy + rad * math.sin(i / n * 2 * math.pi)) for i in range(n)]
        for i, p in enumerate(pts): posts.append(p); ledgers.append((p, pts[(i + 1) % n]))
    ringp(0, 0, R - ring)
    for _, x, y, d in holes: ringp(x, y, d / 2 + ring)
    nring = len(posts)
    ok = lambda x, y: math.hypot(x, y) < R - ring - 350 and all(math.hypot(x - hx, y - hy) > d / 2 + ring + 350 for _, hx, hy, d in holes)
    grid = {}
    n = math.ceil(R / step)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            if ok(i * step, j * step): grid[(i, j)] = (i * step, j * step); posts.append((i * step, j * step))
    for (i, j), p in grid.items():
        for di, dj in ((1, 0), (0, 1)):
            q = grid.get((i + di, j + dj))
            if q: ledgers.append((p, q))
    ringpts = posts[:nring]
    for (i, j), p in grid.items():
        if any((i + a, j + b) not in grid for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            best = min(ringpts, key=lambda q: math.hypot(q[0] - p[0], q[1] - p[1]))
            if math.hypot(best[0] - p[0], best[1] - p[1]) < 1200: ledgers.append((p, best))
    return posts, ledgers

def iso_sheet(c, holes, sheet_no, sheets):
    frame(c)
    H_TOP, T, LIFT = 450.0, 36.0, 1700.0   # top of panel, thickness, explode distance
    s = 0.0255 * mm                         # iso drawing scale (page pts per mm)
    ox, oy = PW * 0.36, PH * 0.27
    cos30, sin30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    def P(x, y, z):  # x east, y north, z up; view from south-east
        u = (x + y) * cos30; v = (y - x) * sin30 + z
        return ox + u * s, oy + v * s
    depth = lambda x, y, z: (x - y) - z * 0.001   # larger = nearer the viewer
    posts, ledgers = scaffold_parts(holes)
    tube_top = H_TOP - T - 24
    items = []
    for (x, y) in posts: items.append((depth(x, y, 0), 'post', (x, y)))
    for a, b in ledgers:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        items.append((depth(mx, my, 0) - 1, 'led', (a, b)))
    items.sort(key=lambda t: t[0])
    # floor shadow ellipse of the disc
    c.setFillColor(Color(0.94, 0.95, 0.97)); p = c.beginPath()
    pts = [P(R * math.cos(t), R * math.sin(t), 0) for t in [i / 120 * 2 * math.pi for i in range(121)]]
    p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]; p.close(); c.drawPath(p, fill=1, stroke=0)
    # scaffold, back to front, with a white halo so crossings read
    for _, kind, d in items:
        if kind == 'post':
            x, y = d; a, b = P(x, y, 0), P(x, y, tube_top)
            c.setStrokeColor(white); c.setLineWidth(2.6); c.line(*a, *b)
            c.setStrokeColor(GREY); c.setLineWidth(1.1); c.line(*a, *b)
            c.setLineWidth(0.6); bp = [P(x - 75, y - 75, 0), P(x + 75, y - 75, 0), P(x + 75, y + 75, 0), P(x - 75, y + 75, 0)]
            q = c.beginPath(); q.moveTo(*bp[0]); [q.lineTo(*t) for t in bp[1:]]; q.close(); c.setFillColor(GREY); c.drawPath(q, fill=1, stroke=0)
        else:
            (ax, ay), (bx, by) = d
            for z in (150, tube_top):
                a, b = P(ax, ay, z), P(bx, by, z)
                c.setStrokeColor(white); c.setLineWidth(2.4); c.line(*a, *b)
                c.setStrokeColor(GREY); c.setLineWidth(0.9); c.line(*a, *b)
    # panel, lifted
    zt, zb = H_TOP + LIFT, H_TOP + LIFT - T
    def ring(cx, cy, rad, z, n=160): return [P(cx + rad * math.cos(t), cy + rad * math.sin(t), z) for t in [i / n * 2 * math.pi for i in range(n + 1)]]
    # leader lines from panel edge down to the scaffold rim
    c.setStrokeColor(ACCENT); c.setLineWidth(0.5); c.setDash(3, 2)
    for t in (math.radians(-45), math.radians(135), math.radians(45 + 90 + 90)):
        c.line(*P(R * math.cos(t), R * math.sin(t), zb), *P((R - 150) * math.cos(t), (R - 150) * math.sin(t), tube_top))
    c.setDash()
    # outer edge band (front half)
    top = ring(0, 0, R, zt); bot = ring(0, 0, R, zb)
    c.setFillColor(Color(0.82, 0.72, 0.55)); c.setStrokeColor(INK); c.setLineWidth(0.8)
    p = c.beginPath(); p.moveTo(*top[0]); [p.lineTo(*q) for q in top[1:]]; [p.lineTo(*q) for q in reversed(bot)]; p.close(); c.drawPath(p, fill=1, stroke=0)
    # bottom silhouette line on the near side
    n = len(bot) - 1
    p = c.beginPath(); started = False
    for i, t in enumerate([i / n * 2 * math.pi for i in range(n + 1)]):
        near = (math.cos(t) - math.sin(t)) > 0
        if near: (p.lineTo if started else p.moveTo)(*bot[i]); started = True
        else: started = False if not started else started
    c.drawPath(p, stroke=1, fill=0)
    # top face with holes
    c.setFillColor(FILL); p = c.beginPath(); p.moveTo(*top[0]); [p.lineTo(*q) for q in top[1:]]; p.close()
    for _, x, y, d in holes:
        hp = ring(x, y, d / 2, zt); p.moveTo(*hp[0]); [p.lineTo(*q) for q in hp[1:]]; p.close()
    c.drawPath(p, fill=1, stroke=1, fillMode=0)
    # inside wall of each hole (far side visible)
    for _, x, y, d in holes:
        ht = ring(x, y, d / 2, zt); hb = ring(x, y, d / 2, zb); nn = len(ht) - 1
        c.setFillColor(Color(0.82, 0.72, 0.55)); c.setStrokeColor(INK); c.setLineWidth(0.5)
        for i in range(nn):
            t = i / nn * 2 * math.pi
            if (math.cos(t) - math.sin(t)) < 0:   # far wall, faces the viewer
                q = c.beginPath(); q.moveTo(*ht[i]); q.lineTo(*ht[i + 1]); q.lineTo(*hb[i + 1]); q.lineTo(*hb[i]); q.close(); c.drawPath(q, fill=1, stroke=0)
        c.setLineWidth(0.8); q = c.beginPath(); q.moveTo(*ht[0]); [q.lineTo(*t) for t in ht[1:]]; c.drawPath(q, stroke=1, fill=0)
        q = c.beginPath(); first = True
        for i in range(nn + 1):
            t = i / nn * 2 * math.pi
            if (math.cos(t) - math.sin(t)) < 0: (q.moveTo if first else q.lineTo)(*hb[i]); first = False
        c.setLineWidth(0.5); c.drawPath(q, stroke=1, fill=0)
    # labels
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 16); c.drawString(20 * mm, PH - 26 * mm, 'Isometric · panel on scaffold (Option 3)')
    c.setFont('Helvetica', 9); c.setFillColor(GREY); c.drawString(20 * mm, PH - 32 * mm, 'Panel shown lifted 1700 mm for clarity. Viewed from the south-east. Not to scale.')
    def callout(x, y, z, tx, ty_, txt):
        a = P(x, y, z); b = (tx * mm, ty_ * mm); right = b[0] >= a[0]
        c.setStrokeColor(INK); c.setLineWidth(0.4); c.line(*a, *b); c.setFillColor(INK); c.circle(*a, 0.8 * mm, fill=1, stroke=0)
        c.setFont('Helvetica', 8.5)
        for i, ln in enumerate(txt.split('\n')): (c.drawString if right else c.drawRightString)(b[0] + (1.5 if right else -1.5) * mm, b[1] - 1 * mm - i * 3.8 * mm, ln)
    t = math.radians(-60)
    callout(R * math.cos(t), R * math.sin(t), zt, 300, 205, 'Top panel, Ø 7000\nsee sheets 01–03')
    _, hx, hy, hd = holes[2]; t = math.radians(-150)
    callout(hx + hd / 2 * math.cos(t), hy + hd / 2 * math.sin(t), zt, 75, 205, 'Holes\nsee sheets 01–03')
    t = math.radians(-75)
    callout((R - 150) * math.cos(t), (R - 150) * math.sin(t), tube_top, 300, 108, 'Rim ring of standards and ledgers\n150 mm in from the panel edge')
    _, hx, hy, hd = holes[1]; t = math.radians(-30)
    callout(hx + (hd / 2 + 150) * math.cos(t), hy + (hd / 2 + 150) * math.sin(t), tube_top, 300, 175, 'Ring of standards round each hole\n150 mm back from the cut edge')
    callout(900, -900, tube_top, 300, 145, 'Infill standards on a 900 mm grid,\nledgers at the top and near the floor,\nØ 48.3 tube on base plates')
    # side notes
    rx = PW - 12 * mm - 120 * mm; ty = PH - 44 * mm
    c.setFont('Helvetica-Bold', 8); c.setFillColor(INK); c.drawString(rx, ty, 'Notes')
    notes = ['Scaffold height: about 400 mm from the floor to the top of the scaffold, so the finished top of the panel sits at +450 mm (to be confirmed). Adjust to suit the panel build.',
             'Scaffold layout is indicative. Supplier to design for the load and confirm spacing.']
    from reportlab.lib.utils import simpleSplit
    c.setFont('Helvetica', 7.8)
    for i, n_ in enumerate(notes, 1):
        lines = simpleSplit(n_, 'Helvetica', 7.8, 112 * mm); ty -= 4.8 * mm; c.drawString(rx, ty, f'{i}.')
        for j, ln in enumerate(lines):
            if j: ty -= 3.7 * mm
            c.drawString(rx + 5 * mm, ty, ln)
    title_block(c, '3', 'Isometric · top panel on scaffold (Option 3)', 'NTS', sheet_no, sheets)

c = canvas.Canvas(OUT, pagesize=landscape(A3))
c.setTitle('Dream Con Fair 2026 · Brick table top panel'); c.setAuthor('Dream Con Fair 2026'); c.setSubject('CNC cutting drawings, Ø 7000 top panel, options A–C')
sheets = len(OPTIONS) + 1
for i, (code, name, holes) in enumerate(OPTIONS, 1):
    plan_sheet(c, code, name, holes, i, sheets); c.showPage()
iso_sheet(c, OPTIONS[2][2], sheets, sheets); c.showPage()
c.save()
for code, name, holes in OPTIONS:
    print(code, [round(v) for v in clearances(holes) if v is not None])
print(OUT)

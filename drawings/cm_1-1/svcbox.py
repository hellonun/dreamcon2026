# Laptop service box under the middle table: 500 x 500 footprint x 450 high, 18 ply, no bottom, stands on the floor.
# CNC sheet at real scale 1:1, labels in cm, Arial (Latin) only. Red = cut, grey = dimensions.
import sys; sys.path.insert(0, '/home/claude/svgt'); from cmconv import cm
OUT = '/home/claude/svgt/DreamCon2026_CNC_laptop-service-box_1-1_cm_RevW.svg'
K = 72 / 25.4                                   # pt per mm at 1:1
T = 18                                          # ply
W = D = 500; H = 450; WH = H - T                # walls under an 18 top
RED, GREY, INK = '#e5483d', '#777777', '#222222'
TD, TT, TN = 30 * K, 46 * K, 22 * K          # text heights: 30 mm dims, 46 mm titles, 22 mm notes
f = lambda v: f'{v * K:.4f}'
out = []
def path(pts, col=RED, w=2.0, close=True):
    d = 'M' + ' L'.join(f'{f(x)},{f(y)}' for x, y in pts) + (' Z' if close else '')
    out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}"/>')
def rect(x, y, w, h, col=RED, w_=2.0): path([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], col, w_)
def slot(cx, cy, L, h):                          # rounded slit, cut
    r = h / 2; x0, x1 = cx - L / 2 + r, cx + L / 2 - r
    out.append(f'<path d="M{f(x0)},{f(cy - r)} L{f(x1)},{f(cy - r)} A{f(r)},{f(r)} 0 0 1 {f(x1)},{f(cy + r)} L{f(x0)},{f(cy + r)} A{f(r)},{f(r)} 0 0 1 {f(x0)},{f(cy - r)} Z" fill="none" stroke="{RED}" stroke-width="2"/>')
def circle(cx, cy, r): out.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="none" stroke="{RED}" stroke-width="2"/>')
def text(x, y, s, size=TD, col=INK, anchor='middle', weight=400, rot=0):
    tr = f' transform="rotate({rot} {f(x)} {f(y)})"' if rot else ''
    out.append(f'<text x="{f(x)}" y="{f(y)}" font-family="Arial, Helvetica, sans-serif" font-size="{size:.2f}" font-weight="{weight}" fill="{col}" text-anchor="{anchor}"{tr}>{s}</text>')
def dim_h(x0, x1, y, label):
    path([(x0, y), (x1, y)], GREY, 1.2, False)
    for x in (x0, x1): path([(x, y - 14), (x, y + 14)], GREY, 1.2, False); path([(x - 7, y + 7), (x + 7, y - 7)], GREY, 2, False)
    text((x0 + x1) / 2, y - 8, cm(label))
def dim_v(x, y0, y1, label):
    path([(x, y0), (x, y1)], GREY, 1.2, False)
    for y in (y0, y1): path([(x - 14, y), (x + 14, y)], GREY, 1.2, False); path([(x - 7, y + 7), (x + 7, y - 7)], GREY, 2, False)
    text(x + 10, (y0 + y1) / 2, cm(label), anchor='middle', rot=90)

# vents: rows of slits, 12 wide, counted from the floor (y up); the page has y down, so a panel of height h at (x0, y0top)
SL = 12
def panel(x0, y0, w, h, title, note, vents=(), holes=(), door=None):
    rect(x0, y0, w, h)
    for (cy, L, xs) in vents:
        for cx in xs: slot(x0 + w / 2 + cx, y0 + h - cy, L, SL)
    for (cx, cy, r) in holes: circle(x0 + w / 2 + cx, y0 + h - cy, r)
    if door:
        dw, dh, dy = door; rect(x0 + (w - dw) / 2, y0 + h - dy - dh, dw, dh)
        text(x0 + w / 2, y0 + h - dy - dh / 2, 'door opening', TN, GREY)
        dim_h(x0 + (w - dw) / 2, x0 + (w + dw) / 2, y0 + h - dy - dh - 30, f'{dw:g}')
        dim_v(x0 + (w + dw) / 2 + 40, y0 + h - dy - dh, y0 + h - dy, f'{dh:g}')
        dim_v(x0 + (w + dw) / 2 + 40, y0 + h - dy, y0 + h, f'{dy:g}')
    text(x0, y0 - 110, title, TT, INK, 'start', 700)
    dim_h(x0, x0 + w, y0 + h + 70, f'{w:g}'); dim_v(x0 - 60, y0, y0 + h, f'{h:g}')
    text(x0, y0 + h + 150, note, TN, GREY, 'start')

SIDE_V = [(70, 80, (-150, -50, 50, 150)), (100, 80, (-150, -50, 50, 150)), (320, 80, (-150, -50, 50, 150)), (350, 80, (-150, -50, 50, 150))]
BACK_V = [(320, 70, (-160, -80, 0, 80, 160)), (350, 70, (-160, -80, 0, 80, 160))]
DOOR = (420, 330, 50)                            # opening w, h, bottom above the floor
X0, Y0, GAP = 140, 260, 260
x = X0
panel(x, Y0, W, WH, 'FRONT · door', 'make 1 · door on the face towards the rim', door=DOOR); x += W + GAP
panel(x, Y0, W, WH, 'BACK', 'make 1 · 2 x 5 vent slits 7 x 1.2 high up, 2 cable holes Ø5 low', vents=BACK_V, holes=[(-120, 70, 25), (120, 70, 25)]); x += W + GAP
panel(x, Y0, D - 2 * T, WH, 'SIDE x 2', 'make 2 · fits between front and back · 4 x 4 vent slits 8 x 1.2, low and high', vents=SIDE_V); x += D - 2 * T + GAP
X1 = x
# second row: top and door leaf
Y1 = Y0 + WH + 560
rect(X0, Y1, W, D); text(X0, Y1 - 110, 'TOP', TT, INK, 'start', 700); dim_h(X0, X0 + W, Y1 + D + 70, f'{W:g}'); dim_v(X0 - 60, Y1, Y1 + D, f'{D:g}')
text(X0, Y1 + D + 150, 'make 1 · sits on the four walls', TN, GREY, 'start')
lx = X0 + W + GAP; lw, lh = DOOR[0] - 6, DOOR[1] - 6
rect(lx, Y1, lw, lh); text(lx, Y1 - 110, 'DOOR LEAF', TT, INK, 'start', 700)
dim_h(lx, lx + lw, Y1 + lh + 70, f'{lw:g}'); dim_v(lx - 60, Y1, Y1 + lh, f'{lh:g}')
for hy in (60, lh - 60): rect(lx + lw - 12, Y1 + hy - 25, 12, 50, GREY, 1.2)          # hinge positions (reference)
circle(lx + 40, Y1 + lh / 2, 9.5)
text(lx, Y1 + lh + 150, 'make 1 · 0.3 gap all round · Ø1.9 cam lock, 2 hinges', TN, GREY, 'start')
# assembly note
nx = lx + lw + GAP
for i, s in enumerate(['LAPTOP SERVICE BOX', 'outside 50 x 50 cm, 45 high · 1.8 ply · no bottom, stands on the floor',
                       'under the middle table, X +86 · Y +191 from the table centre', 'door faces out to the rim · vents: low on the sides, high on the sides and back',
                       'all dimensions in cm · real scale 1:1']):
    text(nx, Y1 + 40 + i * 80, s, TT if i == 0 else TN, INK if i == 0 else GREY, 'start', 700 if i == 0 else 400)
PW, PH = max(X1, nx + 1500), Y1 + D + 260
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(PW)} {f(PH)}" width="{PW / 10:.3f}cm" height="{PH / 10:.3f}cm">',
       f'<rect width="{f(PW)}" height="{f(PH)}" fill="#fff"/>', *out, '</svg>']
open(OUT, 'w').write('\n'.join(svg)); print(OUT, f'{PW / 10:.1f} x {PH / 10:.1f} cm')
